# Feasibility Verdict — IEC 62351-6 secure-GOOSE reference/verifier
> Defense-direction, 2026-10-28. Bottom line up top, then the "why."

## TL;DR (the recommendation)
**Skip a permissive full stack. Build a permissively-licensed, clean-room, PROVISIONAL-aware
conformance/interop TEST HARNESS + a patent register + a claim-charting SOP. Do not ship a
certifiable product. Do not imply freedom-to-operate.**

Why (one line each):
- *Full stack* is **technically feasible but legally/admissibly wrong** for a "help not get
   sued" defense-direction effort: the only complete stack (`libiec61850`) is **GPLv3 and does
   not implement 62351-6**; the permissive fresh attempts (cB-Sigma, Apache-2.0) ship **no
   conformance oracle**; and a **permissive license grants *distribution* freedom, not
   *patent FTO***.
- *Interop/conformance harness* is **feasible, materially lower SEP exposure, and fills the real
   gap** (a co-op's ability to verify vendor claims), with the honesty property that turns it
   into a liability *reducer* rather than a liability *multiplier*.

## Feasible vs not
| Option | Feasible? | SEP/patent exposure | Recommended? | Why |
|---|---|---|---|---|
| **Permissive full IED/GOOSE agent stack (62351-6 + 62351-9)** | Technically feasible; **not admissible** for this goal | **HIGH** (implements the exact wire shape the patent register flags) | **NO** | No permissive complete stack exists; GPL blocks forking; no oracle to certify; permissive ≠ FTO; "not certified" but product-shaped = high "get sued" risk. |
| **Spec-to-spec conformance/interop test harness + patent register** | **Feasible** | **LOW–MEDIUM and *manageable*** | **YES (primary)** | It's a *test of the standard*, not a product; PROVISIONAL marking + clean-room + FRAND record keep it defensible; it directly serves co-ops' "verify the vendor" need without us claiming conformance. |
| **Vendor-specific FTO opinion / "this IED is safe" service** | Feasible but legal-heavy | HIGH per-engagement | **NO as a build; YES as a paid external service later** | Out of scope for a scaffold; belongs to counsel, not the repo. |
| **Skip / do nothing** | — | — | **NO** | Doing nothing *is* the gap we're trying to close; the co-ops stay blind. |

## Is a permissive stack feasible *and* safe? Honest accounting
- **License axis — feasible.** You *can* license fresh, original work permissively (Apache-2.0
   *with its §3 patent grant and a NOTICE field* is the right permissive choice). No permissive
   license is "blocked" by SEP existence on its face.
- **FTO axis — NOT feasible via license.** A permissive license does **not** give freedom-to-
   operate, does not license-around a pre-existing SEP, and does not indemnify third-party
    patent claims. SEP exposure on the 62351-6 framing + 62351-9 group-key/nonce scheme is **real
   and unavoidable**; it can only be *managed* (FRAND good-faith record + claim charting +
    mechanism avoidance + no-FTO disclaimer), not *removed* by a code license. Residual:
    MEDIUM and permanent.
- **GPL contamination — the real license-killer,** not SEPs. The two complete references
    (`libiec61850`, `wendy512`) are GPLv3. Embedding or forking them into a permissive co-op
    project **forces the result to GPL**, or — worse for a co-op — taints a permissive build.
    Rule: **test-peer only, out-of-tree (Docker), never vendored.**
- **Oracle — the real gap.** No second implementation **and** no real secured capture exists to
    check the 62351-6 wire shape. So a *certifiable* permissive reference **cannot exist yet**;
    the *verifier that honestly reports "PROVISIONAL"* **can** and **is the deliverable**.
- **No Rust 61850 reference exists** — filling it would be the new, defensible thing, and is the
    path to unblocking PROVISIONAL→PASS for WIRE.*.

## Why the harness is safer (the legal shape of it)
- **Exposure falls with product-shaped surface.** A product-shaped, certifiable, embeddable
   stack is exactly what invites a "you're making/using a patented method" claim AND the
    "you marketed it as conformant" aggravation. A *test harness with a PROVISIONAL-aware,
    not-certified, no-FTO posture* is a materially different, lower-exposure artifact: it's a
    verifier *about* the standard that **cannot itself be marked conformant or shipped into a
    product**, so the "willful/marketed-as-conformant" aggravator doesn't attach to the harness
    itself.
- **FRAND good-faith posture is where injunctions are defensible — not the license.** With a
   documented FRAND/FTO posture + claim chart + the EU SEP framework's mandatory 9-month
    FRAND-determination-before-court path, the anti-injunction shield is a **posture you adopt
   in the repo's process**, not a clause of `LICENSE`.
- **Clean-room kills two of the three "sued" vectors.** It defeats copyright copying and the
   *willful* infringement aggravator; it can't defeat a valid literal/equivalent claim, and we
   say so.
- **No-FTO + not-certified + PROVISIONAL** is the project's headline *anti*-liability property.
   A fabricated PASS is the single worst thing this project could emit (it's the "trust the
    vendor" failure, now dressed up as an independent verdict).

## What "done" looks like (from `PRD.md §6`, restated as the safety bar)
1. `NOTICE.md` / `LICENSE` Apache-2.0 at the root; `NOTICE` carries the no-FTO / not-certified /
   clean-room / provisional-aware disclaimer.
2. `patents/README.md` running register + 1 worked claim chart (US 20220376923 + IEC 62351-6
   framing).
3. `checks/` table v0.1: AUTH.1 / REPL.1 / KEY.1 / IV.1 / ENC.1 / WIRE.1 with **PROVISIONAL**
   defaults for WIRE.*/ENC.* and the IV-reuse footgun first-class.
4. Go executor + PASS/FAIL/PROVISIONAL reporting; `libiec61850` as a Docker **test peer only**.
5. `provenance/*.md` audit trail per check; CI license-scan (fails on GPL/vendored), gitleaks
   (no secrets), clean-room hook, cross-build matrix.
6. v0.2 (next quarter): Rust port = 2nd oracle; first honest PROVISIONAL→PASS promotion.
7. v0.3: co-op pilot with 1 real vendor, FRAND record filed, first real secured capture ingested.

## Honest caveats (state these *in the repo*, not just here)
- **Residual SEP risk is real and permanent.** We can manage it (FRAND record + clean-room +
   per-mechanism avoiding + no-FTO notice), not eliminate it. The 62351-6 framing and 62351-9
   nonce/group-key scheme are the highest-exposure zones; prefer FRAND/public-domain primitives
   and abstain from flagged-specific mechanisms over shipping them.
- **"PROVISIONAL" is not "PROBLEM."** Until a 2nd impl or secured capture exists, the harness
   *cannot* say "this IED is 62351-6 compliant" — we report "provisional; no oracle." That's the
   feature, not the bug.
- **This is not legal advice.** Everything here is an engineering *risk posture* for a project
   whose explicit goal is "help not get sued." A co-op deploying 62351-6 in production needs a
    **real FTO opinion + a FRAND negotiation** with the relevant SEP holders and IP counsel in
    the relevant jurisdiction. The EU SEP framework / EUIPO Competence Centre (2025+) is the
    *process* to adopt, not a *guarantee* of safety.
- **What we did NOT research in this pass:** exact SPDX tag for `polepakamo/GOOSE-ASCON-*`;
    `openMUC/IEC61850` / `libiec61850bean2` / `djfarrelly/iec61850bean` real slugs (404'ed
    that day); whether the EU SEP framework's EUIPO Competence Centre is live yet; whether a
    2nd 62351-6 wire-shape impl or real secured capture has surfaced since 2026-10-28. See
    `LICENSE_SEP_ASSESSMENT.md §6` for the same checklist plus the patent register to start.

## Decision (recorded)
**Ship the harness. Skip the stack. License permissive (Apache-2.0, with NOTICE). Maintain a
running patent register + FRAND record + claim chart. Mark WIRE.*/ENC.* checks PROVISIONAL by
default. Never ship a certifiable product or imply FTO. Target the Rust 2nd-impl port as v0.2.**
