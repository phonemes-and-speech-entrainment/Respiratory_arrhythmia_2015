#!/usr/bin/env python3
"""Reproduce Experiment 03 using the fixed-time-constant C source.

Requires GCC. Matplotlib is optional and is only needed for plots.
Run from any directory: python run_experiment.py
"""
from pathlib import Path
import csv
import re
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "02_time_constant_comparison" / "fixed" / "HH1neuron.cpp"
OUTPUT = HERE / "output"
INTERVAL_COUNTS = (10_000, 20_000, 50_000, 100_000)

def summarise(path):
    rows = []
    with path.open() as stream:
        for line in stream:
            values = [float(x) for x in line.split()]
            if len(values) != 3:
                raise ValueError(f"Expected three columns in {path}")
            rows.append(values)
    if not rows:
        raise ValueError(f"No output rows in {path}")
    times = [r[0] for r in rows]
    currents = [r[1] for r in rows]
    voltage = [r[2] for r in rows]
    if not all(map(lambda x: x == x and abs(x) != float("inf"),
                   times + currents + voltage)):
        raise ValueError(f"Non-finite value in {path}")
    imin = min(range(len(voltage)), key=voltage.__getitem__)
    imax = max(range(len(voltage)), key=voltage.__getitem__)
    upward, downward = [], []
    for i in range(1, len(voltage)):
        if voltage[i-1] <= 0 < voltage[i]:
            upward.append(times[i])
        if voltage[i-1] >= 0 > voltage[i]:
            downward.append(times[i])
    return {
        "step": 1000.0 / int(round((times[-1] - times[0]) / (len(rows)-1) * 0 + 1000)),
        "rows": len(rows),
        "minimum_voltage": voltage[imin],
        "time_of_minimum": times[imin],
        "maximum_voltage": voltage[imax],
        "time_of_maximum": times[imax],
        "final_voltage": voltage[-1],
        "upward_zero_crossings": ";".join(f"{x:.2f}" for x in upward),
        "downward_zero_crossings": ";".join(f"{x:.2f}" for x in downward),
        "times": times,
        "voltage": voltage,
        "current": currents,
    }

def main():
    source = SOURCE.read_text()
    OUTPUT.mkdir(exist_ok=True)
    summaries = []
    plot_data = []
    for n in INTERVAL_COUNTS:
        variant = re.sub(r"\\bn\\s*=\\s*\\d+\\s*;", f"n = {n};", source, count=1)
        if variant == source:
            raise RuntimeError("Could not find the n assignment in the source")
        run_dir = OUTPUT / f"dt_{1000/n:.2f}"
        run_dir.mkdir(exist_ok=True)
        c_file = run_dir / "HH1neuron.cpp"
        executable = run_dir / "HH1neuron"
        c_file.write_text(variant)
        subprocess.run(["gcc", "-x", "c", "-std=gnu89", "-O0",
                        str(c_file), "-lm", "-o", str(executable)], check=True)
        subprocess.run([str(executable)], cwd=run_dir, check=True)
        result = summarise(run_dir / "HH1neuron.dat")
        result["step"] = 1000.0 / n
        summaries.append({k: v for k, v in result.items()
                          if k not in ("times", "voltage", "current")})
        plot_data.append(result)
        print(f"Completed dt={1000/n:.2f}: {result['rows']} rows")
    csv_path = HERE / "summary.csv"
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    print(f"Wrote {csv_path}")
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed; skipped plots. Install it with: python -m pip install matplotlib")
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    for result in plot_data:
        ax.plot(result["times"], result["voltage"],
                label=f"dt = {result['step']:.2f}")
    ax.set_xlim(0, 20)
    ax.set_xlabel("Model time (units to be confirmed)")
    ax.set_ylabel("Membrane voltage (units to be confirmed)")
    ax.set_title("Experiment 03 — Integration step-size comparison")
    ax.legend()
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(HERE / "step_size_comparison.svg")
    fig.savefig(HERE / "step_size_comparison.png", dpi=180)
    print("Wrote step_size_comparison.svg and .png")

if __name__ == "__main__":
    main()
