# Single-neuron membrane model (2015 source)

This repository preserves a 2015 C/C++-style implementation of a single-neuron membrane model, alongside a set of clearly separated retrospective code investigations carried out in 2026.

## Historical context

The starting point was a small C++ implementation supplied by Prof. Alain Nogaret, based on a FitzHugh–Nagumo model, as a learning and development exercise during Oana Cucu's project in the Wellcome Trust Neural Dynamics programme at the University of Bristol. The task was to develop a three-channel Hodgkin–Huxley-type neuron model within that existing scaffold. The original code was developed with supervisory input; a small indexing/order issue in the derivative calculations was also corrected during that work.

The repository contains a single-neuron simulation. It does not implement a multi-neuron network, a vagus-nerve model, a heartbeat model, or a complete respiratory–cardiac system. The wider physiological motivation and the precise relationship between this source file and the original FitzHugh–Nagumo starting implementation have not yet been verified against the 2015 project records. The retrospective notes therefore distinguish the received source and its observable behaviour from recollections about the wider project.

## What the original program implements

The main source is [`HH1neuron.cpp`](HH1neuron.cpp), with an annotated copy in [`HH1neuron_commented.cpp`](HH1neuron_commented.cpp).

It integrates four state variables using classical fourth-order Runge–Kutta (RK4):

- `y[0]`: membrane voltage;
- `y[1]`: sodium activation gate (`m`);
- `y[2]`: sodium inactivation gate (`h`);
- `y[3]`: potassium activation gate (`n`).

The voltage equation includes leak, sodium and potassium conductance currents, together with an applied external current. The three gates follow voltage-dependent steady-state curves and time-constant expressions. The source calculates the gate time constants once, at the initial voltage, and uses those fixed values in the gate equations. This fixed-time-constant behaviour is retained as the intended reference implementation.

The initial values of all four state variables are zero. The program applies a current pulse with amplitude `I = 10` for `0 < t < 1000`, over a simulation window from `-1000` to `1000`. In the original source, `n = 10000`, giving a time step of `0.1`. The output file contains time, applied current and membrane voltage.

The code also calculates a quantity named `yy0old` using a delayed-voltage interpolation. The value is not used by the differential equations or by the RK4 update. Experiment 06 investigates this calculation separately and finds that, in the tested implementation, it is initially zero and subsequently follows the current membrane voltage rather than providing a delayed copy.

## Units and parameter conventions

The model uses the classical membrane-model units confirmed by the author:

| Quantity | Unit |
|---|---|
| Membrane voltage and reversal potentials | mV |
| Time, integration step and time constants | ms |
| Membrane capacitance | µF/cm² |
| Membrane current density | mA/cm² |
| Injected/applied current | nA |
| Conductance density | mS/cm² |
| Gating variables (`m`, `h`, `n`) | Dimensionless |
| Rate constants (α, β; denoted `a`, `b` in the model notation) | ms⁻¹ |

The parameter values in the source are therefore interpreted using these units. In particular, conductances are conductance densities, while the applied stimulus `I` is an injected current, not a current density. The source's `a[,]` array stores the steady-state gate values; it should not be confused with a generic rate-constant symbol.

## Reproducing the original simulation

The original source is preserved without changing its model equations. It can be compiled as legacy C using a C compiler:

```sh
gcc -x c -std=gnu89 -O0 HH1neuron.cpp -lm -o HH1neuron
./HH1neuron
```

The program writes `HH1neuron.dat` in the current working directory. See [`simulation-output/`](simulation-output/README.md) for the reproduced output and plotting instructions.

## Retrospective experiments (2026)

The experiments below are later investigations of the received source. They are not represented as part of the 2015 project, and the original source remains available unchanged.

| Experiment | Question | Main result |
|---|---|---|
| [01 — Baseline reproduction](experiments/01_baseline_reproduction/README.md) | Does the original source run and reproduce a baseline trace? | The original program runs and produces a finite single-spike response for the supplied stimulus and parameters. |
| [02 — Time-constant comparison](experiments/02_time_constant_comparison/README.md) | What changes if the gate time constants are recalculated continuously from voltage instead of held fixed? | The alternative produces substantially different firing behaviour. Fixed time constants remain the intended model; the alternative is a sensitivity test, not a correction. |
| [03 — Integration-step comparison](experiments/03_integration_step_comparison/README.md) | How sensitive is the fixed-time-constant solution to the integration step? | A step of 0.02 gives a useful accuracy/cost compromise; 0.01 gives very similar peak measures. |
| [04 — Initial conditions](experiments/04_initial_conditions/README.md) | What is the effect of starting the gates at zero versus their steady-state values? | The initial transients differ, but after the long pre-stimulus interval the stimulus-evoked responses converge at the reported precision. The original zero initialisation is retained. |
| [05 — Stimulus-boundary handling](experiments/05_stimulus_boundary/README.md) | Is the first RK4 derivative refreshed after the applied current changes? | The original loop can carry a stale first derivative across stimulus transitions. A minimal refresh makes the RK4 stages consistent with the current stimulus value. |
| [06 — Delayed-voltage calculation](experiments/06_delayed_vagus_output/README.md) | Does the legacy interpolation calculate a delayed membrane-voltage output? | In the tested C implementation, the candidate output is initially zero and then matches the current membrane voltage; it is not a functioning delay line. |

Each experiment has its own README, source variants and, where relevant, reproducibility scripts and numerical summaries. Results from exploratory reimplementations are explicitly identified as such and are not presented as direct C execution results.

## Scope and limitations

- This repository documents one single-neuron implementation, not a complete physiological system.
- The source is preserved as received for historical reference; retrospective experimental variants are kept separately.
- The model's physiological interpretation, original publication/reference and exact 2015 project title have not yet been independently confirmed.
- The retrospective experiments test implementation choices and numerical behaviour. They do not establish physiological validity or parameter identifiability.
- Output values are written after each integration step but labelled with the step-start time in the original program; this historical convention is retained in the comparisons unless a README says otherwise.
- The delayed-voltage calculation is retained as a source-level remnant, even though it does not feed back into the neuron equations.

## Provenance and attribution

The 2015 project work was carried out by Oana Cucu as a project student in the Wellcome Trust Neural Dynamics programme at the University of Bristol, under the supervision of Prof. Alain Nogaret, Department of Physics, University of Bath. The initial code scaffold and scientific supervision were provided by Prof. Nogaret; the three-channel neuron implementation was developed by Oana with supervisory input.

Copyright (c) 2015 Oana Cucu, Department of Physiology and Pharmacology, University of Bristol. Supervised by Prof. Alain Nogaret, Department of Physics, University of Bath.

No publication or exact project title has yet been identified. Add the relevant reference if it becomes available. This repository is distributed under the MIT License; see [`LICENSE`](LICENSE).
