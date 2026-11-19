import numpy as np
import matplotlib.pyplot as plt

fixed = np.loadtxt("fixed/HH1neuron.dat")
dynamic = np.loadtxt("voltage_dependent/HH1neuron.dat")

fig, ax = plt.subplots(figsize=(11, 5.5))
ax.plot(fixed[:, 0], fixed[:, 2], label="Fixed time constants (original)")
ax.plot(dynamic[:, 0], dynamic[:, 2], label="Voltage-dependent (alternative)")
ax.set_xlim(0, 200)
ax.set_xlabel("Model time (units to be confirmed)")
ax.set_ylabel("Membrane voltage (units to be confirmed)")
ax.set_title("Experiment 02: gating time-constant comparison")
ax.legend()
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig("experiment02_comparison.svg")
fig.savefig("experiment02_comparison.png", dpi=180)
