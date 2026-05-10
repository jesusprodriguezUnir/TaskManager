/**
 * i18n bootstrap — English + German + Spanish.
 *
 * The language is derived from the user's saved `locale` in app_settings
 * (the Date-format dropdown in Settings). `de-*` maps to German; `es-*`
 * maps to Spanish; every other locale falls through to English. On first
 * render we use whatever is in localStorage (saved by AppShell) so there's
 * no flash of English.
 */
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "@/locales/en.json";
import de from "@/locales/de.json";
import es from "@/locales/es.json";

export type AppLanguage = "en" | "de" | "es";

const LS_KEY = "openstudy:lang";

export function languageFromLocale(locale: string | null | undefined): AppLanguage {
  if (!locale) return "en";
  const lower = locale.toLowerCase();
  if (lower.startsWith("de")) return "de";
  if (lower.startsWith("es")) return "es";
  return "en";
}

function readInitial(): AppLanguage {
  if (typeof localStorage !== "undefined") {
    const raw = localStorage.getItem(LS_KEY);
    if (raw === "de" || raw === "en" || raw === "es") return raw;
  }
  if (typeof navigator !== "undefined") {
    const navLang = navigator.language?.toLowerCase();
    if (navLang?.startsWith("de")) return "de";
    if (navLang?.startsWith("es")) return "es";
  }
  return "en";
}

export function currentLanguage(): AppLanguage {
  if (i18n.language === "de") return "de";
  if (i18n.language === "es") return "es";
  return "en";
}

export function getDateLocale(lang: string): string {
  if (lang === "de") return "de-DE";
  if (lang === "es") return "es-ES";
  return "en-GB";
}

/** Explicit user choice set via the picker. If true, the auto-sync from
 * settings.locale is ignored — the user's pick wins until they change it. */
const MANUAL_KEY = "openstudy:lang-manual";
export function hasExplicitLanguage(): boolean {
  if (typeof localStorage === "undefined") return false;
  return localStorage.getItem(MANUAL_KEY) === "1";
}
export function markLanguageExplicit(): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(MANUAL_KEY, "1");
}

void i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      de: { translation: de },
      es: { translation: es },
    },
    lng: readInitial(),
    fallbackLng: "en",
    interpolation: { escapeValue: false },
    returnEmptyString: false,
  });

export function setLanguage(lang: AppLanguage): void {
  if (i18n.language === lang) return;
  void i18n.changeLanguage(lang);
  try {
    localStorage.setItem(LS_KEY, lang);
  } catch {
    /* ignore */
  }
}

export default i18n;
