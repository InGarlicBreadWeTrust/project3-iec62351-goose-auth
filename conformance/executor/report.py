"""report.py — PASS / FAIL / PROVISIONAL reporting. No conformance/cert claim wording.

The footer is FIXED and non-negotiable (conformance/README.md §"Reporting grammar"). It
must appear on every report. It is the project's headline anti-liability property.
"""
from __future__ import annotations

# Verbatim from conformance/README.md. Do not weaken.
NO_CERT_FOOTER = (
    "This is not a certification and does not confer conformance. "
    "No freedom-to-operate is implied. PROVISIONAL results cannot be read as conformance. "
    "See NOTICE."
)

# Forbidden wording the report generator must never emit (CI can grep these too).
FORBIDDEN_WORDS = ("conformant", "certified", "passes 62351-6", "is 62351-6 compliant")


def render(results, fixture_name="fixture", spec_refs=None):
    """Render a human + machine report. Returns (text, structured_dict)."""
    lines = []
    lines.append("=" * 78)
    lines.append("IEC 62351-6 secure-GOOSE / SV conformance REPORT  (v0.1, PROVISIONAL-aware)")
    lines.append(f"fixture            : {fixture_name}")
    lines.append(f"checks evaluated   : {len(results)}")

    status_counts = {}
    for r in results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
    order = ["PASS", "FAIL", "PROVISIONAL", "SKIPPED"]
    counts = ", ".join(f"{k}={status_counts.get(k,0)}" for k in order if status_counts.get(k))
    lines.append(f"result tally       : {counts or 'none'}")
    lines.append("")
    for r in results:
        lines.append(r.line())
    lines.append("")

    # Machine-readable tail (one JSON-ish line per result; keeps the no-FTO footer last).
    for r in results:
        lines.append(f"MACHINE {r.check_id} {r.status} oracle={r.oracle} "
                      f"reason='{r.reason}'")
    lines.append("")
    if spec_refs:
        lines.append("spec_refs: " + ", ".join(spec_refs))
    lines.append("-" * 78)
    # NO-CERT footer last so no one skims the top and thinks this was certified.
    lines.append(NO_CERT_FOOTER)
    lines.append("=" * 78)
    text = "\n".join(lines)

    structured = {
        "fixture": fixture_name,
        "spec_refs": spec_refs or [],
        "counts": status_counts,
        "results": [
            {"check_id": r.check_id, "title": r.title, "status": r.status,
             "reason": r.reason, "detail": r.detail, "oracle": r.oracle}
            for r in results
        ],
        "no_cert_footer": NO_CERT_FOOTER,
    }
    return text, structured
