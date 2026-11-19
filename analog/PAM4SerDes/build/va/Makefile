include ../config.mk

# The original OSDI targets use the Nix environment. The portable VerA
# targets below can also run outside Nix with explicit executable paths.
TX_GOALS := tx-lint tx-check tx-test tx-help
ifneq ($(strip $(filter-out $(TX_GOALS),$(if $(MAKECMDGOALS),$(MAKECMDGOALS),all))),)
ifndef IN_NIX_SHELL
  $(error This Makefile must be run inside the nix-shell environment. Run ./env.sh first to enter the nix-shell)
endif
endif

# Verilog-A -> OSDI.
#
# OpenVAF compiles a .va model to a .osdi shared object that ngspice and VACASK both
# load at runtime, and SpiceRack attaches with `tb.osdi(path)`. That is the whole
# integration: a behavioural model becomes just another device the same testbenches can
# drive, rather than a separate simulation world.
#
# The stateful transmitter models have separate VerA targets below. Their
# event and transport-delay behavior is not validated through OpenVAF/OSDI.

# openvaf-r is the name the packaged OpenVAF fork installs; plain openvaf is the
# upstream binary. Take whichever is on PATH.
OPENVAF := $(shell command -v openvaf-r 2>/dev/null || command -v openvaf 2>/dev/null)

VA_DIR = ../../va
OSDI_DIR = osdi
VA_SRCS = $(wildcard $(VA_DIR)/*.va)
OSDI_OBJS = $(patsubst $(VA_DIR)/%.va,$(OSDI_DIR)/%.osdi,$(VA_SRCS))

.PHONY: all va clean list

all: va

## va - compile every ../../va/*.va to osdi/
va: $(OSDI_OBJS)
	@if [ -z "$(VA_SRCS)" ]; then \
		echo "No .va models in $(VA_DIR)/ — nothing to compile."; \
	else \
		echo "Verilog-A models built into $(OSDI_DIR)/"; \
	fi

$(OSDI_DIR)/%.osdi: $(VA_DIR)/%.va
	@if [ -z "$(OPENVAF)" ]; then \
		echo "openvaf not found on PATH."; \
		echo "It ships in the nix shell via EDA-Packaged; re-enter ./env.sh."; \
		exit 1; \
	fi
	@mkdir -p $(OSDI_DIR)
	@echo "Compiling $< -> $@"
	@$(OPENVAF) $< -o $@

## list - show what a testbench can load
list:
	@if [ -d $(OSDI_DIR) ] && ls $(OSDI_DIR)/*.osdi >/dev/null 2>&1; then \
		for f in $(OSDI_DIR)/*.osdi; do echo "  $$(cd $$(dirname $$f) && pwd)/$$(basename $$f)"; done; \
	else \
		echo "No .osdi built yet — run 'make va'."; \
	fi

clean:
	@rm -rf $(OSDI_DIR)
	@echo "Clean complete"

# Explicit sources in va/Transmitter are selected by this runner; unlike the
# OSDI wildcard above, these targets do not skip models in the subdirectory.
# Keep this flow separate: compiling a stateful model is not evidence that
# another backend implements its events and delays correctly.
PYTHON ?= python3
VERA ?= vera
VERA_ZIG ?=
TX_RUNNER := ../../test/tx_cml_ffe/run_checks.py
TX_TOOL_ARGS = --vera "$(VERA)" $(if $(VERA_ZIG),--zig "$(VERA_ZIG)")

.PHONY: tx-lint tx-check tx-test tx-help
tx-lint:
	$(PYTHON) "$(TX_RUNNER)" $(TX_TOOL_ARGS) --mode lint

tx-check:
	$(PYTHON) "$(TX_RUNNER)" $(TX_TOOL_ARGS) --mode check

tx-test:
	$(PYTHON) "$(TX_RUNNER)" $(TX_TOOL_ARGS)

tx-help:
	@echo "tx-lint: lint the two TX cells and their test wrapper"
	@echo "tx-check: also compile and check repeated includes"
	@echo "tx-test: run output, clock-phase, load and reset comparisons"
	@echo "Set VERA=/path/to/vera and optionally VERA_ZIG=/path/to/zig."
	@echo "See ../../va/Transmitter/README.md."
