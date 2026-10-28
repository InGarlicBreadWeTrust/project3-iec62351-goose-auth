# Provenance of the v0.1 check set

**Clean-room statement.** Every check in `../checks/*.yaml` derives from *public, open
standards documents only* (IEC 61850-8-1 / -6 / -9, IEEE P2030.100.2, and the public
IEEE P2030.400 paper — see `../../NOTICE.md`). **No reference-implementation source and
no paid 62351-6 secured capture were consulted.** This is declared in NOTICE.md (legal
posture) and enforced behaviourally by `../executor/model.py` (enforce_ceiling).

## 2026-10-28 — v0.1 seed check set

| check | oracle | notes |
|---|---|---|
| AUTH.1 | PARTIAL | HMAC-SHA256/CMAC primitive demo only; wire shape/Construction PROVISIONAL |
| IV.1    | PARTIAL | 62351-9 per-publisher requirement; Construction PROVISIONAL |
| REPL.1  | PUBLIC  | stNum/sqNum window + TimeAllowedToLive — public behaviour |
| KEY.1   | PUBLIC  | unknown/expired keyID -> transition + GROUP-PULL + alarm (T5) — public |
| WIRE.1  | PROVISIONAL / **hard-capped** | 0x85 tag / AuthValue order / BER Extension — no oracle |
| ENC.1   | PROVISIONAL / **hard-capped** | AES-GCM/CBC — wire shape unsettled; <3ms class encrypts nothing |

The hard caps exist specifically because the published IEEE P2030.400 paper (a
*security-evaluation / assessment* paper, not a normative spec or a capture oracle)
cannot certify wire shape. See `../../testvectors/README.md` and the v0.1 smoke results.
