-- Migración para la integración de Google Calendar y Autenticación

ALTER TABLE public.app_settings
ADD COLUMN IF NOT EXISTS google_access_token text,
ADD COLUMN IF NOT EXISTS google_refresh_token text,
ADD COLUMN IF NOT EXISTS google_token_expires_at timestamp with time zone,
ADD COLUMN IF NOT EXISTS google_email text;

CREATE TABLE IF NOT EXISTS public.google_calendar_events (
    id text PRIMARY KEY,
    summary text NOT NULL,
    description text,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    color_id text,
    html_link text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

CREATE TRIGGER trg_updated_at 
BEFORE UPDATE ON public.google_calendar_events 
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE INDEX IF NOT EXISTS idx_google_calendar_events_start 
ON public.google_calendar_events (start_time);
