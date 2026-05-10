import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { KeyRound, Loader2, ShieldCheck } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useLogin, useSession } from "@/lib/queries";
import { ApiError } from "@/lib/api";
import { Wordmark } from "@/components/brand/wordmark";
import { useDocumentTitle, useHtmlLang } from "@/lib/document-head";

export default function Login() {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const session = useSession();
  const login = useLogin();

  useDocumentTitle();
  useHtmlLang();
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [needsTotp, setNeedsTotp] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const next = new URLSearchParams(location.search).get("next") ?? "/app";

  if (session.data?.authed) {
    return <Navigate to={next} replace />;
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr(null);
    try {
      await login.mutateAsync({ password, totp_code: needsTotp ? totpCode : undefined });
      if (next.startsWith("/oauth") || next.startsWith("/mcp") || next.startsWith("/.well-known")) {
        window.location.href = next;
      } else {
        navigate(next, { replace: true });
      }
    } catch (e) {
      if (e instanceof ApiError) {
        // ApiError.detail is unwrapped: when FastAPI returns {"detail": "x"},
        // detail is the string "x" (not an object).
        const detailStr = typeof e.detail === "string"
          ? e.detail
          : (e.detail as { detail?: string } | undefined)?.detail;
        if (e.status === 429) {
          setErr(t("login.tooMany", "Too many attempts. Try again in a few minutes."));
        } else if (e.status === 401 && detailStr === "totp_required") {
          setNeedsTotp(true);
          setErr(null);
        } else if (e.status === 401 && detailStr === "invalid totp code") {
          setErr(t("login.totpWrong", "Wrong 6-digit code. Try again."));
          setTotpCode("");
        } else if (e.status === 401) {
          setErr(t("login.wrong"));
          setNeedsTotp(false);
          setTotpCode("");
        } else {
          setErr(e.message);
        }
      } else {
        setErr(t("common.failed"));
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-bg">
      <div className="w-full max-w-sm flex flex-col items-center">
        <div className="mb-8 flex items-center justify-center text-fg">
          <Wordmark className="h-16 md:h-20" title={t("login.brand", "OpenStudy")} />
        </div>

        <div className="w-full card p-6 md:p-7 flex flex-col gap-5 shadow-xl shadow-black/20">
          <div>
            <h2 className="text-base font-semibold">{t("login.title")}</h2>
            <p className="text-xs text-muted mt-1">
              {t("login.intro", "Enter your password to continue.")}
            </p>
          </div>
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-muted">{t("login.password")}</span>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
                <input
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoFocus={!needsTotp}
                  disabled={needsTotp}
                  className="w-full bg-surface-2 border border-border/60 rounded-md pl-10 pr-3 py-2.5 text-sm text-fg placeholder:text-subtle focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-bg disabled:opacity-60"
                  placeholder="••••••••••••"
                />
              </div>
            </label>

            {needsTotp && (
              <label className="flex flex-col gap-1.5">
                <span className="text-xs font-medium text-muted">{t("login.totp", "6-digit code from your authenticator")}</span>
                <div className="relative">
                  <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    autoComplete="one-time-code"
                    value={totpCode}
                    onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ""))}
                    required
                    autoFocus
                    className="w-full bg-surface-2 border border-border/60 rounded-md pl-10 pr-3 py-2.5 text-sm tracking-[0.3em] text-fg placeholder:text-subtle focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
                    placeholder="123456"
                  />
                </div>
              </label>
            )}

            {err && (
              <p className="text-xs text-critical bg-critical/10 border border-critical/30 rounded-md px-3 py-2">
                {err}
              </p>
            )}

            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => { window.location.href = "/api/auth/google/login"; }}
                className="touch-target inline-flex items-center justify-center gap-2 rounded-md bg-surface-2 border border-border/60 text-fg text-sm font-medium px-4 py-2.5 hover:bg-surface-3 transition-colors"
              >
                <svg viewBox="0 0 24 24" className="w-5 h-5">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  <path fill="none" d="M1 1h22v22H1z" />
                </svg>
                {t("login.continueWithGoogle", "Continuar con Google")}
              </button>
              
              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/40"></span>
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-bg px-2 text-muted">{t("login.or", "O")}</span>
                </div>
              </div>

              <button
                type="submit"
                disabled={login.isPending || !password}
                className="touch-target inline-flex items-center justify-center gap-2 rounded-md bg-primary text-primary-fg text-sm font-medium px-4 py-2.5 disabled:opacity-60 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
              >
                {login.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> {t("login.signingIn", "Signing in…")}
                  </>
                ) : (
                  t("login.submit")
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
