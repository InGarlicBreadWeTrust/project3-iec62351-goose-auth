# grid-ot / project3 — IEC 62351-6 Secure GOOSE reference (DEFENSE-DIRECTION)

Status: **DRAFT v0.1 — research + scaffold.** Not certified. No conformance claim.
No freedom-to-operate (FTO) warranty. For a cooperative / small-utility audience.
Goal of this project: **help co-ops and small utilities NOT get sued** — i.e. let them
*verify vendor security claims* instead of being blind to them.

> **One-sentence verdict (from `FEASIBILITY_VERDICT.md`):** Do **not** build a permissive
> full stack (a permissive license buys you distribution freedom, *not* patent
> freedom-to-operate, and the only complete stack — `libiec61850` — is GPLv3 and
> doesn't implement 62351-6 anyway). **Do** build a permissively-licensed
> **spec-to-spec conformance/interop test harness + patent-register + claim-charting
> tool**, clean-room, public-domain/FRAND crypto, with an explicit no-FTO disclaimer.
> That is the maximum *defensible* artifact for a "help not get sued" defense-direction
> effort.

## Why this exists
IEC 62351-6:2020 (+ the 2026 IEEE P2030.100.2 guide) specifies how to secure GOOSE /
Sampled Value PDUs on the IEC 61850 process bus (Layer-2 authentication + replay
protection, with optional encryption). For years **there was no open, interoperable
implementation a co-op could actually run to test a vendor's claim** that "our GOOSE is
secure." This project supplies that missing verifiability layer **as a test of the
standard**, which carries materially less standard-essential-patent (SEP) exposure than
shipping a certifiable product.

## What is (and isn't) here
- **In:** harness design; threat model; spec-derived check list; test-vector registry
  scaffold; patent/SEP register + claim-charting skeleton; license + build approach; an
  honest feasibility verdict. Plus a clean-room protocol that keeps you out of copyright
  *and* willful-infringement trouble.
- **Out:** no production IED/GSE agent, no certifiable stack, no claim of
  62351-6 conformance, and — critically — **no representation that this code is
  infringing-free.** A permissive license does not grant freedom-to-operate.

## Files
| File | What it is |
| --- | --- |
| `README.md` | this page |
| `PRD.md` | problem → goals → non-goals → acceptance → risks |
| `SECURITY_DESIGN.md` | 62351-6 threat model, MAC profiles, replay, GDOI/62351-9 key mgmt |
| `LICENSE_SEP_ASSESSMENT.md` | license feasibility vs SEP/FRAND; what a permissive license does/doesn't buy |
| `BUILD_APPROACH.md` | clean-room method, tech choice, module layout, CI, the harness build |
| `FEASIBILITY_VERDICT.md` | honest feasible-vs-not; full-impl vs interop-harness vs skip |
| `docs/landscape.md` | surveyed OSS repos with license + language + last activity |
| `NOTICE.md` | the legal disclaimer every downstream must inherit (no FTO, not certified) |
| `patents/README.md` | SOP for a running patent + claim chart |
| `conformance/README.md` | the harness's target module layout |
| `testvectors/README.md` | how vectors get in (and how to avoid the trap of fabricating them) |

## Provenance (all claims trace)
Research performed 2026-10-28 via web search + GitHub page inspection (API was rate/403-gated
that day; HTML landing pages + raw LICENSE used). Every factual line about a third-party repo is
reproducible — URLs in `docs/landscape.md`.

## License & disclaimer
This scaffold (these documents) is released **Apache-2.0** (`LICENSE`). Apache-2.0 §3's express
patent grant is the strongest *permissive* posture but grants freedom only against **the
project's own contributors'** patents — **nothing** about pre-existing SEPs in IEC 61850 /
62351. Read `LICENSE_SEP_ASSESSMENT.md` and `NOTICE.md` before relying on any of this.
**Not legal advice. Consult qualified IP counsel and obtain your own FRAND/FTO position.**
