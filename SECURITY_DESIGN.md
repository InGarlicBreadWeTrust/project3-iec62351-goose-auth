# Security Design — IEC 62351-6 secure GOOSE / SV (threat model + what a verifier checks)

> Defense-direction. Threat model for the *verifier/harness*, not a production design.
> Standard of reference: IEC 62351-6:2020, IEC 62351-9, IEEE P2030.100.2 (2026 guide).

## 0. Reality checks that change the design
- **GOOSE is not encrypted by default.** For the <3 ms (trip) class the spec *recommends
  against* encryption; confidentiality is meant to come from the GOOSE/SV being restricted to
  the substation LAN (Electronic Security Perimeter, "path selection"). **Authentication is the
  primary mechanism, not confidentiality.** The 62351-6 security extension carries an
   **authentication value (MAC tag), not a ciphertext.** So "verify secure GOOSE" mostly means
   *verify message authentication + replay protection* — and the frame is otherwise in the clear.
- **62351-6 ≠ 62351-4.** The TLS profile (62351-3/4) secures *MMS/ACSE* (client/server). The
   GOOSE/SV security is a **separate Layer-2 mechanism** (extended PDU). Vendors often conflate
   the two — "we have TLS, therefore secure GOOSE" is a common and *wrong* claim the harness is
   meant to expose.
- **As of 2026-10-28 there is no public/2nd-implementation oracle for the 62351-6 GOOSE
  `Extension` wire shape (`0x85` tag, `AuthValue` field order, BER `Extension` framing).**
  Two independent clean-room attempts (cB-Sigma Apache-2.0; zaxified/zig-libs MIT) confirm the
  gap; all 493 real GOOSE frames in 5 public captures had `Extension` = empty (unsecured).
  ⇒ Any 62351-6 framing check the harness prints must be `PROVISIONAL`, not `PASS`, until a
  2nd impl or real secured capture exists.

## 1. Threat model (what 62351-6 actually buys, and what it doesn't)
Adversary on the substation LAN (or a compromised IED / MITM on the LAN).

| # | Threat | 62351-6 counter | Residual / caveat (what the harness must surface) |
| - | --- | --- | --- |
| T1 | **Message modification / impersonation of a publisher** | MAC over the APDU (`AuthValue`) keyed per publication/group | Auth ≠ publisher-auth: a **symmetric group key lets any group member forge any publisher's frame**. Harness must flag this loudly — it's the single most misunderstood point. |
| T2 | **Replay of a captured trip/reset** | Replay protection (window over stNum/sqNum + a freshness check) | Window must respect GOOSE retransmission semantics (stNum bumps, TAL). A naive window drops legitimate retransmits; a loose loop accepts replays. |
| T3 | **MITM / unauthenticated new device on LAN** | Publisher/subscriber reference + key-ID match | 62351-6 gives message auth, not device-onboarding auth — pair with 62351-8 RBAC + PKI for full chain-of-trust; harness notes this boundary. |
| T4 | **Key reuse / IV–nonce repeat under GMAC** | Per-publisher IV/nonce; key rotation via 62351-9 | **Reused (key,IV) under GMAC leaks the GHASH subkey ⇒ anyone can forge any frame.** Because 62351-9 hands the *same group key to every IED*, IV must be partitioned per publisher or repeats by default. This is a real, cited footgun (see `LICENSE_SEP_ASSESSMENT` §1). |
| T5 | **Stale / expired key used after compromise** | Expiry + GROUP-PULL on unknown/expired keyID (62351-9) | Verify the subscriber *transitions and pulls*, not just keeps decrypting with a dead key. |

**What 62351-6 does NOT provide (be explicit in reports):**
- confidentiality of GOOSE contents unless encryption (AES-GCM/CBC) is enabled — and only
  "where the 3 ms criterion is not a concern";
- device onboarding / mutual device identity (that's PKI + 62351-8 RBAC territory);
- protection against a *correct* but *compromised* group key (rotation + key-ID match only).

## 2. The checks a harness actually runs (verifier surface)
### 2.1 MAC / message-authentication profiles
| Profile | Tag / output | Note |
| --- | --- | --- |
| `HMAC-SHA-256` (128-bit trunc) | 16-octet MAC | Primary, in-budget for the 3 ms class |
| `AES-GMAC-64` | 8-octet tag | **requires an IV source** — check it exists AND is per-publisher |
| `AES-GMAC-128` | 16-octet tag | same IV caveat (T4) |
| `RSA/RSASSA` | signature | *out of the 3 ms budget in practice*; S-GoSV/62351 historically cited RSA for GOOSE auth, but timing makes it unusable for real trip traffic. Note it as "spec-cited, impractical." |
- For each: confirm (a) the MAC key is the publication/group key, (b) the `AuthValue`
  covers the APDU bytes *before* the extension tag, (c) for GMAC, the IV/nonce is
  per-publisher and not constant. **T4 must be a first-class check.**

### 2.2 Replay protection
- Check window/freshness over `(stNum, sqNum)` + `TimeAllowedToLive`; verify stale/replayed
  frames are discard**ed** *and* that legitimate retransmits are **not** discarded.
- 62351-6 replay protection applies to both GOOSE and Multicast SV; with or without the
  security extension (informative clause) — harness should cover both, marking unsecured paths
  as "replay-only / extension-absent".

### 2.3 Key management surface (IEC 62351-9 / GDOI)
Verify at the protocol-stub level (no full GDOI server needed for v0.1):
- unknown keyID ⇒ subscriber **transitions to failure and performs GROUP-PULL**, alarms
- expired key with unknown new key ⇒ **GROUP-PULL**, alarm "key delivery failed / expired"
- keyID present & fresh ⇒ `GOOSEEncryptionInUse` / `SVEncryptionInUse` matches the XfrNumber
  of the cert used for auth+encryption (where encryption is on)
- at least one `GOOSESecurity` (and `SVSecurity`) instance per claiming IED

### 2.4 Wire-shape checks (PROVISIONAL — no oracle as of date)
- `Extension` tag (`0x85` per the spec readings), `AuthValue` field order, BER `Extension`
  `SEQUENCE` framing — all **PROVISIONAL**, logged with "no public 2nd impl" caveat.
- The 61850-8-1 `Reserved1`/`Reserved2` = `0x0000` ⇒ "unsecured extension" signal is the
  oracle-free default; real secured frames are what's *absent* from public captures.

## 3. Design principles
1. **Provisional, never fake.** A check with no oracle prints `PROVISIONAL` with the reason.
   This is the project's defining property and the anti-sued property (you're a verifier, not a
   certifier).
2. **Crypto from vetted primitives only.** HMAC/AES-GCM/GMAC/RSA from a mainstream,
   audited crypto library (Rust `crypto` / Go `crypto` / C OpenSSL). No self-written crypto.
3. **Auth ≠ confidentiality ≠ publisher-auth.** Every report line that mentions "security"
    explicitly states which.
4. **Group-key footguns are first-class.** T1/T4 get dedicated, visible checks.
5. **Boundaries are loud.** "TLS/62351-4 present does NOT imply 62351-6 GOOSE security."
6. **No secrets in repo.** No keys, no vendor PII, no real capture PII; capture *metadata*
   with a provenance pointer only, redacted.
7. **Out of scope: production agent.** No packet-pumping loop, no raw-socket IED. Keep it a
   verifier so SEP exposure stays low and "product" status stays off the table.
8. **Clean-room.** Spec-only; no reference-impl contact; provenance logged per module.

## 4. Threat-model → check matrix (for `testvectors/`)
| Threat | Check id | Inputs | Expected | Oracle status @2026-10-28 |
| --- | --- | --- | --- | --- |
| T1 | AUTH.1 | group key + APDU + (optional) IV | recomputed MAC = frame MAC; mismatch ⇒ reject | PARTIAL (MAC primitive known; wire shape PROVISIONAL) |
| T2 | REPL.1 | (stNum,sqNum,TAL) history | stale ⇒ discard; current ⇒ accept | PUBLIC (window semantics published) |
| T3 | KEY.1 | frame keyID + local known keys | unknown/expired ⇒ GROUP-PULL | PUBLIC (protocol behavior) |
| T4 | IV.1 | GMAC + IV source | per-publisher, non-repeating IV | PUBLIC (IV *must exist & vary*); the *construction* PROVISIONAL |
| T5 | ENC.1 | AES-GCM/CBC frame | decrypt+verify tag | PROVISIONAL (wire shape unsettled) |
| — | WIRE.1 | `Extension` bytes | tag/order/framing parse | PROVISIONAL (no 2nd impl / secured capture) |

> "PUBLIC" = the *behavior* is defined in published text the harness can check without an
> oracle (e.g. "reject on MAC mismatch"). "PROVISIONAL" = the exact wire shape/field order has
> no confirmed public oracle, so a `PASS` cannot yet be asserted unconditionally.

## 5. Open questions
- Final oracle status: has any 2nd 62351-6 impl or secured GOOSE capture appeared since
  2026-10-28? (Deps the PROVISIONAL→PASS promotions.)
- Should the harness accept 62351-8 RBAC / PKI as a co-dependency for a "full chain-of-trust"
  report, or stay strictly 62351-6/9? (Recommend: reference it, don't implement it, in v0.1.)
