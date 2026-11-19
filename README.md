# UWASIC Design Template

A template for mixed-signal ASIC design using open-source tools, featuring automated workflows for digital, analog, and integration for TinyTapeout chip projects.

## Transmitter behavioral models

The half-rate CML mux and FFE cells, their pin/clock contract, and VerA test
commands are documented in [the transmitter README](analog/PAM4SerDes/va/Transmitter/README.md).
These use the explicit `tx-lint`, `tx-check`, and `tx-test` targets in
`analog/PAM4SerDes/build/va`; they are separate from the OpenVAF/OSDI flow.

## Documentation

**Full documentation is available in the [`docs/`](./docs) directory.**

Please refer to the documentation for:

- [Environment Setup](./docs/src/content/Environment)
- [Digital Workflow](./docs/src/content/Flows/Digital.ts)
- [Analog Workflow](./docs/src/content/Flows/Analog.ts)
- [Mixed-Signal Workflow](./docs/src/content/Flows/MixedSignal.ts)
- [TinyTapeout Integration](./docs/src/content/TinyTapeout)

### Quick Start Docs

To view the documentation locally:

```bash
cd docs/
bun install
bun run dev
```
