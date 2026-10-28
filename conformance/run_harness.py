#!/usr/bin/env python3
"""run_harness.py -- top-level entrypoint (Python v0.1).

Usage:
    python3 run_all.py                 # full human + machine report
    python3 run_harness.py --machine   # JSON only, machine-readable
    python3 run_harness.py --no-cert   # also prints the NO-CERT footer (default)

The fixed NO-CERT footer is always emitted on the human report (report.py) and echoed
here so no one skims the top and mistakes this for a certification.
"""
from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from executor import run_all, machine_report
from executor.report import NO_CERT_FOOTER


def main(argv):
    machine_only = "--machine" in argv
    if machine_only:
        print(json.dumps(machine_report(), indent=2))
        return 0

    text, hits, counts, all_results = run_all()
    print(text)
    print()
    print(NO_CERT_FOOTER)
    if hits:
        sys.stderr.write("[WARNING] forbidden wording detected: " + ", ".join(hits) + "\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
