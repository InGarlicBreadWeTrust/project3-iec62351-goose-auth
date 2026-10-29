# Security Disclosure

This project is the research scaffold for IEEE 62351-authenticated GOOSE
authentication on IEDs/RTUs and GOOSE relay protection. A defect here can affect
safety-critical protection logic, so we take reports seriously.

## Responsible disclosure

1. **Do not disclose publicly** before a coordinated fix exists.
2. Email a summary + repro to the maintainers (see `CONTRIBUTING.md`) or open an
   issue labelled `security`.
3. We aim to acknowledge within 5 business days and patch material findings within
   30 days.

## In scope

- Key-management, replay-protection, and conformance-check logic in
  `conformance/executor/`.
- The conformance test harness and fixtures.
- Any path that exposes a co-op to a replay, downgrade, or bypass in an
  authenticated GOOSE flow.

## Out of scope

- Vendor IED firmware itself — report defects to the IED vendor.
- Misuse of a correct harness for active attack testing.

## Security model summary

See `SECURITY_DESIGN.md` and `PRD.md`. The conformance executor is intentionally
passive: it parses and asserts conformance of captured/recorded GOOSE frames; it
does not drive protection commands.

<!-- TODO(maintainer): fill in a real disclosure channel / PGP key here. -->
