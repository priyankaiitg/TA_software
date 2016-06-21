# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 01:07:15 2016

@author: thomasaref
"""

from taref.core.log import log_debug
from taref.physics.fundamentals import sinc_sq, pi, eps0
from taref.physics.legendre import lgf, lgf_arr#, lgf_fixed
from taref.core.agent import Agent
from atom.api import Float, Int, Enum, Value, Property, Typed
from taref.core.api import private_property, get_tag, SProperty, log_func, t_property, s_property, sqze, Complex, Array, tag_callable
from numpy import arange, linspace, sqrt, imag, real, sin, cos, interp, array, absolute, exp, ones, log10, fft, float64, int64, cumsum
#from matplotlib.pyplot import plot, show, xlabel, ylabel, title, xlim, ylim, legend
from scipy.signal import hilbert
from taref.plotter.api import line, Plotter, scatter
from taref.physics.surface_charge import Rho


class IDT(Rho):
    """Theoretical description of IDT"""
    base_name="IDT"
    #main_params=["K2", "Dvv"] #"ft", "f0", "lbda0", "a", "g", "eta", "Np", "ef", "W", "Ct",
    #            "material", "Dvv", "K2", "vf", "epsinf"]

    def _observe_ft(self, change):
        if change["type"]=="update":
            self.ft_mult=None
            self.Ga0_mult=None
            self.Ct_mult=None
            self.mu_mult=None

    @t_property(dictify={"single" : 1.694**2, "double" : (1.247*sqrt(2))**2}) #{"single":2.87, "double":3.11}
    def Ga0_mult(self, ft):
        return get_tag(self, "Ga0_mult", "dictify")[ft]

    @t_property(dictify={ "single" : 1.0, "double" : sqrt(2)})
    def Ct_mult(self, ft):
        return get_tag(self, "Ct_mult", "dictify")[ft]

    @t_property()
    def mu_mult(self, ft):
        return {"single" : 1.694, "double" : 1.247}[ft]

    couple_mult=SProperty().tag(desc="single: 0.71775. double: 0.54995")
    @couple_mult.getter
    def _get_couple_mult(self, Ga0_mult, Ct_mult):
        return Ga0_mult/(4*Ct_mult)

    Np=Float(9).tag(desc="\# of finger pairs", low=0.5, tex_str=r"$N_p$", label="\# of finger pairs")

    ef=Int(0).tag(desc="for edge effect compensation",
                    label="\# of extra fingers", low=0)

    W=Float(25.0e-6).tag(desc="height of finger.", unit="um")

    C=SProperty().tag(unit="fF", desc="Total capacitance of IDT", reference="Morgan page 16/145")
    @C.getter
    def _get_C(self, epsinf, Ct_mult, W, Np):
        """Morgan page 16, 145"""
        return Ct_mult*W*epsinf*Np

    @C.setter
    def _get_epsinf(self, C, Ct_mult, W, Np):
        """reversing capacitance to extract eps infinity"""
        return C/(Ct_mult*W*Np)

    K2=SProperty().tag(desc="coupling strength", unit="%", tex_str=r"K$^2$", expression=r"K$^2=2\Delta v/v$")
    @K2.getter
    def _get_K2(self, Dvv):
        r"""Coupling strength. K$^2=2\Delta v/v$"""
        return Dvv*2.0

    @K2.setter
    def _get_Dvv(self, K2):
        """other coupling strength. free speed minus metal speed all over free speed"""
        return K2/2.0

    Ga0=SProperty().tag(desc="Conductance at center frequency")
    @Ga0.getter
    def _get_Ga0(self, Ga0_mult, f0, epsinf, W, Dvv, Np):
        """Ga0 from morgan"""
        return Ga0_mult*2*pi*f0*epsinf*W*Dvv*(Np**2)

    Ga0div2C=SProperty()
    @Ga0div2C.getter
    def _get_Ga0div2C(self, couple_mult, f0, K2, Np):
        """coupling at center frequency, in Hz (2 pi removed)"""
        return couple_mult*f0*K2*Np

    X=SProperty()
    @X.getter
    def _get_X(self, Np, f, f0):
        """standard frequency dependence"""
        return Np*pi*(f-f0)/f0

    couple_type=Enum("sinc^2", "giant atom", "df giant atom", "full expr", "full sum")

    coupling=SProperty().tag(desc="""Coupling adjusted by sinc sq""", unit="GHz", tex_str=r"$G_f$")
    @coupling.getter
    def _get_coupling(self, f, couple_mult, f0, K2, Np, eta, ft_mult, N_legendre, Ct_mult):
        if self.couple_type=="full sum":
            return self.get_fix("coupling", f)
        gX=self._get_X(Np=Np, f=f, f0=f0)
        if self.couple_type=="full expr":
            ele_f=self._get_alpha(f, f0, eta, ft_mult, N_legendre)
            return f0*K2*Np/(4*Ct_mult)*(ele_f*2*cos(pi*f/(4*f0))*(1.0/Np)*sin(gX)/sin(gX/Np))**2
        gamma0=self._get_Ga0div2C(couple_mult=couple_mult, f0=f0, K2=K2, Np=Np)
        if self.couple_type=="giant atom":
            return gamma0*(1.0/Np*sin(gX)/sin(gX/Np))**2
        elif self.couple_type=="df giant atom":
            return gamma0*(sqrt(2.0)*cos(pi*f/(4*f0))*1.0/Np*sin(gX)/sin(gX/Np))**2
        return gamma0*(sin(gX)/gX)**2.0

    def fixed_reset(self):
        """resets fixed properties in proper order"""
        super(IDT, self).fixed_reset()
        self.get_member("fixed_X").reset(self)
        self.get_member("fixed_Asum").reset(self)
        self.get_member("fixed_coupling").reset(self)
        self.get_member("fixed_Lamb_shift").reset(self)
        self.get_member("fixed_Ga").reset(self)
        self.get_member("fixed_Ba").reset(self)
        self.get_member("fixed_S11").reset(self)

    @private_property
    def fixed_X(self):
        return self._get_X(f=self.fixed_freq)

    @private_property
    def fixed_w(self):
        return 2.0*pi*self.fixed_freq

    def get_fix(self, name, f):
        return interp(f, self.fixed_freq, getattr(self, "fixed_"+name))

    @private_property
    def fixed_coupling(self):
        gamma0=self.f0*self.K2*self.Np/(4*self.Ct_mult)
        if self.couple_type=="full sum":
            return gamma0*(self.fixed_alpha)**2*absolute(self.fixed_Asum)**2
        f, X, Np, f0=self.fixed_freq, self.fixed_X, self.Np, self.f0
        if self.couple_type=="full expr":
            ele_f=self.fixed_alpha
            return gamma0*(ele_f*2*cos(pi*f/(4*f0))*(1.0/Np)*sin(X)/sin(X/Np))**2
        if self.couple_type=="giant atom":
            return self.Ga0div2C*(1.0/Np*sin(X)/sin(X/Np))**2
        elif self.couple_type=="df giant atom":
            return self.Ga0div2C*(sqrt(2.0)*cos(pi*f/(4*f0))*1.0/Np*sin(X)/sin(X/Np))**2
        return self.Ga0div2C*(sin(X)/X)**2.0

    dloss1=Float(0.0)
    dloss2=Float(0.0)

    #propagation_loss=SProperty()
    #@propagation_loss.getter
    #def _get_propagation_loss(self, f, f0, dloss1, dloss2):
    #    return exp(-f/f0*dloss1-dloss2*(f/f0)**2)

    @t_property(sub=True)
    def polarity(self, Np, ft):
        if ft=="single":
            return arange(int(Np))+0.5
        return array(sqze(zip(arange(Np)+0.5, arange(Np)+0.75)))

    @t_property(sub=True)
    def g_arr(self, polarity):
        return ones(len(polarity))

    Asum=SProperty().tag(sub=True)
    @Asum.getter
    def _get_Asum(self, f, f0, Np, dloss1, dloss2, g_arr, polarity):
        return 1.0/Np*array([sum([g_arr[i]*exp(2.0j*pi*frq/f0*n-frq/f0*dloss1*n-n*dloss2*(frq/f0)**2)
               for i, n in enumerate(polarity)]) for frq in f])

    @private_property
    def fixed_Asum(self):
        return self._get_Asum(f=self.fixed_freq)

    @private_property
    def fixed_Lamb_shift(self):
        if self.Lamb_shift_type=="formula":
            X, Np=self.fixed_X, self.Np
            if self.couple_type=="sinc^2":
                return -self.Ga0div2C*(sin(2.0*X)-2.0*X)/(2.0*X**2.0)
            if self.couple_type=="giant atom":
                return self.Ga0div2C*(1.0/Np)**2*2*(Np*sin(2*X/Np)-sin(2*X))/(2*(1-cos(2*X/Np)))
        return imag(hilbert(self.fixed_coupling))

    max_coupling=SProperty().tag(desc="""Coupling at IDT center frequency""", unit="GHz",
                     label="Coupling at center frequency", tex_str=r"$\gamma_{f0}$")
    @max_coupling.getter
    def _get_max_coupling(self, couple_mult, f0, K2, Np, eta, ft_mult, N_legendre, Ct_mult):
        return self._get_coupling(f=f0+0.0001, couple_mult=couple_mult, f0=f0,
                K2=K2, Np=Np, eta=eta, ft_mult=ft_mult, N_legendre=N_legendre, Ct_mult=Ct_mult)

    Lamb_shift_type=Enum("hilbert", "formula")

    Lamb_shift=SProperty().tag(desc="""Lamb shift""", unit="GHz", tex_str=r"$G_f$")
    @Lamb_shift.getter
    def _get_Lamb_shift(self, f, couple_mult, f0, K2, Np, eta, ft_mult, N_legendre, Ct_mult):
        """returns Lamb shift"""
        if self.Lamb_shift_type=="formula":
            gamma0=self._get_Ga0div2C(couple_mult=couple_mult, f0=f0, K2=K2, Np=Np)
            gX=self._get_X(Np=Np, f=f, f0=f0)
            if self.couple_type=="sinc^2":
                return -gamma0*(sin(2.0*gX)-2.0*gX)/(2.0*gX**2.0)
            if self.couple_type=="giant atom":
                return gamma0*(1.0/Np)**2*2*(Np*sin(2*gX/Np)-sin(2*gX))/(2*(1-cos(2*gX/Np)))
        if self.couple_type=="full sum":
            return self.get_fix("Lamb_shift", f)
        yp=imag(hilbert(self._get_coupling(f=self.fixed_freq, couple_mult=couple_mult, f0=f0,
                K2=K2, Np=Np, eta=eta, ft_mult=ft_mult, N_legendre=N_legendre, Ct_mult=Ct_mult)))
        return interp(f, self.fixed_freq, yp)

    ZL=Float(50.0)
    ZL_imag=Float(0.0)
    GL=Float(1/50.0)
    dL=Float(0.0)
    YL=Float(1.0/50.0)

    S_type=Enum("simple", "RAM")

    @private_property
    def fixed_S(self):
        P=self.fixed_P
        return self.PtoS(*P, YL=self.YL)


    def PtoS(self, P11, P12, P13,
             P21, P22, P23,
             P31, P32, P33, YL=1/50.0):
         YLplusP33=YL+P33
         sqrtYL=sqrt(YL)
         S11=P11-P13*P31/YLplusP33
         S12=P12-P13*P32/YLplusP33
         S13=2.0*sqrtYL*P13/YLplusP33
         S21=P21-P23*P31/YLplusP33
         S22=P22-P23*P32/YLplusP33
         S23=-P31*sqrtYL*P23/YLplusP33
         S31=-P31*sqrtYL/YLplusP33
         S32=-P32*sqrtYL/YL+P33
         S33=(YL-P33)/YLplusP33
         return (S11, S12, S13,
                 S21, S22, S23,
                 S31, S32, S33)


    rs=Complex()

    ts=SProperty()
    @ts.getter
    def _get_ts(self, rs):
        return sqrt(1-absolute(rs)**2)

    Gs=SProperty().tag(desc="Inglebrinsten's approximation of Gamma_s (Morgan)")
    @Gs.getter
    def _get_Gs(self, Dvv, epsinf):
        return Dvv/epsinf

    RAM_P=SProperty().tag(sub=True)
    @RAM_P.getter
    def _get_RAM_P(self, f, f0, W, rs, Np, vf, Dvv, epsinf, alpha):
        """returns A^N, the matrix representing mechanical reflections and transmission"""
        rho=alpha*epsinf
        N=2*Np+2*(Np+1)
        w=2*pi*f
        w0=2.0*pi*f0
        lbda0=vf/f0
        p=lbda0/4.0 #2*80.0e-9
        k=2*pi*f/vf
        ts = sqrt(1-absolute(rs)**2)
        A = 1.0/ts*matrix([[exp(-1.0j*k*p),       rs      ],
                           [-rs,             exp(1.0j*k*p)]])#.astype(complex128)
        AN=A**N
        AN11, AN12, AN21, AN22= AN[0,0], AN[1,0], AN[0,1], AN[1,1]

        P11=-AN21/AN22
        P21=AN11-AN12*AN21/AN22
        P12=1.0/AN22
        P22=AN12/AN22
        D = -1.0j*rho*sqrt(w*W*Gs/2.0)
        B = matrix([(1.0-rs/ts+1.0/ts)*exp(-1.0j*k*p/2.0), (1.0+rs/ts+1.0/ts)*exp(1.0j*k*p/2.0)])

        P32=D*B*(A**2+A**3)*inv(eye(2)-A**4)*(eye(2)-A**(2*N_p+2))*matrix([[0],
                                                                          [1.0/AN[1,1]]])[0] #geometric series
        P13=P23=-P31/2.0=-P32/2.0
        Ga=2.0*absolute(P13)**2
        Ba=hilbert(Ga)
        P33=Ga+1.0j*Ba+1.0j*w*C
        return (P11, P12, P13,
                P21, P22, P23,
                P31, P32, P33)

    @private_property
    def
    S11=SProperty()
    @S11.getter
    def _get_S11(self, f, couple_mult, f0, K2, Np, C, ZL):
        Ga=self._get_Ga(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C)
        Ba=self._get_Ba(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C)
        w=2*pi*f
        return Ga/(Ga+1j*Ba+1j*w*C+1.0/ZL)

    @private_property
    def fixed_S11(self):
        f, Ga, Ba=self.fixed_freq, self.fixed_Ga, self.fixed_Ba
        w=2*pi*f
        C, ZL=self.C, self.ZL
        return Ga/(Ga+1j*Ba+1j*w*C+1.0/ZL)

    S13=SProperty()
    @S13.getter
    def _get_S13(self, f, couple_mult, f0, K2, Np, C, ZL, ZL_imag, GL, dL, eta):
        Ga=self._get_Ga(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C, eta=eta)
        Ba=self._get_Ba(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C, eta=eta)
        w=2*pi*f
        return 1j*sqrt(2*Ga*GL)/(Ga+1j*Ba+1j*w*C-1j/w*dL+1.0/ZL)

    S33=SProperty()
    @S33.getter
    def _get_S33(self, f, couple_mult, f0, K2, Np, C, ZL, ZL_imag, GL, dL):
        Ga=self._get_Ga(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C)
        Ba=self._get_Ba(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, C=C)
        w=2*pi*f
        return (Ga+1j*Ba+1j*w*C-1j/w*dL-1.0/ZL)/(Ga+1j*Ba+1j*w*C-1j/w*dL+1.0/ZL)

    Ga=SProperty().tag(desc="Ga adjusted for frequency f")
    @Ga.getter
    def _get_Ga(self, f, couple_mult, f0, K2, Np, C, eta):
        return self._get_coupling(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, eta=eta)*2*C*2*pi
    @private_property
    def fixed_Ga(self):
        return self._get_Ga(f=self.fixed_freq)

    Ba=SProperty()
    @Ba.getter
    def _get_Ba(self, f, couple_mult, f0, K2, Np, C, eta):
        return -self._get_Lamb_shift(f=f, couple_mult=couple_mult, f0=f0, K2=K2, Np=Np, eta=eta)*2*C*2*pi
    @private_property
    def fixed_Ba(self):
        return self._get_Ba(f=self.fixed_freq)

    @private_property
    def view_window2(self):
        from enaml import imports
        with imports():
            from taref.saw.idt_e import IDT_View
        return IDT_View(idt=self)

#from functools import wraps
#
#class idt_plot(tag_callable):
#    def __call__(self, func):
#        @wraps(func)
#        def new_plot(self, *args, **kwargs):
#            self.idt=kwargs.pop("idt", self.idt)
#            if self.idt is None:
#                self.idt=IDT()
#            return func(self, *args, **kwargs)
#        return super(idt_plot, self).__call__(new_plot)

def idt_process(kwargs):
    idt=kwargs.pop("idt", None)
    if idt is None:
        return IDT()
    return idt



def element_factor_plot(pl="element_factor", **kwargs):
    idt=idt_process(kwargs)
    idt.ft="single"
    print "start plot"
    pl, pf=line(idt.fixed_freq/idt.f0, idt.fixed_alpha/idt.fixed_freq*idt.f0, plotter=pl, plot_name="single", color="blue", label="single finger", **kwargs)
    print "finish plot"
    #idt.ft="double"
    #idt.fixed_reset()
    #pl= line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="double", color="red", label="double finger", linestyle="dashed")[0]
    pl.xlabel="frequency/center frequency"
    pl.ylabel="element factor"
    #pl.set
    pl.legend()
    return pl



def surface_charge_plot(pl="surface charge", **kwargs):
    idt=idt_process(kwargs)
    idt.ft="single"
    charge=real(fft.fftshift(fft.ifft(idt.fixed_alpha))).astype(float64)

    #x=linspace()
    x=linspace(-idt.N_fixed/2+.001, idt.N_fixed/2+0.0, idt.N_fixed)/800.0
    print charge.shape, x.shape
    pl, pf=line(x, charge, plotter=pl, plot_name="single", color="blue", label="single finger", **kwargs)
    charge=real(fft.fftshift(fft.ifft(idt.fixed_alpha/idt.fixed_freq*idt.f0))).astype(float64)
    pl, pf=line(x, charge, plotter=pl, plot_name="singled", color="red", label="single finger2", **kwargs)

    #def charge_f(xin):
    #    return interp(xin, x, charge/absolute(x-xin))

    #x=arange(len(idt.fixed_alpha))
    xprime=linspace(-0.02000001, 0.02, 200) #[0.01, 1.01] #range(10)
    print "trapz"
    #print array([quad(charge_f, x.min(), x.max())])
    #for xp in xprime:
    #line(trapz(charge/absolute(x-xprime), x))
    #dx=x[1]-x[0]
    #line(xprime, array([sum(charge*dx/absolute(x-xp)) for xp in xprime]))

    line(xprime, array([trapz(charge/absolute(x-xp), x) for xp in xprime]))
    #idt.ft="double"
    #idt.fixed_reset()
    #pl= line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="double", color="red", label="double finger", linestyle="dashed")[0]
    pl.xlabel="frequency/center frequency"
    pl.ylabel="element factor"
    #pl.legend()
    return pl

def surface_charge_plot2(pl="surface charge2", **kwargs):
    idt=idt_process(kwargs)
    idt.ft="single"
    charge=fft.fftshift(fft.ifft(idt.fixed_alpha))

    pl, pf=line( charge[:-400]+charge[400:], plotter=pl, plot_name="single", color="blue", label="single finger", **kwargs)


    #idt.ft="double"
    #idt.fixed_reset()
    #pl= line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="double", color="red", label="double finger", linestyle="dashed")[0]
    pl.xlabel="frequency/center frequency"
    pl.ylabel="element factor"
    #pl.legend()
    return pl

element_factor_plot()#.show()
surface_charge_plot().show()
surface_charge_plot2().show()

def metallization_plot(pl="metalization", **kwargs):
    idt=idt_process(kwargs)
    idt.eta=0.5
    idt.ft="single"
    idt.N_legendre=1000

    idt.fixed_reset()
    pl=line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="0.5", color="blue", label="0.5", **kwargs)[0]
    idt.eta=0.75
    idt.fixed_reset()
    line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="0.6", color="red", label="0.6", **kwargs)
    idt.eta=0.25
    idt.fixed_reset()
    line(idt.fixed_freq/idt.f0, idt.fixed_alpha, plotter=pl, plot_name="0.4", color="green", label="0.4", **kwargs)
    idt.eta=0.5
    return pl
#metallization_plot().show()

def metallization_couple(pl="metalization", **kwargs):
    idt=idt_process(kwargs)
    frq=linspace(0e9, 10e9, 10000)
    idt.eta=0.5
    #idt.ft="single"
    idt.couple_type="full sum"
    idt.fixed_reset()
    pl=line(frq/idt.f0, idt.get_fix("coupling", frq), plotter=pl, plot_name="0.5", color="blue", linewidth=0.3, label="0.5", **kwargs)[0]
    idt.eta=0.6
    idt.fixed_reset()
    line(frq/idt.f0, idt.get_fix("coupling", frq), plotter=pl, plot_name="0.6", color="red", linewidth=0.3, label="0.6", **kwargs)
    idt.eta=0.4
    idt.fixed_reset()
    line(frq/idt.f0, idt.get_fix("coupling", frq), plotter=pl, plot_name="0.4", color="green", linewidth=0.3, label="0.4", **kwargs)
    idt.eta=0.5
    return pl
metallization_couple()#.show()
def metallization_Lamb(pl="metalization", **kwargs):
    idt=idt_process(kwargs)
    frq=linspace(0e9, 10e9, 10000)
    idt.eta=0.5
    #idt.ft="single"
    idt.couple_type="full sum"
    idt.fixed_reset()
    pl=line(frq/idt.f0, idt.get_fix("Lamb_shift", frq), plotter=pl, plot_name="0.5", color="blue", linewidth=0.3, label="0.5", **kwargs)[0]
    idt.eta=0.6
    idt.fixed_reset()
    #line(idt.fixed_freq/idt.f0, idt.fixed_Lamb_shift/idt.max_coupling, plotter=pl, linewidth=0.3, color="purple")
    line(frq/idt.f0, idt.get_fix("Lamb_shift", frq), plotter=pl, plot_name="0.6", color="red", linewidth=0.3, label="0.6", **kwargs)
    idt.eta=0.4
    idt.fixed_reset()
    line(frq/idt.f0, idt.get_fix("Lamb_shift", frq), plotter=pl, plot_name="0.4", color="green", linewidth=0.3, label="0.4", **kwargs)
    idt.eta=0.5
    return pl
metallization_Lamb().show()

def center_coupling_vs_eta(pl="f0_vs_eta", **kwargs):
    idt=idt_process(kwargs)
    eta=linspace(0.0, 1.0, 100)
    idt.ft="single"
    #idt.N_legendre=1000
    alpha=idt._get_alpha(f=idt.f0, eta=eta, N_legendre=1000)
    pl=line(eta, alpha, plotter=pl)[0]
    alpha=idt._get_alpha(f=3*idt.f0, eta=eta, N_legendre=1000)
    line(eta, alpha, plotter=pl, color="red")
    alpha=idt._get_alpha(f=5*idt.f0, eta=eta, N_legendre=1000)
    line(eta, alpha, plotter=pl, color="green")
    return pl #line(eta, idt._get_alpha(f=3*idt.f0, eta=eta))[0]

center_coupling_vs_eta().show()

def couple_comparison(pl="couple_compare", **kwargs):
    idt=idt_process(kwargs)
    frq=linspace(0e9, 10e9, 10000)
    idt.couple_type="sinc^2"
    pl, pf=line(frq/idt.f0, 10*log10(idt._get_coupling(frq)/idt.max_coupling), plotter=pl, linewidth=0.3, label=idt.couple_type, **kwargs)
    idt.couple_type="giant atom"
    line(frq/idt.f0, 10*log10(idt._get_coupling(frq)/idt.max_coupling), plotter=pl, color="red", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="df giant atom"
    line(frq/idt.f0, 10*log10(idt._get_coupling(frq)/idt.max_coupling), plotter=pl, color="green", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full expr"
    line(frq/idt.f0, 10*log10(idt._get_coupling(frq)/idt.max_coupling), plotter=pl, color="black", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full sum"
    line(frq/idt.f0, 10*log10(idt._get_coupling(frq)/idt.max_coupling), plotter=pl, color="purple", linewidth=0.3, label=idt.couple_type)
    pl.xlabel="frequency/center frequency"
    pl.ylabel="coupling/max coupling (dB)"
    pl.set_ylim(-30, 1.0)
    pl.legend()
    return pl

def fix_couple_comparison(pl="fix couple", **kwargs):
    idt=idt_process(kwargs)
    idt.couple_type="sinc^2"
    idt.fixed_reset()
    frq=linspace(0e9, 10e9, 10000)
    pl, pf=line(frq/idt.f0, 10*log10(idt.get_fix("coupling", frq)/idt.max_coupling), plotter=pl, linewidth=0.3, label=idt.couple_type, **kwargs)
    idt.couple_type="giant atom"
    idt.fixed_reset()
    line(frq/idt.f0, 10*log10(idt.get_fix("coupling", frq)/idt.max_coupling), plotter=pl, color="red", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="df giant atom"
    idt.fixed_reset()
    line(frq/idt.f0, 10*log10(idt.get_fix("coupling", frq)/idt.max_coupling), plotter=pl, color="green", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full expr"
    idt.fixed_reset()
    line(frq/idt.f0, 10*log10(idt.get_fix("coupling", frq)/idt.max_coupling), plotter=pl, color="black", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full sum"
    idt.fixed_reset()
    line(frq/idt.f0, 10*log10(idt.get_fix("coupling", frq)/idt.max_coupling), plotter=pl, color="purple", linewidth=0.3, label=idt.couple_type)
    pl.xlabel="frequency/center frequency"
    pl.ylabel="coupling/max coupling (dB)"
    pl.set_ylim(-30, 1.0)
    pl.legend()
    return pl

def Lamb_shift_comparison(pl="ls_comp", **kwargs):
    idt=idt_process(kwargs)
    idt.Lamb_shift_type="formula"
    idt.couple_type="sinc^2"
    #idt=IDT(Lamb_shift_type="formula", couple_type="sinc^2")
    frq=linspace(0e9, 10e9, 10000)
    pl, pf=line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, linewidth=0.3, label="sinc^2", **kwargs)
    #a=IDT(Lamb_shift_type="formula", couple_type="giant atom")
    idt.couple_type="giant atom"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="red", linewidth=0.3, label=idt.couple_type)
    #a=IDT(Lamb_shift_type="hilbert", couple_type="sinc^2")
    idt.Lamb_shift_type="hilbert"
    idt.couple_type="sinc^2"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="green", linewidth=0.3, label="h(sinc^2)")
    #a=IDT(Lamb_shift_type="hilbert", couple_type="giant atom")
    idt.couple_type="giant atom"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="black", linewidth=0.3, label="h(giant atom)")
    pl.xlabel="frequency/center frequency"
    pl.ylabel="Lamb shift/max coupling"
    pl.set_ylim(-1, 0.8)
    pl.legend()

    #line(frq, a._get_full_Lamb_shift(frq)/a.max_coupling, plotter=pl, color="black", linewidth=0.3)
    return pl

def Lamb_shift_check(pl="ls_check", **kwargs):
    idt=idt_process(kwargs)
    idt.Lamb_shift_type="formula"
    idt.couple_type="sinc^2"
    frq=linspace(0e9, 10e9, 10000)
    pl, pf=line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, linewidth=0.3, label=idt.couple_type, **kwargs)
    idt.couple_type="giant atom"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="red", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="df giant atom"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="green", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full expr"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="black", linewidth=0.3, label=idt.couple_type)
    idt.couple_type="full sum"
    line(frq/idt.f0, idt._get_Lamb_shift(frq)/idt.max_coupling, plotter=pl, color="purple", linewidth=0.3, label=idt.couple_type)
    pl.xlabel="frequency/center frequency"
    pl.ylabel="Lamb shift/max coupling (dB)"
    pl.set_ylim(-1.0, 1.0)
    pl.legend()

    #line(frq, a._get_full_Lamb_shift(frq)/a.max_coupling, plotter=pl, color="black", linewidth=0.3)
    return pl

def formula_comparison(pl=None, **kwargs):
    a=IDT()
    frq=linspace(3e9, 7e9, 10000)
    print a._get_coupling(frq)
    print a.max_coupling
    pl, pf=line(frq, a._get_coupling(frq)/a.max_coupling, plotter=pl, linewidth=1.0, **kwargs)
    line(frq, a._get_Lamb_shift(frq)/a.max_coupling, plotter=pl, color="red", linewidth=1.0)
    #line(frq, coup, color="purple", plotter=pl, linewidth=0.3)
    line(frq, a._get_full_coupling(frq)/a.max_coupling, plotter=pl, color="green", linewidth=0.3)
    line(frq, a._get_full_Lamb_shift(frq)/a.max_coupling, plotter=pl, color="black", linewidth=0.3)
    return pl

idt=IDT()
element_factor_plot(idt=idt)#.show()

Lamb_shift_comparison(idt=idt)

couple_comparison(idt=idt)#.show()

fix_couple_comparison(idt=idt)#.show()

Lamb_shift_check(idt=idt).show()

#formula_comparison()#.show()

#element_factor_plot(idt=idt).show()
if __name__=="__main__":
    #a=IDT(dloss1=0.0, dloss2=0.0, eta=0.6, ft="double")
    a=IDT(material='LiNbYZ',
          ft="double",
          a=80.0e-9, #f0=5.35e9,
          Np=9,
          #Rn=3780.0, #(3570.0+4000.0)/2.0, Ejmax=h*44.0e9,
          W=25.0e-6,
          eta=0.5,)
          #flux_factor=0.515, #0.2945, #0.52,
          #voltage=1.21,
          #offset=-0.07)
    a.f=a.f0
    print a.fixed_polarity
    print a.alpha
    print a.fixed_element_factor
    print a._get_element_factor(a.f0)
    from scipy.signal import hilbert
    from numpy import imag, real, sin, cos, exp, array, absolute


    frq=linspace(1e9, 10e9, 10000)

    X=a._get_X(f=frq)
    Np=a.Np
    f0=a.f0

    if 0:
        def Asum(N, k1=0.0, k2=0.0):
            return array([sum([exp(2.0j*pi*f/f0*n-f/f0*k1-k2*(f/f0)**2) for n in range(N)]) for f in frq])

        def Asum2(M):
            return array([sum([exp(2j*pi*M*f/f0)*exp(2j*pi*f/f0*m) for m in range(-M, M+1)]) for f in frq])

        def Asum3(M, k=1.0):
            return array([sum([exp(2j*pi*f/f0*m) for m in range(-M, M+1)]) for f in frq])

        def Asum4(M):
            return array([sum([2*cos(2*pi*f/f0*m) for m in range(0, M+1)]) for f in frq])-1

        def Asum5(M, g=0.9, g2=1.0):
            return array([g*2*cos(2*pi*f/f0*M) for f in frq])+array([g2*2*cos(2*pi*f/f0*(M-1)) for f in frq])+Asum4(M-2)

        def Asum6(g=1.0):
            return array([(g*exp(-2j*pi*f/f0*4)+exp(-2j*pi*f/f0*3)+exp(-2j*pi*f/f0*2)+exp(-2j*pi*f/f0*1)+1.0
            +exp(2j*pi*f/f0*1)+exp(2j*pi*f/f0*2)+exp(2j*pi*f/f0*3)+g*exp(2j*pi*f/f0*4)) for f in frq])

        def Asum7(g=1.0):
            return array([(g+exp(2j*pi*f/f0*1)+exp(2j*pi*f/f0*2)+exp(2j*pi*f/f0*3)+exp(2j*pi*f/f0*4)
            +exp(2j*pi*f/f0*5)+exp(2j*pi*f/f0*6)+exp(2j*pi*f/f0*7)+g*exp(2j*pi*f/f0*8)) for f in frq])

        A=Asum(9, k1=0.05, k2=0.05)
        A2=Asum2(4)
        A3=Asum3(4)
        A4=Asum4(4)
        A5=Asum5(4, 1.2, 1.0)
        A6=Asum6(0.5)
        A7=Asum7(0.5)

        pl=Plotter()
        #line(frq/1e9, real(A), plotter=pl)
        #line(frq/1e9, imag(A), plotter=pl, color="red")

        #line(frq/1e9, real(A2), plotter=pl, color="green", linewidth=0.5)
        #line(frq/1e9, imag(A2), plotter=pl, color="black", linewidth=0.5)

        line(frq/1e9, sin(pi*9*frq/f0)/sin(pi*frq/f0), plotter=pl)

        line(frq/1e9, real(A3), plotter=pl, color="green", linewidth=0.5)
        line(frq/1e9, imag(A3), plotter=pl, color="black", linewidth=0.5)

        line(frq/1e9, A4, plotter=pl, color="red", linewidth=0.5)
        #line(frq/1e9, A5, plotter=pl, color="purple", linewidth=0.5)
        line(frq/1e9, real(A6), plotter=pl, color="darkgray", linewidth=0.5)
        line(frq/1e9, imag(A6), plotter=pl, color="darkgray", linewidth=0.5)

        #pl.show()
        pl=Plotter()

        line(frq/1e9, 1/81.0*absolute(A)**2, plotter=pl, color="black")
        #line(frq/1e9, 1/81.0*absolute(sin(pi*9*frq/f0)/sin(pi*frq/f0))**2, plotter=pl, color="green", linewidth=0.4)
        #line(frq/1e9, 1/81.0*absolute(A5)**2, plotter=pl, color="blue", linewidth=0.5)
        line(frq/1e9, 1/81.0*absolute(A6)**2, plotter=pl, color="red", linewidth=0.5)
        line(frq/1e9, 1/81.0*absolute(A7)**2, plotter=pl, color="purple", linewidth=0.5)

        #line(frq/1e9, 1/9.0*absolute(A6), plotter=pl, color="red", linewidth=0.5)

        #line(frq/1e9, 1/9.0*absolute(A7), plotter=pl, color="purple", linewidth=0.5)

        pl.show()

    frq=linspace(0, 40e9, 10000)

    X=a._get_X(f=frq)
    Np=a.Np
    f0=a.f0

    #coup=(sqrt(2)*cos(pi*frq/(4*f0))*(1.0/Np)*sin(X)/sin(X/Np))**2
    coup=(sin(X)/X)**2

    #coup=(1.0/Np*sin(X)/sin(X/Np))**2


    element_factor_plot(a)
    pl=Plotter()
    line(frq, a._get_coupling(frq)/a.max_coupling, plotter=pl, linewidth=1.0)
    line(frq, a._get_Lamb_shift(frq)/a.max_coupling, plotter=pl, color="red", linewidth=1.0)
    line(frq, coup, color="purple", plotter=pl, linewidth=0.3)
    line(frq, a._get_full_coupling(frq)/a.max_coupling/1.247**2/2, plotter=pl, color="green", linewidth=0.3)
    line(frq, a._get_full_Lamb_shift(frq)/a.max_coupling/1.247**2/2, plotter=pl, color="black", linewidth=0.3)

    #hb=hilbert(coup) #a._get_coupling(frq))
    #line(frq, real(hb), plotter=pl, color="green", linewidth=0.3)
    #line(frq, imag(hb), plotter=pl, color="black", linewidth=0.3)
    #Baa= (1+cos(X/(4*Np)))*(1.0/Np)**2*2*(Np*sin(2*X/Np)-sin(2*X))/(2*(1-cos(2*X/Np)))
    Baa=-(sin(2.0*X)-2.0*X)/(2.0*X**2)
    #Baa= (1.0/Np)**2*2*(Np*sin(2*X/Np)-sin(2*X))/(2*(1-cos(2*X/Np)))
    line(frq, Baa, plotter=pl, color="cyan", linewidth=0.3)

    pl.show()

    b=IDT(ft="single")
    a.ft_mult=5
    print a.mu_mult, a.ft_mult, b.mu_mult, b.ft_mult
    print a.couple_mult, b.couple_mult
    a.ft="single"
    a.ft_mult=None
    print a.mu_mult, a.ft_mult, b.mu_mult, b.ft_mult
    print a.couple_mult, b.couple_mult

    print a.epsinf, a.C
    a.epsinf=4e-10
    print a.C
    a.C=7.1e-14
    print a.epsinf, a.C

    print a._get_C(W=35)



    #log_debug(a.K2, b.K2)
    #a.Dvv=5
    #a.K2=4
    #for name in a.all_params:
    #    print name, getattr(a, name)
    #a.a=90e-9
    #for name in a.all_params:
    #    print name, getattr(a, name)

    #print a._get_Dvv(4)
    #print a.K2_f(2)
    #log_debug(a.get_member("K2").fget.fset_list)
    #log_debug(a.get_member("K2").fset(a, 3))
    #log_debug(a.get_member("K2").fset)

    #print a.K2, b.K2
#    for param in a.all_params:
#        print get_tag(a, param, "unit")
        #print a.call_func("eta", a=0.2e-6, g=0.8e-6)#, vf=array([500.0, 600.0]), lbda0=array([0.5e-6, 0.6e-6]))
        #a.plot_data("f0", lbda0=linspace(0.1e-6, 1.0e-6, 10000))
        #print a.get_tag("lbda0", "unit_factor")
    a.show()
    if 0:
        print a.K2, a.Dvv
        #print dir(a.get_member("K2").fget.fset)
        a.K2=5
        a.Dvv=5
        print a.K2
        shower(a)
        #print a.K2, a.Dvv
        #print a.K2, a.Dvv


    if 0:
        print a.property_dict
        print a.get_member("p").fget()#.func_code.co_varnames#(a, 1, 1)
        #print a.p()
        #a.eta=0.6
        print a.p
        a.a=5e-6
        print a.p
        show(a)
        #a.get_member("lbda0").setter(a.set_func("lbda0"))
        #a.lbda0=1.0e-6

    if 0:
        print a.f0
        print a.a, a.f0
        a.a=0.5e-6
        print a.eta, a.a, a.g, a.f0
        a.eta=0.1
        print a.eta, a.a, a.g
        a.g=0.5e-6
        print a.eta, a.a, a.g
        print a.lbda0, a.f0

        print a.Ga_f