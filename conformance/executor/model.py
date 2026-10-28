"""Model + loader for the conformance harness.

Language-neutral, clean-room, no-FTO reference (Python v0.1). A second implementation
(Go/Rust, v0.2) re-drives the SAME `checks/*.yaml` declarative table — no code rewrite.

PROVENANCE: clean-room, published-spec-only. No reference-impl source or paid capture was
consulted. See ../../provenance/conformance.checks.md and NOTICE.
"""
from __future__ import annotations

import glob
import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS_DIR = os.path.normpath(os.path.join(HERE, os.pardir, "checks"))

# Result status grammar (fixed, non-negotiable — see conformance/README.md §"Reporting grammar").
PASS = "PASS"
FAIL = "FAIL"
PROVISIONAL = "PROVISIONAL"
SKIPPED = "SKIPPED"  # check not applicable to this fixture (e.g. unsecured frame, no MAC)

# The single anti-fabrication guardrail, restated here as code:
# a check may only return PASS if its declared oracle is not PROVISIONAL AND it is not
# hard-capped. Every WIRE.*/ENC.* check is hard-capped -> PROVISIONAL, always.
HARD_CEIL = "PROVISIONAL"


class CheckResult:
    """One check's verdict on one fixture. status is one of PASS/FAIL/PROVISIONAL/SKIPPED."""

    __slots__ = ("check_id", "title", "status", "reason", "detail", "oracle")

    def __init__(self, check_id, title, status, reason="", detail="", oracle=""):
        self.check_id = check_id
        self.title = title
        self.status = status
        self.reason = reason
        self.detail = detail
        self.oracle = oracle

    @classmethod
    def provisional(cls, check, reason):
        return cls(check["id"], check["title"], PROVISIONAL, reason,
                   "oracle: " + str(check.get("oracle", "PROVISIONAL")), check.get("oracle", ""))

    @classmethod
    def pass_(cls, check, detail=""):
        return cls(check["id"], check["title"], PASS, "", detail, check.get("oracle", ""))

    @classmethod
    def fail(cls, check, reason, detail=""):
        return cls(check["id"], check["title"], FAIL, reason, detail, check.get("oracle", ""))

    @classmethod
    def skip(cls, check, reason):
        return cls(check["id"], check["title"], SKIPPED, reason,
                   "not applicable to this fixture", check.get("oracle", ""))

    def line(self):
        head = f"  [{self.status:<11}] {self.check_id}  {self.title}"
        if self.status == PROVISIONAL:
            head += f"\n                 PROVISIONAL: {self.reason}"
        elif self.status == FAIL:
            head += f"\n                 FAIL: {self.reason}"
        if self.detail:
            head += f"\n                 {self.detail}"
        return head

    def __repr__(self):
        return f"<{self.check_id} {self.status}>"


def load_checks(spec_dir=None):
    """Load every checks/*.yaml and flatten to a list of check dicts.

    Each check dict must carry: id, title, oracle (PUBLIC|PARTIAL|PROVISIONAL),
    and optionally hard_ceiling + provisional_reason.
    """
    spec_dir = spec_dir or CHECKS_DIR
    checks = []
    for path in sorted(glob.glob(os.path.join(spec_dir, "*.yaml")) +
                       glob.glob(os.path.join(spec_dir, "*.yml"))):
        with open(path, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        base = {
            "as_of": doc.get("as_of", ""),
            "spec_refs": doc.get("spec_refs", []),
            "file": os.path.basename(path),
        }
        for c in doc.get("checks", []):
            c = dict(c)
            # inherit file-level provenance
            c.setdefault("as_of", base["as_of"])
            c.setdefault("spec_refs", base["spec_refs"])
            c.setdefault("hard_ceiling", None)
            c.setdefault("provisional_reason", "")
            checks.append(c)
    return checks


def enforce_ceiling(check, internal_ok, internal_detail, skip=False, skip_reason=""):
    """ANTI-FABRICATION GATE.

    Decide the status. A PASS is refused whenever the check is hard-capped or its oracle is
    PROVISIONAL. This is the project's defining property: a verifier that cannot say PASS it
    shouldn't. Returns a CheckResult.
    """
    ceil = check.get("hard_ceiling")
    oracle = check.get("oracle", "PROVISIONAL")
    reason = check.get("provisional_reason") or \
        (f"no public/2nd-implementation oracle for {check['id']}")

    # 1) Hard cap wins: a WIRE.*/ENC.* check is PROVISIONAL no matter what the logic says.
    if ceil == HARD_CEIL:
        return CheckResult.provisional(check, reason)
    # 2) Any PROVISIONAL oracle check is PROVISIONAL when it actually tried the wire shape.
    if oracle == "PROVISIONAL":
        return CheckResult.provisional(check, reason)
    # 3) PARTIAL: the public primitive is checkable; the PROVISIONAL construction is noted.
    if oracle == "PARTIAL":
        if skip:
            return CheckResult.skip(check, skip_reason)
        if internal_ok:
            r = CheckResult.pass_(check, internal_detail +
                                  " [PARTIAL: wire-shape/construct still PROVISIONAL — not a conformance PASS]")
            return r
        return CheckResult.fail(check, "primitive check did not match", internal_detail)
    # 4) PUBLIC oracle: checkable outright.
    if skip:
        return CheckResult.skip(check, skip_reason)
    if internal_ok:
        return CheckResult.pass_(check, internal_detail)
    return CheckResult.fail(check, "public behaviour did not match expected", internal_detail)


if __name__ == "__main__":
    checks = load_checks()
    print(f"loaded {len(checks)} checks from {CHECKS_DIR}")
    for c in checks:
        print(f"  {c['id']:<8} oracle={c.get('oracle'):<12} "
              f"hard_ceiling={c.get('hard_ceiling')}  {c['title'][:50]}")
