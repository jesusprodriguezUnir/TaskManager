"""Full-text search index over the course tree.

Walks `STUDY_ROOT`, extracts text from PDFs / notebooks / markdown / typst,
and upserts each file's text into the `file_index` table. Search is exposed
via a Postgres RPC (`search_files`) so PostgREST can run ranking and
snippet generation server-side in one round-trip.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from ..db import client
from . import storage as storage_svc

log = logging.getLogger(__name__)

# Extensions we know how to extract text from. PPTX deliberately excluded
# until we add python-pptx; not worth the dep weight today.
_INDEXABLE_SUFFIXES = (".pdf", ".md", ".txt", ".typ", ".ipynb")


def _course_code_from_path(path: str) -> str | None:
    """Top-level folder name is treated as the course code.

    The course tree under STUDY_ROOT is `<course-folder>/...`, where
    `<course-folder>` matches a `course.folder_name` in the database. The
    indexer just records the folder name on each file row; courses table
    is the source of truth for the human-readable name + display code.
    """
    if "/" not in path:
        return None
    return path.split("/", 1)[0] or None


def _extract_text(path: str, data: bytes) -> str | None:
    """Return extracted text, or None if extraction failed/unsupported."""
    if path.endswith(".pdf"):
        try:
            import fitz  # pymupdf
        except ImportError as e:
            log.error("pymupdf not installed: %s", e)
            return None
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            chunks = [page.get_text() for page in doc]
            doc.close()
            return "\n".join(chunks)
        except Exception as e:
            log.warning("PDF extract failed for %s: %s", path, e)
            return None
    if path.endswith((".md", ".txt", ".typ")):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return None
    if path.endswith(".ipynb"):
        try:
            nb = json.loads(data.decode("utf-8", errors="ignore"))
            cells = nb.get("cells", [])
            parts: list[str] = []
            for c in cells:
                src = c.get("source", "")
                if isinstance(src, list):
                    parts.append("".join(src))
                else:
                    parts.append(str(src))
            return "\n\n".join(parts)
        except Exception as e:
            log.warning("ipynb parse failed for %s: %s", path, e)
            return None
    return None


def index_all() -> dict[str, Any]:
    """Walk the entire course tree and index any file whose sha256 differs from
    the stored row (or that's not yet indexed). Returns a stats dict."""
    db = client()
    keys = storage_svc.list_recursive("")

    # Pull existing rows in one go so we don't make 100 round-trips
    existing: dict[str, str] = {}
    try:
        page = db.table("file_index").select("path,sha256").limit(10000).execute()
        for row in page.data or []:
            existing[row["path"]] = row.get("sha256") or ""
    except Exception as e:
        log.warning("could not preload existing rows (table may not exist yet): %s", e)

    indexed = 0
    skipped = 0
    failed = 0
    for path in keys:
        if not path.endswith(_INDEXABLE_SUFFIXES):
            skipped += 1
            continue
        try:
            data = storage_svc.download(path)
        except Exception as e:
            log.warning("download failed %s: %s", path, e)
            failed += 1
            continue
        sha = hashlib.sha256(data).hexdigest()
        if existing.get(path) == sha:
            skipped += 1
            continue
        text = _extract_text(path, data)
        if text is None:
            failed += 1
            continue
        # PostgREST's text columns choke on raw NULs; strip them
        text = text.replace("\x00", "")
        row = {
            "path": path,
            "course_code": _course_code_from_path(path),
            "size": len(data),
            "sha256": sha,
            "text_content": text,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            db.table("file_index").upsert(row, on_conflict="path").execute()
            indexed += 1
        except Exception as e:
            log.warning("upsert failed for %s: %s", path, e)
            failed += 1

    # Drop rows whose paths no longer exist on disk
    pruned = 0
    try:
        all_paths = set(keys)
        for stale in [p for p in existing if p not in all_paths]:
            db.table("file_index").delete().eq("path", stale).execute()
            pruned += 1
    except Exception as e:
        log.warning("prune phase failed: %s", e)

    return {
        "indexed": indexed,
        "skipped": skipped,
        "failed": failed,
        "pruned": pruned,
        "total_seen": len(keys),
    }


def search(q: str, limit: int = 20) -> list[dict[str, Any]]:
    """Query the search_files Postgres RPC. Returns ranked results with snippets."""
    if not q or len(q.strip()) < 2:
        return []
    db = client()
    try:
        resp = db._pg.rpc("search_files", {"q": q.strip(), "lim": limit}).execute()
    except Exception as e:
        log.warning("search rpc failed: %s", e)
        return []
    return resp.data or []
