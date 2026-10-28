# docs/landscape.md — surveyed OSS for IEC 62351-6 / 61850 secure-GOOSE references
> Snapshot 2026-10-28. Sources: GitHub landing pages + raw `LICENSE` (HTML path; GitHub API was
> 403/rate-gated that day, HTML used — every URL below is reproducible). "Last activity" is the
> proxy the landing page exposed (Created / most recent release / "Updated" date / release count /
> star-fork counts). Where the exact last-push wasn't shown, it says "created …, releases to
> vX". **Nothing below is an interop certificate; "secure/GOOSE" is each project's self-claim.**

## Headline finding
> **There is no interoperable, permissively-licensed, independently-verified reference of the
> IEC 62351-6 GOOSE security *extension* (the 0x85 tag / `AuthValue` field order / BER
> `Extension` framing) as of 2026-10-28.** Two independent clean-room attempts (cB-Sigma,
> Apache-2.0; zaxified/zig-libs, MIT) both explicitly state there is **no public 62351-6
> implementation or real secured capture to check the wire shape against** — which is also the
> reason a verifier must mark WIRE.* checks `PROVISIONAL`, and why this project is the gap to
> fill, not the product to ship.

## Table
| repo | lang | license | last activity (proxy) | 62351-6 GOOSE security? | Verdict / why |
|---|---|---|---|---|---|
| `cB-Sigma/iec61850` | Go | **Apache-2.0** | Created 2026-10-11; interop vs `libiec61850` v1.6.2.1 dated 2026-10-11; Docker + cross-build | **Yes — but unverified.** Extends to 62351-3 TLS + 62351-4 + 62351-6 (HMAC/GMAC/AES-GCM) + 62351-9 GDOI, **interop for unsecured GOOSE/SV transport only**; "Not certified; no conformance claim" | **Most relevant.** Permissive; the clean-room reference to *port or test-against*. Not a 62351-6 conformance oracle. No 2nd impl to peer with. |
| `cB-Sigma/iec62351` | Go | **Apache-2.0** | Created 2026-10-11; 0★ / 1 tag; pure security-seams monorepo | **Partially.** 62351-3 TLS + CRL/OCSP + **62351-9 GDOI key mgmt + KMS** + 62351-8 RBAC; the 62351-6 seams live in `cB-Sigma/iec61850` which imports here | Good **key-mgmt** surface. Permissive. Unverified. Part of the same fresh cluster. |
| `zaxified/zig-libs` (module `iec62351`) | **Zig** (not Rust; task said Rust) | **MIT** | Created 2026-07-10; 9★ / 9 releases; **active** (many modules) | **As a security seam — clean-room, self-declared "no public 62351-6/4/3 implementation or capture … (as of 2026-08-08 verified)."** Operates on PDU bytes only, parses no PDU | Permissive and clean-room; the **best 2nd-impl target for a Rust/Zig port**. Confirms the "no oracle" gap independently. |
| `mz-automation/libiec61850` | C | **GPL-3.0** | Created 2017-02-10; 1237★ / 618 forks; 23 releases; v1.6.2; **very active** | **No.** Implements 62351-3 TLS + 62351-4 client/server auth **only**; no 62351-6 GOOSE security extension + "no conformance testing performed" disclaimer + MZ commercial license for enterprise use | **Canonical 61850 stack, but GPLv3 = cannot be a permissive base; also lacks 62351-6 entirely.** Use as a **Docker test peer only**, out-of-tree. |
| `wendy512/iec61850` | Go (cgo) | **GPL-3.0** | Stale (Go v1.0-61C wrapper; no recent release signal) | No — wraps `libiec61850`; inherits its TLS-only + GPLv3 | GPL cgo wrapper; not embeddable; not a target. |
| `otfabric/go-iec61850` | Go (pure) | **MIT** | Created 2026-03-20; 0★ / 2 forks; **13–14 releases, active** | **No — MMS + Model + Report + Controls; no security extension in scope** | Permissive, no-cgo pure-Go MMS. Good as an **MMS base** but not as a 62351-6 reference. Candidate only if the scope widens to MMS auth (62351-4). |
| `beanit/iec61850bean` (a.k.a. OpenIEC61850) | Java | **Apache-2.0** | "Updated Jul 6, 2023"; 186★ / 96 forks; MMS client/server + **62351-3 TLS** | **No 62351-6** (MMS/TLS only; stale ~3 yrs, not actively maintained) | Permissive Java, but no 62351-6; too old to be a current peer. Reference-for-history only. |
| `polepakamo/GOOSE-ASCON-*` (POLEP) | C (academic) | "for academic and research use" (single-file, **need to confirm exact SPDX; likely permissive but unconfirmed**) | Created 2026-07-25; 0★ / 1 release | **Off-standard: uses ASCON-AEAD (NIST SP 800-232)** not HMAC/GMAC, +nonce + sliding-window; built on `libIEC61850` v1.5.3 | **Best design *reference* for the IV/nonce footgun (this very attack is in `SECURITY_DESIGN`: "reused key+nonce ⇒ anyone forges any frame").** Not permissive-confirmable, not standard-aligned. Read for design, don't fork. |
| IEEE P2030.100.2 (IEEE guide, 2026) | — | IEEE (copyright, not permissive) | 2026, new | **The 2026 implementer guide** for "Securing GOOSE and SV using IEC 62351-6 and IEC 62351-9" | **Authoritative source**, not a codebase. Read it; quote the framing/nonce parts into `checks/` and `SECURITY_DESIGN`. |
| `mgeier/pygoose`, `mgeyer` pygoose | Python | (lib, permissive family; exact SPDX to confirm) | — | GOOSE client; unsecured (no 62351-6) | Not a 62351-6 peer; skip for this project unless the scope widens to GOOSE client-side. |
| openMUC/IEC61850 — 404 | — | — | — | — | Slug changed or not at that path; see note below |
| `djfarrelly/iec61850bean` — 404 | — | — | — | — | The real beanit repo is `beanit/iec61850bean` (above). No separate djfarrelly one. |

> Note (2026-10-28, GitHub API 403/rate-gated): `libiec61850bean2`, `openMUC/IEC61850`,
> `libiec61850bean/iec61850bean` all 404'ed that day. Likely path renames under beanit or
> openMUC org, or archived. Re-verify slugs on next research pass. `Rust iec61850` search
> returned "No results found" — confirming **no Rust 61850 reference exists yet** (a gap worth
> filling if the v0.2 2nd-impl port proceeds).

## Cross-cutting findings that drive the recommendation
1. **Permissive *license* ≠ permissive *FTO*.** Three of the four most complete 62351-6-ish
   attempts carry permissive or permissive-family code licenses (Apache-2.0, MIT) — good. But
   none claims FTO, none is certified, and none has a 2nd-impl or capture to certify its
   `WIRE.*`.
2. **The canonical full stack is GPL — cannot be permissively forked or embedded.** `libiec61850`
   is GPLv3; `wendy512` inherits it. A permissive per-co-op project must be **fresh clean-room**,
   not a fork.
3. **Two independent clean-room attempts confirm the "no oracle" gap** and both ship **no
   interop certificate** — this is the space to fill *safely as a verifier, not as a product*.
4. **No Rust 61850 reference exists yet** (web search: No results found) — a v0.2 2nd-impl
   port would be the *new* thing, and it's what unblocks `PROVISIONAL`→`PASS` for `WIRE.*`.
5. **IEEE P2030.100.2 (2026)** is the new guide — a *very* recent, directly-on-topic
   implementer reference worth pulling `checks/` and `SECURITY_DESIGN` from.
6. **62351-8 RBAC / 62351-3 TLS / 62351-9 GDOI are the *adjacencies* that make "secured GOOSE"
   real.** cB-Sigma/iec62351 is the only permissive 62351-9 GDOI reference; pair your own 62351-6
   verifier with a 62351-9 key-check, don't build a 62351-9 server from scratch.
