# Security policy

Thanks for helping keep OpenStudy and its users safe.

## Supported versions

OpenStudy is a fast-moving project. Security fixes land on the **`main` branch only**. If you're running a pinned commit or a fork, rebase onto `main` (or cherry-pick the fix) to pick them up.

| Version          | Supported |
| ---------------- | --------- |
| `main` (rolling) | ✅        |
| Older commits    | ❌ — update |

## Reporting a vulnerability

**Please do not open a public GitHub issue**, social media post, or blog entry for security-impacting bugs. Use one of the private channels below:

- **Email:** [security@openstudy.dev](mailto:security@openstudy.dev) — preferred.
- **GitHub private security advisory:** [open one here](https://github.com/openstudy-dev/OpenStudy/security/advisories/new). End-to-end private until the advisory is published.

What to include:

- A clear description of the issue and its potential impact.
- Step-by-step reproduction (URLs, payloads, code, screenshots).
- Your assessment of severity and any suggested fix or mitigation.
- Whether you'd like to be credited publicly when the fix ships.

## What's in scope

- The OpenStudy codebase in this repository (backend, frontend, MCP server, build scripts).
- The hosted service at `openstudy.dev` and its infrastructure (Vercel deployment, Supabase project configuration).
- Any first-party packages we publish to npm / PyPI.

## What's out of scope

- Denial-of-service that requires significant traffic from the reporter.
- Self-XSS (attacks that require the victim to paste attacker-supplied code into their own browser console).
- Missing security headers that don't lead to a concrete, exploitable impact.
- Social-engineering or phishing attempts against maintainers.
- Vulnerabilities in third-party dependencies that are already publicly tracked — please report to the upstream project, then open an issue here asking for an upgrade.
- Reports generated solely by automated scanners with no demonstrated impact.

## What to expect from us

- **Acknowledgement:** within 72 hours on weekdays.
- **Initial triage + severity:** within 7 days.
- **Fix timeline:** depends on severity. Critical issues get same-day / next-day patches; lower-severity issues are scheduled into regular development.
- You'll be kept in the loop through the whole process.

## Coordinated disclosure

- Once a fix is merged to `main` (and, where relevant, deployed to the hosted service), we publish a GitHub Security Advisory — with a CVE if appropriate — and credit the reporter by default.
- Prefer to stay anonymous? Say so and we'll honour it.
- We don't currently offer paid bounties. Substantive reports get a public thank-you, a line in the changelog, and our gratitude.

## Machine-readable contact

RFC 9116 contact file: [`/.well-known/security.txt`](https://openstudy.dev/.well-known/security.txt) (same email, same canonical URL).
