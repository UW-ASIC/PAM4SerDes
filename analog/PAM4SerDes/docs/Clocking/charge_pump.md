# charge_pump

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf, ideal (the circuit was scrapped from the design) |
| Model | [`va/Clocking/charge_pump.va`](../../va/Clocking/charge_pump.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_cp`); [rx_cdr](rx_cdr.md), once (`u_cp`) |
| Section | [Clocking](README.md) |

## Architecture

`charge_pump` turns the two pulse outputs of the phase-frequency detector into a current into the loop filter: current flows into the filter while `up` is high and out of it while `dn` is high.

The model's header is direct about what it is: an **ideal** charge pump. The charge-pump circuit was scrapped from the design, and this block only does the conversion, perfectly:

```
I(into out) = icp * en * (u - d)
```

where `u`, `d` and `en` are the pin voltages divided by the supply and clamped to 0..1. With rail-to-rail logic inputs that is exactly `+icp`, `-icp` or 0.

### Where it sits

- In [tx_pll](tx_pll.md): fed by [pfd](pfd.md), output on `vctl`, enable tied to `vdd` (always on), `icp` = 100 uA.
- In [rx_cdr](rx_cdr.md): fed by [pfd](pfd.md), output on the shared `vctl` node, `icp` = 400 uA. Its enable is `!(lock | force_lock)`, made by the `nor2` cell on the [glue](glue.md) page, so the pump works only during frequency acquisition.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `up`, `dn` | input | Pulses from the PFD |
| `en` | input | Enable. Low switches the pump off; tie to `vdd` for always on |
| `out` | output | Current into the loop filter node |
| `vdd`, `vss` | inout | Supply and ground; the inputs are read as a fraction of the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `icp` | 100 uA | Pump current. `rx_cdr` sets 400 uA |

### What the model leaves out

The header lists it: no threshold, no delay, no mismatch between the up and down currents, no leakage and no output compliance limit. The output is a perfect current source at any `vctl`.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

Before starting: the model's header says the charge-pump circuit was scrapped from the design and that this block is ideal. Ask the Clocking lead what is meant to provide this function in the real circuit, and record the answer here.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Pump current 100 uA in the transmitter PLL (`tx_pll.va`, parameter `icp`)
- Pump current 400 uA in the receiver's frequency loop (`rx_cdr.va`, parameter `icp`)
- An enable input: the receiver switches the pump off after lock (`charge_pump.va`, header)

To be added by the owner:

- (add requirements here)

### Candidate topologies

One row per circuit you seriously considered. Two or three good candidates are enough.

| Candidate | Source / reference | Pros | Cons |
|---|---|---|---|
| | | | |

### Chosen topology

Which candidate you chose and the reasons, measured against the requirements above. Say what you gave up by not choosing the others.

### Schematic

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `charge_pump_<what>.svg` (or `.png`), and reference it from this page as `![charge_pump schematic](../img/charge_pump_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

*To be filled in by the owner during the sizing-research stage, once the topology is chosen.*

The goal of this section is to record the device sizes that meet the block's specs, how they were found, and the simulations that show it.

### Target specs

Copy the requirements from the Topology research section and turn each one into a number you can simulate.

| Spec | Target | Source |
|---|---|---|
| | | |

### Sizing method

How the sizes were found (hand calculation, gm/Id, sweep), with enough detail that someone else can repeat it.

### Devices

| Device | W/L or fingers | Bias point |
|---|---|---|
| | | |

### Simulation results

One row per spec. Name the testbench file so the result can be reproduced.

| Spec | Target | Result | Testbench | Conditions |
|---|---|---|---|---|
| | | | | |

### Corners checked

List the process, voltage and temperature corners you simulated, and say which one was worst.

### Open issues

- (specs not met yet, things left to check)
