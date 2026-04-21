// Locale list used by Settings → Semester picker. We only ship English + German
// for now; the label is the actual date format so users pick by sample, not by
// language name (the field is "Date format", not "Language").
function sampleDate(locale: string): string {
  // Fixed reference date so the option labels are stable across renders and
  // unambiguous about ordering (year is recognisable regardless of locale).
  const ref = new Date(2026, 0, 21); // 21 Jan 2026
  try {
    return new Intl.DateTimeFormat(locale).format(ref);
  } catch {
    return locale;
  }
}

export const LOCALE_OPTIONS: { value: string; label: string }[] = [
  { value: "en-US", label: sampleDate("en-US") },
  { value: "en-GB", label: sampleDate("en-GB") },
  { value: "de-DE", label: sampleDate("de-DE") },
];

// Full IANA timezone list via Intl.supportedValuesOf — supported in Chrome 99+,
// Safari 15.4+, Firefox 93+. Falls back to a short curated list if unavailable.
const FALLBACK_TIMEZONES = [
  "UTC",
  "Europe/Berlin",
  "Europe/London",
  "Europe/Paris",
  "Europe/Madrid",
  "Europe/Rome",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Sao_Paulo",
  "Asia/Tokyo",
  "Asia/Shanghai",
  "Asia/Singapore",
  "Asia/Dubai",
  "Asia/Kolkata",
  "Australia/Sydney",
];

function loadTimezones(): string[] {
  try {
    const intl = Intl as typeof Intl & {
      supportedValuesOf?: (key: string) => string[];
    };
    if (typeof intl.supportedValuesOf === "function") {
      return intl.supportedValuesOf("timeZone");
    }
  } catch {
    // fall through
  }
  return FALLBACK_TIMEZONES;
}

export const TIMEZONE_OPTIONS: string[] = loadTimezones();
