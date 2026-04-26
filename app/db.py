"""Thin Postgres client via PostgREST.

PostgREST is the data-plane HTTP interface in front of Postgres. By default
the FastAPI talks to a local PostgREST container at `http://postgrest:3000`
(see `docker-compose.yml`). Configurable via `POSTGREST_URL` and
`POSTGREST_API_KEY` env vars.

Use as: `from app.db import client; client().table("courses").select(...)`.
"""
from functools import lru_cache
from postgrest import SyncPostgrestClient
from .config import get_settings


@lru_cache
def client() -> "_Client":
    s = get_settings()
    if not s.postgrest_url:
        raise RuntimeError("POSTGREST_URL must be set.")
    # Use URL as-is; the env should already include any path suffix needed.
    rest_url = s.postgrest_url.rstrip("/")
    headers: dict[str, str] = {}
    if s.postgrest_auth:
        if not s.postgrest_api_key:
            raise RuntimeError(
                "POSTGREST_API_KEY required when POSTGREST_AUTH=true."
            )
        headers = {
            "apikey": s.postgrest_api_key,
            "Authorization": f"Bearer {s.postgrest_api_key}",
        }
    pg = SyncPostgrestClient(rest_url, headers=headers)
    return _Client(pg)


class _Client:
    """Shim exposing the same `.table(name)` / `.rpc(name, params)` API the
    existing services use."""

    def __init__(self, pg: SyncPostgrestClient):
        self._pg = pg

    def table(self, name: str):
        return self._pg.from_(name)
