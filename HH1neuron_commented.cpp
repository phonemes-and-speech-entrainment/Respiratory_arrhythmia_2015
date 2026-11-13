#include<math.h>
#include<stdio.h>
#define PI 3.1415926

/*
 * Copyright (c) 2015 Oana Cucu, Department of Physiology and Pharmacology,
 * University of Bristol.
 * Supervised by Prof. Alain Nogaret, Department of Physics, University of Bath.
 *
 * Source-level interpretation:
 * This file simulates one conductance-based neuron (the parameters are
 * commented as those of neuron 1). The state vector is membrane voltage
 * followed by three channel-gating variables, and the equations are advanced
 * with the classical fourth-order Runge-Kutta method. Its three gates and
 * sodium/potassium ionic currents have a Hodgkin-Huxley-like form, rather
 * than the usual two-state FitzHugh-Nagumo form. The file alone does not
 * establish the model's publication, project title, or physical units.
 *
 * The code also calculates a delayed/interpolated voltage value, but that
 * value is not used by the differential equations or output in this file.
 * It contains no explicit second neuron, interneuron, vagus-nerve, or heart
 * coupling; those may be represented in other program files.
 */

void rk4(double *, double *, double, double, double *);
void derivs(double, double *, double *);

/* State, derivatives, and temporary output for the four ODE variables. */
double y[4],dydx[4],yout[4];

/* Steady-state activation and time constants for the m, h, and n gates. */
double a[3],taui[3];

/* Previous-step voltage samples used when constructing the delayed value. */
double y0top,y0bot;

/*
 * Membrane/channel parameters; units are not specified in this source.
 * vm, vh, and vn are voltage midpoints for the m, h, and n gate curves;
 * they are not the membrane-voltage state (y[0]).
 */
double gl,vl,gna,vna,gk,vk,C,vm,dvm,vh,dvh,vn,dvn,tm0,tm1,th0,th1,tn0,tn1,tau,I,Iexc,yy0old;

/* Run the simulation, write tab-separated time/current/voltage data. */
main()
{
   double ttime,tt,tstep;
   double a0,b0;
   short i,j,k,n,p1,p2;
   FILE *pf;

   n = 10000;		/* Number of intervals in the positive-time window. */
   ttime = 1000.;	/* Positive-time window length (model time units). */
   tstep = ttime/n;	/* Integration step: 0.1 for these settings. */

   /* Leak, sodium, and potassium conductances and reversal potentials. */
   gl = 0.2955; /*leak conductance of neuron 1*/
   vl = -54.11; /*leak potential of neuron 1*/
   gna = 118.79; /*sodium channel conductance of neuron 1*/
   vna = 49.99; /*sodium channel potential of neuron 1*/
   gk = 20.35; /*potassium channel conductance of neuron 1*/
   vk = -76.97; /*potassium channel potential of neuron 1*/

   /* Gate-curve voltage midpoints and slope parameters. */
   vm = -40.08;
   dvm = 14.9;
   vh = -59.91;
   dvh = -14.88;
   vn = -54.91;
   dvn = 29.28;
   /* Coefficients defining the voltage-dependent gate time constants. */
   tm0 = 0.1009;
   tm1 = 0.3982;
   th0 = 1.004;
   th1 = 7.047;
   tn0 = 1.012;
   tn1 = 4.99;
   C = 1.;
   I = 10.;              /* Amplitude of the applied current stimulus. */
   tau = 500.;		/* Delay parameter, in the model's unspecified time units. */
   k = (short)(tau/tstep);	/* Delay expressed as an integer number of steps. */

   /* Open the output file, replacing any existing file with this name. */
   pf = fopen("HH1neuron.dat","w+");

   /* Initial conditions: V, m, h, and n are all set to zero. */
   y[0] = 0.;
   y[1] = 0.;
   y[2] = 0.;
   y[3] = 0.;

   /* Evaluate each gate's steady-state value and time constant at V = y[0].
      The dV == 0 branches avoid evaluating the corresponding tanh formulas. */
   if (dvm==0)
   {a[0]=0; taui[0]=0;}
   else
   {a[0] = 0.5*(1.+tanh((y[0]-vm)/dvm));
   taui[0] = tm0 + tm1*(1.-tanh((y[0]-vm)/dvm)*tanh((y[0]-vm)/dvm)); }

   if (dvh==0)
   {a[1]=0; taui[1]=0;}
   else
   {a[1] = 0.5*(1.+tanh((y[0]-vh)/dvh));
   taui[1] = th0 + th1*(1.-tanh((y[0]-vh)/dvh)*tanh((y[0]-vh)/dvh));}
   if (dvn==0)
   {a[2]=0; taui[2]=0;}
   else
   {a[2] = 0.5*(1.+tanh((y[0]-vn)/dvn));
   taui[2] = tn0 + tn1*(1.-tanh((y[0]-vn)/dvn)*tanh((y[0]-vn)/dvn));}

   dydx[0] = (gl*(vl-y[0])+gna*y[1]*y[1]*y[1]*y[2]*(vna-y[0])+gk*y[3]*y[3]*y[3]*y[3]*(vk-y[0]))/C;
   dydx[1] = (a[0]-y[1])/taui[0];
   dydx[2] = (a[1]-y[2])/taui[1];
   dydx[3] = (a[2]-y[3])/taui[2];

   /*
    * Iterate from -ttime through +ttime. This provides a negative-time
    * pre-stimulus segment; the current is applied only for 0 < tt < ttime.
    * Because both endpoints are included, this loop executes 2*n+1 steps.
    */
   for(i=-n;i<=n;i++)
   {
      tt = tstep*(double)i;
	  if (tt>0 && tt<ttime)  {Iexc=I;}  else  {Iexc=0.;}

      /* Indices and linear interpolation used to estimate V(tt - tau). */
      p2 = i+n-k;
	  p1 = p2-1;
	  if (p1 > 0)   /* Collecting the time interval of delayed pulse for ith iteration */
	  {
		y0bot = y0top;
	  }

	  if (p2 > 0)
	  {
		 y0top = y[0];
	  }
	  else
	  {
		 y0top = 0.;   y0bot = 0.;
	  }

      a0 = (y0top-y0bot)/tstep;		/* Slope between the delayed-voltage samples. */
	  b0 = p2*y0bot-p1*y0top;
      yy0old = a0*(tstep*(double)(i+n)-tau)+b0;

      /* Advance the state by one RK4 step, then prepare derivatives for the
         next step. Iexc is global and remains fixed during this RK4 step. */
      rk4(y,dydx,tt,tstep,yout);

      for(j=0;j<4;j++)   y[j] = yout[j];
      derivs(tt+tstep,y,dydx);


      /* Record time, applied current, and updated membrane voltage. */
      fprintf(pf,"%lf\t%lf\t%lf\n",tt,Iexc,y[0]);
   }

   fclose(pf);
   return(0);
}
   void derivs(double z, double *yy, double *dyydx)
{
   double aa0[3],ttaui[3];

   /* Recompute voltage-dependent gate steady states and time constants. */
   if (dvm==0) {aa0[0]=0; ttaui[0]=0;}
   else
   {aa0[0] = 0.5*(1.+tanh((yy[0]-vm)/dvm));
   ttaui[0] = tm0 + tm1*(1.-tanh((yy[0]-vm)/dvm)*tanh((yy[0]-vm)/dvm));}

   if (dvh==0) {aa0[1]=0; ttaui[1]=0;}
   else
   {aa0[1] = 0.5*(1.+tanh((yy[0]-vh)/dvh));
   ttaui[1] = th0 + th1*(1.-tanh((yy[0]-vh)/dvh)*tanh((yy[0]-vh)/dvh));}
   if (dvn==0) {aa0[2]=0; ttaui[2]=0;}
   else
   {aa0[2] = 0.5*(1.+tanh((yy[0]-vn)/dvn));
   ttaui[2] = tn0 + tn1*(1.-tanh((yy[0]-vn)/dvn)*tanh((yy[0]-vn)/dvn));}

   /*
    * Membrane-current balance and gate kinetics. Note: these expressions
    * divide by the global taui[], not the local voltage-dependent ttaui[].
    * taui[] is assigned once in main at the initial voltage, so the gate
    * time constants are effectively fixed despite the recomputation above.
    * This looks unintended, but is left unchanged in this commented copy.
    */
   dyydx[0] = (gl*(vl-yy[0])+gna*yy[1]*yy[1]*yy[1]*yy[2]*(vna-yy[0])+gk*yy[3]*yy[3]*yy[3]*yy[3]*(vk-yy[0])+Iexc)/C;
   dyydx[1] = (aa0[0]-yy[1])/taui[0];
   dyydx[2] = (aa0[1]-yy[2])/taui[1];
   dyydx[3] = (aa0[2]-yy[3])/taui[2];

}

void rk4(double *yy, double *dyydx, double x, double h, double *yyout)
{
   double dym[4], dyt[4], yt[4];
   double xh,hh,h6;
   short i;

   /* Classical fourth-order Runge-Kutta stages for the four state variables.
      dyydx is the derivative at the beginning of the step. */
   hh = h*0.5;
   h6 = h/6.0;
   xh = x+hh;

   for(i=0;i<4;i++)  yt[i] = yy[i]+hh*dyydx[i];
   derivs(xh,yt,dyt);
   for(i=0;i<4;i++)  yt[i] = yy[i]+hh*dyt[i];
   derivs(xh,yt,dym);
   for(i=0;i<4;i++)
   {
      yt[i] = yy[i]+h*dym[i];
      dym[i] += dyt[i];
   }

   derivs(x+h,yt,dyt);
   for (i=0;i<4;i++)  yyout[i] = yy[i]+h6*(dydx[i]+dyt[i]+2.0*dym[i]);
}


