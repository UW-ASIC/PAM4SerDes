#!/usr/bin/env python3
"""Write the specs the Verilog-A simulations measured into README.md.

Every deck that `make link` runs prints lines of the form

    SPEC <what> | <value>

This collects those lines from OUT/<deck>.log, adds what the hierarchy contains (from
OUT/architecture.txt, written by `make arch`), and puts the table between the two marker
lines in the README. Nothing in that table is typed by hand: a number changes when the
design does.

    python3 .flows/tools/va_specs.py OUT README.md deck1 deck2 ...
"""
import re
import sys
from pathlib import Path

BEGIN, END = "<!-- specs:begin -->", "<!-- specs:end -->"


def main():
    out, readme, decks = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
    rows = []
    for deck in decks:
        log = out / f"{deck}.log"
        if not log.exists():
            sys.exit(f"{log}: run `make link` first")
        text = log.read_text()
        if not re.search(r"^PASS", text, re.M):
            sys.exit(f"{deck} did not pass: no specs written")
        rows += [(what.strip(), value.strip(), f"`{deck}`")
                 for what, value in re.findall(r"^SPEC (.*?)\|(.*)$", text, re.M)]
    arch = dict(ln.split(": ", 1) for ln in (out / "architecture.txt").read_text().splitlines())
    counts = [int(n) for n in re.findall(r" x(\d+)", arch["cells"])]
    rows.append(("Cells in the design", f"{sum(counts)} instances of {len(counts)} cell types", "`architecture.txt`"))
    rows.append(("Ideal placeholders still in use", arch["placeholders"], "`architecture.txt`"))
    table = "\n".join(["| Spec | Value | Measured by |", "|---|---|---|",
                       *(f"| {a} | {b} | {c} |" for a, b, c in rows)])
    text = readme.read_text()
    if BEGIN not in text or END not in text:
        sys.exit(f"{readme}: the marker lines {BEGIN} and {END} are missing")
    head, rest = text.split(BEGIN, 1)
    new = head + BEGIN + "\n" + table + "\n" + END + rest.split(END, 1)[1]
    if new != text:
        readme.write_text(new)
    print(f"PASS specs: {len(rows)} rows in {readme.name}" + ("" if new == text else " (updated)"))


if __name__ == "__main__":
    main()
