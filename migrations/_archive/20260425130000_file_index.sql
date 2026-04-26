-- Full-text search across course materials.
--
-- Schema: one row per indexed file. text_content is the extracted text
-- (PDF body, notebook cells, markdown source). search_vector is a generated
-- tsvector using the 'simple' config (no stemming) so German + English
-- words both match exactly without lossy stem rewrites.

CREATE TABLE IF NOT EXISTS file_index (
  path         TEXT PRIMARY KEY,
  course_code  TEXT,
  size         BIGINT,
  sha256       TEXT,
  text_content TEXT,
  search_vector TSVECTOR
    GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text_content, ''))) STORED,
  indexed_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS file_index_search_idx
  ON file_index USING gin(search_vector);

CREATE INDEX IF NOT EXISTS file_index_course_idx
  ON file_index(course_code);

-- RPC: search_files(q, lim)
-- Returns ranked matches with a 60-char headline snippet around the first hit.
-- Called via PostgREST: POST /rest/v1/rpc/search_files {"q": "...", "lim": 20}
CREATE OR REPLACE FUNCTION search_files(q TEXT, lim INT DEFAULT 20)
RETURNS TABLE(
  path TEXT,
  course_code TEXT,
  size BIGINT,
  rank REAL,
  snippet TEXT
) AS $$
  WITH query AS (
    SELECT websearch_to_tsquery('simple', q) AS tsq
  )
  SELECT
    f.path,
    f.course_code,
    f.size,
    ts_rank(f.search_vector, query.tsq) AS rank,
    ts_headline(
      'simple',
      f.text_content,
      query.tsq,
      'StartSel=<<,StopSel=>>,MaxFragments=2,MaxWords=15,MinWords=5,FragmentDelimiter=" … "'
    ) AS snippet
  FROM file_index f, query
  WHERE f.search_vector @@ query.tsq
  ORDER BY rank DESC
  LIMIT lim;
$$ LANGUAGE SQL STABLE;
