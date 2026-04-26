-- TOTP (RFC 6238) second-factor on the OpenStudy login.
--
-- Stored as a column on the singleton app_settings row so we don't need a
-- separate table. The secret is base32-encoded; protected by service-role
-- access only (RLS-bypassing key).

ALTER TABLE app_settings
  ADD COLUMN IF NOT EXISTS totp_secret  TEXT,
  ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN NOT NULL DEFAULT FALSE;
