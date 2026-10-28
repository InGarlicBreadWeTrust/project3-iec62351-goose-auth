# License + SEP / Patent Assessment

> Defense-direction. This is a risk map, not advice. Consult IP counsel. Dates/facts as of 2026-10-28.

## 0. The single most important point
**Choosing a permissive license (MIT/Apache/BSD) does NOT give you freedom-to-operate
against standard-essential patents (SEPs).** License and patent are two independent axes:

- **License** governs who may copy/modify/distribute your *code*. Apache-2.0 lets anyone use
  your harness — fine.
- **Patent** governs whether implementing a *mechanism* infringes a third party's right,
  regardless of your license. Writing the 62351-6 GOOSE security extension clean-room
  still may "make, use, offer to sell, import" a patented method under 35 USC 271 — and
  **a permissive license does not stop that.** No code license "licenses around" a patent.

So the question "is it feasible to ship permissive code that touches SEP territory?" splits:
- **Copyrightable-distribution feasibility: YES.** You can always license your own original
  work permissively, whatever spec you implement.
- **Freedom-to-operate feasibility: NOT by licensing; only by FRAND good-faith posture +
  claim charting + choosing non-infringing mechanisms.** See §4.

## 1. What has SEPs, and how much?
| Layer | Examples | SEP risk | Notes |
| --- | --- | --- | --- |
| **Crypto primitives** | HMAC-SHA256, AES-GCM, GMAC, RSA(RSASSA) | LOW | HMAC (RFC 2104, 1996); GCM/AES/GMAC in prior art or long-expired; AES expired ~2026. These are FRAND-or-public domain and used across dozens of standards — hard to assert essentially. |
| **GOOSE/SV wire framing for security** (`0x85` tag, `AuthValue` field order, BER `Extension` SEQUENCE shape) | IEC 62351-6 clause 8 | MEDIUM–HIGH | This *is* the patented-feeling surface. It is also **not publicly verified** (no second impl, no real-capture oracle — see §3). Wire shape you can't verify is wire shape you can't be sure is patent-safe, AND it's the least certain part of the spec. |
| **Key distribution via GDOI / IEC 62351-9** | group-key delivery to IEDs | MEDIUM | GDOI (RFC 3723 / IETF, permissive family) is FRAND/public; the *62351-9 group-key-to-substation mapping* is where vendor claims live. |
| **Nonce/IV construction & replay window for sub-3ms GOOSE** | e.g. US 20220376923 "MESSAGE AUTHENTICATION" (ESINER/CHEN/… Singapore, likely NXP); polepakamo ASCON nonce work | MEDIUM-HIGH | Concrete patent-like objects cite IEC 62351-6 RSA-for-GOOSE by name. IV-per-publisher partitioning is exactly what 62351-9 group-keying makes repeat — a real, cited attack surface. |
| **62351-4 TLS / ACSE auth** | libiec61850 implements these | LOW-MED | Mature, widely implemented; many competing FRAND claims — lower injunction risk. |

**Net:** the MAC *primitives* are largely safe; the **specific 62351-6 framing + 62351-9
group-key/nonce scheme for GOOSE is the SEP-relevant zone**, and that's also the part of the
spec that has *never been second-checked by another implementation.*

## 2. IEC's patent posture (why the exposure is asymmetric)
- IEC's IPR policy requires participants who believe their patents are essential to disclose
  them to the responsible technical committee and to offer a **FRAND** licence to implementers.
- **But IEC does not maintain a public, searchable SEP registry / essentiality database**
  (unlike ETSI or ARM, which keep patent lists). *Flag: confirm against current IEC IPR
  policy before relying on this.* The consequence is a **search-and-notice asymmetry**: a
  would-be implementer cannot cheaply discover *all* SEPs, so (a) litigation risk is real and
  partly un-mappable, and (b) many "SEP" claims may be over-broad/non-essential.
- IEC/CENELEC standards carry the boilerplate *"Attention is drawn to the possibility that
  some of the elements of this document may be the subject of patent rights … IEC shall not
  be held responsible for identifying any such patent rights."* This is the disclosure
  disclaimer, not a FRAND guarantee for you.

## 3. The FRAND / anti-injunction safety net (and its limits)
- **Willing-licensee defense (global).** Under Huawei v ZTE / Unwired Planet (CJEU, EU- and
  increasingly US-aligned), an SEP holder generally **cannot get an injunction** against a
  licensee who (i) is "willing," (ii) makes a **good-faith FRAND offer/counter**, and (iii)
  doesn't unreasonably delay. A **documented FRAND posture** is the practical anti-injunction
  shield — even if claims still must be *paid*.
- **EU SEP framework (Regulation on SEPs / COM(2023) 232; European Parliament
  P9_TA(2024)0100, in force 2025).** Introduces an **EUIPO "Competence Centre"** with:
  an SEP registry + essentiality checks, and a **mandatory 9-month FRAND determination that
  must be attempted before court** ("safe harbour" from litigation during good-faith
  negotiation). Practical effect: **in-junctive relief against a good-faith implementer who
  has engaged the Centre or a FRAND negotiation becomes much harder across the EU.** Royalties
  are not eliminated — the framework is about *predictable FRAND, not royalty-free*.
- **Limits that matter here:**
  1. FRAND protection is **contractual and party-specific**; it covers a *disclosed, claimable*
     SEP. It does **not** shield you from **undisclosed** patents or **non-SEP** patents
     (ordinary patents covering a *specific* nonce/IV trick are not FRAND-obligated in the
     same way — and may be enforceable with injunction).
  2. **Willingness is judged by your behavior** (you must actively seek a licence). A passive
     "we shipped, sue me" posture fails.
  3. A **permissive code license is orthogonal** — it neither supplies this protection nor
     substitutes for it.
  4. EU framework ≠ worldwide. Outside the EU, injunction risk and FRAND treatment vary by
     jurisdiction; a co-op with cross-border vendors needs multi-jurisdiction FTO.

## 4. What actually de-risks (the "help not get sued" playbook)
Order of impact, most to least:
1. **Prefer non-infringing mechanisms.** Use only public-domain / FRAND-cleared crypto
   (HMAC, AES-GCM). For framing, implement the *published, publicly-known* fields and **do not
   invent** the unverified bits; if a specific scheme is patent-claim-charted as risky, provide
   a non-infringing alternative or a documented abstention rather than shipping it.
2. **Keep a running patent register + claim chart** (`patents/README.md`). Per mechanism:
   patent IDs, claim scope, essentiality guess, FRAND posture logged, last checked.
3. **Maintain a documented FRAND good-faith record** for every vendor/SEP you rely on.
   This is what defeats injunctions, not a GitHub license.
4. **Clean-room provenance** (independent implementation of the *published spec*, no contact
   with a paid reference impl or vendor source). This kills *copyright* copying and the
   *willful-infringement* aggravator (damages multiplier), even though it can't defeat a
   valid *literal/equivalent* claim.
5. **No-FTO disclaimer, inherited by downstreams** (`NOTICE.md`). Do not assert conformance or
   "certified." A *test/verifier* of a standard is not a certified product — keep it that way.
6. **Avoid the GPL forks as a permissive base.** `libiec61850` / `wendy512` are GPLv3
   copyleft; they cannot be relicensed permissively or embedded in a permissive closed
   product, and `libiec61850` doesn't implement 62351-6 anyway. Use them only as a *test
   peer* (out-of-tree, e.g. Docker), never vendored — exactly the pattern cB-Sigma already
   uses for its interop target.

## 5. License feasibility, verdict
- **Code license:** Apache-2.0 is the recommended permissive choice — it has an **express
  patent grant (§3)** and a **Notice/NOTICE** field for exactly this kind of disclosure
  situation. MIT/BSD are fine but lack the patent-grant clause and NOTICE mechanism Apache
  adds.
- **FTO:** cannot be achieved by license choice. Achievable *only* via §4 (clean-room + FRAND
  record + claim charting + mechanism avoidance + disclaimer). **Residual risk: MEDIUM and
  unavoidable** for the specific GOOSE framing + 62351-9 key/nonce scheme; LOW–MEDIUM for
  crypto primitives.
- **Conclusion for this project:** ship it, but as a **clean-room verifier/harness with a
  patent register and no-FTO disclaimer**, *not* a "you can now deploy secure GOOSE" product.
  The harness shape is *lower exposure* than a full stack (see `FEASIBILITY_VERDICT.md`),
  not zero — be honest with downstreams about that.

## 6. Things to verify before trusting this
- [ ] Current IEC IPR policy: does IEC now publish any public SEP list? (affects §2.)
- [ ] Status of the EU SEP Regulation implementation / EUIPO Competence Centre go-live date.
- [ ] Claim chart on US 20220376923 and any NXP "GOOSE message authentication" family.
- [ ] Whether a 62351-6 wire-shape oracle (real secured capture or 2nd impl) exists post-2026-10.
- [ ] Counsel sign-off on the no-FTO NOTICE wording.
