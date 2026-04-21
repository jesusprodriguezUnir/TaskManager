-- Add user-selected visual theme. Null / missing = editorial (the current
-- default Claude Design look). Other shipped values: minimal, terminal, dense.
-- Free text column rather than an enum so new themes can land without a
-- migration; the client whitelists known values.
alter table app_settings
  add column if not exists theme text default 'editorial';
