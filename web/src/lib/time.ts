import {
  differenceInCalendarDays,
  differenceInHours,
  differenceInMinutes,
  formatISO,
  isToday,
  isTomorrow,
  isThisWeek,
} from "date-fns";
import { formatInTimeZone, toZonedTime } from "date-fns-tz";

export const TZ = "Europe/Berlin";

export const now = () => new Date();

export function fmtBerlin(d: Date | string, pattern: string) {
  return formatInTimeZone(typeof d === "string" ? new Date(d) : d, TZ, pattern);
}

export function fmtDate(d: Date | string) {
  return fmtBerlin(d, "EEE, d MMM yyyy");
}

export function fmtDateShort(d: Date | string) {
  return fmtBerlin(d, "d MMM");
}

export function fmtDateTime(d: Date | string) {
  return fmtBerlin(d, "EEE d MMM, HH:mm");
}

export function fmtTime(d: Date | string) {
  return fmtBerlin(d, "HH:mm");
}

export function fmtIsoDate(d: Date) {
  return formatISO(d, { representation: "date" });
}

export type RelativeSeverity = "done" | "past" | "urgent" | "soon" | "later" | "far";

export function relative(
  target: Date | string,
  reference: Date = now()
): { label: string; severity: RelativeSeverity } {
  const t = typeof target === "string" ? new Date(target) : target;
  const mins = differenceInMinutes(t, reference);
  const hours = differenceInHours(t, reference);
  const days = differenceInCalendarDays(t, reference);

  if (mins < -60) {
    if (days <= -1) return { label: `${Math.abs(days)}d ago`, severity: "past" };
    return { label: `${Math.abs(hours)}h ago`, severity: "past" };
  }
  if (mins < 0) return { label: "just now", severity: "past" };
  if (mins < 60) return { label: `in ${mins}m`, severity: "urgent" };
  if (hours < 24) return { label: `in ${hours}h`, severity: hours < 6 ? "urgent" : "soon" };
  if (days === 0) return { label: "today", severity: "urgent" };
  if (days === 1) return { label: "tomorrow", severity: "soon" };
  if (days <= 3) return { label: `in ${days}d`, severity: "soon" };
  if (days <= 7) return { label: `in ${days}d`, severity: "later" };
  return { label: `in ${days}d`, severity: "far" };
}

export function humanWhen(d: Date | string): string {
  const date = typeof d === "string" ? new Date(d) : d;
  const zoned = toZonedTime(date, TZ);
  if (isToday(zoned)) return `Today, ${fmtTime(date)}`;
  if (isTomorrow(zoned)) return `Tomorrow, ${fmtTime(date)}`;
  if (isThisWeek(zoned, { weekStartsOn: 1 })) return fmtBerlin(date, "EEEE, HH:mm");
  return fmtDateTime(date);
}

export const weekdayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const weekdayLabelsShort = ["M", "T", "W", "T", "F", "S", "S"];

// Week-of-semester: 1-based count from the configured semester_start date.
// Returns null if the semester start is unknown; returns 0 before it begins.
export function semesterWeek(now: Date, startIso: string | null | undefined): number | null {
  if (!startIso) return null;
  const start = new Date(startIso + "T00:00:00");
  const ms = now.getTime() - start.getTime();
  if (ms < 0) return 0;
  return Math.floor(ms / (7 * 24 * 60 * 60 * 1000)) + 1;
}

// ISO-8601 calendar week number (1..53). Used as a fallback when no
// semester_start is configured.
export function isoWeek(d: Date): number {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  return Math.ceil(((date.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
}
