"""executor/ — the PROVISIONAL-aware conformance harness (Python v0.1).

Public API:
    run_all()        -> (text_report, forbidden_hits, counts, per_fixture_results)
    machine_report() -> list[dict]   (machine-readable, no prose/claim wording)

The check definitions live in ../checks/*.yaml (declarative, language-neutral).
A second implementation (Go/Rust, v0.2) re-drives the same table — see BUILD_APPROACH.md §3.
"""
from .harness import run_all, machine_report
from .model import load_checks

__all__ = ["run_all", "machine_report", "load_checks"]
