# Experiment 06 — Delayed neuronal output and the vagus nerve

**Classification:** Retrospective investigation (2026), based on the author's recollection of the intended 2015 project.  
**Status:** Experimental source added; numerical execution and comparison remain to be run locally.

## Aim

Investigate the legacy delayed-voltage calculation in the single-neuron model, in light of the author's recollection that this neuron was intended to provide an output signal to the vagus nerve.

The working historical interpretation is a one-way output from the modelled neuron towards the vagus nerve. The vagus nerve, its receiving dynamics, any cardiac response, and heartbeat/respiratory-arrhythmia coupling are not modelled in this experiment. The exact physiological meaning, units, and intended downstream interpretation of the signal remain unconfirmed and should be checked against project records or the former supervisor if possible.

## What the source does

The original source sets `tau = 500` and calculates `yy0old` from `y0top`, `y0bot`, and the loop indices. The comment describes this as calculating membrane voltage at `tt - tau`.

However, inspection of the indexing and interpolation expression shows that, after the delayed index becomes positive, the expression algebraically returns `y0top`, which has just been assigned the current `y[0]`. Before that point, both stored values are set to zero and `yy0old` is zero. In other words, in this implementation the candidate output is zero initially and then follows the current membrane voltage; it does not demonstrably provide a 500-time-unit delayed copy.

This is a source-level finding, not a claim about what the author originally intended. The original calculation is retained so its behaviour can be inspected rather than silently replaced with a newly invented delay implementation.

## Experimental source

[`HH1neuron_vagus_output.cpp`](HH1neuron_vagus_output.cpp) is based on the fixed-time-constant source used for Experiment 05. It:

- preserves the four-state-variable neuron, its equations, parameters, initial conditions, stimulus, and RK4 integration;
- retains the legacy calculation of `yy0old`;
- writes four tab-separated columns: loop time, applied current, current membrane voltage before the integration step, and the legacy candidate output `yy0old`;
- uses integer loop/index types, consistent with the later retrospective experiment files.

The two voltage columns are recorded at the same point in the loop, before the RK4 step, so they can be compared directly. This changes the output sampling convention relative to the original program, which wrote the voltage after the step while labelling it with the step-start time. It does not intentionally change the neuronal equations or integration.

Compile and run from a directory where the output file can be created:

```sh
gcc -x c -std=gnu89 -O0 HH1neuron_vagus_output.cpp -lm -o experiment06
./experiment06
```

The program writes `HH1neuron.dat`.

## Interpretation and limitations

If the two voltage columns match after the initial zero segment, that confirms that the current implementation's candidate output is not functioning as a delayed voltage signal. It would be inappropriate to describe it as a verified neuron-to-vagus transmission signal or to infer excitation versus inhibition from it.

A true delayed output would require retaining past voltage samples (or an equivalent delay-line/history mechanism) and retrieving the value corresponding to the chosen delay. That would be a separate reconstruction choice and is deliberately not introduced here because the historical implementation and intended timing have not been established.

No additional neuron is introduced. No vagus-nerve model, feedback pathway, gain, polarity, or cardiac model is added. Physical units are not assigned because they have not yet been confirmed.

## Conclusion

Experiment 06 documents and exposes the legacy candidate output without changing the neuronal dynamics. The source suggests that the historical delay calculation does not currently implement the delay indicated by its comment. The likely one-way neuron-to-vagus purpose is recorded as the author's recollection, not as a verified physiological mechanism.
