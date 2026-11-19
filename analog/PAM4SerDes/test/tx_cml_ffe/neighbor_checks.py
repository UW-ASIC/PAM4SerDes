"""Connect actual team retimers/predrivers/driver to both CML/FFE paths.

The current pam4_driver accepts one MSB/LSB pair, so only MAIN drives it.
PRE/POST are checked through real predrivers, not falsely treated as summed FFE.
"""
import csv
import json
import random

from half_rate_checks import UI, STEPS, drive_pair, print_voltages, read_rows, write_fixture


def check_neighbors(invoke, passed, out, build, generated, models):
    rng = random.Random(20261119)
    # Includes all four PAM4 codes, long runs, alternating bits and random bits.
    patterns = {
        "m": [0, 0, 1, 1]*4 + [0]*8 + [1]*8 + [0, 1]*8 + [rng.randrange(2) for _ in range(16)],
        "l": [0, 1, 0, 1]*4 + [1]*8 + [0]*8 + [1, 0]*8 + [rng.randrange(2) for _ in range(16)],
    }
    symbols = len(patterns["m"])
    count = (symbols+10)*STEPS+1
    times = [i*UI/STEPS for i in range(count)]
    waves, inputs = {}, []
    for prefix, bits in patterns.items():
        for lane in range(4):
            values = []
            for i in range(count):
                frame = (i-round(3.5*STEPS))//(4*STEPS)
                n = 4*frame+lane
                bit = bits[n] if 0 <= n < symbols else 0
                # Stable at the retimer's rising edge (4+4k UI), then inverted.
                # Correct downstream data therefore requires actual DFF storage.
                poison = i >= round((4.25+4*frame)*STEPS)
                values.append(1-bit if poison else bit)
            pin = f"{prefix}{lane}"
            drive_pair(waves, pin, values)
            inputs += [pin+"_p", pin+"_n"]
    drive_pair(waves, "clk7", [i >= 4*STEPS and ((i-4*STEPS)//(2*STEPS)) % 2 == 0
                               for i in range(count)])
    drive_pair(waves, "clk14", [i >= STEPS and ((i-STEPS)//STEPS) % 2 == 0
                                for i in range(count)])
    waves["rst"] = [0.7 if i < 3.5*STEPS else 0 for i in range(count)]
    clocks = ["clk7_p", "clk7_n", "clk14_p", "clk14_n", "rst"]
    retimed = [f"q_{prefix}{lane}" for prefix in patterns for lane in range(4)]
    taps = [f"{prefix}_{tap}" for prefix in patterns for tap in ("pre", "main", "post")]
    buffered = ["b_"+tap for tap in taps]
    nodes = retimed+taps+buffered+["tx"]
    ports = inputs+clocks+[node+s for node in nodes for s in ("_p", "_n")]+["vdd", "vss"]
    body = ('`include "cml_dff_x4.va"\n`include "tx_cml_ffe_path.va"\n'
            '`include "predriver_cml.va"\n`include "pam4_driver.va"\n')
    body += "module neighbor_vectors("+", ".join(ports)+");\n"
    body += "inout "+", ".join(ports)+";\nelectrical "+", ".join(ports)+";\n"
    for prefix in patterns:
        args = ["clk7_p", "clk7_n"]
        args += [f"{prefix}{lane}{s}" for lane in range(4) for s in ("_p", "_n")]
        args += [f"q_{prefix}{lane}{s}" for lane in range(4) for s in ("_p", "_n")]
        body += f"cml_dff_x4 retimer_{prefix}("+", ".join(args)+");\n"
        args = [f"q_{prefix}{lane}{s}" for lane in range(4) for s in ("_p", "_n")]
        args += clocks+[f"{prefix}_{tap}{s}" for tap in ("pre", "main", "post") for s in ("_p", "_n")]
        args += ["vdd", "vss"]
        body += f"tx_cml_ffe_path path_{prefix}("+", ".join(args)+");\n"
    for tap in taps:
        body += f"predriver_cml buffer_{tap}({tap}_p, {tap}_n, b_{tap}_p, b_{tap}_n);\n"
    body += "pam4_driver driver(b_m_main_p, b_m_main_n, b_l_main_p, b_l_main_n, tx_p, tx_n);\n"
    body += "analog begin\n"+print_voltages("NEIGHBOR", nodes)+"\nend\nendmodule\n"
    fixture = generated/"neighbor_vectors.va"
    write_fixture(fixture, times, waves, {"vdd": 0.7, "vss": 0}, body)
    output = invoke("team-neighbors", ["--run", str(fixture), "-I", str(models.parent/"Clocking"),
                                      "--work-dir", str(build/"team-neighbors")])
    fields = ["time_s"]+[n+"_V" for n in nodes]+[n+"_cm_V" for n in nodes]
    _, sampled = read_rows(output, "NEIGHBOR", count, fields, out/"team-neighbors-waveforms.csv")
    columns = {node: 1+i for i, node in enumerate(nodes)}
    max_error = 0.0

    def check(row, node, voltage, cm, tolerance=0.001):
        nonlocal max_error
        index = columns[node]
        error = abs(row[index]-voltage)
        max_error = max(max_error, error)
        assert error < tolerance, (node, row[0], "differential", row[index], voltage)
        assert abs(row[index+len(nodes)]-cm) < tolerance, (node, row[0], "common-mode")

    retimer_checks = 0
    for frame in range(symbols//4):
        row = sampled[round((4.5+4*frame)*STEPS)]
        for prefix, bits in patterns.items():
            for lane in range(4):
                check(row, f"q_{prefix}{lane}", 0.2*(2*bits[4*frame+lane]-1), 0.6)
                retimer_checks += 1
    samples, pam4_codes = [], set()
    for n in range(symbols):
        row = sampled[(7+n)*STEPS+STEPS//2]
        for prefix, bits in patterns.items():
            for delay, tap in enumerate(("pre", "main", "post")):
                bit = bits[n-delay] if n >= delay else 0
                node = prefix+"_"+tap
                check(row, node, 0.3*(2*bit-1), 0.55)
                check(row, "b_"+node, 0.2*(2*bit-1), 1.2)
        # MAIN is one symbol behind PRE, independent of the implementation's state names.
        m = patterns["m"][n-1] if n else 0
        l = patterns["l"][n-1] if n else 0
        code = 2*(2*m-1)+(2*l-1)
        wanted = code*0.8/6
        check(row, "tx", wanted, 0.9, tolerance=2e-6)
        pam4_codes.add(code)
        samples.append({"symbol": n, "time_s": row[0], "main_m": m, "main_l": l,
                        "expected_pam4_V": wanted, "actual_pam4_V": row[columns["tx"]]})
    assert pam4_codes == {-3, -1, 1, 3}, ("missing PAM4 code", pam4_codes)
    with (out/"team-neighbors-samples.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    summary = {"symbols": symbols, "retimer_checks": retimer_checks,
               "serialized_tap_checks": symbols*6, "predriver_checks": symbols*6,
               "pam4_checks": symbols, "pam4_codes": sorted(pam4_codes),
               "max_voltage_error_V": max_error, "status": "PASS",
               "scope": "Actual cml_dff_x4 + two CML/FFE paths + six predriver_cml + MAIN-only pam4_driver. "
                        "Ideal clocks; driver does not yet accept PRE/POST or implement FFE summation."}
    (out/"team-neighbors-summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    passed("team-neighbors", f"{retimer_checks} retimed bits, {symbols*6} taps, {symbols*6} buffered taps, "
           f"{symbols} MAIN-only PAM4 symbols; all four levels")
