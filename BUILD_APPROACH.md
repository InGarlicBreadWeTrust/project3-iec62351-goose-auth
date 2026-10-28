# Build Approach

> Defense-direction, 2026-10-28. Goal: stand up a **permissive, clean-room, no-FTO,
> provisional-aware conformance/interop harness**, not a product.

## 1. Clean-room protocol (non-negotiable)
Clean-room is the **legal core**, not a nicety. It (a) defeats copyright copying and (b) removes
the *willful infringement* aggravator. It does **not** defeat a valid literal/equivalent patent
claim — say that plainly.

- **Two-phase barrier.**
  - **Phase A (spec reader / "the clean room"):** a person (and a model) reads ONLY the published
   text (IEC 62351-6 / 62351-9 / 61850-8-1, the IEEE P2030.100.2 2026 guide). Produces a
   **neutral spec sheet** — field names, ordering, tag ids, window rules, *in the abstract*,
   with **no** look at any vendor source, paid reference impl, or vendor capture.
  - **Barrier + audit:** the spec sheet is audited for "did you look at proprietary material?"
   (a second person + a git-branch/commit log attestation). No proprietary artifact may enter.
  - **Phase B (implementer):** writes the harness *only* from the spec sheet. No access to
    Phase-A source notes beyond the neutral sheet during coding.
- **Provenance log per module** (`provenance/<module>.md`): spec section cited, date, who did
   it, attestation "no proprietary material consulted."
- **No reference-impl source** in the repo or CI. Test peers run out-of-tree in Docker
   (see §5). No vendoring of `libiec61850` / `wendy512`.
- **No secrets:** no keys, no vendor PII, no unredacted captures. Capture *metadata + pointer*
   only.

## 2. Language / runtime (decision: **Go**, with a portability note)
- **Go** for v0.1, because: (a) the two closest clean-room peers are Go (`cB-Sigma/iec61850`,
  Apache-2.0) and Zig (`zaxified/zig-libs`, MIT) — a Go harness can interop/test-against the
   Go peer natively; (b) cB-Sigma already ships Docker images + a cross-build matrix (linux
   x86/arm, windows, macos) and a permissive interop-vs-`libiec61850` pattern we want to reuse;
   (c) `crypto` in Go is battle-tested.
- **Portability note:** the *harness logic* should stay language-neutral so a Rust or Zig
   port is cheap. Keep the "check definitions" as data (a declarative check table — JSON/
   YAML spec) decoupled from the executor. A second impl (Rust, mirroring zig-libs) is the
   fastest route to a **second oracle** that can promote `PROVISIONAL`→`PASS`. Recommend a
   Rust port as v0.2 precisely because a *second clean-room* impl is what kills the
   "no 62351-6 oracle" problem.
- **Not C**, despite `libiec61850` being C/goals: C makes safe interop and clean-room harder
   and the GPL reference can't be a permissive base anyway.

## 3. Repo layout
```
grid-ot/project3-iec62351-goose-auth/
  README.md                 # overview + "no FTO, not certified, provisional-aware" banners
  LICENSE                   # Apache-2.0
  NOTICE                    # the no-FTO / clean-room / not-certified disclaimer (mirror NOTICE.md)
  README.md / docs/landscape.md / PRD.md / SECURITY_DESIGN.md
  LICENSE_SEP_ASSESSMENT.md
  patents/                  # running SEP register + claim-chart SOP + worked example
  provenance/               # per-module clean-room audit trail
  conformance/
    checks/                 # declarative check table (JSON/YAML), decoupled from executor
      auth.yaml  replay.yaml  keymgmt.yaml  wire.yaml   # ids: AUTH.1, REPL.1, KEY.1, IV.1, ENC.1, WIRE.1
    executor/               # Go runtime that runs checks on a fixture
      auth.go  iv.go  ...   # thin; crypto via stdlib/golang.org/x/crypto, NO self-written crypto
    reporting/              # PASS / FAIL / PROVISIONAL(reason) report generator
  testvectors/
    README, ingest.md, provenance schema   # ingestion protocol; NO fabricated vectors
    (fixtures captured as METADATA + pointer only; no unredacted frames)
  ci/                       # license scan (flag GPL/vendored), clean-room audit hook, cross-build matrix
  docker/                   # test-peer containers (libiec61850 unsecured GOOSE), NOT vendored
```
Keep the `checks/*` declarative so the executor stays tiny (low surface, low risk) and a
second-language port is a matter of re-driving the same table.

## 4. CI
- **License scan** (`license-eye` / `scanoss` / `gitleaks`): fail the build if a GPL/LGPL
  dependency or any vendored `libiec61850`/`wendy512` appears. (The GPL repos are a top
   contamination risk for a permissive tree — see `LICENSE_SEP_ASSESSMENT.md §4.6`.)
- **Clean-room audit hook:** `git diff` + a "no proprietary material" attestation on
   check-definition commits; require the `provenance/*.md` to be present and non-empty for
   each new check.
- **Cross-build matrix** (reuse cB-Sigma's list): linux x86/arm, windows, macos.
- **Vector integrity:** hashes of every fixture + its PROVISIONAL/PASS status are pinned in
   `testvectors/manifest`; a `PROVISIONAL`→`PASS` transition requires a linked 2nd-impl or
   real-capture reference (see §6) — no silent "just call it pass."
- **No secrets** check (gitleaks) on every PR.
- **Report smoke test:** a deliberately-unsecured GOOSE frame ⇒ the harness prints the right
   "extension absent / unsecured" report *and* marks WIRE.* `PROVISIONAL`.

## 5. Test peers (out-of-tree, Docker only)
- **Unsecured GOOSE/SV:** `libiec61850` (GPLv3, v1.6.2) as a Docker container — the cB-Sigma
   interop pattern. **Do not vendor; do not import its code; do not embed in the permissive
   tree.** It's a *peer test process*, like a black-box IED.
- **TLS / MMS:** `cB-Sigma/iec61850` / `iec62351` (Apache-2.0) as the security-transport
   interop target (they implement 62351-3 TLS + 62351-9 GDOI key delivery, interop-tested vs
   `libiec61850` v1.6.2.1 *for unsecured GOOSE transport only*).
- **Second oracle (v0.2 target):** a Rust port mirroring zaxified/zig-libs' iec62351 module
   — to cross-check framing and enable PROVISIONAL→PASS promotion.

## 6. Oracle / PROVISIONAL→PASS discipline
- A check's status is `PASS` only if it is (a) a check on published behavior *or* (b) a `WIRE.*`
   check with **a linked, traceable 2nd implementation or real secured capture** in
   `testvectors/`. Else it is `PROVISIONAL` with the reason string. No silent upgrades.
- **Ingestion protocol (`testvectors/ingest.md`):** every vector entry must carry: source
   URL + provenance date, capture metadata (no unredacted frame bytes unless separately
   redacted), the 62351-6 check ids it exercises, the implementing peer + its license, and a
   "clean-room attested" flag. No entry without all of these.
- **Anti-fabrication:** the harness's headline property is *honest reporting.* A fabricated
   `PASS` on an unverified wire shape is the most dangerous output this project could produce
   — it's the exact "trust the vendor's claim" failure the co-op was trying to avoid, now
   *worse* because it looks like an independent confirmation.

## 7. Sequence (realistic order of work)
1. Repo + `LICENSE` (Apache-2.0) + `NOTICE` + license scan + gitleaks CI. **Day 1.**
2. `patents/README.md` SOP + 1 worked claim chart (US 20220376923 + IEC 62351-6 framing).      **Week 1.**
3. Threat-model-driven `checks/` table v0.1 (AUTH.1/REPL.1/KEY.1/IV.1/ENC.1/WIRE.1) with
   PROVISIONAL defaults for WIRE.*.                                                          **Weeks 1–2.**
4. Go executor + reporting (PASS/FAIL/PROVISIONAL) + unsecured GOOSE Docker test-peer + a
   smoke test.                                                                               **Weeks 2–3.**
5. `provenance/*.md` attestation for each check; barrier audit log.                          **Ongoing.**
6. v0.2: Rust port for 2nd oracle; first real PROVISIONAL→PASS promotion.                     **Next quarter.**
7. v0.3: co-op pilot with 1 real vendor (FRAND record filed per `patents/`); first real secured
   GOOSE capture ingested under the protocol.

## 8. Done (per PRD §6) when
- Every acceptance box checked; the harness runs on an unsecured GOOSE frame and produces a
   PROVISIONAL-aware report; a `patents/` entry exists; CI (license scan, secrets, clean-room
   hook, cross-build) is green; `NOTICE.md` is at the root and referenced; the unsecured peer
   Docker runs and proves the "unsecured ⇒ extension-absent report" path.

## 9. Open questions
- Exact crypto library choice: `golang.org/x/crypto`/stdlib vs `rust-crypto` crate for the
   Rust port. Recommend stdlib first (fewer supply-chain concerns, smaller CVE surface), crate
   for v0.2 only.
- Whether to also reference 62351-8 RBAC / PKI for a "full chain-of-trust" report path (v0.3+).
- Whether the harness should consume real unredacted captured frames or metadata + pointer
   only (security/IC-SCADA-data-privacy reason: **metadata+pointer only**, per §1 no-secrets).
- Licensing: confirm Apache-2.0 vs dual; and whether a "no-FTO" field in the NOTICE is
   standard enough to be inheritable (it's a NOTICE-style extension, but a plain permissive
   license is the safer default).
