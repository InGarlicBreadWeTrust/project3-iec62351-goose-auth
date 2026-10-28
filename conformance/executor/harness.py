"""harness.py -- orchestrator.

Loads the declarative table, runs the check logic, then applies the
enforcement-ceiling gate and renders the report.

Anti-fabrication property lives here: every check result passes through
model.enforce_ceiling(), which FORCES PROVISIONAL on hard-capped / PROVISIONAL-oracle
checks no matter what the internal logic returns.
"""
from __future__ import annotations

from . import checks
from . import fixtures
from .model import load_checks, enforce_ceiling, CheckResult
from .report import render, FORBIDDEN_WORDS


def _run_one(fx):
    """Run every applicable check for one fixture; return a list[CheckResult]."""
    loaded = load_checks()
    frame = checks.parse_frame(fx["frame"])
    results = []
    for c in loaded:
        fn = checks.CHECKS.get(c["id"])
        if fn is None:
            results.append(CheckResult(
                c["id"], c["title"], "FAIL",
                "internal: no check function for " + c["id"] + " in CHECKS",
                "", c.get("oracle", "")))
            continue
        try:
            ok, detail_or_skip = fn(c, frame, fx)
        except Exception as e:     # a check error is never a PASS -- surface it
            results.append(CheckResult(
                c["id"], c["title"], "FAIL",
                "check raised: " + repr(e), "", c.get("oracle", "")))
            continue
        skip = ok is None
        reason = detail_or_skip if skip else ""
        detail = detail_or_skip if not skip else ""
        res = enforce_ceiling(c, ok, detail, skip=skip, skip_reason=reason)
        results.append(res)
    return results


def run_all():
    """Run all fixtures; return (text_report, forbidden_hits, counts, per_fixture_results)."""
    all_results = []
    for fx in fixtures.FIXTURES:
        all_results.append((fx, _run_one(fx)))

    # forbidden-word gate (defence-in-depth; CI greps these too)
    notes = "\n".join((fx.get("note", "") or "") for fx in fixtures.FIXTURES)
    reasons = "\n".join(
        (r.reason + " " + r.detail)
        for _fx, rs in all_results
        for r in rs
    )
    blob = (notes + "\n" + reasons).lower()
    hits = [w for w in FORBIDDEN_WORDS if w in blob]

    # render, one section per fixture
    parts = []
    counts_total = {}
    for fx, rs in all_results:
        text, structured = render(rs, fx["name"], fx.get("spec_refs"))
        parts.append(text)
        for k, v in structured["counts"].items():
            counts_total[k] = counts_total.get(k, 0) + v

    combined = "\n\n".join(parts)
    if hits:
        combined += "\n[WARNING] forbidden wording detected: " + ", ".join(hits) + "\n"
    return combined, hits, counts_total, all_results


def machine_report():
    """Return the structured, machine-readable form (no prose, no claim wording)."""
    out = []
    for fx in fixtures.FIXTURES:
        rs = _run_one(fx)
        entry = {
            "fixture": fx["name"],
            "note": fx.get("note", ""),
            "results": [
                {
                    "check_id": r.check_id,
                    "status": r.status,
                    "reason": r.reason,
                    "oracle": r.oracle,
                }
                for r in rs
            ],
            "count_by_status": {},
        }
        for r in rs:
            s = r.status
            entry["count_by_status"][s] = entry["count_by_status"].get(s, 0) + 1
        out.append(entry)
    return out
