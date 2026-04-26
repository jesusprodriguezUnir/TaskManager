"""Walk the course_files bucket and (re)index full-text content.

Run this once after creating the file_index table:
    uv run --no-sync python scripts/index_files.py

Triggered automatically by /api/internal/index-files after each Moodle sync.
Idempotent — re-runs are cheap because rows are skipped when sha256 matches.
"""
import logging
import sys
from pathlib import Path

# Allow running from anywhere by putting the repo root on sys.path
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

from app.services.file_index import index_all  # noqa: E402

if __name__ == "__main__":
    stats = index_all()
    print(f"indexer done: {stats}")
