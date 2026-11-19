"""Portable VerA checks for the transmitter mux and half-rate FFE.

Only Python's standard library is required. Run from any working directory.
Pass executable paths with --vera/--zig or set VERA/VERA_ZIG; otherwise use PATH.
"""
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from half_rate_checks import check_ffe, check_stream
from mux_transient_checks import check_mux_transient
from repository_checks import check_includes, check_supply_reset
from neighbor_checks import check_neighbors

HERE = Path(__file__).resolve().parent
BLOCK = HERE.parents[1]
MODELS = BLOCK / "va" / "Transmitter"
FIXTURES = HERE / "fixtures"


def executable(value, label):
    found = shutil.which(value)
    if found:
        return str(Path(found).resolve())
    candidate = Path(value).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    raise RuntimeError(f"{label} executable not found: {value!r}. See va/Transmitter/README.md for setup.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vera", default=os.environ.get("VERA", "vera"), help="VerA executable path")
    parser.add_argument("--zig", default=os.environ.get("VERA_ZIG"), help="Zig executable path; optional for wrapped VerA")
    parser.add_argument("--mode", choices=("lint", "check", "test"), default="test")
    parser.add_argument("--output", type=Path, default=BLOCK/"build"/"va"/"tx-cml-ffe-results")
    args = parser.parse_args()
    if not __debug__:
        parser.error("Do not use python -O: assertions are part of the output checkers.")
    out = args.output.resolve()
    build, generated = out/"build", out/"generated"
    for directory in (out, build, generated):
        directory.mkdir(parents=True, exist_ok=True)
    results = []
    sources = [MODELS/"mux2_cml_hr.va", MODELS/"ffe_tapgen_hr.va", FIXTURES/"tx_cml_ffe_path.va"]
    neighbors = [MODELS.parent/"Clocking"/"cml_dff_x4.va", MODELS/"predriver_cml.va", MODELS/"pam4_driver.va"]
    status, version, zig = 0, None, None

    def passed(name, detail):
        results.append({"name": name, "status": "PASS", "detail": detail})
        print(f"PASS {name}: {detail}", flush=True)

    try:
        vera = executable(args.vera, "VerA")
        zig = executable(args.zig, "Zig") if args.zig else None
        environment = os.environ.copy()
        environment["ZIG_GLOBAL_CACHE_DIR"] = str(out/"cache"/"zig-global")
        environment["ZIG_LOCAL_CACHE_DIR"] = str(out/"cache"/"zig-local")

        def invoke(name, flags, expected_exit=0):
            command = [vera]
            if zig:
                command += ["--zig", zig]
            command += ["--color=never", "-I", str(MODELS), "-I", str(FIXTURES), *flags]
            proc = subprocess.run(command, cwd=out, env=environment, timeout=240,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, encoding="utf-8", errors="replace")
            output = proc.stdout+proc.stderr
            (out/(name+".log")).write_text(output, encoding="utf-8")
            if proc.returncode != expected_exit:
                raise RuntimeError(f"{name}: exit {proc.returncode}, expected {expected_exit}. "
                                   f"See {out/(name+'.log')}\n{output[-2500:]}")
            return output

        version = invoke("version", ["--version"]).strip()
        print(version, flush=True)
        actions = ("lint",) if args.mode == "lint" else ("lint", "check")
        for source in sources:
            for action in actions:
                invoke(source.stem+"-"+action, ["--"+action, str(source),
                       "--work-dir", str(build/(source.stem+"-"+action))])
            passed(source.stem+"-"+args.mode, " and ".join(actions)+" passed")

        if args.mode != "lint":
            check_includes(invoke, passed, out, build, generated, MODELS)
        if args.mode == "test":
            mux = invoke("mux-dc", ["--run", str(FIXTURES/"mux_dc.va"),
                                    "--work-dir", str(build/"mux-dc")])
            rows = [tuple(map(float, m)) for m in re.findall(
                r"^MUX de=(\S+) odd=(\S+) clk=(\S+) vp=(\S+) vn=(\S+)", mux, re.M)]
            assert len(rows) == 8, ("mux DC combinations", len(rows))
            observed = set()
            for even, odd, clock, vp, vn in rows:
                observed.add((even > 0, odd > 0, clock > 0))
                wanted = 0.3 if (even if clock > 0 else odd) > 0 else -0.3
                assert abs(vp-vn-wanted) < 1e-5, (even, odd, clock, vp, vn)
                assert abs((vp+vn)/2-0.55) < 1e-5
            assert observed == set(itertools.product((False, True), repeat=3))
            passed("mux-dc", "all eight input/clock combinations, polarity, swing and common-mode")
            check_mux_transient(invoke, passed, out, build, generated, MODELS)
            check_ffe(invoke, passed, out, build, generated, MODELS)
            check_stream(invoke, passed, out, build, generated, MODELS)
            check_supply_reset(invoke, passed, out, build, generated, MODELS)
            check_neighbors(invoke, passed, out, build, generated, MODELS)
    except Exception as error:
        status = 1
        results.append({"name": "run", "status": "FAIL", "detail": str(error)})
        print("FAIL "+str(error), file=sys.stderr, flush=True)
    finally:
        report = {
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "PASS" if status == 0 else "FAIL", "mode": args.mode,
            "vera_version": version, "checks": results,
            "scope": "Transmitter behavioral models with VerA fixed-grid simulation. "
                     "No PLL/clock-generator, OpenVAF/OSDI, transistor or full-link signoff.",
            "model_sha256": {p.relative_to(BLOCK).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sources if p.is_file()},
            "neighbor_sha256": {p.relative_to(BLOCK).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in neighbors if p.is_file()},
        }
        report_path = out/("report.json" if args.mode == "test" else args.mode+"-report.json")
        report_path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        print("Report: "+str(report_path), flush=True)
    return status


if __name__ == "__main__":
    sys.exit(main())
