# Contributing

This is the research scaffold for `project3-` (IEEE 62351-authenticated GOOSE
authentication and conformance checking). It is small and safety-adjacent, so the
bar for a merged change is "prove it without risking protection logic."

## How to contribute

1. Fork the repo.
2. Work on a feature branch.
3. Add or extend a conformance check under `conformance/checks/` plus a fixture
   under `conformance/testvectors/`, and make it pass the executor.
4. Keep the executor **passive**: it parses and asserts on captured/recorded
   frames. Do not add code that drives protection or sends packets.
5. Open a PR with a short description of what changed and which check/fixture
   you added.

## We accept

- New conformance checks (auth, key management, replay, wire format).
- New test fixtures + `.meta` files under `conformance/testvectors/`.
- Documentation and clarity improvements.
- Bug fixes that keep the harness passive and CI green.

## We do not accept

- Any active/attacking capability or a path that drives IED protection commands.
- Secret material, credentials, or vendor private keys.
- Changes that weaken the passive design without a documented rationale.

## Before you push

- Run the executor against the committed fixtures; CI must stay green.
- Re-confirm the conformance `.yaml` checks still reference the right fixtures.
