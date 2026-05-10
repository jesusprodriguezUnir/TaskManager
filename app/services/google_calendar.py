import json
from datetime import datetime, timezone
from urllib.parse import urlencode

import httpx

from .. import db
from ..config import get_settings


async def get_google_oauth_url(redirect_uri: str) -> str:
    settings = get_settings()
    if not settings.google_client_id:
        raise ValueError("Google Client ID not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/calendar.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def exchange_google_code(code: str, redirect_uri: str) -> str:
    """Exchanges code for tokens, saves them, returns user email."""
    settings = get_settings()
    
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to exchange token: {resp.text}")
        
        token_data = resp.json()
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token") # might be absent if already consented
        expires_in = token_data["expires_in"]
        
        # Get user info
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        email = user_resp.json().get("email")

    # Save to db
    query = """
        UPDATE app_settings 
        SET google_access_token = %s,
            google_token_expires_at = now() + interval '%s seconds',
            google_email = %s
    """
    args = [access_token, expires_in, email]
    
    if refresh_token:
        query += ", google_refresh_token = %s "
        args.append(refresh_token)
        
    query += " WHERE id = 1"
    
    await db.execute(query, *args)
    return email


async def _get_valid_access_token() -> str | None:
    row = await db.fetchrow("""
        SELECT google_access_token, google_refresh_token, 
               extract(epoch from (google_token_expires_at - now())) as seconds_left
        FROM app_settings WHERE id = 1
    """)
    if not row or not row.get("google_access_token"):
        return None
        
    if row["seconds_left"] and row["seconds_left"] > 60:
        return row["google_access_token"]
        
    # Refresh needed
    refresh_token = row.get("google_refresh_token")
    if not refresh_token:
        return None
        
    settings = get_settings()
    data = {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://oauth2.googleapis.com/token", data=data)
        if resp.status_code != 200:
            return None # e.g. revoked
            
        token_data = resp.json()
        new_access = token_data["access_token"]
        expires_in = token_data["expires_in"]
        
        await db.execute(
            "UPDATE app_settings SET google_access_token = %s, google_token_expires_at = now() + interval '%s seconds' WHERE id = 1",
            new_access, expires_in
        )
        return new_access


async def pull_from_google() -> None:
    """Fetch events from Google Calendar and update local DB."""
    access_token = await _get_valid_access_token()
    if not access_token:
        return
        
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Simple strategy: fetch next 50 upcoming events
    params = {
        "timeMin": now_iso,
        "maxResults": 50,
        "singleEvents": "true",
        "orderBy": "startTime",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if resp.status_code != 200:
            return
            
        events = resp.json().get("items", [])
        
    # Upsert events into google_calendar_events
    for item in events:
        event_id = item["id"]
        summary = item.get("summary", "Sin título")
        description = item.get("description")
        color_id = item.get("colorId")
        html_link = item.get("htmlLink")
        
        # DateTime or Date
        start_time = item["start"].get("dateTime") or item["start"].get("date")
        end_time = item["end"].get("dateTime") or item["end"].get("date")
        
        await db.execute("""
            INSERT INTO google_calendar_events (id, summary, description, start_time, end_time, color_id, html_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                summary = EXCLUDED.summary,
                description = EXCLUDED.description,
                start_time = EXCLUDED.start_time,
                end_time = EXCLUDED.end_time,
                color_id = EXCLUDED.color_id,
                html_link = EXCLUDED.html_link,
                updated_at = now()
        """, event_id, summary, description, start_time, end_time, color_id, html_link)

async def get_google_events():
    return await db.fetch("SELECT * FROM google_calendar_events ORDER BY start_time ASC")
