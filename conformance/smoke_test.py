#!/usr/bin/env python3
"""smoke_test.py -- prove the invariants that make this harness *a verifier that
cannot say PASS it shouldn't*:

   1. An UNSECURED GOOSE frame prints "extension absent / unsecured" with WIRE.* PROVISIONAL.
   2. The harness CAN report FAIL when behaviour is wrong (replay / dead-key fixtures).
   3. WIRE.* / ENC.* NEVER return PASS in any fixture (anti-fabrication hard cap).

Exits non-zero if any invariant is violated. This is the BUILD_APPROACH 4 smoke test.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from executor import checks, model
from executor import fixtures
from executor.harness import _run_one


def _check(ok, label):
    tag = "PASS" if ok else "FAIL"
    print("  [" + tag + "] " + label)
    return ok


def main():
    results = True

     # INV.1 / INV.2: unsecured frame -> WIRE/ENC PROVISIONAL, AUTH SKIPPED.
    u = {r.check_id: r for r in _run_one(fixtures.UNSECURED)}
    results &= _check(
         u.get("WIRE.1") and u["WIRE.1"].status == model.PROVISIONAL,
         "INV.1  unsecured frame -> WIRE.1 is PROVISIONAL (never PASS)")
    results &= _check(
         u.get("ENC.1") and u["ENC.1"].status == model.PROVISIONAL,
         "INV.1  unsecured frame -> ENC.1 is PROVISIONAL (never PASS)")
    results &= _check(
         u.get("AUTH.1") and u["AUTH.1"].status == model.SKIPPED,
         "INV.2  unsecured frame -> AUTH.1 SKIPPED (no MAC to verify, honest)")

     # INV.3: FAIL must be reportable.
    rep = {r.check_id: r for r in _run_one(fixtures.REPLAY)}
    results &= _check(
         rep.get("REPL.1").status == model.FAIL,
         "INV.3  replay fixture -> REPL.1 FAIL")
    dk = {r.check_id: r for r in _run_one(fixtures.DEADKEY)}
    results &= _check(
         dk.get("KEY.1").status == model.FAIL,
         "INV.3  dead-key fixture -> KEY.1 FAIL")

     # INV.4: no fixture may ever yield PASS on a hard-capped (PROVISIONAL) check.
    hard_ids = {c["id"] for c in model.load_checks()
               if c.get("hard_ceiling") == model.HARD_CEIL}
    for fx in fixtures.FIXTURES:
        for r in _run_one(fx):
            if r.check_id in hard_ids and r.status == model.PASS:
                 results &= _check(
                     False,
                     f"INV.4   {fx['name']}:{r.check_id} returned PASS "
                     "against a PROVISIONAL hard cap (fabrication!)")
    results &= _check(True, "INV.4 held (no PASS on hard-capped checks)")

     # INV.5: the raw-file unsecured frame parses to extension_present False.
    hexpath = os.path.join(model.CHECKS_DIR, "..", "testvectors",
                          "unsecured_goose.frame.hex")
    raw = bytes.fromhex(open(hexpath).read())
    f = checks.parse_frame(raw)
    results &= _check(
         f.get("extension_present") is False,
         "INV.5  raw-file unsecured frame parsed -> extension_present False")

    print()
    print("SMOKE TEST " + ("PASSED" if results else "FAILED"))
    return 0 if results else 1


if __name__ == "__main__":
     raise SystemExit(main())
