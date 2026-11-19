#!/usr/bin/env python3
"""Plot Experiment 05 original and refreshed-k1 voltage traces.

Run the two compiled C variants in folders named 'original' and 'refreshed'
so each folder contains HH1neuron.dat, then run this script.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
original = np.loadtxt(HERE / "original" / "HH1neuron.dat")
refreshed = np.loadtxt(HERE / "refreshed" / "HH1neuron.dat")
if original.shape != refreshed.shape:
    raise ValueError("The two output files have different shapes")
if not np.allclose(original[:, 0], refreshed[:, 0]):
    raise ValueError("The two output time columns do not match")

time = original[:, 0]
difference = refreshed[:, 2] - original[:, 2]
fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
axes[0].plot(time, original[:, 2], label="Original derivative handling")
axes[0].plot(time, refreshed[:, 2], label="Refreshed k1")
axes[0].set_xlim(-5, 20)
axes[0].set_ylabel("Membrane voltage (units unconfirmed)")
axes[0].set_title("Stimulus onset response")
axes[0].legend()
axes[0].grid(True, alpha=0.25)
axes[1].plot(time, difference, label="Refreshed − original")
axes[1].axhline(0, linewidth=0.8)
axes[1].set_xlim(-5, 20)
axes[1].set_xlabel("Model time (units unconfirmed)")
axes[1].set_ylabel("Voltage difference")
axes[1].set_title("Pointwise difference near stimulus onset")
axes[1].grid(True, alpha=0.25)
fig.savefig(HERE / "experiment05_comparison.svg")
fig.savefig(HERE / "experiment05_comparison.png", dpi=160)
print("Saved experiment05_comparison.svg and .png")
