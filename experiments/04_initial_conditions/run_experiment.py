#!/usr/bin/env python3
"""Run Experiment 04: compare initial gating-variable values.

Requires GCC. Matplotlib is optional and is only needed for the plot.
Run with: python run_experiment.py
"""
from pathlib import Path
import csv
import math
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "HH1neuron_initial_conditions.cpp"
OUTPUT = HERE / "output"
CASES = {
    "zero_gates": (0.0, 0.0, 0.0),
    "half_steady_state": (
        0.49770634991433505,
        0.00015911476628582833,
        0.4885189796956313,
    ),
    "full_steady_state": (
        0.9954126998286701,
        0.00031822953257165665,
        0.9770379593912626,
    ),
}

def read_data(path):
    rows = []
    with path.open() as stream:
        for line_number, line in enumerate(stream, 1):
            values = [float(value) for value in line.split()]
            if len(values) != 3 or not all(math.isfinite(v) for v in values):
                raise ValueError(f"Invalid output at {path}:{line_number}")
            rows.append(values)
    if not rows:
        raise ValueError(f"No data in {path}")
    return rows

def main():
    OUTPUT.mkdir(exist_ok=True)
    executable = HERE / "HH1neuron_initial_conditions"
    subprocess.run(
        ["gcc", "-x", "c", "-std=gnu89", "-O0", str(SOURCE),
         "-lm", "-o", str(executable)],
        check=True,
    )
    data = {}
    for name, gates in CASES.items():
        folder = OUTPUT / name
        folder.mkdir(exist_ok=True)
        subprocess.run(
            [str(executable), *(format(value, ".17g") for value in gates)],
            cwd=folder,
            check=True,
        )
        data[name] = read_data(folder / "HH1neuron.dat")
        print(f"Completed {name}: {len(data[name])} rows")

    baseline = data["zero_gates"]
    summaries = []
    for name, gates in CASES.items():
        rows = data[name]
        times = [r[0] for r in rows]
        voltage = [r[2] for r in rows]
        pre = [i for i, t in enumerate(times) if t < 0]
        post = [i for i, t in enumerate(times) if t >= 0]
        pre_min = min(pre, key=lambda i: voltage[i])
        peak = max(post, key=lambda i: voltage[i])
        up = sum(
            voltage[i - 1] <= 0 < voltage[i] and times[i] >= 0
            for i in range(1, len(rows))
        )
        max_post_difference = max(
            abs(voltage[i] - baseline[i][2]) for i in post
        )
        summaries.append({
            "case": name,
            "m0": gates[0], "h0": gates[1], "n0": gates[2],
            "pre_stimulus_min_V": voltage[pre_min],
            "pre_stimulus_min_time": times[pre_min],
            "stimulus_peak_V": voltage[peak],
            "stimulus_peak_time": times[peak],
            "final_V": voltage[-1],
            "upward_zero_crossings_during_stimulus": up,
            "max_abs_difference_from_zero_gates_after_stimulus":
                max_post_difference,
        })

    with (HERE / "summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    print("Wrote summary.csv")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed; skipped plot generation.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(9, 6), constrained_layout=True)
    labels = {
        "zero_gates": "Zero gates (original)",
        "half_steady_state": "Half steady-state gates",
        "full_steady_state": "Steady-state gates",
    }
    for name, rows in data.items():
        times = [r[0] for r in rows]
        voltage = [r[2] for r in rows]
        pre = [i for i, t in enumerate(times) if -1000 <= t <= -960]
        post = [i for i, t in enumerate(times) if 0 <= t <= 20]
        axes[0].plot([times[i] for i in pre],
                     [voltage[i] for i in pre], label=labels[name])
        axes[1].plot([times[i] for i in post],
                     [voltage[i] for i in post], label=labels[name])
    for ax, title in zip(
        axes,
        ("Initial transient before stimulation", "Response during stimulus"),
    ):
        ax.set_title(title)
        ax.set_xlabel("Model time (units to be confirmed)")
        ax.set_ylabel("Membrane voltage (units to be confirmed)")
        ax.legend()
        ax.grid(True, alpha=0.25)
    fig.suptitle("Experiment 04 — Initial gating-variable conditions")
    fig.savefig(HERE / "experiment04_initial_conditions.svg")
    fig.savefig(HERE / "experiment04_initial_conditions.png", dpi=160)
    print("Wrote experiment04_initial_conditions.svg and .png")

if __name__ == "__main__":
    main()
