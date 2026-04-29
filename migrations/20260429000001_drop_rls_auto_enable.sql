-- Drop the unused rls_auto_enable() function. Audit on 2026-04-29
-- confirmed it's wired to no event trigger and no other function
-- references it. It was scaffolding for a never-built RLS-on-create
-- policy; removing reduces audit surface.

DROP FUNCTION IF EXISTS public.rls_auto_enable() CASCADE;
