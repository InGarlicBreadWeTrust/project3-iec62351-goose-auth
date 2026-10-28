# PRD — IEC 62351-6 Secure GOOSE verifiability harness

> Defense-direction for rural co-ops / small utilities / BESS-integrators.
> Status: DRAFT v0.1, 2026-10-28.

## 1. Problem
IEC 62351-6:2020 (and the 2026 IEEE P2030.100.2 guide) define how to secure GOOSE /
Sampled Value (SV) on the IEC 61850 substation process bus: Layer-2 message
authentication (HMAC / AES-GMAC) + replay protection, optional encryption (AES-GCM/CBC),
with group keys distributed per IEC 62351-9 (GDOI). Vendors sell IEDs/agents that
**claim** to do this. Today a co-op or small utility has **no open, interoperable way to
verify the claim** — the only reference-grade stack (`libiec61850`) is GPLv3 and does not
implement 62351-6; fresh attempts are unverified and explicitly admit "no interop oracle"
to check the 62351-6 *wire shape*. Result: co-ops must **trust vendor marketing**, which
is exactly the "get sued / get burned later" failure mode this effort is meant to prevent.

## 2. North-star goal
Give an independent operator a **defensible, permissively-licensed, clean-room tool that can
check a vendor's 62351-6 / 62351-9 GOOSE-security claim without requiring the operator to
trust the vendor** — while keeping the project itself **legally defensible** (low SEP
exposure, no conformance claim, no FTO representation). *Secondary:* raise the bar on what
"secured GOOSE means" by fixing the unverified wire shapes into test vectors.

## 3. In scope (v0.1)
- **Conformance/interop harness** for the *published, publicly-known* parts of 62351-6 GOOSE
  security (extended PDU / `Extension` SEQUENCE, `AuthValue` tag, MAC profiles, replay).
- **Test-vector registry** (scaffold + ingestion protocol + provenance), to *grow* a public
  oracle as real secured captures / 2nd implementations surface.
- **Key-management conformance surface** for 62351-9 group-key / GDOI pull-and-check
  (GROUP-PULL, key-ID match, expiry handling) at the *protocol-stub* level.
- **Patent / SEP register + claim-charting SOP** (`patents/README.md`) + `NOTICE.md`.
- **Threat model** (`SECURITY_DESIGN.md`) scoped to the threat 62351-6 actually addresses.
- **License + build approach** sufficient to stand up a real repo.

## 4. Non-goals (hard boundaries — read carefully)
- **Not** a certifiable product, IED, or production GOOSE agent.
- **Not** a claim of IEC 62351-6 / 61850-8-1 conformance or certification.
- **Not** a freedom-to-operate / FTO opinion; **no representation that use is
  non-infringing.** (License is not FTO — see `LICENSE_SEP_ASSESSMENT.md`.
)
- **Do not** ship the unverified 62351-6 framing as if it were settled. Where there is no
  oracle, emit the check as **"provisional"** and log it.
- **Do not** embed GPL code (`libiec61850`, `wendy512`) in a permissive tree. Test-peer
  only, out-of-tree (Docker), un-vendored.
- **Do not** fabricate test vectors. A fabricated "conformance pass" is worse than no pass.

## 5. Users / personas
- **Co-op / small-utility engineer** — wants a one-command "does my IED actually do secure
  GOOSE the way the spec says?" check + a readable report.
- **Vendor (defensive)** — wants to ship to co-ops *and* demonstrate compliance to a skeptic.
- **BESS / DER integrator** — wants to prove a substation-interfacing device's GOOSE
  (breaker/trip signalling) is authenticated before commissioning.
- **Academic / standards reviewer** — wants to submit vectors / challenge a "pass."

## 6. Acceptance criteria (v0.1)
- [ ] `NOTICE.md` (no-FTO / not-certified / clean-room) lives in repo root and is referenced
      from the top of the harness README.
- [ ] `patents/README.md` SOP exists with at least the template + 1 worked example
   (US 20220376923 and/or an IEC 62351-6 framing claim).
- [ ] Threat model scoped to: unauthenticated/replayed/tampered GOOSE *and* the "group-key
   ⇒ any group member can forge any publisher" caveat (auth ≠ publisher-auth ≠ confidentiality).
- [ ] A MAC-profile check table covering HMAC-SHA-256 / AES-GMAC-64/128 with the IV/nonce
   per-publisher caveat made explicit.
- [ ] Replay-protection check surface (window semantics, stale-frame discard) as published.
- [ ] A 62351-9 key-check surface: GROUP-PULL on unknown/expired key, keyID match, expiry.
- [ ] **Honest reporting:** any check lacking a public oracle prints `PROVISIONAL`, not `PASS`.
- [ ] Repo is `git init`-able, Apache-2.0-licensed, with a CI that runs the harness on the
   scaffold and proves the provisional-vs-pass distinction.
- [ ] `docs/landscape.md` records the surveyed OSS repos with license + last activity.

## 7. Key risks (→ mitigations)
| Risk | Mitigation |
| --- | --- |
| SEP/patent exposure on 62351-6 framing + 62351-9 nonce/group-key scheme | mechanism avoidance, patent register, FRAND record, no-FTO NOTICE, provisional checks. See `LICENSE_SEP_ASSESSMENT.md`. |
| **Trap: shipping a permissive *full impl* and implying FTO** | Non-goal §4. Harness-not-product. License ≠ FTO documented. |
| **Trap: fabricating "pass" vectors** | Ingestion provenance required; no oracle ⇒ PROVISIONAL. |
| GPL contamination in a permissive tree | Test-peer out-of-tree; no vendoring; CI license scan (scans for GPL). |
| Wire shape unsettled (no 2nd impl as of 2026-10-28) | Provisional marking vectors; log "no oracle"; invite 2nd-impl submissions. |
| Scope creep into a giant 61850 stack | Hard non-goals; harness is a *thin verifier* over published fields only. |

## 8. Success metric
A co-op can point at a vendor IED and get a **reproducible, legible, honestly-caveated
"the claim holds to X; these checks are PROVISIONAL because no public oracle exists" report**
— and a vendor can run the *same* tool against its own product with confidence the project
won't be pulled for infringement because it is a clearly-labeled, non-certified standard
*verifier* with a FRAND posture and no FTO claim.

## 9. Open questions
- Will the EU SEP Regulation / EUIPO Competence Centre be in force at pilot time? (affects
  the FRAND-safe posture we advise co-ops to adopt — see `LICENSE_SEP_ASSESSMENT.md §3.2`.)
- Is a 62351-6 wire-shape oracle available post-2026-10 (any 2nd impl or real secured
  capture)? Determines HOW many checks can be marked `PASS` vs `PROVISIONAL`.
- Language for the harness: Rust (safety + cross-crypto, mirrors the permissive crypto
  ecosystem) vs Go (matches the cB-Sigma/zig-libs interop peers, easiest test-peer story in
  Docker) vs C (matches `libiec61850` test peer, embeddable). See `BUILD_APPROACH.md`.
