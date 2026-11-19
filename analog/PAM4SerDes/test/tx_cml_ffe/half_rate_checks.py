"""Functional tests for the detailed half-rate TX partition (standard library).
Expected taps are addressed by serial-bit index, not by copying the DUT recurrence.
"""
import csv
import json
import random

UI = 1.0 / 28.0e9
STEPS = 64
AMP = 0.3
CM = 0.55
TOL = 0.01


def write_fixture(path, times, waves, biases, body):
    def numbers(values):
        return ", ".join(f"{value:.16g}" for value in values)
    lines = ["//! time " + numbers(times)]
    lines += [f"//! wave V({pin}) = " + numbers(values) for pin, values in waves.items()]
    lines += ["//! bias " + ", ".join(f"V({pin}) = {value}" for pin, value in biases.items()),
              "//! solve", "//! print none", "//! display record"]
    path.write_text("\n".join(lines) + "\n" + body, encoding="ascii")


def drive_pair(waves, name, bits):
    waves[name + "_p"] = [0.7 if b else 0.4 for b in bits]
    waves[name + "_n"] = [0.4 if b else 0.7 for b in bits]


def read_rows(output, tag, count, fields, csv_path):
    rows = [tuple(map(float, line.split()[1:])) for line in output.splitlines()
            if line.startswith(tag + " ")]
    assert rows and all(len(row) == len(fields) for row in rows), (tag, "malformed output")
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        writer.writerows(rows)
    sampled = {}
    for row in rows:
        index = round(row[0] * STEPS / UI)
        if abs(row[0] - index * UI / STEPS) < 1e-18:
            sampled[index] = row
    assert set(range(count)) <= sampled.keys(), (tag, "missing time points")
    return rows, sampled


def print_voltages(tag, nodes, extra=()):
    values = ["$abstime", *extra]
    values += [f"V({n}_p,{n}_n)" for n in nodes]
    values += [f"0.5*(V({n}_p,vss)+V({n}_n,vss))" for n in nodes]
    return '$strobe("' + tag + ' %.12e' + ' %g' * (len(values) - 1) + '",\n' + ",\n".join(values) + ");"


def check_ffe(invoke, passed, out, build, generated, root):
    pairs = 20
    rng = random.Random(601)
    bits = [1, 0, 0, 1, 1, 1, 0, 0] + [rng.randrange(2) for _ in range(2*pairs-8)]
    count = (2*pairs + 6) * STEPS + 1
    times = [i*UI/STEPS for i in range(count)]
    waves = {}
    even, odd, clock, reset = [], [], [], []
    for i in range(count):
        # Pair k is valid around rising t=(4+2k) UI. Deliberately invert
        # both inputs between captures, including every falling edge.
        k = (i - 4*STEPS + STEPS//4) // (2*STEPS)
        phase = i - (4 + 2*k)*STEPS
        poison = phase >= STEPS//4
        for lane, parity in ((even, 0), (odd, 1)):
            b = bits[2*k+parity] if 0 <= k < pairs else 0
            lane.append(1-b if poison else b)
        edge = (i - 4*STEPS)//STEPS
        clock.append(edge >= 0 and edge % 2 == 0)
        reset.append(0.7 if (i < STEPS or (20.75*STEPS <= i < 25.75*STEPS)) else 0.0)
    drive_pair(waves, "de", even)
    drive_pair(waves, "do", odd)
    drive_pair(waves, "clk", clock)
    waves["rst"] = reset
    nodes = ["pre_e", "pre_o", "main_e", "main_o", "post_e", "post_o"]
    ports = ["de_p", "de_n", "do_p", "do_n", "clk_p", "clk_n", "rst"]
    ports += [n+s for n in nodes for s in ("_p", "_n")] + ["vdd", "vss"]
    body = '`include "ffe_tapgen_hr.va"\nmodule hr_ffe_vectors(' + ", ".join(ports) + ");\n"
    body += "inout " + ", ".join(ports) + ";\nelectrical " + ", ".join(ports) + ";\n"
    body += "parameter integer initial_bit=0;\n"
    body += "ffe_tapgen_hr #(.init_bit(initial_bit)) dut(" + ", ".join(ports) + ");\n"
    body += "analog begin\n" + print_voltages("HRFFE", nodes) + "\nend\nendmodule\n"
    fixture = generated / "hr_ffe_vectors.va"
    write_fixture(fixture, times, waves, {"vdd": 0.7, "vss": 0}, body)
    for init in (0, 1):
        name = f"ffe-half-rate-init{init}"
        output = invoke(name, ["--run", str(fixture), "-I", str(root),
                              "--param", f"initial_bit={init}", "--work-dir", str(build/name)])
        fields = ["time_s"] + [n+"_V" for n in nodes] + [n+"_cm_V" for n in nodes]
        rows, sampled = read_rows(output, "HRFFE", count, fields, out/(name+".csv"))
        checks = 0
        for k in range(pairs):
            for phase in (0, 1):  # settled after rising, then falling
                i = (4+2*k+phase)*STEPS + STEPS//2
                in_reset = 20.75*STEPS <= i < 25.75*STEPS
                epoch = 11 if i >= 20.75*STEPS else 0
                # Rising: both banks describe previous pair.
                # Falling: EVEN moves to current pair, ODD still previous.
                ke = k-1 if phase == 0 else k
                ko = k-1

                def serial(n, bank_pair):
                    if in_reset or bank_pair < epoch or n < 2*epoch:
                        return init
                    return bits[n]
                expected = [serial(2*ke, ke), serial(2*ko+1, ko),
                            serial(2*ke-1, ke), serial(2*ko, ko),
                            serial(2*ke-2, ke), serial(2*ko-1, ko)]
                row = sampled[i]
                for label, got, b in zip(nodes, row[1:7], expected):
                    assert abs(got - AMP*(2*b-1)) < TOL, (name, k, phase, label, got, b)
                    checks += 1
                assert all(abs(v-CM) < TOL for v in row[7:]), (name, "common mode", k)
        # Check asynchronous clearing before the next clock edge.
        reset_row = sampled[20*STEPS + 15*STEPS//16]  # 20.9375 UI, before next edge
        assert all(abs(v-AMP*(2*init-1)) < TOL for v in reset_row[1:7]), (name, "reset")
        passed(name, f"{checks} half-rate tap values; phase hold, poisoned inputs, reset/refill, all six common-modes")


def check_stream(invoke, passed, out, build, generated, root):
    rng = random.Random(20261106)
    bits_m = ([1,0,1,1,0,0,0,1,0,1,0,0,1,1,1,0]
              + [0]*8 + [1]*8 + [0,1]*16 + [rng.randrange(2) for _ in range(64)])
    bits_l = ([0,1,0,0,1,1,1,0,1,0,1,1,0,0,0,1]
              + [1]*8 + [0]*8 + [1,0]*16 + [rng.randrange(2) for _ in range(64)])
    patterns = {"m": bits_m, "l": bits_l}
    symbols = len(bits_m)
    count = (symbols+9)*STEPS+1
    times = [i*UI/STEPS for i in range(count)]
    waves = {}
    source_ports = []
    for prefix, bits in patterns.items():
        for lane in range(4):
            values = []
            start = 3.5 if lane < 2 else 5.5
            for i in range(count):
                frame = (i-round(start*STEPS)) // (4*STEPS)
                n = 4*frame+lane
                values.append(bits[n] if 0 <= n < symbols else 0)
            pin = f"{prefix}{lane}"
            drive_pair(waves, pin, values)
            source_ports += [pin+"_p", pin+"_n"]
    # clk7 toggles on falling clk14 edges, as in the user's detailed image.
    drive_pair(waves, "clk7", [(i >= 4*STEPS and ((i-4*STEPS)//(2*STEPS)) % 2 == 0)
                               for i in range(count)])
    drive_pair(waves, "clk14", [(i >= STEPS and ((i-STEPS)//STEPS) % 2 == 0)
                                for i in range(count)])
    waves["rst"] = [0.7 if i < 3.5*STEPS else 0 for i in range(count)]
    clock_ports = ["clk7_p", "clk7_n", "clk14_p", "clk14_n", "rst"]
    nodes = [prefix+"_"+tap for prefix in patterns for tap in ("pre", "main", "post")]
    ports = source_ports + clock_ports + [n+s for n in nodes for s in ("_p","_n")] + ["vdd","vss"]
    body = '`include "tx_cml_ffe_path.va"\nmodule hr_tx_vectors(' + ", ".join(ports) + ");\n"
    body += "inout " + ", ".join(ports) + ";\nelectrical " + ", ".join(ports) + ";\n"
    for prefix in patterns:
        args = [f"{prefix}{lane}{s}" for lane in range(4) for s in ("_p", "_n")]
        args += clock_ports + [prefix+"_"+tap+s for tap in ("pre","main","post") for s in ("_p","_n")] + ["vdd","vss"]
        body += f"tx_cml_ffe_path path_{prefix}(" + ", ".join(args) + ");\n"
    body += "analog begin\n" + print_voltages("HRTX", nodes) + "\nend\nendmodule\n"
    fixture = generated / "hr_tx_vectors.va"
    write_fixture(fixture, times, waves, {"vdd":0.7, "vss":0}, body)
    output = invoke("tx-half-rate", ["--run", str(fixture), "-I", str(root),
                                    "--work-dir", str(build/"tx-half-rate")])
    fields = ["time_s"] + [n+"_V" for n in nodes] + [n+"_cm_V" for n in nodes]
    rows, sampled = read_rows(output, "HRTX", count, fields, out/"tx-half-rate-waveforms.csv")
    samples = []
    errors = []
    for n in range(symbols):
        # First pair captured at 5 UI; E0 selected at 7 UI, O0 at 8 UI.
        index = (7+n)*STEPS + STEPS//2
        row = sampled[index]
        for p, (prefix, bits) in enumerate(patterns.items()):
            expected = [bits[n-tap] if n >= tap else 0 for tap in range(3)]
            actual = row[1+3*p:4+3*p]
            err = [abs(v-AMP*(2*b-1)) for v,b in zip(actual, expected)]
            errors.extend(err)
            cmerr = [abs(v-CM) for v in row[7+3*p:10+3*p]]
            samples.append({"path":prefix, "symbol":n, "time_s":row[0],
                            "expected_pre":expected[0], "pre":int(actual[0]>0),
                            "expected_main":expected[1], "main":int(actual[1]>0),
                            "expected_post":expected[2], "post":int(actual[2]>0),
                            "pre_V":actual[0], "main_V":actual[1], "post_V":actual[2],
                            "pass":all(e<TOL for e in err+cmerr)})
            # Also check the remaining settled part of every selected half-cycle.
            # This detects a bank being overwritten while selected.
            for offset in range(STEPS//2, 7*STEPS//8+1):
                window = sampled[(7+n)*STEPS+offset][1+3*p:4+3*p]
                assert all(abs(v-AMP*(2*b-1))<TOL for v,b in zip(window,expected)), ("selected-bank hold",prefix,n,offset)
    with (out/"tx-half-rate-samples.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    summary = {"architecture":"4x7 -> 2x14 -> half-rate FFE 6x14 -> 3 final muxes -> 3x28 Gb/s, duplicated MSB/LSB",
               "symbols_per_path":symbols, "paths":2, "serialized_tap_checks":len(samples)*3,
               "evaluated_time_points":len(rows), "ui_s":UI, "voltage_tolerance_V":TOL,
               "max_voltage_error_V":max(errors), "input_m":"".join(map(str,bits_m)),
               "input_l":"".join(map(str,bits_l)), "failed_samples":[s for s in samples if not s["pass"]]}
    (out/"tx-half-rate-summary.json").write_text(json.dumps(summary,indent=2)+"\n", encoding="utf-8")
    preview = ["# Half-rate TX test results", "",
               "Two actual CML/FFE paths, one each for MSB and mapped LSB. Shared clk14.",
               "Per path: two first-stage muxes -> six-lane FFE -> three final muxes.", "",
               "| Path | Symbol | Expected PRE | PRE | MAIN | POST | Result |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
    for s in samples[:24]:
        preview.append(f"| {s['path'].upper()} | {s['symbol']} | {s['expected_pre']} | {s['pre']} | {s['main']} | {s['post']} | {'PASS' if s['pass'] else 'FAIL'} |")
    preview += ["", "Targets: +/-0.3 V differential (0.6 Vppd); 0.55 V common-mode at VDD=0.7 V.",
                "Each path checks 128 serialized symbols and 384 tap values. Standalone FFE tests cover reset/refill.",
                "Common pair-capture-to-final-mux selection latency is 2 UI; mux propagation/RC delay is additional.",
                "These functional fixed-grid results do not validate BER, jitter, PVT or physical timing margins."]
    (out/"TX_HALF_RATE_RESULTS.md").write_text("\n".join(preview)+"\n", encoding="utf-8")
    assert all(s["pass"] for s in samples), ("half-rate chain", summary["failed_samples"][:4])
    passed("half-rate-tx-msb-lsb", f"{symbols} symbols/path; {len(samples)*3} final tap values; 10 muxes + 2 FFEs; bank hold and common-mode")
