"""Checks for header integration and configurable reset/supply behavior."""
from half_rate_checks import UI, STEPS, print_voltages, read_rows, write_fixture


def check_includes(invoke, passed, out, build, generated, root):
    # Mimic a top level that includes individual cells, then a wrapper which
    # includes them again. Each module must still be declared exactly once.
    path = generated / "duplicate_includes.va"
    path.write_text('`include "mux2_cml_hr.va"\n'
                    '`include "ffe_tapgen_hr.va"\n'
                    '`include "tx_cml_ffe_path.va"\n'
                    '`include "tx_cml_ffe_path.va"\n', encoding="ascii")
    invoke("include-guards", ["--check", str(path), "-I", str(root),
                              "--work-dir", str(build/"include-guards")])
    passed("include-guards", "cells and test wrapper can be included repeatedly without duplicate modules")


def check_supply_reset(invoke, passed, out, build, generated, root):
    count = 22*STEPS+1
    times = [i*UI/STEPS for i in range(count)]
    taps = ["pre_e", "pre_o", "main_e", "main_o", "post_e", "post_o"]
    nodes = [kind+"_"+tap for kind in ("auto", "fixed") for tap in taps]
    ports = ["de_p", "de_n", "do_p", "do_n", "clk_p", "clk_n", "rst"]
    ports += [n+s for n in nodes for s in ("_p", "_n")] + ["vdd", "vss"]
    body = '`include "ffe_tapgen_hr.va"\nmodule supply_reset_vectors(' + ", ".join(ports) + ");\n"
    body += "inout " + ", ".join(ports) + ";\nelectrical " + ", ".join(ports) + ";\n"
    for kind in ("auto", "fixed"):
        pins = ports[:7] + [kind+"_"+tap+s for tap in taps for s in ("_p", "_n")] + ["vdd", "vss"]
        override = " #(.vth_rst(0.35))" if kind == "fixed" else ""
        body += "ffe_tapgen_hr" + override + " dut_"+kind+"("+", ".join(pins)+");\n"
    body += "analog begin\n"+print_voltages("SUPPLY", nodes)+"\nend\nendmodule\n"

    for supply, ground in ((1.0, 0.0), (1.8, 0.2)):
        name = "supply-reset-"+str(supply).replace(".", "p")
        high, low = ground+supply, ground+supply-0.3
        clock = [2*STEPS <= i < 18*STEPS and ((i-2*STEPS)//STEPS) % 2 == 0 for i in range(count)]
        reset = []
        for i in range(count):
            t = i/STEPS
            # Keep release clear of clock crossings: releasing at 12 UI
            # would race the rising clock within the interpolated input step.
            asserted = t < 1 or 8.25 <= t < 11.75 or t >= 19.25
            # 40% supply is below the automatic 50% threshold, but above
            # the explicit fixed 0.35 V threshold for both tested supplies.
            reset.append(ground+supply*(0.8 if asserted else 0.4))
        waves = {"de_p": [high]*count, "de_n": [low]*count,
                 "do_p": [low]*count, "do_n": [high]*count,
                 "clk_p": [high if b else low for b in clock],
                 "clk_n": [low if b else high for b in clock], "rst": reset}
        fixture = generated/(name+".va")
        write_fixture(fixture, times, waves, {"vdd": high, "vss": ground}, body)
        output = invoke(name, ["--run", str(fixture), "-I", str(root),
                               "--work-dir", str(build/name)])
        fields = ["time_s"]+[n+"_V" for n in nodes]+[n+"_cm_V" for n in nodes]
        _, sampled = read_rows(output, "SUPPLY", count, fields, out/(name+".csv"))
        checks = 0
        for t in (4.5, 6.5, 10.5, 16.5, 18.5, 19.5, 20.5):
            # At 4.5 UI the output banks still describe the FIRST captured
            # pair: POST has reset history. By 6.5 UI the history is filled.
            if t == 4.5:
                expected_auto = [1, 0, 0, 1, 0, 0]
            elif t in (6.5, 16.5, 18.5):
                expected_auto = [1, 0, 0, 1, 1, 0]
            else:
                expected_auto = [0]*6
            expected = expected_auto+[0]*6  # fixed-threshold cell stays reset
            row = sampled[round(t*STEPS)]
            for label, got, bit in zip(nodes, row[1:13], expected):
                assert abs(got-0.3*(2*bit-1)) < 0.001, (name, t, label, got, bit)
                checks += 1
            assert all(abs(v-(supply-0.15)) < 0.001 for v in row[13:]), (name, t, "common mode")
        passed(name, f"{checks} tap values; automatic/fixed reset thresholds, stopped-clock reset, VSS={ground} V")
