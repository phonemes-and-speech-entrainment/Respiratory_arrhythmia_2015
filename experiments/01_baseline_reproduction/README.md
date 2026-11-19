# Experiment 01 — Baseline reproduction

**Classification:** New retrospective experiment (2026) using the original 2015 source  
**Status:** Reproduced successfully

## Aim

Reproduce the behaviour of the original `HH1neuron.cpp` without changing its source code, equations, initial conditions, stimulus, or parameter values. This run provides the reference dataset for the subsequent retrospective experiments.

## Source and method

The original source remains at the repository root: [`HH1neuron.cpp`](../../HH1neuron.cpp).

It was compiled as legacy C (the file uses an old-style `main()` declaration, despite its `.cpp` extension) and run without source modifications:

```sh
mkdir -p /tmp/hh1-baseline
gcc -x c -std=gnu89 -O0 HH1neuron.cpp -lm -o /tmp/hh1-baseline/HH1neuron
(cd /tmp/hh1-baseline && ./HH1neuron)
```

The executable writes `HH1neuron.dat` to its working directory. The reproduced file was compared with the repository's existing baseline dataset. They are byte-for-byte identical: both have 637,811 bytes and Git blob SHA:

```
c364ec52eab46e8b3c4b1a564c4721a8852e3987
```

The committed baseline data and plot are retained in [`simulation-output/`](../../simulation-output/README.md):

- [Baseline data](../../simulation-output/HH1neuron.dat)
- [Baseline plot](../../simulation-output/HH1neuron.svg)
- [Plot-generation script](../../simulation-output/create_plots.py)

No changes were made to the original simulation source for this experiment.

## Original settings

| Setting | Value |
| --- | ---: |
| Positive-time window (`ttime`) | 1000 |
| Number of intervals (`n`) | 10,000 |
| Integration step (`tstep`) | 0.1 |
| Applied-current amplitude (`I`) | 10 |
| Stimulus condition | `0 < tt < 1000` |
| Initial membrane voltage | 0 |
| Initial gate values | 0, 0, 0 |
| Integration method | Classical fourth-order Runge–Kutta (RK4) |

The loop runs from `i = -n` through `i = n`, producing 20,001 output rows over the labelled time range −1000 to +1000. The author has confirmed the model units: time and time step are in ms, membrane voltage is in mV, injected current is in nA, conductance density is in mS/cm², and capacitance is in µF/cm².

## Results

The reproduced dataset contains three finite-valued columns: time, applied current, and membrane voltage.

| Measurement | Result |
| --- | ---: |
| Number of rows | 20,001 |
| Time step represented in output | 0.1 |
| Minimum recorded voltage | −72.749909 at labelled time 4.6 |
| Maximum recorded voltage | +34.432211 at labelled time 2.1 |
| Upward crossing of voltage 0 | Labelled time 2.0 |
| Downward crossing of voltage 0 | Labelled time 3.3 |
| Final recorded voltage | −59.268612 |

The voltage trace shows an initial spike followed by a return towards a sustained level. There is no sustained repetitive firing in this baseline run.

## Implementation observations retained for later experiments

This experiment deliberately preserves the original implementation, including behaviours that will be investigated separately:

1. **Output time label:** The program advances the state by one time step and then writes the current loop time `tt`. Consequently, the voltage written on a row corresponds to the end of that integration step (`tt + tstep`), while the row is labelled with its start time. The recorded voltage trace is therefore labelled one step earlier than the state time.
2. **Stimulus transitions:** The derivative array is calculated at the end of each loop iteration using the current stimulus, but the stimulus is updated before the next RK4 call. At a stimulus transition, the first RK4 derivative can therefore reflect the previous stimulus value while the intermediate RK4 stages use the new value. This is preserved in the baseline and will be tested separately.
3. **Fixed gate time constants:** The `taui` values are calculated once in `main()` at the initial membrane voltage and are used throughout. The local `ttaui` values recalculated in `derivs()` are not used. The fixed-time-constant behaviour is retained here, consistent with the clarification about the intended model.
4. **Delayed-voltage calculation:** The interpolated delayed voltage is calculated but does not feed into the differential equations or output in this single-neuron file. It is retained as a historical remnant associated with earlier vagus-nerve-related code.

These are not corrections made in Experiment 01. They are recorded so later experiments can isolate and evaluate them without changing the reference implementation.

## Conclusion

The original source compiles and runs in legacy C mode, and its output has been reproduced exactly. The resulting dataset is therefore suitable as the baseline reference for the subsequent experiments. Any later changes to equations, numerical handling, or parameters must be documented as retrospective experimental variants, not as part of the original 2015 implementation.
