"""Exercise the actual mux with streams, a resistive load, and held clocks."""
import csv
import json
import random

from half_rate_checks import UI, STEPS, CM, drive_pair, print_voltages, read_rows, write_fixture


def check_mux_transient(invoke, passed, out, build, generated, root):
    rng = random.Random(20261111)
    bits = ([1, 0, 1, 1, 0, 0, 0, 1] + [0]*8 + [1]*8
            + [0, 1]*8 + [rng.randrange(2) for _ in range(24)])
    count = 70*STEPS + 1
    times = [i*UI/STEPS for i in range(count)]
    waves = {}
    source_ports = []
    input_diff = {}

    for prefix, width in (("fast", 1), ("slow", 2)):
        # width is the output bit duration in 28 Gb/s UI units.
        # Change each lane only while that lane is unselected.
        for suffix, parity, start in (("e", 0, 4-width), ("o", 1, 4)):
            values = []
            for i in range(count):
                pair = (i-start*STEPS)//(2*width*STEPS)
                n = 2*pair+parity
                values.append(bits[n] if 0 <= n < len(bits) else 0)
            pin = prefix+suffix
            drive_pair(waves, pin, values)
            source_ports += [pin+"_p", pin+"_n"]
            input_diff[pin] = [0.3*(2*b-1) for b in values]
        clock = [i >= 4*STEPS and ((i-4*STEPS)//(width*STEPS)) % 2 == 0
                 for i in range(count)]
        drive_pair(waves, prefix+"clk", clock)
        source_ports += [prefix+"clk_p", prefix+"clk_n"]
        input_diff[prefix+"clk"] = [0.3 if b else -0.3 for b in clock]

    # Hold clock positive for 12 UI, then negative. Within each interval,
    # change selected data and unselected data independently. An edge-only
    # sampler would fail this test; a transparent mux must track its input.
    probe_e, probe_o, probe_clk = [], [], []
    for i in range(count):
        t = i/STEPS
        probe_e.append(int(2 <= t < 6 or 10 <= t < 16 or t >= 20))
        probe_o.append(int(4 <= t < 8 or 14 <= t < 18 or t >= 22))
        probe_clk.append(t < 12)
    for suffix, values in (("e", probe_e), ("o", probe_o), ("clk", probe_clk)):
        pin = "probe"+suffix
        drive_pair(waves, pin, values)
        source_ports += [pin+"_p", pin+"_n"]
        input_diff[pin] = [0.3*(2*b-1) for b in values]

    nodes = ["fastout", "slowout", "loaded", "probeout"]
    ports = source_ports + [n+s for n in nodes for s in ("_p", "_n")] + ["vdd", "vss"]
    body = '`include "mux2_cml_hr.va"\nmodule mux_transient_vectors(' + ", ".join(ports) + ");\n"
    body += "inout " + ", ".join(ports) + ";\nelectrical " + ", ".join(ports) + ";\n"
    for source, node in (("fast", "fastout"), ("slow", "slowout"),
                         ("fast", "loaded"), ("probe", "probeout")):
        pins = [source+p+s for p in ("e", "o", "clk") for s in ("_p", "_n")]
        pins += [node+"_p", node+"_n", "vdd", "vss"]
        body += "mux2_cml_hr dut_" + node + "(" + ", ".join(pins) + ");\n"
    body += "analog begin\nI(loaded_p,loaded_n) <+ V(loaded_p,loaded_n)/100.0;\n"
    body += print_voltages("MUXTRAN", nodes) + "\nend\nendmodule\n"
    fixture = generated/"mux_transient_vectors.va"
    write_fixture(fixture, times, waves, {"vdd": 0.7, "vss": 0}, body)
    output = invoke("mux-transient", ["--run", str(fixture), "-I", str(root),
                                     "--work-dir", str(build/"mux-transient")])
    fields = ["time_s"] + [n+"_V" for n in nodes] + [n+"_cm_V" for n in nodes]
    rows, sampled = read_rows(output, "MUXTRAN", count, fields, out/"mux-transient-waveforms.csv")
    with (out/"mux-transient-inputs.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["time_s", *input_diff])
        writer.writerows([times[i], *(v[i] for v in input_diff.values())] for i in range(count))

    tolerance = 0.001  # 1 mV settled differential/common-mode accuracy
    samples = []
    hold_checks = 0

    def record(label, node, index, bit, amplitude, symbol):
        row = sampled[index]
        wanted = amplitude*(2*bit-1)
        actual, common = row[1+node], row[5+node]
        samples.append({"case": label, "symbol": symbol, "time_s": row[0],
                        "expected_bit": bit, "actual_bit": int(actual > 0),
                        "expected_V": wanted, "actual_V": actual,
                        "error_V": abs(actual-wanted), "common_mode_V": common,
                        "pass": abs(actual-wanted) < tolerance and abs(common-CM) < tolerance})

    for label, node, width, amplitude, symbols in (
            ("14GHz_interleave", 0, 1, 0.3, 64),
            ("7GHz_interleave", 1, 2, 0.3, 32),
            ("100ohm_differential_load", 2, 1, 0.06, 64)):
        # Independent oracle: the output must reproduce the original serial
        # bit list; no software implementation of tanh/absdelay is compared.
        for n in range(symbols):
            start = (4+n*width)*STEPS
            record(label, node, start+width*STEPS//2, bits[n], amplitude, n)
            for offset in range(width*STEPS//2, 7*width*STEPS//8+1):
                row = sampled[start+offset]
                assert abs(row[1+node]-amplitude*(2*bits[n]-1)) < tolerance, (label, n, offset, row)
                hold_checks += 1

    # Mid-interval samples are well after each data change and propagation.
    # Expected results are explicitly listed to keep the checker independent.
    probe_expected = [0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1]
    for n, bit in enumerate(probe_expected):
        record("held_clock_transparency", 3, (1+2*n)*STEPS, bit, 0.3, n)

    with (out/"mux-transient-samples.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    summary = {"status": "PASS" if all(s["pass"] for s in samples) else "FAIL",
               "voltage_tolerance_V": tolerance, "settled_output_checks": len(samples),
               "additional_hold_checks": hold_checks, "evaluated_time_points": len(rows),
               "max_voltage_error_V": max(s["error_V"] for s in samples),
               "input_bits": "".join(map(str, bits)),
               "failed_samples": [s for s in samples if not s["pass"]]}
    (out/"mux-transient-summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    assert summary["status"] == "PASS", summary["failed_samples"][:4]
    passed("mux-transient", f"{len(samples)} outputs: 7/14 GHz interleaving, held-clock transparency, 100-ohm load; {hold_checks} settled hold checks")
