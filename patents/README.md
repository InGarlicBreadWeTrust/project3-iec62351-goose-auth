# patents/README.md — running SEP register + claim charting SOP

> This is the **legal backbone** of the project. No code change, check definition, or
> public-facing claim is merged without its `patents/` entry being current. Without this,
> the project is a "trust the vendor" failure dressed as a "help not get sued" project.

## What goes in the register
One entry per *mechanism* the harness touches (not per patent). Each entry has:

- **id** — e.g. `MECH-62351-6-AUTHVALUE-FRAG` / `MECH-62351-9-KEYDELIVERY-PULL` /
  `MECH-GOESE-IV-PER-PUBLISHER`.
- **claim chart (per patent)** — patent number, claims asserted, claim language quoted with
  claim numbers, independent-claim-by-independent-claim, mapped to the mechanism we touch.
- **essentiality guess** (not a legal opinion; engineering best-effort):
   - `likely-essential` — the mechanism is the standard's only published path.
   - `likely-nonessential` — alternative published paths exist (e.g. AES-GCM vs HMAC).
   - `undetermined` — must chart each independent claim.
- **FRAND posture** — "on offer / in negotiation / no claim found / N/A (public domain)" +
   the date + the link to the negotiation record.
- **our position** — `use` / `use-with-alternative` / `abstain` + justification.
- **last reviewed** — date + reviewer.
- **links** — patent text, IEC clause quote, our `checks/` entry that exercises it.

## Worked example — template + first entry (to be filled in by counsel)
### `MECH-62351-6-AUTHVALUE-FRAG`
- **Claims asserted (to be charted):** US 20220376923 "MESSAGE AUTHENTICATION"
  (ESINER/CHEN/… Singapore, published 2022-12-01, cites IEC 62351-6 RSA-for-GOOSE by name) —
  chart each independent claim against the 62351-6 `AuthValue` field construction.
- **Other suspects to chart:** any "GOOSE/SV authentication / group MAC / per-publisher IV /
  sliding-window replay" family (search WIPO/USPTO/EPO/ESPACenet for IEC 62351-6 + RSA +
  GOOSE). NXP-family suspected.
- **Essentiality guess:** `likely-essential` for the RSA-GOOSE MAC (it's the standard path);
   `likely-nonessential` for HMAC/AES-GCM (public-domain / FRAND-covered across dozens of
   standards).
- **FRAND posture:** `to be determined` — engage the EUIPO Competence Centre once live;
   file a FRAND request to named SEP holders as part of the co-op pilot.
- **Our position:** **`use-with-alternative`.** For real trip traffic use `HMAC-SHA-256`
   (public-domain family), **abstain** from `AES-GMAC` unless IV-per-publisher is confirmed,
   **do not use** `RSA/RSASSA` for 3 ms GOOSE (impractical, out-of-budget, and the most
   patent-claim-cited variant — see `SECURITY_DESIGN §2` T1/T4).
- **Last reviewed:** 2026-10-28, pending counsel sign-off.
- **Links:** `LICENSE_SEP_ASSESSMENT.md §1`, `SECURITY_DESIGN §2.1/§2.2`, US 20220376923.

## Process (non-negotiable)
1. **Before any new check or public claim** about 62351-6/61850/62351-9, run this SOP.
2. **Chart the independent claims** of every patent found via WIPO INPADOC / USPTO PAIR /
   EPO Open Patent / ESPACenet / the IEC IPR disclosure (if any now publish one — verify the
   current IEC policy before relying on it).
3. **Log the FRAND posture** (date, who, where we sent it, what was offered), and re-log on
   every status change.
4. **No public-facing claim** ("we check 62351-6," "this is conformant," "no infringement")
   is merged without its `patents/` entry showing a current FRAND posture + a claim chart.
5. **When an EPO/US/EUIPO decision or a new SEP disclosure appears**, reopen the affected
   mechanism entry, log the date, and re-review dependent `checks/` entries.
6. **The register is part of the repo's legal posture.** No code change bypasses it.

## Things the register must NOT do
- Claim FTO (that's counsel's job).
- Assume a patent is/ isn't essential without the chart.
- Rely on IEC's IPR disclosures as a comprehensive SEP registry — IEC's IPR policy is
   currently a *disclosure* obligation, not a public list (verify before relying).
- Let any "PASS" claim be published without its dependent mechanism entry being current.
