# Experiment 07 — Phase-plane and equilibrium analysis

**Classification:** Retrospective analysis (2026) of the fixed-time-constant model. The original 2015 source is not modified.

## Aim and model

The model is a four-dimensional system with state x = [V,m,h,n]. V is membrane voltage (mV); m, h and n are dimensionless gates. The equations copied from the root source are:

dV/dt = [gL(VL−V) + gNa m³h(VNa−V) + gK n⁴(VK−V) + Iexc] / C

dm/dt = [m∞(V)−m]/τm; dh/dt = [h∞(V)−h]/τh; dn/dt = [n∞(V)−n]/τn

q∞(V) = ½[1 + tanh((V−Vq)/dVq)] for q = m,h,n.

The three τ values are calculated once at the initial voltage V=0 mV and held fixed, exactly as in the intended reference interpretation. The C++ exporter is a separate copy of the model equations. It records all four states so that the analysis is based on the C++ trajectory, not a separately recreated trajectory.

A two-dimensional V–m, V–h or V–n graph is a projection of the four-dimensional trajectory. It is not a complete two-dimensional dynamical system: the voltage derivative also depends on the other two gates.

## Reproduce the analysis

From this folder:

    g++ -std=c++11 -O2 phase_plane.cpp -o phase_plane
    ./phase_plane
    python -m pip install numpy scipy pandas matplotlib
    python phase_plane_analysis.py

The C++ program writes phase_trajectory.csv with time_ms, applied_current_nA, V_mV, m, h and n. It uses the original zero initial state, dt=0.02 ms, 10 nA stimulus and rule 0<t<1000 ms. It preserves the original first-derivative handling at stimulus boundaries. New output times are labelled at the end of each integration step, matching the state recorded on that row.

The Python script generates figures/gate_nullclines.png, figures/phase_plane_projections.png and figures/equilibrium_report.txt.

## 1. Gate nullclines

A nullcline for a variable is the set of states where its derivative is zero. For the m gate:

dm/dt=0 iff m=m∞(V).

Likewise h=h∞(V) and n=n∞(V). These curves are also the gate steady-state curves in the source. At a given voltage, they identify the gate value towards which the gate relaxes; the gate does not jump instantly to that value. Its fixed τ controls the rate of approach.

To draw the gate-nullcline figure by hand:
1. Put voltage V (mV) on the horizontal axis, over approximately −100 to +60 mV.
2. Choose a sequence of voltage values across that range.
3. For each V, evaluate the three tanh expressions using the source values Vq and dVq.
4. Plot each calculated gate value on the vertical axis, from 0 to 1.
5. Label the three curves m∞, h∞ and n∞.

The negative dVh value is intentional and comes from the original source; it makes h∞ decrease as V increases.

## 2. Projected phase-plane trajectories

Every row in phase_trajectory.csv contains V,m,h,n at the same time. To make a V–m plot, put V on the horizontal axis and m on the vertical axis, then plot the successive (V,m) pairs in time order. Repeat for (V,h) and (V,n). The script colours points by time, so the progression through the projected state space is visible.

The two columns separate rows with Iexc=0 and Iexc=10 nA. These represent the resting portions and the stimulated portion of this particular pulse simulation.

Interpretation:
- V–m displays sodium activation alongside depolarisation and helps inspect the fast rising phase.
- V–h displays sodium inactivation and its recovery as voltage evolves.
- V–n displays potassium activation, which contributes to the delayed outward potassium current and repolarisation.

Because the other gates are changing too, a projected trajectory can cross itself without the full four-dimensional state repeating. The projection alone does not define a closed two-variable model.

## 3. Conditional voltage-nullcline slices

The gate nullcline in each panel is the dashed q=q∞(V) curve. The dotted curve is a conditional slice of dV/dt=0. For a V–m panel, hold h and n at their equilibrium values h* and n*, then solve the voltage equation for m:

m³ = −[gL(VL−V)+gK n*⁴(VK−V)+Iexc] / [gNa h*(VNa−V)].

Where the right-hand side is non-negative, take its real cube root and retain values in [0,1]. For V–h, solve linearly for h while holding m and n fixed. For V–n, solve for n⁴ and take the non-negative fourth root while holding m and h fixed. Points with near-zero denominators or values outside [0,1] are omitted.

These are conditional two-dimensional slices, not global nullclines of the four-dimensional system. The two unplotted gates are frozen at the equilibrium values for the current being shown. Their intersection with the gate nullcline marks the equilibrium in that slice.

## 4. Equilibria (steady states)

An equilibrium requires all four derivatives to be zero simultaneously:

dV/dt = dm/dt = dh/dt = dn/dt = 0.

The three gate equations imply m=m∞(V), h=h∞(V), n=n∞(V). Substituting these into the voltage equation reduces the equilibrium problem to one scalar equation:

F(V;Iexc) = gL(VL−V) + gNa m∞(V)³h∞(V)(VNa−V)
             + gK n∞(V)⁴(VK−V) + Iexc = 0.

The script evaluates F over a voltage grid from −150 to +100 mV, finds intervals where its sign changes, then refines each bracketed root using Brent's root-finding method. At each voltage root, it evaluates the three gate steady-state functions to obtain the full equilibrium [V,m,h,n].

The calculation is repeated for Iexc=0 and Iexc=10 nA. Each is an equilibrium of a system with that input held constant. The pulsed simulation itself switches input, so it is a transient rather than one constant-input equilibrium problem.

## 5. Local stability: Jacobian and eigenvalues

Near an equilibrium x*, a small displacement δx is approximated by the linear system:

d(δx)/dt ≈ J(x*)δx, where Jij = ∂fi/∂xj evaluated at x*.

J is a 4×4 Jacobian because there are four state variables. The script estimates each partial derivative with a centred finite difference:

∂f/∂xj ≈ [f(x*+εjej)−f(x*−εjej)]/(2εj).

It then calculates the four eigenvalues of J. If all eigenvalues have negative real parts, small perturbations decay in the linearised system and the equilibrium is locally asymptotically stable. A positive real part indicates instability. A complex-conjugate pair describes an oscillatory mode; its real part indicates whether the oscillation decays or grows.

This is a local conclusion only. It does not prove global stability, rule out other attractors or replace simulation of the nonlinear equations. The Jacobian uses numerical finite differences, so results should be reported to sensible precision rather than treating the last digits as exact.

## 6. Interpretation and limitations

The equilibrium report is generated by the script. For this parameter set, the scalar equilibrium search finds one root in the searched voltage range for each constant-current condition. The Jacobian eigenvalues have negative real parts at both roots, including a complex-conjugate pair. Thus both fixed-input equilibria are locally asymptotically stable and have a damped oscillatory linear mode.

The zero-input equilibrium describes the resting fixed point when the applied current is held at zero. The 10 nA equilibrium describes the fixed point that would apply if the stimulus were held on indefinitely. The actual simulation uses a finite pulse, so it is not expected to settle at the stimulated equilibrium during that finite interval.

These calculations describe this model and its parameter values. They do not by themselves establish physiological validity or prove a detailed biological mechanism.

## Files

- phase_plane.cpp — C++ trajectory exporter based on the original fixed-time-constant equations.
- phase_plane_analysis.py — nullclines, projections, equilibrium search and Jacobian/eigenvalue analysis.
- phase_trajectory.csv — generated trajectory data.
- figures/ — generated plots and equilibrium report.

The original root-level HH1neuron.cpp remains unchanged.
