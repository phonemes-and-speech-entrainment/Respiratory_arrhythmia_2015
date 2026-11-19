# Experiment 05 — Stimulus-boundary derivative handling

**Classification:** New retrospective numerical investigation (2026); not part of the documented 2015 work.  
**Status:** C implementation and controlled comparison prepared; numerical output still needs execution/validation.

## Aim

Investigate whether the first RK4 derivative (the (k_1) slope) is evaluated using the same stimulus current as the remaining RK4 stages when the applied current switches on and off.

## Finding from source inspection

At the beginning of each time-loop iteration, the program updates the global `Iexc` according to the current time. However, it does not immediately recalculate `dydx`. The first RK4 slope therefore remains the derivative calculated at the end of the previous iteration, using the previous iteration's stimulus value. The other three RK4 stages call `derivs()` after `Iexc` has been updated.

This mismatch occurs at the stimulus transitions. It affects the first integration step after the stimulus turns on and the first step after it turns off. Away from the two transitions, the previous derivative and the newly required derivative use the same stimulus current.

## Variants

- **Original handling:** retains the existing order of operations.
- **Refreshed (k_1):** calls `derivs(tt, y, dydx)` immediately after updating `Iexc` and before calling `rk4()`. This ensures that all four RK4 stages use the stimulus value applicable to the current step.

No model parameters, initial conditions, fixed time constants, stimulus amplitude, stimulus duration, delayed-voltage remnant or output format are otherwise changed. The comparison uses `dt = 0.02`, following Experiment 03.

The experimental source is [`HH1neuron_stimulus_boundary.cpp`](HH1neuron_stimulus_boundary.cpp). Compile the original and corrected variants by defining or omitting `REFRESH_K1`:

```sh
gcc -x c -std=gnu89 -O0 HH1neuron_stimulus_boundary.cpp -lm -o original
gcc -x c -std=gnu89 -O0 -DREFRESH_K1 HH1neuron_stimulus_boundary.cpp -lm -o refreshed
```

Run each executable in a separate output directory, since both write `HH1neuron.dat`.

## Interpretation

This is a numerical-consistency correction to the RK4 implementation, not a change to the Hodgkin–Huxley-type equations. At a discontinuity in the external input, the derivative supplied as (k_1) should correspond to the same input value used for the other stages of that integration step. The refreshed version enforces that consistency.

The output-time convention is deliberately left unchanged in this experiment: the program still writes the state after a step against the step's starting time. The delayed-voltage calculation is also retained as an unrelated historical remnant.

## Results

The quantitative comparison and generated plot will be added after the two C variants have been executed and their output files checked. Until then, this README records the code-level finding and reproducible test design only.

## Conclusion

The original loop has a stale-(k_1) derivative at each stimulus transition. Refreshing the derivative immediately after changing `Iexc` is the minimal correction. This should be treated as a small RK4/input-handling inconsistency, not as evidence that the underlying model equations were incorrect.
