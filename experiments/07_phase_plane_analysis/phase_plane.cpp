// Experiment 07: C++ exporter for the original fixed-tau four-state neuron.
// Writes endpoint time, applied current, V, m, h, n. Original root source is untouched.
#include <cmath>
#include <cstdio>
static const double gl=.2955,vl=-54.11,gna=118.79,vna=49.99,gk=20.35,vk=-76.97,C=1.;
static const double vm=-40.08,dvm=14.9,vh=-59.91,dvh=-14.88,vn=-54.91,dvn=29.28;
static const double tm0=.1009,tm1=.3982,th0=1.004,th1=7.047,tn0=1.012,tn1=4.99;
static const double dt=.02,stim=10.,window=1000.;
static double tau[3],y[4],k1[4];
double inf(double V,double v,double d){return .5*(1.+std::tanh((V-v)/d));}
void f(const double x[4],double I,double out[4]){
 double V=x[0],m=x[1],h=x[2],n=x[3];
 out[0]=(gl*(vl-V)+gna*m*m*m*h*(vna-V)+gk*n*n*n*n*(vk-V)+I)/C;
 out[1]=(inf(V,vm,dvm)-m)/tau[0]; out[2]=(inf(V,vh,dvh)-h)/tau[1]; out[3]=(inf(V,vn,dvn)-n)/tau[2];
}
void rk4(const double x[4],const double first[4],double I,double out[4]){
 double a[4],b[4],c[4],z[4];
 for(int j=0;j<4;j++)z[j]=x[j]+.5*dt*first[j]; f(z,I,a);
 for(int j=0;j<4;j++)z[j]=x[j]+.5*dt*a[j]; f(z,I,b);
 for(int j=0;j<4;j++)z[j]=x[j]+dt*b[j]; f(z,I,c);
 for(int j=0;j<4;j++)out[j]=x[j]+dt/6.*(first[j]+2*a[j]+2*b[j]+c[j]);
}
int main(){
 double mid[3]={vm,vh,vn},slope[3]={dvm,dvh,dvn},t0[3]={tm0,th0,tn0},t1[3]={tm1,th1,tn1};
 for(int j=0;j<3;j++){double q=std::tanh(-mid[j]/slope[j]);tau[j]=t0[j]+t1[j]*(1-q*q);}
 for(int j=0;j<4;j++)y[j]=0.;
 k1[0]=(gl*(vl-y[0])+gna*y[1]*y[1]*y[1]*y[2]*(vna-y[0])+gk*y[3]*y[3]*y[3]*y[3]*(vk-y[0]))/C;
 for(int j=1;j<4;j++){double v=mid[j-1],d=slope[j-1];k1[j]=(inf(0.,v,d)-y[j])/tau[j-1];}
 FILE *fp=std::fopen("phase_trajectory.csv","w"); if(!fp){std::perror("phase_trajectory.csv");return 1;}
 std::fprintf(fp,"time_ms,applied_current_nA,V_mV,m,h,n\n");
 const int nsteps=50000;
 for(int i=-nsteps;i<=nsteps;i++){
  double t=dt*i,I=(t>0.&&t<window)?stim:0.,z[4];rk4(y,k1,I,z);
  for(int j=0;j<4;j++)y[j]=z[j];
  std::fprintf(fp,"%.8f,%.8f,%.10f,%.10f,%.10f,%.10f\n",t+dt,I,y[0],y[1],y[2],y[3]);
  f(y,I,k1);
 }
 std::fclose(fp);return 0;
}