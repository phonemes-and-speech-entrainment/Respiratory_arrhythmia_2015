from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent
OUT=HERE/"figures"; OUT.mkdir(exist_ok=True)
GL,VL=.2955,-54.11; GNA,VNA=118.79,49.99; GK,VK,C=20.35,-76.97,1.
MID=np.array([-40.08,-59.91,-54.91]); SLOPE=np.array([14.9,-14.88,29.28])
T0=np.array([.1009,1.004,1.012]); T1=np.array([.3982,7.047,4.99])
TAU=T0+T1*(1-np.tanh(-MID/SLOPE)**2)

def qinf(V): return .5*(1+np.tanh((np.asarray(V)[...,None]-MID)/SLOPE))
def field(x,I):
 V,m,h,n=x; mi,hi,ni=qinf(V)
 return np.array([(GL*(VL-V)+GNA*m**3*h*(VNA-V)+GK*n**4*(VK-V)+I)/C,
 (mi-m)/TAU[0],(hi-h)/TAU[1],(ni-n)/TAU[2]])
def voltage_balance(V,I):
 m,h,n=qinf(V)
 return GL*(VL-V)+GNA*m**3*h*(VNA-V)+GK*n**4*(VK-V)+I
def equilibria(I):
 grid=np.linspace(-150,100,10001); vals=np.array([voltage_balance(v,I) for v in grid]); roots=[]
 for a,b,fa,fb in zip(grid[:-1],grid[1:],vals[:-1],vals[1:]):
  if fa*fb<0: roots.append(brentq(lambda v:voltage_balance(v,I),a,b,xtol=1e-12))
 return [np.r_[v,qinf(v)] for v in roots]
def jacobian(x,I):
 J=np.empty((4,4))
 for j in range(4):
  e=np.zeros(4); e[j]=1e-5*max(1,abs(x[j]))
  J[:,j]=(field(x+e,I)-field(x-e,I))/(2*e[j])
 return J
def main():
 data=pd.read_csv(HERE/"phase_trajectory.csv")
 # Gate nullclines: qdot=0 iff q=q_inf(V). Plot the source's three tanh curves.
 V=np.linspace(-100,60,1000); gates=qinf(V)
 fig,ax=plt.subplots(figsize=(8,5))
 for j,name in enumerate(["m_inf","h_inf","n_inf"]): ax.plot(V,gates[:,j],label=name)
 ax.set(xlabel="Membrane voltage V (mV)",ylabel="Steady-state gate value",title="Gate nullclines")
 ax.set_ylim(-.03,1.03);ax.grid(alpha=.3);ax.legend();fig.tight_layout()
 fig.savefig(OUT/"gate_nullclines.png",dpi=180);plt.close(fig)
 # Equilibrium requires all gates at q_inf(V); reduce four equations to one root F(V;I)=0.
 report=["Fixed gate time constants at initial V=0 mV (ms): "+str(TAU)]
 eqs={}
 for I in (0.,10.):
  eqs[I]=equilibria(I); report.append(f"\nI = {I:g} nA")
  for x in eqs[I]:
   eig=np.linalg.eigvals(jacobian(x,I))
   report += ["Equilibrium [V,m,h,n] = "+np.array2string(x,precision=9),
    "Jacobian eigenvalues = "+np.array2string(eig,precision=7),
    "Locally asymptotically stable" if np.all(eig.real<0) else "Not locally asymptotically stable"]
 (OUT/"equilibrium_report.txt").write_text("\n".join(report)+"\n")
 # Three projected trajectories. The dotted voltage nullcline is a 2-D slice:
 # the two unplotted gates are frozen at their values at that condition's equilibrium.
 fig,axes=plt.subplots(3,2,figsize=(13,12),sharex=True)
 for col,I in enumerate((0.,10.)):
  sub=data[np.isclose(data.applied_current_nA,I)]
  eq=eqs[I][0] if eqs[I] else None
  for row,(idx,name) in enumerate(((1,"m"),(2,"h"),(3,"n"))):
   ax=axes[row,col]; sc=ax.scatter(sub.V_mV,sub[name],c=sub.time_ms,s=2,cmap="viridis",rasterized=True)
   if eq is not None:
    ax.plot(V,qinf(V)[:,idx-1],"--",label=f"d{name}/dt = 0")
    fixed=eq[1:].copy(); vnul=[]
    for v in V:
     m,h,n=fixed
     if idx==1:
      den=GNA*h*(VNA-v); num=-(GL*(VL-v)+GK*n**4*(VK-v)+I); z=num/den if abs(den)>1e-12 else np.nan
      value=np.cbrt(z) if z>=0 else np.nan
     elif idx==2:
      den=GNA*m**3*(VNA-v); num=-(GL*(VL-v)+GK*n**4*(VK-v)+I); value=num/den if abs(den)>1e-12 else np.nan
     else:
      den=GK*(VK-v); num=-(GL*(VL-v)+GNA*m**3*h*(VNA-v)+I); z=num/den if abs(den)>1e-12 else np.nan
      value=z**.25 if z>=0 else np.nan
     vnul.append(value if np.isfinite(value) and 0<=value<=1 else np.nan)
    ax.plot(V,vnul,":",lw=2,label="dV/dt = 0 (other gates fixed)")
    ax.plot(eq[0],eq[idx],"r*",ms=12,label="Equilibrium")
   ax.set(title=f"V–{name} projection, I = {I:g} nA",ylabel=f"{name} gate value")
   ax.set_ylim(-.03,1.03);ax.grid(alpha=.25)
   if row==0: ax.legend(fontsize=7)
   if row==2: ax.set_xlabel("Membrane voltage V (mV)")
 fig.colorbar(sc,ax=axes.ravel().tolist(),label="Simulation time (ms)",shrink=.7)
 fig.suptitle("Projected four-state trajectories and conditional nullcline slices")
 fig.savefig(OUT/"phase_plane_projections.png",dpi=180,bbox_inches="tight");plt.close(fig)
 print("\n".join(report));print("Figures and report saved in",OUT)
if __name__=="__main__": main()
