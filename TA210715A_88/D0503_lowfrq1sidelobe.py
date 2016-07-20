# -*- coding: utf-8 -*-
"""
Created on Tue May 17 20:49:11 2016

@author: thomasaref
"""


from TA88_fundamental import TA88_Lyzer, TA88_Read
from taref.physics.fitting_functions import lorentzian

a=TA88_Lyzer( on_res_ind=256, VNA_name="RS VNA",
              rd_hdf=TA88_Read(main_file="Data_0503/S1A4_lowfrq_trans_1st_sidelobe.hdf5"),
            #fit_func=lorentzian,# p_guess=[5e6,4.32e9, 3e-7, 3e-6], #[0.2,2.3, 3e-7, 7.5e-7],
            #offset=-0.03,
            fit_indices=[range(111, 570)]) #33, 70
a.filt.center=22
a.filt.halfwidth=10
a.fitter.fit_type="lorentzian"
a.fitter.gamma=0.01
a.flux_axis_type="flux"
a.end_skip=10
a.read_data()


if __name__=="__main__":
    a.filter_type="FFT"
    pl=a.magabs_colormesh()
    a.filter_type="Fit"
    a.magabs_colormesh(pl=pl)
    a.ifft_plot()

    #line(a.frequency, a.ls_f)[0].show()
    a.widths_plot()
    a.center_plot()
    a.heights_plot()
    a.background_plot().show()
    #pl=a.magabs_colormesh()#magabs_colormesh3(s3a4_wg)
    pl=a.hann_ifft_plot()
    #pl=a.ifft_plot()
    #a.filt_compare(a.on_res_ind)
    #filt=filt_prep(601, s3a4_wg.filt_start_ind, s3a4_wg.filt_end_ind)
    #line(filt*0.001, plotter=pl)
    #colormesh(s3a4_wg.MagAbsFilt)#, plotter="magabsfilt_{}".format(self.name))

    a.magabsfilt_colormesh().show()
