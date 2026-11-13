# HH1neuron

This README is intended to accompany the original `HH1neuron.cpp` and its
annotated copy, `HH1neuron_commented.cpp`.

## Overview

`HH1neuron.cpp` is a single-neuron numerical simulation, apparently intended
as one component of a larger model of two neurons and one interneuron. As
described by Oana Cucu, that system was intended to investigate vagal
stimulation and the maintenance of respiratory arrhythmia in the heart.

This source file alone implements only one neuron: it has a membrane-voltage
state and three channel-gating states, with leak, sodium, and potassium
currents. It does not show the other neurons, their connections, vagus-nerve
stimulation, or a heart model. The intended system-level role above is based
on the author's current recollection and should be checked against the
original project materials.

## Model and numerical method

The code integrates four state variables using the classical fourth-order
Runge-Kutta (RK4) method. The voltage equation includes leak, sodium, and
potassium currents; the other three equations describe voltage-dependent
channel gates conventionally labelled `m`, `h`, and `n`.

Although the supervisor has described the project as using a
FitzHugh-Nagumo model, the equations in this particular file look more like a
conductance-based Hodgkin-Huxley-style model: they explicitly include three
gating variables and separate sodium and potassium currents. The classical
FitzHugh-Nagumo model is usually a reduced two-variable voltage/recovery
system. The supervisor may be referring to a larger model, a reduction, or a
different source file; confirm the intended model name and citation before
treating this distinction as settled.

The source also computes an interpolated delayed voltage, but that value is
not used by the equations or output here. It calculates voltage-dependent
gate time constants in `derivs`, but the gate equations divide by the global
`taui` values assigned once at the initial voltage. These are observations
about the code as received, not changes to its behavior.

## Parameters in the source

The source does not state the units. Names and interpretations below are
tentative, based on their use in the equations.

| Symbol | Value | Apparent meaning |
| --- | ---: | --- |
| `gl`, `vl` | 0.2955, -54.11 | Leak conductance and leak reversal potential |
| `gna`, `vna` | 118.79, 49.99 | Sodium conductance and reversal potential |
| `gk`, `vk` | 20.35, -76.97 | Potassium conductance and reversal potential |
| `C` | 1.0 | Membrane capacitance factor |
| `vm`, `vh`, `vn` | -40.08, -59.91, -54.91 | Voltage midpoints for the `m`, `h`, and `n` gate curves; not the membrane-voltage state |
| `dvm`, `dvh`, `dvn` | 14.9, -14.88, 29.28 | Voltage scale/slope parameters for those curves |
| `tm0`, `tm1` | 0.1009, 0.3982 | Coefficients in the `m` gate time-constant expression |
| `th0`, `th1` | 1.004, 7.047 | Coefficients in the `h` gate time-constant expression |
| `tn0`, `tn1` | 1.012, 4.99 | Coefficients in the `n` gate time-constant expression |
| `I` | 10.0 | Applied-current amplitude |
| `tau` | 500.0 | Delay used in the delayed-voltage calculation; that calculation currently does not affect the simulation |

The membrane voltage is `y[0]`; the other state values `y[1]`, `y[2]`, and
`y[3]` are the three gates. Initial values for all four states are zero.

## Running and output

The program uses `n = 10000`, a positive-time window of `1000`, and a time
step of `0.1`. It advances from time `-1000` to `1000`; the applied current
`I` is used when `0 < t < 1000`. The program writes three tab-separated
columns to `HH1neuron.dat`: time, applied current, and membrane voltage.

The received source uses legacy C style and does not check whether the output
file opened successfully. No build instructions or external dependencies
were provided with the file.

## Provenance and attribution

Created by Oana Cucu in 2015 as a project student in the Wellcome Trust Neural
Dynamics CDT programme, at the University of Bristol, under the supervision
of Prof. Alain Nogaret, Department of Physics, University of Bath. The file
was later sent to the author by the supervisor.

Copyright (c) 2015 Oana Cucu, Department of Physiology and Pharmacology,
University of Bristol. Supervised by Prof. Alain Nogaret, Department of
Physics, University of Bath.

No publication, report, or exact project title has yet been identified. Add
the relevant references and confirm the project title when available. This
repository is distributed under the MIT License; see `LICENSE`.
