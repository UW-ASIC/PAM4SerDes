#!/usr/bin/env python3
"""Turn a structural Verilog-A hierarchy into a deck ngspice can run.

VerA compiles one .va file into one OSDI device, and a device holds at most 255
unknowns. The transmitter, the receiver and the full SerDes are far past that, so the
hierarchy runs as subcircuits of small devices:

  * a module with no analog block that instantiates modules from other files is
    STRUCTURAL: it becomes a `.subckt` of its instances;
  * every other module is a DEVICE: `vera --emit-osdi` builds its file, flattening
    whatever that file instantiates (file-local helpers, or a small loop like tx_pll),
    and the deck loads it with `pre_osdi`.

The .va files stay the only source. Nothing in the generated deck is edited by hand.

    python3 .flows/tools/va_deck.py analog/PAM4SerDes/va/pam4_serdes.va -o out/pam4_serdes.cir

writes out/pam4_serdes.cir and builds out/osdi/*.osdi (again when a .va changes). A testbench
deck `.include`s the result and places `X1 <pins> pam4_serdes`. Pins follow the module's
port order, buses expanded as declared (`[31:0] d` -> d_31 ... d_0). Devices the
testbench itself needs (a checker, a source) go through `--also file.va`, which builds
and loads them with the rest.

Three things a deck needs from ngspice: version 45 or newer (44 cannot place a device
with more than 18 pins); the default solver (`.option klu` is faster on a netlist this
size but gives wrong node voltages with these devices); and a fourth `tran` argument,
e.g. `tran 1p 26n 0 1m` (the minimum time step is 1e-11 times it, and without it runs
die with "timestep too small" just before a clock edge).

Structural modules use a plain subset: named or positional port connections to a net,
a bit `n[i]`, a slice `n[a:b]` or a concatenation `{...}` of those, and `#(.p(expr))`
overrides. No generate loops: write the instances out.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def strip(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//.*", "", text)
    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.S)   # (* desc = "..." *) attributes


def span(rng):
    a, b = rng
    return range(a, b + (1 if b >= a else -1), 1 if b >= a else -1)


def split_top(s):
    """Split on commas that are not inside (), [] or {}."""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += {"(": 1, "[": 1, "{": 1, ")": -1, "]": -1, "}": -1}.get(ch, 0)
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return [x for x in out + [cur.strip()] if x]


def closing(s, i):
    """Index just past the parenthesis that closes the one at s[i]."""
    depth = 0
    for j in range(i, len(s)):
        depth += {"(": 1, ")": -1}.get(s[j], 0)
        if depth == 0:
            return j + 1
    raise ValueError(f"unbalanced parentheses: {s[i:i + 60]}")


class Mod:
    def __init__(self, name, ports, body, path):
        self.name, self.path = name, path
        self.ports = re.findall(r"\w+", ports)
        at = re.search(r"\banalog\b", body)
        self.has_analog = at is not None
        self.head = body[:at.start()] if at else body
        self.ranges, self.ground, self.params, self.insts = {}, set(), {}, []

    def parse(self, mods):
        for st in (s.strip() for s in self.head.split(";")):
            word = re.match(r"\w+", st)
            if not word:
                continue
            word = word.group(0)
            if word in ("input", "output", "inout", "electrical"):
                rng = re.match(r"\w+\s*\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\]", st)
                if rng:
                    for n in re.findall(r"\w+", st[rng.end():]):
                        self.ranges[n] = (int(rng.group(1)), int(rng.group(2)))
            elif word == "ground":
                self.ground.update(re.findall(r"\w+", st[len(word):]))
            elif word == "parameter":
                m = re.match(r"parameter\s+(?:real\s+|integer\s+)?(\w+)\s*=\s*(.*?)\s*(?:\bfrom\b.*|\bexclude\b.*)?$", st, re.S)
                self.params[m.group(1)] = " ".join(m.group(2).split())
            elif word in mods:
                self.insts.append(self.instance(st, word))

    def instance(self, st, type_):
        i, over = len(type_), {}
        rest = st[i:].lstrip()
        if rest.startswith("#"):
            i = st.index("(", i)
            j = closing(st, i)
            for it in split_top(st[i + 1:j - 1]):
                m = re.fullmatch(r"\.(\w+)\s*\((.*)\)", it, re.S)
                over[m.group(1)] = " ".join(m.group(2).split())
            i = j
        m = re.match(r"\s*(\w+)\s*", st[i:])
        name, i = m.group(1), i + m.end()
        return type_, name, over, split_top(st[i + 1:closing(st, i) - 1])

    def bits(self, n):
        return [f"{n}_{i}" for i in span(self.ranges[n])] if n in self.ranges else [n]

    def pins(self):
        return [b for p in self.ports for b in self.bits(p)]

    def nodes(self, expr):
        """SPICE nodes of a connection: a net, n[i], n[a:b] or {a, b, ...}."""
        expr = expr.strip()
        if expr.startswith("{"):
            return [x for part in split_top(expr[1:-1]) for x in self.nodes(part)]
        m = re.fullmatch(r"(\w+)\s*(?:\[\s*(-?\d+)\s*(?::\s*(-?\d+)\s*)?\])?", expr)
        if not m:
            raise ValueError(f"{self.name}: cannot connect `{expr}`")
        n, a, b = m.groups()
        if n in self.ground:
            return ["0"]
        if a is None:
            return self.bits(n)
        return [f"{n}_{i}" for i in span((int(a), int(b) if b is not None else int(a)))]


def load(top):
    """Every module reachable from `top` through `include, by name."""
    mods, local, seen, todo = {}, {}, set(), [top.resolve()]
    while todo:
        path = todo.pop(0)
        if path in seen:
            continue
        seen.add(path)
        text = strip(path.read_text())
        todo += [(path.parent / inc).resolve() for inc in re.findall(r'`include\s+"([^"]+\.va)"', text)]
        for m in re.finditer(r"\bmodule\s+(\w+)\s*\((.*?)\)\s*;(.*?)\bendmodule\b", text, re.S):
            mod = Mod(m.group(1), m.group(2), m.group(3), path)
            mods.setdefault(mod.name, mod)
            local.setdefault(path, set()).add(mod.name)
    for m in mods.values():
        m.parse(mods)
        # A helper defined in the module's own file is part of its device, even when
        # another file defines a module of the same name (phase_aligner, cdr_pd_linear).
        m.foreign = [t for t, *_ in m.insts if t not in local[m.path]]
    return mods, seen


def param(v):
    # ponytail: VA and SPICE agree on every scale factor but M (VA mega, SPICE milli).
    if re.search(r"\d\s*M\b", v):
        raise ValueError(f"`{v}`: write 1e6 instead of M, SPICE reads M as milli")
    return v if re.fullmatch(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?[a-zA-Z]*", v) else "{" + v + "}"


def compose(top, osdi_dir, also=()):
    """The deck text, and the device modules it loads: {module: its .va file}."""
    mods, seen = load(top)
    newest = max(p.stat().st_mtime for p in seen)
    name = top.stem
    if name not in mods:
        sys.exit(f"{top}: no module named {name}")
    structural = lambda m: not m.has_analog and bool(m.foreign)
    devices, defs = {}, {}

    def use(m):
        """True for a subcircuit, False for a device; emits a subcircuit once."""
        if not structural(m):
            devices[m.name] = m.path
            return False
        if m.name not in defs:
            defs[m.name] = None   # reserve the slot: children are emitted after it
            lines = []
            for type_, inst, over, conn in m.insts:
                child = mods[type_]
                named = [re.fullmatch(r"\.(\w+)\s*\((.*)\)", c, re.S) for c in conn]
                if all(named):
                    by_port = {n.group(1): n.group(2) for n in named}
                    unknown = set(by_port) - set(child.ports)
                    if unknown:
                        raise ValueError(f"{m.name}.{inst}: {type_} has no port {sorted(unknown)}")
                else:
                    if any(named) or len(conn) != len(child.ports):
                        raise ValueError(f"{m.name}.{inst}: {len(conn)} connections for {type_}'s {len(child.ports)} ports")
                    by_port = dict(zip(child.ports, conn))
                nodes = []
                for p in child.ports:
                    want = child.bits(p)
                    got = m.nodes(by_port[p]) if by_port.get(p, "").strip() else [f"nc_{inst}_{b}" for b in want]
                    if len(got) != len(want):
                        raise ValueError(f"{m.name}.{inst}: .{p} is {len(want)} wide, `{by_port[p]}` is {len(got)}")
                    nodes += got
                unknown = set(over) - set(child.params)
                if unknown:
                    raise ValueError(f"{m.name}.{inst}: {type_} has no parameter {sorted(unknown)}")
                values = [f"{k}={param(v)}" for k, v in over.items()]
                if use(child):
                    lines.append(" ".join([f"X{inst}", *nodes, type_, *values]))
                else:   # an OSDI device takes its parameters on a .model card
                    lines.append(" ".join([f".model m_{inst}", type_, *values]))
                    lines.append(" ".join([f"N{inst}", *nodes, f"m_{inst}"]))
            head = " ".join([f".subckt {m.name}", *m.pins(), *(f"{k}={param(v)}" for k, v in m.params.items())])
            defs[m.name] = [head, *lines, f".ends {m.name}"]
        return True

    if not use(mods[name]):
        sys.exit(f"{name} is a single device: `vera --emit-osdi` it and load it with pre_osdi")
    for extra in also:   # testbench equipment: single devices
        devices[extra.stem] = extra.resolve()
        newest = max(newest, extra.stat().st_mtime)
    deck = "\n".join([
        f"* {name}: composed from {top} by .flows/tools/va_deck.py. Do not edit.",
        f"* pins: {' '.join(mods[name].pins())}",
        ".control",
        *(f"pre_osdi {osdi_dir.resolve() / (d + '.osdi')}" for d in devices),
        ".endc",
        *(ln for d in defs.values() for ln in d), ""])
    return deck, devices, newest


def tree(top):
    """The architecture as text: who places what, how many of each cell, what is left out.

    One line per module that places modules from other files, then the flattened count of
    every cell in the design, the placeholder cells in use, and the .va files next to the
    top that nothing includes. Stable order, so it can be compared with a reference file.
    """
    import collections
    mods, seen = load(top)
    lines, total = [], collections.Counter()

    def walk(name, times):
        kids = collections.Counter(mods[name].foreign)
        if not kids:
            total[name] += times
        for kid, n in kids.items():
            walk(kid, times * n)

    walk(top.stem, 1)
    reach, todo = set(), [top.stem]
    while todo:
        name = todo.pop()
        if name not in reach:
            reach.add(name)
            todo += mods[name].foreign
    for name in sorted(reach):
        kids = collections.Counter(mods[name].foreign)
        if kids:
            lines.append(f"{name}: " + ", ".join(k if n == 1 else f"{k} x{n}" for k, n in sorted(kids.items())))
    lines.append("cells: " + ", ".join(f"{k} x{n}" for k, n in sorted(total.items())))
    held = sorted(n for n in total if "placeholders" in mods[n].path.parts)
    lines.append("placeholders: " + (", ".join(held) or "none"))
    root = top.resolve().parent
    unused = sorted(str(f.relative_to(root)) for f in root.rglob("*.va") if f.resolve() not in seen)
    lines.append("not in the design: " + (", ".join(unused) or "none"))
    return "\n".join(lines) + "\n"


def build(devices, osdi_dir, newest):
    """vera --emit-osdi every device whose .osdi is older than the newest .va."""
    # ponytail: one edited .va rebuilds every device (about two minutes). Track each
    # device's own includes if that gets in the way.
    stale = [d for d in devices
             if not (osdi_dir / f"{d}.osdi").exists() or (osdi_dir / f"{d}.osdi").stat().st_mtime < newest]
    if not stale:
        return
    if not shutil.which("vera"):
        sys.exit("vera is not on PATH: it builds the .osdi devices ngspice loads")
    osdi_dir.mkdir(parents=True, exist_ok=True)

    def one(d):
        r = subprocess.run(["vera", "--emit-osdi", devices[d].name, f"--expect-module={d}",
                            "-o", str((osdi_dir / f"{d}.osdi").resolve()),
                            "--work-dir", str((osdi_dir / "work" / d).resolve())],
                           cwd=devices[d].parent, capture_output=True, text=True)
        return d, r

    print(f"building {len(stale)} OSDI device(s) into {osdi_dir}/ ...", file=sys.stderr)
    # Each build is a Zig compile of several hundred MB. Three at once is safe on a 16 GB
    # machine; VA_DECK_JOBS=1 if memory is tight, more if there is plenty.
    with ThreadPoolExecutor(int(os.environ.get("VA_DECK_JOBS", "3"))) as pool:
        for d, r in pool.map(one, stale):
            if r.returncode != 0:
                errors = [ln for ln in r.stderr.splitlines() if ln.startswith("error")] or [r.stderr[-400:]]
                sys.exit(f"vera --emit-osdi {devices[d]}:\n  " + "\n  ".join(errors))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("top", type=Path, help="top-level .va; the module has the file's name")
    ap.add_argument("-o", "--out", type=Path, help="deck to write; devices go to <its folder>/osdi/")
    ap.add_argument("--tree", action="store_true", help="print the architecture (see tree) and stop")
    ap.add_argument("--also", type=Path, nargs="*", default=[], metavar="FILE.va",
                    help="testbench devices to build and load too (one module per file, named like it)")
    ap.add_argument("--no-build", action="store_true", help="write the deck only")
    a = ap.parse_args()
    if a.tree:
        sys.stdout.write(tree(a.top))
        return
    if not a.out:
        ap.error("give -o OUT, or --tree")
    osdi_dir = a.out.parent / "osdi"
    try:
        deck, devices, newest = compose(a.top, osdi_dir, a.also)
    except ValueError as e:
        sys.exit(f"error: {e}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(deck)
    if not a.no_build:
        build(devices, osdi_dir, newest)
    print(f"{a.out}: {deck.count('.subckt ')} subcircuits, {len(devices)} devices")


if __name__ == "__main__":
    main()
