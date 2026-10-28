"""fixtures.py — the smoke fixtures + testvectors entries.

Each fixture is a plain dict the executor re-drives against the declarative check table.
Fixtures must be REAL and traceable (testvectors/README.md). This module seeds the
smoke fixtures; a `raw` fixture also exercises parse_frame's raw-byte path against a
file under testvectors/ so the parse layer is exercised, not just the check layer.

Nothing here asserts wire-shape conformance. WIRE.* / ENC.* are hard-capped PROVISIONAL
by the ceiling gate in model.enforce_ceiling — no fixture can flip them to PASS.
"""
from __future__ import annotations

import hashlib
import hmac
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_TV = os.path.normpath(os.path.join(_HERE, os.pardir, "testvectors"))

# canonical group key + APDU so AUTH.1's PARTIAL result is reproducible / traceable
_GROUP_KEY = b"coop-2030.100.2-grp01"
_APDU = (b"\x08\x00" + b"\x01\x03" + b"\x01\x02" + b"\x00\x00"
        + bytes.fromhex("00" * 8))
_FRAME_MAC = hmac.new(_GROUP_KEY, _APDU, hashlib.sha256).digest()[:16]


# 1) Headline smoke test: an UNSECURED GOOSE frame (61850-8-1 Reserved1/2 = 0x0000).
#    Expected: WIRE.* PROVISIONAL (hard cap), AUTH/IV SKIPPED (no extension),
#    REPL PASS (replay protection must work on the unsecured path too).
UNSECURED = {
 "name": "unsecured_goose",
 "note": "unsecured GOOSE (61850-8-1 Reserved1/2 = 0x0000 => no 62351-6 extension). "
       "replay-only path: replay protection must still apply. Wire shape PROVISIONAL.",
 "spec_refs": ["IEC 61850-8-1", "IEC 62351-6 (informational, unsecured extension)"],
 "frame": {
      "protocol": "GOOSE",
      "tpid": 1,
      "square_number": 1,
      "stnumber": 42,
      "reserved1": 0,
      "reserved2": 0,
      "extension_present": False,
      "gmac": False,
  },
 "replay_history": [36, 37, 38, 39, 40, 41],   # stNum 42 is fresh -> accept
 }

# 1b) Same unsecured message via the RAW byte path, to exercise parse_frame itself.
_RAW_UNSECURED = bytes([0x01, 0x01, 0x00, 0x2a, 0x00, 0x00, 0x00, 0x00])
# layout tpid=0x01, sqn=0x01, stNum=0x002a=42, reserved1=0, reserved2=0 => unsecured
UNSECURED_RAW = {
 "name": "unsecured_goose__raw",
 "note": "raw-bytes unsecured GOOSE front; exercises parse_frame's best-effort path. "
       "Front is PROVISIONAL; only the well-known front is asserted.",
 "spec_refs": ["IEC 61850-8-1"],
 "frame": _RAW_UNSECURED,
 "replay_history": [],
 }

# 2) A synthetic SECURE frame (NOT a real capture) to exercise the PARTIAL/FAIL paths so
#    the harness demonstrably discriminates, not just prints PROVISIONAL.
SECURED = {
 "name": "secured_goose__synthetic",
 "note": "synthetic secure frame (NOT a real capture, NOT a 2nd-impl oracle): exercises "
       "AUTH.1/IV.1 PARTIAL + KEY.1 PASS. WIRE.* still PROVISIONAL (no oracle). "
       "Do NOT read any PASS here as wire-shape conformance.",
 "spec_refs": ["IEC 62351-6:2020", "IEC 62351-9:2019", "IEEE P2030.100.2 (2026)"],
 "frame": {
      "protocol": "GOOSE",
      "tpid": 1,
      "square_number": 1,
      "stnumber": 10,
      "reserved1": 0x1111,      # non-zero -> extension_present via parse only if raw; force here
      "reserved2": 0x2222,
      "extension_present": True,
      "tag": "0x85",
      "auth_value": _FRAME_MAC,
      "gmac": True,
      "iv": b"\x01\x02\x03\x04\x05\x06\x07\x08",
      "iv_per_publisher": True,
      "key_id": "grp01-2026",
      "key_expired": False,
      "ciphertext": None,
  },
 "group_key": _GROUP_KEY,
 "apdu": _APDU,
 "frame_mac": _FRAME_MAC,
 "local_keyring": {"grp01-2026", "grp02-2026"},
 "replay_history": [1, 2, 3, 4, 5, 6, 7, 8, 9],
 }

# 3) Replay attack: stale stNum back in the window -> REPL.1 FAIL.
REPLAY = {
 "name": "replay_attack",
 "note": "replay: stNum 8 already seen -> REPL.1 must FAIL (discard). Proves FAIL path.",
 "spec_refs": ["IEC 62351-6 (informational replay)"],
 "frame": {
      "protocol": "GOOSE",
      "stnumber": 8,
      "reserved1": 0,
      "reserved2": 0,
      "extension_present": False,
      "gmac": False,
  },
 "replay_history": [4, 5, 6, 7, 8],    # 8 is in window -> replay
 }

# 4) Dead key, no transition: KEY.1 FAIL (kept decrypting with a dead/unknown key).
DEADKEY = {
 "name": "dead_key_no_transition",
 "note": "keyID unknown/expired but subscriber did NOT transition+GROUP-PULL -> KEY.1 FAIL.",
 "spec_refs": ["IEC 62351-9:2019"],
 "frame": {
      "protocol": "GOOSE",
      "stnumber": 55,
      "reserved1": 0,
      "reserved2": 0,
      "extension_present": False,
      "gmac": False,
      "key_id": "grp99-1999",
      "key_expired": True,
      "transitioned": False,
  },
 "local_keyring": {"grp01-2026"},
 "replay_history": [],
 }

FIXTURES = [UNSECURED, UNSECURED_RAW, SECURED, REPLAY, DEADKEY]
