---
name: threat-check
description: Use when reviewing a change for security as the security-reviewer, or whenever code touches untrusted input, auth, secrets, files, network, crypto or dependencies, for a structured threat checklist and the audit commands per stack.
---

# Threat check

## Steps
1. **Map the trust boundaries.** List where untrusted data enters the changed code (user
   input, files, network, environment, other services), and where privileged actions happen.
   **Done when:** each entry point and each privileged action in the diff is listed.
2. **Walk the checklist** for each entry point.
   **Done when:** each item is marked ok, a finding, or not applicable.
3. **Run the audits** for each stack (below) and read the results. A clean exit isn't enough
   if there are warnings.
   **Done when:** each audit's output is summarised in the findings.
4. **Demonstrate** each critical/major finding with a test or a reproduction, redacting any real secrets.

## Checklist
| Category | Questions |
|---|---|
| Spoofing / auth | Is identity checked on every new path? Are tokens validated (signature, expiry, audience)? |
| Tampering / input | Is every input validated for type, length, range and format at the boundary? Is a parser used instead of a regex where a grammar is involved? |
| Injection | SQL with bound parameters only? Shell commands without string concatenation? Templates auto-escaped? Paths normalised and confined to a base directory? |
| Deserialisation | Is untrusted data deserialised into arbitrary types (pickle, BinaryFormatter, YAML load)? |
| Authorisation | Is there an owner or role check on every object access, not just at the UI? |
| Information disclosure | Are secrets, tokens or PII kept out of logs, errors and URLs? Are error messages generic to callers? |
| Denial of service | Are sizes, recursion depth, timeouts and rate limits bounded? Can a regex backtrack catastrophically? |
| Secrets | Are there no hard-coded secrets? Is config read from the environment or a vault? Is the `builtin:secrets` gate clean? |
| Crypto | Are only vetted libraries used? No custom crypto, no ECB, no MD5/SHA1 for security, random from a CSPRNG? |
| Memory safety (cpp, unsafe rust) | Bounds checks, lifetimes, integer overflow in size calculations? Are sanitizers run in CI? |
| Supply chain | Is each new dependency needed, maintained, licence-compatible, and pinned in the lockfile? Do install scripts run? |

## Audit commands
| Stack | Command |
|---|---|
| python | `pip-audit`, `bandit -r <src>` |
| javascript / typescript | `npm audit --audit-level=high` |
| rust | `cargo audit`, `cargo deny check` |
| go | `govulncheck ./...` |
| dotnet | `dotnet list package --vulnerable --include-transitive` |
| cpp | `cppcheck`, a sanitizer build (`-fsanitize=address,undefined`) running the tests |
| any | `gitleaks detect` (used by `builtin:secrets` when installed) |
