# The reference conformance executor (Python v0.1)

A PROVISIONAL-aware conformance/interop harness for IEC 62351-6 secure GOOSE/SV.
It re-drives the **language-neutral declarative check table** (`../checks/*.yaml`)
so that a second implementation (Go/Rust, v0.2) can run the *same* table with no
code rewrite. **This is a verifier that cannot say PASS it shouldn't.**

## Run

    python3 -c "import yaml" 2>/dev/null || pip install -r requirements.txt
    python3 smoke_test.py          # invariant checks; non-zero exit on violation
    python3 run_harness.py                # human + machine report
    python3 run_harness.py --machine      # JSON only

## Status grammar (four-valued)

- **PASS**        — behaviour matches the public/declared expectation (oracle PUBLIC, or PARTIAL for a primitive).
- **FAIL**        — behaviour clearly deviates from public expectation (oracle PUBLIC).
- **PROVISIONAL** — no decisive oracle: no public/2nd-implementation oracle or real 62351-6
                    secured capture. **The report cannot be read as conformance.**
- **SKIPPED**     — the frame does not exercise the behaviour (e.g. unsecured frame, no MAC to verify).

## Anti-fabrication property

`model.enforce_ceiling()` forces **PROVISIONAL** on every check whose `oracle: PROVISIONAL`
or `hard_ceiling: PROVISIONAL`, **regardless of internal logic** — including a *successful
decryption that could not be cross-checked against a trusted implementation's tag*. WIRE.*
and ENC.* can never return PASS until such an oracle appears (see `../README.md` §4,
`../../testvectors/README.md`).

## Outputs

Every report carries a fixed **NO-CERT footer** and CI greps for forbidden wording
(`conformant`, `certified`, `passes 62351-6`, `is 62351-6 compliant`). See
`../../NOTICE.md`.
