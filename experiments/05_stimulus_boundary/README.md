# Experiment 05 — Stimulus-boundary derivative handling

**Classification:** New retrospective numerical investigation (2026); not part of the documented 2015 work.  
**Status:** Both committed C variants have been compiled and run with GCC (`-std=gnu89`, `dt = 0.02`, 100,001 rows per run).

## Aim

Investigate whether the first RK4 derivative (`k1`) is evaluated using the same stimulus current as the remaining RK4 stages when the applied current switches on and off.

## Finding from source inspection

At the beginning of each time-loop iteration, the program updates the global `Iexc` according to the current time. However, it does not immediately recalculate `dydx`. The first RK4 slope therefore remains the derivative calculated at the end of the previous iteration, using the previous iteration's stimulus value. The other three RK4 stages call `derivs()` after `Iexc` has been updated.

This mismatch occurs at the first integration step after the stimulus turns on and the first step after it turns off. Away from these transitions, the previous derivative and the newly required derivative use the same stimulus current.

## Variants

- **Original handling:** retains the existing order of operations.
- **Refreshed `k1`:** calls `derivs(tt, y, dydx)` immediately after updating `Iexc` and before calling `rk4()`. This ensures that all four RK4 stages use the stimulus value applicable to the current step.

The two variants are selected at compile time in [`HH1neuron_stimulus_boundary.cpp`](HH1neuron_stimulus_boundary.cpp):

```sh
gcc -x c -std=gnu89 -O0 HH1neuron_stimulus_boundary.cpp -lm -o original
gcc -x c -std=gnu89 -O0 -DREFRESH_K1 HH1neuron_stimulus_boundary.cpp -lm -o refreshed
```

Run each executable from a separate working directory, because both write `HH1neuron.dat`. The experimental source uses `n = 50,000`, corresponding to `dt = 0.02`, as selected in Experiment 03.

No model parameters, initial conditions, fixed time constants, stimulus amplitude, stimulus duration, delayed-voltage remnant or output format are otherwise changed.

## Results — provisional Python comparison

The following values were reproduced by compiling and running the two C variants. The minimum, maximum and final voltages and maximum absolute difference agree with the stored summary to the reported precision.

| Measure | Original handling | Refreshed `k1` |
|---|---:|---:|
| Minimum voltage | −72.782122 | −72.782327 |
| Maximum voltage | 40.921776 | 40.922774 |
| Final voltage | −58.629568 | −58.662234 |
| Upward zero crossing | 1.98 | 1.98 |
| Downward zero crossing (linearly interpolated) | 3.26 | 3.26 |

The largest absolute difference between the two voltage traces during the stimulus interval was approximately 1.771 mV in the C execution. The trajectories are identical before the stimulus begins, as expected. The initial stimulus-boundary difference appears immediately after the current changes from zero to 10; a second small difference is introduced when the current switches off.

The values are stored in [`summary.csv`](summary.csv).

## Interpretation

This is a numerical-consistency correction to the RK4 implementation, not a change to the Hodgkin–Huxley-type equations. At a discontinuity in the external input, the derivative supplied as `k1` should correspond to the same input value used for the other stages of that integration step. The refreshed version enforces that consistency.

The difference in the final voltage is small (approximately 0.033), and the main qualitative response remains the same: one stimulus-evoked spike rather than sustained repetitive firing. This suggests the boundary inconsistency has a measurable but limited effect for the current parameter set and step size.

The output-time convention is deliberately left unchanged: the program still writes the state after a step against the step's starting time. The delayed-voltage calculation is also retained as an unrelated historical remnant.

## Plot

[`plot_comparison.py`](plot_comparison.py) plots the two voltage traces and their pointwise difference from two generated `HH1neuron.dat` files. It uses Matplotlib. Run the C variants in separate folders named `original` and `refreshed`, then run:

```sh
python plot_comparison.py
```

The model units are confirmed: model time is in ms and membrane voltage is in mV. The script saves SVG and PNG output in this folder.

## Conclusion

The original loop has a stale-`k1` derivative at each stimulus transition. Refreshing the derivative immediately after changing `Iexc` is the minimal correction. The C comparison shows that this changes the exact trajectory slightly without changing the broad firing pattern. Direct C execution confirms the numerical comparison.
