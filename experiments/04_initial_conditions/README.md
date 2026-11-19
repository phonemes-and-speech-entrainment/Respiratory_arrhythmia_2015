# Experiment 04 — Initial gating-variable conditions

**Classification:** New retrospective experiment (2026); not part of the documented 2015 work.  
**Status:** Three C implementations compiled and run at `dt = 0.02`.

## Aim

Investigate whether the initial values assigned to the three gating variables affect the simulated response. The original implementation sets membrane voltage and all three gates to zero. This experiment retains that original case and compares it with two alternative gate initialisations.

The membrane voltage is held at its original initial value of zero in all cases. Only the three gating-variable initial values are changed.

## Initial conditions tested

The gate steady-state values are calculated from the same hyperbolic-tangent activation functions used in the model, evaluated at the initial membrane voltage `V = 0`:

| Case | Initial m | Initial h | Initial n |
|---|---:|---:|---:|
| Original: zero gates | 0 | 0 | 0 |
| Half of steady-state values | 0.49770635 | 0.00015911 | 0.48851898 |
| Steady-state values at V = 0 | 0.99541270 | 0.00031823 | 0.97703796 |

The half-steady-state case is an exploratory interpolation between the original zero initialisation and the calculated steady-state values. It is not intended as a physiologically privileged state.

## Method

All runs use the original fixed time constants, original model parameters, original stimulus and classical RK4 integration. The integration step is `0.02`, selected following Experiment 03. The initial membrane voltage remains zero.

The simulation starts at labelled time `−1000`, whereas the stimulus is only applied when `tt > 0`. Consequently, there is a 1000-time-unit pre-stimulus interval during which the model evolves from the selected initial gate values before the external current is applied.

The experimental C source is [`HH1neuron_initial_conditions.cpp`](HH1neuron_initial_conditions.cpp). It accepts the three initial gate values as command-line arguments. It is derived from the fixed-time-constant experimental source and changes only the gate initialisation and the interface for supplying those values.

Compile and run an individual case from this folder:

```sh
gcc -x c -std=gnu89 -O0 HH1neuron_initial_conditions.cpp -lm -o HH1neuron
./HH1neuron 0 0 0
./HH1neuron 0.497706349914 0.000159114766286 0.488518979696
./HH1neuron 0.995412699829 0.000318229533 0.977037959391
```

Each run writes `HH1neuron.dat` in the current directory. Run the cases in separate directories so that the output files are not overwritten.

For convenience, [`run_experiment.py`](run_experiment.py) automates compilation, execution, summary generation and plotting. It requires GCC; Matplotlib is optional and is only required to generate the comparison plot.

## Results

| Case | Minimum V before stimulus | Peak V during stimulus | Peak time | Final V | Difference from baseline after stimulus |
|---|---:|---:|---:|---:|---:|
| Zero gates | −69.079939 | 40.921776 | 2.18 | −58.629568 | 0 |
| Half steady-state | −69.981689 | 40.921776 | 2.18 | −58.629568 | 0 |
| Steady-state | −75.997011 | 40.921776 | 2.18 | −58.629568 | 0 |

The complete machine-readable summary is in [`summary.csv`](summary.csv).

The alternative initial conditions produce visibly different voltage transients immediately after the simulation begins at `t = −1000`. The largest differences occur during this initial settling period. However, the trajectories converge before the stimulus begins. In the six-decimal output data, all three voltage traces are identical from the stimulus period onwards. Each case produces the same single upward zero crossing and the same action-potential-like peak.

## Interpretation

This experiment shows that the initial gate values do affect the early transient, as expected for a system of differential equations whose state includes the gating variables. However, for the particular 1000-time-unit pre-stimulus interval used in this program, the differences have decayed before the external stimulus is applied.

Therefore, the original zero initialisation does not appear to affect the stimulus-evoked response under these settings. This does not establish that initial conditions are unimportant in general: a shorter pre-stimulus interval, different parameters, or a different initial membrane voltage could produce a different result.

The experiment supports retaining the original zero initial conditions as a deliberate modelling choice. It does not justify replacing them with steady-state gate values.

## Plot

The plotting routine in `run_experiment.py` creates a two-panel comparison:

1. The early pre-stimulus transient, where the three initialisations produce different voltage trajectories.
2. The stimulus response, where the three traces overlap.

The axes are labelled with units to be confirmed, pending the separate check of the original model's physical units.

## Conclusion

The three initialisation choices produce different early transients, but the differences decay during the long pre-stimulus interval. At the start of stimulation, and throughout the recorded stimulus response, the outputs are identical to the precision stored in the data file. The original zero gate initialisation is therefore retained. This is a retrospective sensitivity test, not a correction to the original 2015 implementation.
