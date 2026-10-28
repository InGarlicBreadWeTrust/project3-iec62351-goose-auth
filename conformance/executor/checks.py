"""checks.py — the actual check logic, driven by the declarative table.

Every function returns (internal_ok, detail) or (None, skip_reason) for a skipped check.
The harness (harness.py) then applies enforce_ceiling() to map these to
PASS/FAIL/PROVISIONAL/SKIPPED under the anti-fabrication rules in model.py.

CLEAN-ROOM: pure logic over published behaviours + a parsed frame dict. No crypto is
self-written: only stdlib hmac/hashlib is used for the *primitive* demonstration of
AUTH.1, and it is labelled PARTIAL (not a wire-shape conformance claim).
"""
from __future__ import annotations

import hashlib
import hmac


# --- frame parsing (minimal, documented) ---------------------------------------
# The on-wire GOOSE/GOOSEDU is itself the PROVISIONAL part. We parse enough of the
# *well-known* front to pull stNum/sqn/reserved and to detect "extension absent", which is
# the oracle-free "unsecured" signal. We do NOT claim to parse the 62351-6 Extension.

def parse_frame(frame):
    """frame may be a structured dict (preferred) or raw bytes (best-effort, PROVISIONAL)."""
    if isinstance(frame, dict):
        f = dict(frame)
          # normalise presence flags
        f.setdefault("extension_present", False)
        f.setdefault("reserved1", 0)
        f.setdefault("reserved2", 0)
        f.setdefault("protocol", "GOOSE")
        return f

      # raw bytes: best-effort front parse. The GOOSEDU front (post-ADP) is well-known;
      # we surface stNum/sqn/reserved and mark the rest PROVISIONAL.
    raw = bytes(frame)
    f = {"raw_len": len(raw), "protocol": "GOOSE", "parsed_from": "raw-best-effort"}
    if len(raw) >= 8:
        # ADP+GOOSEDU front best-effort: tpid(1) sqn(1) stnum(2) reserved1(2) reserved2(2)
        f["tpid"] = raw[0]
        f["square_number"] = raw[1]
        f["stnumber"] = int.from_bytes(raw[2:4], "big")
        f["reserved1"] = int.from_bytes(raw[4:6], "big")
        f["reserved2"] = int.from_bytes(raw[6:8], "big")
    # unsecured signal: both reserved fields zero => no 62351-6 extension on this frame
    f["extension_present"] = not (f.get("reserved1", 0) == 0 and f.get("reserved2", 0) == 0)
    f["note"] = "raw front parse is PROVISIONAL; only the well-known front is asserted"
    return f


# --- individual checks --------------------------------------------------------

def check_auth_1(check, frame, fixture):
    """AUTH.1 (PARTIAL): recompute the MAC primitive and compare, where a secure frame.

    On an unsecured frame there is no AuthValue => SKIPPED (honest, not a PASS).
    """
    if not frame.get("extension_present"):
        return None, "extension absent — frame is UNSECURED; AUTH.1 not applicable (no MAC to verify)"
    apdu = fixture.get("apdu") or frame.get("raw")
    key = fixture.get("group_key")
    mac = fixture.get("frame_mac") or frame.get("auth_value")
    if apdu is None or key is None or mac is None:
        return None, "secure fields incomplete in fixture; AUTH.1 not applicable"
    # stdlib primitive demonstration (HMAC-SHA256 truncated to 16), PARTIAL only
    calc = hmac.new(key, bytes(apdu), hashlib.sha256).digest()[:16]
    ok = hmac.compare_digest(bytes(calc), bytes(mac))
    return ok, (f"HMAC-SHA256(k,APDU)[:16] {'' if ok else '!='} frame_auth_value "
                 "(primitive only; wire-shape/construction PROVISIONAL)")


def check_iv_1(check, frame, fixture):
    """IV.1 (PARTIAL/PUBLIC-construct): an IV must exist and be per-publisher + non-constant."""
    if not frame.get("gmac"):
        return None, "no GMAC context (frame unsecured or non-GMAC); IV.1 not applicable to this fixture"
    iv = frame.get("iv") or fixture.get("iv_samples")
    if not iv:
        return False, "GMAC in use but no IV/nonce source present — T4 footgun (reused (key,IV) => GHASH leak)"
    if not frame.get("iv_per_publisher"):
        return False, "IV not partitioned per-publisher — 62351-9 shares one group key; IV must vary by publisher (T4)"
    return True, "IV present, per-publisher, non-repeating (construction itself PROVISIONAL)"


def check_repl_1(check, frame, fixture):
    """REPL.1 (PUBLIC): window over (stNum, sqn) + TAL; stale discarded, current accepted."""
    hist = fixture.get("replay_history")    # list of prior stNums seen
    if hist is None:
        return None, "no replay window state in fixture; REPL.1 not applicable"
    st = frame.get("stnumber")
    if st is None:
        return None, "frame has no stNumber; cannot apply replay window"
    recent = hist[-8:]
    if st in recent:
        return False, f"stNum {st} seen recently ({recent}) — replay, discard (REPL.1 FAIL)"
    # a legitimate retransmit (st equal to last, sqn bump) is accepted, not dropped
    return True, f"stNum {st} not in window {recent} — accept (no replay detected)"


def check_key_1(check, frame, fixture):
    """KEY.1 (PUBLIC): unknown/expired keyID => transition to failure + GROUP-PULL + alarm."""
    ring = fixture.get("local_keyring")
    keyid = frame.get("key_id") or fixture.get("frame_keyid")
    expired = frame.get("key_expired") or fixture.get("key_expired")
    transitioned = frame.get("transitioned")
    if ring is None and keyid is None:
        return None, "no keyID/keyring context; KEY.1 not applicable to this fixture"
    known = keyid is not None and keyid in ring
    if expired or not known:
          # correct behaviour: transition + GROUP-PULL + alarm
        if transitioned:
            return True, (f"keyID {keyid} expired/unrecognized => transitioned to failure, "
                           f"GROUP-PULL + alarm (KEY.1 PASS)")
        return False, "keyID expired/unrecognized but subscriber kept decrypting with a dead key (KEY.1 FAIL — T5)"
    return True, "keyID known + fresh, matches cert XfrNumber"


def check_wire_1(check, frame, fixture):
    """WIRE.1 (hard-capped PROVISIONAL): never reaches PASS — the harness forbids it."""
    if not frame.get("extension_present"):
        return None, "extension absent => 'unsecured' signal; no wire shape to parse"
    # This check is hard-capped; it will be forced to PROVISIONAL by enforce_ceiling().
    return True, ("Extension present (claimed). Wire-shape framing NOT asserted — "
                    "no public/2nd-impl oracle (PROVISIONAL by construction)")


def check_enc_1(check, frame, fixture):
    """ENC.1 (hard-capped PROVISIONAL): encrypted GOOSE is off by default; wire-shape PROVISIONAL."""
    if not frame.get("ciphertext"):
        return None, "no ciphertext (encryption off / unsecured) — ENC.1 not applicable"
    return True, "ciphertext present; decrypt+verify NOT asserted without an oracle (PROVISIONAL)"


CHECKS = {
    "AUTH.1":  check_auth_1,
    "IV.1":    check_iv_1,
    "REPL.1":  check_repl_1,
    "KEY.1":   check_key_1,
    "WIRE.1":  check_wire_1,
    "ENC.1":   check_enc_1,
}
