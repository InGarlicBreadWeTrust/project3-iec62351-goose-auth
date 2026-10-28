# testvectors/README.md — ingestion protocol + provenance (anti-fabrication contract)

> Defense-direction, 2026-10-28. The **anti-fabrication contract**. A fabricated `PASS` on an
> unverified wire shape is the single worst thing this project could emit. No entry is merged
> without this protocol satisfied.

## Invariants (CI must fail on violation)
1. **No secrets.** No keys, no certificate material, no unredacted capture bytes.
2. **Provenance mandatory.** Every entry: source URL + capture-provenance date + a
   "clean-room-attested" flag. No entry without all fields.
3. **PROVISIONAL→PASS is gated.** A WIRE.* check becomes `PASS` only when the entry carries a
   **traceable 2nd implementation reference** *or* a **real secured GOOSE capture pointer**.
4. **No silent PASS.** No entry can mark `PASS` without a linked `conformance/checks/*.yaml`
   that consumes it.
5. **No conformance wording** in any entry's human-readable notes.

## Entry schema
```yaml
id: <unique-v1-<uuid>>                 # e.g. v1-0a7c... (stable, monotonic)
type: 2nd-impl | real-capture | public-spec
spec_refs:                            # IEC / IEEE / RFC / paper
  - IEC 62351-6:2020
  - IEEE P2030.100.2
source:
  repo_url: https://github.com/...    # for 2nd-impl
  # or capture_pointer: ...           # for real-capture (metadata + pointer, NOT bytes by default)
  captured_by: <org | user>
  capture_provenance_date: 2026-10-28
  redaction_status: unredacted | redacted-only-metadata
impl:
  name: <peer>
  language: Go | Rust | C | Python | Zig
  license: Apache-2.0 | MIT | ...
  version_or_commit: <sha>            # pin the exact commit
  no_contact_attested: true          # clean-room attestation
  provenance_path: provenance/<impl>.md
checks_exercised: [WIRE.*, AUTH.1, IV.1, ...]
oracle_kind: 2nd-impl | real-capture | public-spec-research
pass_gate:
  # the entry is "PASS-gated" when any of these is true:
  - oracle_kind == 2nd-impl AND no_contact_attested == true
  - oracle_kind == real-capture AND redaction_status == redacted-only-metadata
provisionally_marked: true|false     # false only when pass_gate satisfied
reviewed_at: 2026-10-28
reviewer: <name>
```

## Ingestion workflow
1. **Capture** — record metadata only by default (who, when, which peer, which IED model,
   which publication/group the frame came from). No bytes unless redacted-only is needed;
   bytes are a redacted pointer, not stored.
2. **Provenance log** — add `provenance/<impl>.md` with the clean-room attestation for the
   2nd-impl / capture source. Barrier audit: confirm no vendor material entered Phase B.
3. **Entry up** — add a `tests/` entry under this schema. CI verifies every field present.
4. **Gate** — if `pass_gate` is not satisfied, the entry is `PROVISIONAL` and the
   dependent `conformance/checks/*.yaml` check stays `PROVISIONAL:<reason>`.
5. **Promote** — to move WIRE.* to `PASS`, add a 2nd-impl entry that clears `pass_gate`
   AND is not in violation of §1–§5. `conformance/executor/reporting.go` then flips the
   check output; the commit log records the promotion with the link.

## Anti-fabrication guardrails
- **No `PASS` without a 2nd impl or a real capture pointer.** A "PASS we think is right
   because the spec text implies it" is **PROVISIONAL with reason "spec-only, no
   oracle"** — not PASS. This is the project's defining property.
- **No "conformance" wording in entries** — "this frame passes 62351-6" is forbidden;
   "this frame's wire shape matches the spec reading in this repo" is allowed, and the
   *difference is the whole project*.
- **One reviewer per entry. Barrier audit on every 2nd-impl ingestion.** The Phase-A/Phase-B
   barrier from `BUILD_APPROACH.md §1` is enforced on 2nd-impl ingestion, not just on authoring.
- **PROVISIONAL entries are first-class and expected** as of 2026-10-28 (no 2nd 62351-6 impl
   or real secured capture exists in public — see `docs/landscape.md`).

## First entries to seed
- **v1-spec** — the IEEE P2030.100.2 (2026) as an authoritative *research* oracle, `PASS`
  gate: `oracle_kind == public-spec-research`. This is the only entry that can legitimately
  `pass_gate` on `REPL.1 / KEY.1` as of 2026-10-28, because those *behaviors* are published
  text. WIRE.* stays PROVISIONAL from this entry.
- **v1-prov-1** — `libiec61850` v1.6.2 as a **peer** (Docker test-peer, out-of-tree,
  un-vendored), `pass_gate`: N/A (GPL, not a 62351-6 reference either), included only to
  *prove the "unsecured GOOSE → extension-absent" smoke test in
  `conformance/executor/reporting.go`*.

## Open questions
- Whether to store *redacted* capture bytes at all, vs pointer + hash only (security / IC-SCADA
  data-privacy reason strongly favors pointer + hash only — `redaction_status:
  redacted-only-metadata` is the *minimum*, not the default).
- Whether `pass_gate` should also require a **second independent reviewer** for 2nd-impl
  entries (recommended: yes; this is the whole point of the project — a *single* 2nd impl
  is still not a 2nd *independent* oracle).
