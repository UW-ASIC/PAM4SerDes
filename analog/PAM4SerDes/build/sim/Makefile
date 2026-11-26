include ../config.mk

# Enforce Nix Shell
ifndef IN_NIX_SHELL
  $(error This Makefile must be run inside the nix-shell environment. Run ./env.sh first to enter the nix-shell)
endif

# Run the block's SpiceRack testbenches.
#
# A testbench here is just a Python script under ../../test/ that builds a circuit and
# runs an analysis. Same convention as the netlist scripts one stage over: the script is
# the interface, so a plain sweep and a full DesignBench with corners are the same kind
# of thing to this Makefile and neither needs a plugin API.
#
# Sizing lives in those scripts too. SpiceRack has sweeps, corners and metric extraction
# but no gm/Id or optimiser, so a sizing loop is Python you write — sweep, extract,
# adjust. There is deliberately no target here pretending otherwise.

TEST_DIR = ../../test
VA_OSDI_DIR = ../va/osdi

# The Verilog-A hierarchy on ngspice.
#
# VerA builds one .va file into one OSDI device and caps a device at 255 unknowns, so the
# transmitter, the receiver and the top level cannot each be a device. `make deck` runs
# .flows/tools/va_deck.py, which turns every purely structural module into a .subckt and
# every other module into a device: out/$(VA_TOP).cir plus out/osdi/*.osdi. The .va files
# stay the only source. `make link` then runs the ngspice decks in ../../test/ that
# include that file and prints one PASS or FAIL line per deck; full logs go to out/.
#
#   make link                      every deck in LINK_DECKS
#   make link DECK=tb_datapath     one of them
#   make check                     everything CI runs: lint, arch, link, specs
VA_TOP ?= pam4_serdes
VA_ALSO = $(TEST_DIR)/prbs_chk.va
LINK_DECKS = tx_driver_test tb_pll tb_datapath tb_cdr tb_top
DECK ?= $(LINK_DECKS)
VA_DECK = ../../../../.flows/tools/va_deck.py
VA_SPECS = ../../../../.flows/tools/va_specs.py
ARCH = ../../architecture.txt
README = ../../../../README.md

.PHONY: all sim test list clean deck link lint arch specs check

all: sim

## sim - run every testbench in ../../test/
sim: test

test:
	@if [ ! -d $(TEST_DIR) ]; then echo "No $(TEST_DIR)/ directory."; exit 0; fi
	@found=0; for f in $(TEST_DIR)/*.py; do \
		[ -f "$$f" ] || continue; found=1; \
		echo "=== $$f (backend: $(BACKEND)) ==="; \
		SPICERACK_BACKEND=$(BACKEND) OSDI_DIR=$$(cd $(VA_OSDI_DIR) 2>/dev/null && pwd) \
			python3 "$$f" || exit 1; \
	done; \
	if [ $$found -eq 0 ]; then \
		echo "No testbenches in $(TEST_DIR)/."; \
		echo "A testbench is a .py that builds a circuit and runs an analysis."; \
	fi

## check - what CI runs: every file compiles, the hierarchy matches the architecture,
##         the decks pass, and the measured specs in the README are up to date
check: lint arch link specs

## lint - every .va under ../../va and ../../test compiles on its own (vera --lint)
lint:
	@n=0; rc=0; for f in $$(find ../../va ../../test -name '*.va' | sort); do \
		n=$$((n + 1)); \
		out=$$(cd $$(dirname $$f) && vera --lint $$(basename $$f) 2>&1) || { \
			rc=1; echo "FAIL lint: $$f"; echo "$$out" | grep -A6 '^error' | head -20; }; \
	done; \
	[ $$rc -eq 0 ] && echo "PASS lint: $$n Verilog-A files compile"; exit $$rc

## arch - the hierarchy in the .va files is the one written down in ../../architecture.txt
##        (UPDATE=1 rewrites that file: do it in the commit that changes the architecture)
arch:
	@mkdir -p out && python3 $(VA_DECK) ../../va/$(VA_TOP).va --tree > out/architecture.txt
	@if [ -n "$(UPDATE)" ]; then \
		{ grep '^#' $(ARCH); cat out/architecture.txt; } > out/architecture.new && cp out/architecture.new $(ARCH); \
		echo "$(ARCH) rewritten"; \
	elif grep -v '^#' $(ARCH) | diff -u - out/architecture.txt; then \
		echo "PASS arch: the hierarchy matches architecture.txt"; \
	else \
		echo "FAIL arch: the hierarchy differs from architecture.txt (lines with - are the reference, + the code)"; exit 1; \
	fi

## specs - write the numbers the decks measured into the README (run after link)
specs:
	@python3 $(VA_SPECS) out $(README) $(LINK_DECKS)

## deck - compose ../../va/$(VA_TOP).va into out/$(VA_TOP).cir and build its devices
deck:
	@python3 $(VA_DECK) ../../va/$(VA_TOP).va --also $(VA_ALSO) -o out/$(VA_TOP).cir

## link - run the hierarchy decks on ngspice (DECK=name for one of them)
# OMP_WAIT_POLICY=passive: ngspice's worker threads sleep between tasks instead of
# spinning. On a machine busy with other work, tb_top with eight spinning threads ran
# about 100x slower; if it still crawls, add `set num_threads=2` to the deck's .control.
link: deck
	@v=$$(ngspice --version 2>/dev/null | grep -oE 'ngspice-[0-9]+' | head -1 | cut -d- -f2); \
	if [ "$${v:-0}" -lt 45 ]; then \
		echo "ngspice 45 or newer is needed (found: $${v:-none}): 44 cannot place OSDI devices with more than 18 pins."; \
		exit 1; \
	fi
	@rc=0; for d in $(DECK); do \
		log=$$(pwd)/out/$$d.log; \
		(cd $(TEST_DIR) && OMP_WAIT_POLICY=passive ngspice -b $$d.sp) > $$log 2>&1; \
		if grep -q '^PASS' $$log; then grep '^PASS' $$log; \
		else rc=1; grep -E '^FAIL' $$log || echo "FAIL $$d: no verdict, see $$log"; \
			grep -E 'Timestep too small|^Error' $$log | cut -c1-160 | head -3; \
		fi; \
	done; exit $$rc

## list - which simulators this environment can actually reach
list:
	@echo "BACKEND = $(BACKEND)"
	@for s in ngspice vacask espice; do \
		if command -v $$s >/dev/null 2>&1; then echo "  $$s: available"; \
		else echo "  $$s: not on PATH"; fi; \
	done
	@python3 -c 'import spicerack; print("  spicerack:", spicerack.__name__, "ok")' 2>/dev/null \
		|| echo "  spicerack: not importable — re-enter ./env.sh"

clean:
	@rm -rf __pycache__ $(TEST_DIR)/__pycache__ *.raw *.log out
	@echo "Clean complete"
