"""Course files browser API — backed by the Supabase `course_files` bucket.

Two endpoints, both session-auth-gated:
  GET /files/list?prefix=…     → list entries (folders + files) at that prefix
  GET /files/signed-url?path=… → short-lived URL for direct-from-Supabase download
"""
from __future__ import annotations

import unicodedata
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from ..auth import require_auth
from ..services import storage as storage_svc


_UMLAUT_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
})


def _sanitize_path(p: str) -> str:
    """Match scripts/sync_semester_to_bucket.py's sanitisation so uploads from
    the app land at the same key a local sync would produce."""
    s = p.translate(_UMLAUT_MAP)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    # collapse consecutive slashes, strip leading slash
    parts = [seg for seg in s.split("/") if seg]
    return "/".join(parts)


router = APIRouter(prefix="/files", tags=["files"], dependencies=[Depends(require_auth)])


@router.get("/list")
async def list_files(prefix: str = Query(default=""), limit: int = Query(default=500, le=1000)) -> list[dict[str, Any]]:
    """List entries at the given prefix. Not recursive — drill down by passing
    a folder's path as the next prefix. Returns a sorted list of
    {name, path, type, size?, content_type?, updated_at?}."""
    clean = (prefix or "").strip().strip("/")
    entries = storage_svc.list_files(prefix=clean, limit=limit)
    out: list[dict[str, Any]] = []
    for e in entries:
        name = e.get("name") or ""
        if not name:
            continue
        path = f"{clean}/{name}" if clean else name
        if e.get("id") is None:
            out.append({"name": name, "path": path, "type": "folder"})
        else:
            meta = e.get("metadata") or {}
            out.append(
                {
                    "name": name,
                    "path": path,
                    "type": "file",
                    "size": meta.get("size"),
                    "content_type": meta.get("mimetype"),
                    "updated_at": e.get("updated_at"),
                }
            )
    # Folders first, then files — each alphabetised
    out.sort(key=lambda e: (0 if e["type"] == "folder" else 1, e["name"].lower()))
    return out


@router.get("/signed-url")
async def signed_url(path: str = Query(...), expires_in: int = Query(default=3600, ge=60, le=86400)) -> dict[str, Any]:
    """Mint a signed URL for the given object path. Default 1-hour expiry so
    the browser can cache the PDF response for reasonable repeat views."""
    if not path or ".." in path:
        raise HTTPException(400, "invalid path")
    try:
        url = storage_svc.signed_url(path, expires_in=expires_in)
    except Exception as exc:
        raise HTTPException(404, f"not found: {exc}") from exc
    return {"url": url, "expires_in": expires_in}


@router.post("/upload-url")
async def upload_url(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Mint a single-use upload URL for the browser to PUT the file directly
    to Supabase (bypasses Vercel's function body limit for large uploads).

    Body: {path: string}. Path is sanitised server-side so it ends up keyed
    the same way our local-sync script would key it.
    """
    raw = (body.get("path") or "").strip().strip("/")
    if not raw or ".." in raw:
        raise HTTPException(400, "invalid path")
    key = _sanitize_path(raw)
    if not key:
        raise HTTPException(400, "path empty after sanitisation")
    try:
        result = storage_svc.signed_upload_url(key)
    except Exception as exc:
        raise HTTPException(500, f"failed to sign upload: {exc}") from exc
    return result


def _safe_key(raw: str) -> str:
    """Reject traversal, normalise slashes. Empty result raises."""
    cleaned = (raw or "").strip().strip("/")
    if not cleaned or ".." in cleaned:
        raise HTTPException(400, "invalid path")
    return cleaned


@router.delete("")
async def delete(
    path: str = Query(...),
    kind: str = Query(default="file", pattern="^(file|folder)$"),
) -> dict[str, Any]:
    """Delete a file or a whole folder (recursive) from the bucket."""
    key = _safe_key(path)
    if kind == "file":
        try:
            storage_svc.delete([key])
        except Exception as exc:
            raise HTTPException(500, f"failed to delete: {exc}") from exc
        return {"deleted": [key]}

    # folder: list everything under prefix and bulk-delete
    try:
        children = storage_svc.list_recursive(key)
    except Exception as exc:
        raise HTTPException(500, f"failed to list folder: {exc}") from exc
    if not children:
        # supabase has no real folders — nothing to delete is a no-op
        return {"deleted": []}
    try:
        storage_svc.delete(children)
    except Exception as exc:
        raise HTTPException(500, f"failed to delete folder: {exc}") from exc
    return {"deleted": children}


@router.post("/folder")
async def create_folder(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Create an empty folder. Supabase Storage has no folder primitive — we
    upload a `.keep` placeholder so the prefix shows up in listings."""
    raw = (body.get("path") or "").strip().strip("/")
    if not raw or ".." in raw:
        raise HTTPException(400, "invalid path")
    key = _sanitize_path(raw)
    if not key:
        raise HTTPException(400, "path empty after sanitisation")
    placeholder = f"{key}/.keep"
    try:
        storage_svc.upload(placeholder, b"", content_type="application/octet-stream")
    except Exception as exc:
        raise HTTPException(500, f"failed to create folder: {exc}") from exc
    return {"folder": key, "placeholder": placeholder}


@router.post("/move")
async def move(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Rename or move a file or folder within the bucket.

    Body: {from, to, kind: "file"|"folder"}. For files, calls Supabase
    `/object/move` once. For folders, lists every descendant and moves each.
    """
    src = _safe_key(body.get("from") or "")
    dst_raw = (body.get("to") or "").strip().strip("/")
    if not dst_raw or ".." in dst_raw:
        raise HTTPException(400, "invalid destination")
    dst = _sanitize_path(dst_raw)
    if not dst:
        raise HTTPException(400, "destination empty after sanitisation")
    kind = body.get("kind") or "file"
    if kind not in ("file", "folder"):
        raise HTTPException(400, "kind must be file or folder")
    if src == dst:
        return {"moved": []}
    if kind == "file":
        try:
            storage_svc.move(src, dst)
        except Exception as exc:
            raise HTTPException(500, f"failed to move: {exc}") from exc
        return {"moved": [{"from": src, "to": dst}]}

    # folder: list children, move each preserving relative path
    try:
        children = storage_svc.list_recursive(src)
    except Exception as exc:
        raise HTTPException(500, f"failed to list folder: {exc}") from exc
    moved: list[dict[str, str]] = []
    for child in children:
        rel = child[len(src) :].lstrip("/")
        new_path = f"{dst}/{rel}" if rel else dst
        try:
            storage_svc.move(child, new_path)
            moved.append({"from": child, "to": new_path})
        except Exception as exc:
            raise HTTPException(
                500, f"failed mid-move at {child}: {exc} ({len(moved)} moved so far)"
            ) from exc
    return {"moved": moved}
