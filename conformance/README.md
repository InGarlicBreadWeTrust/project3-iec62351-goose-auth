# conformance/README.md — the harness's target layout

> Defense-direction, 2026-10-28. **Verifier, not product.** Every check that has no public
> oracle prints `PROVISIONAL` with a reason, never `PASS` silently.

## Module layout (v0.1)
```
conformance/
  checks/                # DECLARATIVE check definitions (data, not code)
    auth.yaml            # AUTH.1, IV.1
    replay.yaml          # REPL.1
    keymgmt.yaml         # KEY.1
    wire.yaml            # WIRE.*  (tag/tag-order/BER framing — PROVISIONAL @2026-10-28)
  executor/              # Go runtime that runs a check on a fixture
    harness.go           # loads checks/*.yaml, dispatches
    auth.go              # AUTH.1: recompute MAC with group key + (optional) IV; compare
    iv.go                # IV.1: assert per-publisher IV existence + non-repeat under GMAC (T4)
    reporting.go         # PASS / FAIL / PROVISIONAL(reason) + "not certified" footer
  reporting/
    report.go            # machine + human report; NO conformance/cert claim wording
  docker/
    libiec61850-secured/ # UNSECURED GOOSE peer (libiec61850 v1.6.2) — OUT-OF-TREE, not vendored
```
`checks/*.yaml` is **decoupled** from the executor so a Rust port (v0.2 2nd-impl target)
re-drives the same table — that's how we get `PROVISIONAL`→`PASS` for WIRE.* without a
code-rewrite.

## Check id → definition (v0.1 set; from `SECURITY_DESIGN.md §4`)
- `AUTH.1`  — MAC key = publication/group key; `AuthValue` covers APDU *before* the
   extension tag; for GMAC, per-publisher IV that does not repeat. Oracle: PARTIAL
   (MAC primitive known; wire shape PROVISIONAL).
- `IV.1`    — IV/nonce source exists, per-publisher, non-repeat. Oracle: PUBLIC
   (IV must exist & vary); the *construction* PROVISIONAL (T4 footgun first-class).
- `REPL.1`  — window over `(stNum, sqNum, TAL)`; stale ⇒ discard; current ⇒ accept;
   retransmits not dropped. Oracle: PUBLIC (published window semantics).
- `KEY.1`   — unknown keyID ⇒ transition to failure + GROUP-PULL + alarm; expired key ⇒
   same + "key delivery failed/expired". Oracle: PUBLIC.
- `ENC.1`   — AES-GCM/CBC decrypt + tag verify (only where encryption is on — and only when
   the 3 ms trip budget isn't a concern). Oracle: PROVISIONAL.
- `WIRE.*`  — `Extension` tag (`0x85` per spec readings), `AuthValue` field order, BER
   `Extension` framing. Oracle: **PROVISIONAL @2026-10-28** — no public/2nd-impl or real
   secured capture. Mark every WIRE.* result `PROVISIONAL: no oracle` until then.

## Reporting grammar (fixed, non-negotiable)
- `PASS`    — check ran, oracle exists, result matches; **no conformance claim** appended.
- `FAIL`    — check ran, oracle exists, result doesn't match.
- `PROVISIONAL: <reason>`   — no oracle (or "wiring unconfirmed"); result printed but
   not asserted as a conformance verdict.
- Every report ends with: **"This is not a certification and does not confer conformance.
  No freedom-to-operate is implied. PROVISIONAL results cannot be read as conformance. See
  NOTICE."**

## Hard invariants (CI must check these)
1. **No secret, no key, no unredacted capture bytes** in `conformance/` or `testvectors/`.
2. **No GPL / LGPL / vendored `libiec61850` or `wendy512`** under `conformance/executor/`.
3. **Every `PROVISIONAL`** carries a reason string; **no silent PASS.**
4. **Every `PASS` has a linked `testvectors/` entry with a 2nd-impl or real-capture pointer.**
5. **No claim wording** like "conformant / certified / passes 62351-6" in any public output.

## Out of scope (restate for the executor authors)
- **No packet-pumping loop, no raw-socket IED, no GOOSE agent loop** — keep the executor
  a *verifier over fixtures*, not a *GOOSE agent*.
- **No 62351-8 RBAC / PKI** in v0.1 (reference it, don't implement; v0.3+).
- **No 62351-9 server** in v0.1 — key check is a protocol *stub* against fixtures.
- **No cert claim.**
