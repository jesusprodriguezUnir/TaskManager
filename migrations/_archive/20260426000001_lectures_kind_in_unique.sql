-- Backfill: Supabase's `lectures` table was migrated outside the migration
-- folder to use UNIQUE (course_code, kind, number) instead of the original
-- UNIQUE (course_code, number). This file recreates that change so the local
-- self-hosted Postgres matches the live data shape (two rows can share
-- (course_code, number) as long as `kind` differs — e.g., a lecture and an
-- exercise both numbered 0 for the same course).
--
-- Idempotent: only re-creates the constraint if the old one is still present.

begin;

do $$
begin
  if exists (
    select 1 from pg_constraint
    where conname = 'lectures_course_code_number_key'
      and conrelid = 'public.lectures'::regclass
  ) then
    alter table public.lectures
      drop constraint lectures_course_code_number_key;
  end if;

  if not exists (
    select 1 from pg_constraint
    where conname = 'lectures_course_kind_number_key'
      and conrelid = 'public.lectures'::regclass
  ) then
    alter table public.lectures
      add constraint lectures_course_kind_number_key
        unique (course_code, kind, number);
  end if;
end $$;

commit;
