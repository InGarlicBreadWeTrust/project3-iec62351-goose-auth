# NOTICE — legal disclaimer, inherited by all downstream users

**Read before use. This file must be preserved verbatim in every derivative and downstream
distribution.**

1. **No freedom-to-operate guarantee.** Nothing in this repository — its code, its tests, its
   vectors, or its documentation — grants, implies, or warrants **freedom to operate** under
   any patent, and **none of it should be read as advice that use is non-infringing.**
   Implementing or testing a mechanism described in IEC 61850 / IEC 62351-6 / IEC 62351-9
   may fall within claims of one or more patents (standard-essential or otherwise).

2. **Permissive license ≠ patent clearance.** This project may carry a permissive code license
   (Apache-2.0). That license governs redistribution of *this code* and, under Apache-2.0 §3,
   grants a limited patent licence **from this project's contributors only**. It does **not**
   licence, license-around, or indemnify against any **third-party** patent, including any
   **standard-essential patent** in the IEC 61850 / 62351 family. **A permissive license does
   not confer freedom to operate.**

3. **Not certified. No conformance claim.** This project makes **no claim of conformance,
   certification, or certification-equivalent status** to IEC 62351-6 / IEC 61850-8-1, and
   is **not** a certified security product. It is a **test/conformance harness and reference
   for the purpose of verifying other implementations' claims.** Do not describe it otherwise.

4. **FRAND posture is the user's obligation.** A good-faith FRAND licence posture and a
   documented freedom-to-operate assessment **may be required** for lawful use. Users must
   obtain their own FTO / FRAND position. Where a mechanism is flagged in `patents/README.md`
   as claim-charted at risk, prefer the documented non-infringing alternative or abstention.

5. **Clean-room provenance.** Code claiming to implement a mechanism in a paywalled standard
   was developed **independently from the published specification only**, with **no contact**
   with any paid reference implementation or proprietary IED source, in order to avoid
   copyright copying and willful-infringement exposure. That provenance does not defeat a
   valid literal or equivalent infringement claim.

6. **No warranty of accuracy of the wire shape.** Where the published standard text is
   ambiguous or has **no public/second-implementation oracle** (known at least for the
   62351-6 GOOSE `Extension`/`AuthValue` framing as of 2026-10-28 — see `docs/landscape.md`),
   the wire shape is this project's **reading of the spec**, not a settled truth, and may not
   match a vendor's proprietary implementation. Treat any "pass" as *provisional*.

7. **Not legal advice.** For a freedom-to-operate opinion, an SEP/FRAND negotiation, or any
   deployment decision, consult qualified intellectual-property counsel in the relevant
   jurisdiction(s).

© 2026, project contributors. See `LICENSE`. See `LICENSE_SEP_ASSESSMENT.md`.
