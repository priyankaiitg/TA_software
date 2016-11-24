# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 12:54:58 2016

@author: thomasaref
"""
from taref.core.log import log_debug
from matplotlib import use#('Agg')
use('Agg')

from taref.plotter.plotter_backbone import plot_observe, PlotMaster, simple_set
from atom.api import Bool, Unicode, Float, Enum, Int, observe, cached_property#, Typed

from taref.core.agent import Operative
from enaml import imports
#from plot_format import line_plot, vline_plot, hline_plot, scatter_plot, colormesh, multiline_plot
from taref.core.api import private_property

#from matplotlib import rcParams
##print rcParams
##rcParams["figure.figsize"]=[9.0, 3.0]
#rcParams['axes.labelsize'] = 10
#rcParams['xtick.labelsize'] = 10
#rcParams['ytick.labelsize'] = 10
#rcParams['legend.fontsize'] = 10
#
#rcParams['xtick.major.width']=2
#rcParams['lines.linewidth']=2
#rcParams['xtick.major.size']=4
#rcParams['axes.linewidth']=2
#rcParams['ytick.major.width']=2
#rcParams['ytick.major.size']=4

#adjust matplotlib base cursor
from matplotlib.backend_bases import cursors
from matplotlib.backends import backend_qt4
from PySide.QtCore import Qt
backend_qt4.cursord[cursors.POINTER] = Qt.CursorShape.CrossCursor
from matplotlib import pyplot as plt

class Fig(PlotMaster, Operative):
    cid=Int().tag(private=True)

    base_name="plot"

    corner_label=Unicode()

    def add_label(self, txt):
        self.figure.text(0,1, txt)

    show_cross_cursor=Bool(False)
    xlabel_size=Float(10.0)

    ylabel_size=Float(10.0)

    x_min=Float()
    x_max=Float()
    y_min=Float()
    y_max=Float()

    def _default_x_min(self):
        first_plot=self.plot_dict.values()[0]
        return float(min(first_plot.xdata))

    def _default_x_max(self):
        first_plot=self.plot_dict.values()[0]
        return float(max(first_plot.xdata))

    def _default_y_min(self):
        first_plot=self.plot_dict.values()[0]
        return float(min(first_plot.ydata))

    def _default_y_max(self):
        first_plot=self.plot_dict.values()[0]
        return float(max(first_plot.ydata))

    auto_cs_xlim=Bool(True)
    auto_cs_ylim=Bool(True)

    cs_x_min=Float()
    cs_x_max=Float()
    cs_y_min=Float()
    cs_y_max=Float()

#    def _default_cs_x_min(self):
#        first_plot=self.plot_dict.values()[0]
#        return float(min(first_plot.xdata))
#
#    def _default_x_max(self):
#        first_plot=self.plot_dict.values()[0]
#        return float(max(first_plot.xdata))
#
#    def _default_y_min(self):
#        first_plot=self.plot_dict.values()[0]
#        return float(min(first_plot.ydata))
#
#    def _default_y_max(self):
#        first_plot=self.plot_dict.values()[0]
#        return float(max(first_plot.ydata))

    def _default_cs_x_min(self):
        return self.x_min

    def _default_cs_x_max(self):
        return self.x_max

    def _default_cs_y_min(self):
        return self.y_min

    def _default_cs_y_max(self):
        return self.y_max

    @observe("cs_x_min", "cs_x_max", "cs_y_min", "cs_y_max")
    def cs_lim_update(self, change):
        self.horiz_axe.set_ylim(self.cs_y_min, self.cs_y_max)
        self.vert_axe.set_xlim(self.cs_x_min, self.cs_x_max)
        #if self.horiz_fig.canvas!=None:
        #    self.horiz_fig.canvas.draw()
        #if self.vert_fig.canvas!=None:
        #    self.vert_fig.canvas.draw()

    transparent=Bool(True)
    save_type=Enum("png", "pdf", "ps", "eps","svg")

    auto_xlim=Bool(True)
    auto_ylim=Bool(True)
    auto_zlim=Bool(True)

    selected=Unicode()

    xlabel=Unicode()
    ylabel=Unicode()
    title=Unicode()
    xscale=Enum('linear', 'log')
    yscale=Enum('linear', 'log')

    def axes_set(self, param):
        simple_set(self.axes, self, param)

    @plot_observe("xscale", "yscale", "title", "xlabel", "ylabel", immediate_update=True)
    def axes_update(self, change):
        self.axes_set(change["name"])

    tight_layout=Bool(False)
    dpi=Int(300)

    def figure_set(self, param):
        self.simple_set(self._parent.figure, self, param)

    #@plot_observe("tight_layout", "dpi")
    def figure_update(self, change):
        self.figure_set(change["name"])

    def _default_figure(self):
        return plt.figure(figsize=(self.fig_width, self.fig_height), dpi=self.dpi,
        tight_layout=self.tight_layout)

    def set_xlim(self, xmin, xmax):
        self.x_min=xmin
        self.x_max=xmax
        self.axes.set_xlim(xmin, xmax)

    def set_ylim(self, ymin, ymax):
        self.y_min=ymin
        self.y_max=ymax
        self.axes.set_ylim(ymin, ymax)

    @private_property
    def view_window(self):
        with imports():
            from fig_format_e import Main
        view=Main(pltr=self)
        return view

    @plot_observe("xlabel_size")
    def xlabel_update(self, change):
        self.axes.xaxis.label.set_size(self.xlabel_size)

    @plot_observe("ylabel_size")
    def ylabel_update(self, change):
        self.axes.yaxis.label.set_size(self.ylabel_size)

    @plot_observe("x_min", "x_max")
    def x_lim_update(self, change):
        self.set_xlim(self.x_min, self.x_max)
        if self.show_cross_section:
            self.horiz_axe.set_xlim(self.x_min, self.x_max)
            if self.horiz_fig.canvas!=None:
                self.horiz_fig.canvas.draw()


    @plot_observe("y_min", "y_max")
    def y_lim_update(self, change):
        self.set_ylim(self.y_min, self.y_max)
        if self.show_cross_section:
            self.vert_axe.set_ylim(self.y_min, self.y_max)
            if self.vert_fig.canvas!=None:
                self.vert_fig.canvas.draw()



    @plot_observe("show_legend")
    def legend_update(self, change):
        if self.show_legend:
            self.legend()
        else:
            self.legend_remove()




if __name__=="__main__":

    #pm=PlotMaster()
    a=Plotter(fig_width=9.0, fig_height=3.0)
    from numpy import meshgrid, sqrt, linspace
    n = 300
    x = linspace(-1.5, 1.5, n)
    y = linspace(-1.5, 1.5, n*2)
    X, Y = meshgrid(x, y)
    Z = sqrt(X**2 + Y**2)

    #a.figure=plt.figure(figsize=(8.5,4))

    a.colormesh("colormesh", x, y, Z)
    print a.figure.get_size_inches()
    print a.figure.get_dpi()
    #a.figure.set_size_inches((9.5, 3.0))
    #print plt.plot(x)#,y,Z)
    a.show()
    #a.savefig() #figure.savefig("/Users/thomasaref/Documents/TA_software/test_colorm.pdf")#, format="eps")

    #shower(a)
    #b=Plotter()
    #a.scatter_plot("scatter", [100,200,300], [100,200,300], marker="<", marker_size=300)
    #a.savefig(dir_path="/Users/thomasaref/Dropbox/Current stuff/Linneaus180416/", fig_name="test_colormap")
    #d=CrossCursor(plotter=a)
    #d.add_cursor()
    #shower(a)

#    def line_plot(self, zname, zdata, *args, **kwargs):
#        """Uses LineCollection for efficient plotting of lines.
#           In kwargs, if raw=True, expects zdata is a list of lists of (x,y) tuples.
#           else if no args are sent, auto calculates x data.
#           otherwise assumes zdata is x data and args[0] is y data.
#           In kwargs, if append=False, data overwrites existing data in self.clts
#           If tuples, xlim or ylim are passed in kwargs, will use those for setting limits"""
#
#        xyf=self.xyfs.get(zname, None)
#        if xyf is None:
#            xyf=XYFormat(plotter=self, name=zname, plot_type="line")
#        clt=xyf.clt
#
#        xlim=kwargs.pop("xlim", None)
#        ylim=kwargs.pop("ylim", None)
#
#        if "color" in kwargs:
#            if kwargs["color"]=="auto":
#                kwargs.pop("color")
#                self.autocolor=True
#            else:
#                self.autocolor=False
#        data=[]
#        self.append=kwargs.pop("append", self.append)
#        if self.append:
#            if clt is not None:
#                data=clt.get_segments()
#        data_shape=len(shape(zdata))
#        if data_shape>2:
#            data.extend(zdata)
#        else:
#            if data_shape==2:
#                x=zdata[0]
#                y=zdata[1]
#                data.append(list(zip(x,y)))
#            elif args==():
#                x=arange(len(zdata))
#                y=zdata
#                data.append(list(zip(x,y)))
#            else:
#                x=zdata
#                data.extend([list(zip(x,y)) for y in args])
#        if clt is None:
#            clt=LineCollection(data, **kwargs)
#            self.axe.add_collection(clt)
#        else:
#            clt.set_verts(data)
#            if kwargs!={}:
#                clt.set(**kwargs)
#        if self.autocolor:
#            clt.set_array(arange(len(data)))
#        if "color" in kwargs:
#            clt.set_array(None)
##        if xlim is None or ylim is None: #try autosetting limits if xlim or ylim not specified
##            data=sqze(sqze([item.get_segments() for item in self.clts.values() if isinstance(item, LineCollection)]))
##            if xlim is None:
##                xlim=(min(data, key = lambda t: t[0])[0], max(data, key = lambda t: t[0])[0])
##            if ylim is None:
##                ylim=(min(data, key = lambda t: t[1])[1], max(data, key = lambda t: t[1])[1])
##        self.set_xlim(*xlim)
##        self.set_ylim(*ylim)
#        xyf.clt=clt
#        self.xyfs[zname]=xyf #XYFormat(plotter=self, name=zname, plot_type="line", label=kwargs.get("label", ""), edgecolor=kwargs.get("color", "blue"))
#
#    def scatter_plot(self, zname, *args, **kwargs):
#        self.append=kwargs.pop("append", self.append)
#        if not self.append:
#            self.remove_collection(zname)
#        self.clts[zname]=self.axe.scatter(*args, **kwargs)
#        self.xyfs[zname]=XYFormat(plotter=self, name=zname, plot_type="scatter", label=kwargs.get("label", ""), edgecolor=kwargs.get("color", "blue"))
#
#    def colormesh(self, zname, *args, **kwargs):
#        self.remove_collection(zname)
#        clt=self.axe.pcolormesh(*args, **kwargs)
#        self.xyfs[zname]=XYFormat(plotter=self, name=zname, clt=clt)
#        self.alldata=args[0]
#        #self.line_plot(zname+"lines", arange(len(args[0][0])), *args[0])
#        #self.xyfs[zname+"lines"]=XYFormat(plotter=self, name=zname+"lines")
#        #log_debug(args[0])
#    def axvline(self, zname, x, **kwargs):
#        self.remove_collection(zname)
#        self.axe.axvline(x, **kwargs)
#
#    def poly_plot(self, zname, zdata, zcolor=None):
#        if zname not in self.clts:
#            clt=PolyCollection(zdata, alpha=0.5, antialiased=True)
#            if zcolor is not None:
#                clt.set_color(zcolor) #colorConverter.to_rgba(zcolor))
#            self.clts[zname]=clt
#            self.axe.add_collection(self.clts[zname])
#        else:
#            self.clts[zname].set_verts(zdata)
#
#    def add_text(self, text, x, y, **kwargs):
#         """adds text at data location x,y"""
#         self.axe.text(x, y, text, **kwargs)
#
#    def remove_texts(self):
#        """removes all texts from axes"""
#        self.axe.texts=[]
