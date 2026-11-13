# HH1neuron simulation output

The original `HH1neuron.cpp` was compiled as legacy C and run without changing
its source or equations. The generated `HH1neuron.dat` contains 20,001
tab-separated rows with time, applied current, and membrane voltage. The SVG
plots the applied current and voltage against time; all axes explicitly say
that units are unspecified because the source does not identify them.

## Reproduce

From the repository root:

```sh
clang -x c -std=gnu89 HH1neuron.cpp -lm -o simulation-output/HH1neuron
(cd simulation-output && ./HH1neuron)
python3 simulation-output/create_plots.py
```

The executable writes `HH1neuron.dat` in its current directory. The source
computes an interpolated delayed voltage, but does not use it in the equations
or output, so this run preserves that behavior as-is. The plotter uses only
the Python standard library.

## Continuous-pulse comparison

The original stimulus is already a constant rectangular pulse: it is on for
`0 < t < 1000` and off outside that interval. As an additional example, the
separate `HH1neuron_continuous.cpp` changes only the pulse amplitude from
`I = 10` to `I = 15`; the original source remains unchanged. This is an
illustrative comparison, not a validated physiological parameter choice.

From the repository root:

```sh
mkdir -p simulation-output/continuous-pulse
clang -x c -std=gnu89 simulation-output/HH1neuron_continuous.cpp -lm -o simulation-output/continuous-pulse/HH1neuron
(cd simulation-output/continuous-pulse && ./HH1neuron)
python3 simulation-output/create_plots.py \
  --data simulation-output/continuous-pulse/HH1neuron.dat \
  --output simulation-output/continuous-pulse/HH1neuron.svg \
  --title "HH1neuron continuous pulse (I = 15)"
```
