# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 10:19:24 2014

@author: thomasaref
"""

from atom.api import Float, Enum, Int, Typed, ForwardTyped, observe
from EBL_Item import EBL_Item
from EBL_Polygons import horiz_refl, vert_refl, horizvert_refl, EBL_Polygons, rotate

#from EBL_Combiner import EBL_Combiner

class EBL_test_pads(EBL_Item):
    contact_width=Float(125.0e-6).tag(unit="um", desc="width of contact")
    contact_height=Float(170.0e-6).tag(unit="um", desc="height of contact")
    bridge_gap_x=Float(20.0e-6).tag(unit="um", desc="horizontal gap between testpad electrodes")
    bridge_gap_y=Float(50.0e-6).tag(unit="um", desc="vertical gap between testpad electrodes")
    testpad_width=Float(400.0e-6).tag(unit="um", desc="overall width of testpad")
    testpad_height=Float(450.0e-6).tag(unit="um", desc="overall height of testpad")
    tp_bond_pad=Float(100.0e-6).tag(unit="um", desc="bonding area of testpad")

    def make_polylist(self):
        self.extend(self._s_testpad_TL)
        self.extend(horiz_refl(self._s_testpad_TL))
        self.extend(vert_refl(self._s_testpad_TL))
        self.extend(horizvert_refl(self._s_testpad_TL))

    @property
    def _s_testpad_TL(self):
        return self.sP([(-self.testpad_width/2.0, -self.testpad_height/2.0),
                  (-self.testpad_width/2.0, -self.testpad_height/2.0+self.tp_bond_pad),
                  (-self.contact_width/2.0, -self.contact_height/2.0),
                  (-self.contact_width/2.0, -self.bridge_gap_y/2.0),
                  (-self.bridge_gap_x/2.0, -self.bridge_gap_y/2.0),
                  (-self.bridge_gap_x/2.0, -self.contact_height/2.0),
                  (-self.testpad_width/2.0+self.tp_bond_pad, -self.testpad_height/2.0)])

class EBL_mark_box(EBL_Item):
    chip=ForwardTyped(lambda: EBL_PADSALL)
    M1_size=Float(500.0e-6).tag(unit="um", desc="size of marker 1")
    lbl_height=Float(500.0e-6).tag(unit="um", desc="label height (assumed above marker 1)")
    lbl_width=Float(1100.0e-6).tag(unit="um", desc="label width (label assumed above marker 1)")

    mb_type=Enum("mark_box", "label_box")


    @property
    def outer_width(self):
        return self.chip.xbox-self.chip.mb_x

    @property
    def outer_height(self):
        return self.chip.ybox-self.chip.mb_y

    @property
    def inner_width(self):
        return self.chip.mb_x-self.chip.mb_c

    @property
    def inner_height(self):
        return self.chip.mb_y-self.chip.mb_c

    def make_polylist(self):
        if self.mb_type=="label_box":
            vs=self._s_label_box_TL
        else:
            vs=self._s_mark_box_TL
        self.extend(vs)

    @property
    def _s_label_box_TL(self):
        vs=self.sP([(-self.outer_width, self.outer_height),
                   (self.inner_width, self.outer_height),
                   (self.inner_width, -self.inner_height),
                   (self.M1_size/2.0, -self.inner_height),
                   (self.M1_size/2.0, self.M1_size/2.0),
                   (self.lbl_width/2.0, self.M1_size/2.0),
                   (self.lbl_width/2.0, self.M1_size/2.0+self.lbl_height),
                   (-self.lbl_width/2.0, self.M1_size/2.0+self.lbl_height),
                   (-self.lbl_width/2.0, self.M1_size/2.0),
                   (-self.M1_size/2.0, self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.inner_height),
                   (-self.outer_width, -self.inner_height)])
        vs=self.sP([(self.M1_size/2.0, -self.inner_height),
                   (self.M1_size/2.0, -self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.inner_height)], vs)
        return vs

    @property
    def _s_mark_box_TL(self):
        vs=self.sP([(-self.outer_width, self.outer_height),
                   (self.inner_width, self.outer_height),
                   (self.inner_width, -self.inner_height),
                   (self.M1_size/2.0, -self.inner_height),
                   (self.M1_size/2.0, self.M1_size/2.0),
                   (-self.M1_size/2.0, self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.inner_height),
                   (-self.outer_width, -self.inner_height)])
        vs=self.sP([(self.M1_size/2.0, -self.inner_height),
                   (self.M1_size/2.0, -self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.M1_size/2.0),
                   (-self.M1_size/2.0, -self.inner_height)], vs)
        return vs




class CPW_strip(EBL_Item):
    taper_length=Float(800.0e-6).tag(unit='um', desc="length of taper of from bondpad to center conductor")
    chip=ForwardTyped(lambda: EBL_PADSALL)
    bond_pad=Float(200.0e-6).tag(unit='um', desc="size of bond pad. in general, this should be above 100 um")
    bond_pad_gap=Float(500.0e-6).tag(unit='um', desc="the bond pad gap should roughly match 50 Ohms but chip thickness effects may dominate")

    w=Float(40.0e-6).tag(unit='um', desc= "width of the center strip. should be 50 Ohm impedance matched with gap (40 um)") #50
    gap=Float(120.0e-6).tag(unit='um', desc="gap of center strip. should be 50 Ohm impedance matched with w (120 um)") #180

    Au_sec=Float(300.0e-6).tag(unit='um', desc="x coordinate of left idt")
    Al_sec=Float(200.0e-6).tag(unit='um', desc="x coordinate of left idt")
    overlap=Float(20.0e-6).tag(unit='um', desc="x coordinate of left idt")

    #@property
    #def Au_sec(self):
    #    return -(-self.chip.mb_c+self.Al_sec-self.overlap)
    @property
    def bp_x(self):
        return -self.chip.xbox+abs(self.x_ref)

    def make_polylist(self):
        self.R(self.bp_x, -self.bond_pad/2.0+self.w, self.bond_pad, self.bond_pad)
        self.R(0.0, 0.0, -self.Al_sec, self.w)
        tc=tooth_connect( width=self.w, height=self.Au_sec, theta=-90.0, y_ref=self.w/2.0, x_ref=-self.Au_sec/2.0-self.Al_sec+self.overlap)
        self.pro_vs(tc)
        self.P([(self.bp_x+self.bond_pad, -self.bond_pad/2.0+self.w),
                (self.bp_x+self.bond_pad, self.bond_pad/2.0+self.w),
                (tc.x_ref-self.Au_sec/2.0, self.w),
                (tc.x_ref-self.Au_sec/2.0, 0)])


class EBL_CPW(EBL_Item):
    taper_length=Float(800.0e-6).tag(unit='um', desc="length of taper of from bondpad to center conductor")
    bp_x=Float(2400.0e-6).tag(unit="um", desc="real x edge of chip") #self.chip_width/2.0-self.blade_width/2.0 #set width of from center of pattern

    bond_pad=Float(200.0e-6).tag(unit='um', desc="size of bond pad. in general, this should be above 100 um")
    bond_pad_gap=Float(500.0e-6).tag(unit='um', desc="the bond pad gap should roughly match 50 Ohms but chip thickness effects may dominate")

    w=Float(40.0e-6).tag(unit='um', desc= "width of the center strip. should be 50 Ohm impedance matched with gap (40 um)") #50
    gap=Float(120.0e-6).tag(unit='um', desc="gap of center strip. should be 50 Ohm impedance matched with w (120 um)") #180

    cpw_stop_x_l=Float(-200.0e-6).tag(unit='um', desc="x coordinate of left idt")

    #gate_extension=Float(100.0e-6).tag(unit='um', desc="length gate extends into CPW")
    mark_box_x=Float(-800.0e-6)
    top_mb_y=Float(800.0e-6)
    bot_mb_y=Float(800.0e-6)

    chip=ForwardTyped(lambda: EBL_PADSALL)

    @observe("chip.chip_width")
    def chip_update(self, change):
        self.bp_x=self.chip.xbox

    @observe("chip.idt_x")
    def idt_update(self, change):
        self.cpw_stop_x_l=self.chip.idt_x+27.7e-6/2.0

    @observe("chip.mb_c")
    def mby_update(self, change):
        self.top_mb_y=self.chip.mb_c-self.y_ref
        self.bot_mb_y=self.chip.mb_c+self.y_ref

    gndplane_gap=Float(80.0e-6).tag(unit='um', desc="gap in ground plane that lets SAW through")
    gndplane_big_gap=Float(60.0e-6).tag(unit='um', desc="gap in ground plane where qubit IDT resides")
    gndplane_width=Float(30.0e-6).tag(unit='um', desc="width of ground plane fingers that block SAW")
    gndplane_testgap=Float(500.0e-6).tag(unit='um', desc="gap in ground plane for test structures")
    gndplane_side_gap=Float(30.0e-6).tag(unit='um', desc="side gap in ground plane")

    cpw_type=Enum("L", "R")

    def make_polylist(self):
        #self.cpw_L_strip()
        self.cpw_L_top()
        self.cpw_L_bottom()
        if self.cpw_type=="R":
            self.horiz_refl()

    def cpw_L_strip(self):
        self.R(-self.bp_x, -self.bond_pad/2.0, self.bond_pad, self.bond_pad)
        self.P([(-self.bp_x+self.bond_pad, -self.bond_pad/2.0),
                (-self.bp_x+self.bond_pad, self.bond_pad/2.0),
                (-self.bp_x+self.bond_pad+self.taper_length, self.w/2.0),
                (-self.bp_x+self.bond_pad+self.taper_length, -self.w/2.0)])
        self.P([(-self.bp_x+self.bond_pad+self.taper_length, -self.w/2.0),
                (-self.bp_x+self.bond_pad+self.taper_length, self.w/2.0),
                (self.cpw_stop_x_l, self.w/2.0),
                (self.cpw_stop_x_l, -self.w/2.0)])

    def cpw_L_top(self):
        self.P([(-self.bp_x, self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad), self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad),  self.top_mb_y),
                   (-self.bp_x, self.top_mb_y)])
        self.P([(-(self.bp_x-self.bond_pad), self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad), self.top_mb_y),
                   (-(self.bp_x-self.bond_pad-self.taper_length), self.top_mb_y),
                   (-(self.bp_x-self.bond_pad-self.taper_length), self.w/2.0+self.gap)])
        self.P([(-(self.bp_x-self.bond_pad-self.taper_length), self.w/2.0+self.gap),
                   (-(self.bp_x-self.bond_pad-self.taper_length), self.top_mb_y),
                   (self.mark_box_x, self.top_mb_y),
                   (-self.gndplane_big_gap/2.0-self.gndplane_width-self.gndplane_side_gap, self.w/2.0+self.gap)])

    def cpw_L_bottom(self):
        self.P([(-self.bp_x, -self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad), -self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad),  -self.bot_mb_y),
                   (-self.bp_x, -self.bot_mb_y)])

        self.P([(-(self.bp_x-self.bond_pad), -self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.bp_x-self.bond_pad), -self.bot_mb_y),
                   (-(self.bp_x-self.bond_pad-self.taper_length), -self.bot_mb_y),
                   (-(self.bp_x-self.bond_pad-self.taper_length), -self.w/2.0-self.gap),])
        self.P([(-(self.bp_x-self.bond_pad-self.taper_length), -self.w/2.0-self.gap),
                   (-(self.bp_x-self.bond_pad-self.taper_length), -self.bot_mb_y),
                   (self.mark_box_x, -self.bot_mb_y),
                   (-self.gndplane_big_gap/2.0-self.gndplane_width-self.gndplane_side_gap, -self.w/2.0-self.gap),])

class Al_PADS(EBL_Item):

    chip=Typed(EBL_Item)

    @property
    def end_cpw_x(self):
        return -self.chip.xbox+self.chip.bond_pad+self.chip.taper_length+self.chip.Au_sec-self.chip.overlap
    @property
    def idt_wbox(self):
        return self.chip.idt_wbox

    @property
    def l_idt_x(self):
        return self.chip.l_idt_x

    @property
    def r_idt_x(self):
        return self.chip.r_idt_x

    @property
    def w(self):
        return self.chip.w

    @property
    def gap(self):
        return self.chip.gap

    @property
    def mb_c(self):
        return self.chip.mb_c-self.chip.Au_sec+self.chip.overlap

    @property
    def _s_CPW_strip_L(self):
        vs=self.sP([(self.end_cpw_x, self.gap/2.0),
                        (self.end_cpw_x, self.gap/2.0+self.w),
                        (self.l_idt_x+self.idt_wbox, self.gap/2.0+self.w),
                        (self.l_idt_x+self.idt_wbox, self.gap/2.0)])
        vs=self.sP([(self.end_cpw_x, 3*self.gap/2.0+self.w),
                        (self.end_cpw_x, self.mb_c),
                        (-self.mb_c, self.mb_c),
                        (self.l_idt_x+self.idt_wbox, 3*self.gap/2.0+self.w)], vs)
        return vs


    @property
    def _s_CPW_strip_R(self):
        return self.sP([(-self.end_cpw_x, self.gap/2.0),
                        (-self.end_cpw_x, self.gap/2.0+self.w),
                        (self.r_idt_x-self.idt_wbox, self.gap/2.0+self.w),
                        (self.r_idt_x-self.idt_wbox, self.gap/2.0)])

    def make_polylist(self):
        self.extend(self._s_CPW_strip_L)
        self.extend(self._s_CPW_strip_R)

class EBL_PADSALL(EBL_Item):
    chip_height=Float(5000.0e-6).tag(unit='um', desc="the height of the chip (in um though would be more natural in mm) as defined by the dicing saw")
    chip_width=Float(5000.0e-6).tag(unit='um', desc="the width of the chip (in um though would be more natural in mm) as defined by the dicing saw")
    blade_width=Float(200.0e-6).tag(unit='um', desc="width of blade used to make dicing cuts")
    mb_x=Float(1500.0e-6).tag(unit="um")
    mb_y=Float(1500.0e-6).tag(unit="um")
    l_idt_x=Float(-200e-6).tag(unit="um")
    r_idt_x=Float(300e-6).tag(unit="um")
    idt_wbox=Float(20e-6).tag(unit="um")

    mb_c=Float(800.0e-6).tag(unit="um")
    w=Float(40.0e-6).tag(unit='um', desc= "width of the center strip. should be 50 Ohm impedance matched with gap (40 um)") #50
    gap=Float(120.0e-6).tag(unit='um', desc="gap of center strip. should be 50 Ohm impedance matched with w (120 um)") #180

    Au_sec=Float(250.0e-6).tag(unit="um")


    overlap=Float(50.0e-6).tag(unit="um")

    taper_length=Float(800.0e-6).tag(unit='um', desc="length of taper of from bondpad to center conductor")
    bond_pad=Float(200.0e-6).tag(unit='um', desc="size of bond pad. in general, this should be above 100 um")
    bond_pad_gap=Float(500.0e-6).tag(unit='um', desc="the bond pad gap should roughly match 50 Ohms but chip thickness effects may dominate")

    h_idt=Float(52.0e-6).tag(unit='um', desc="height of idt electrode one is trying to connect to.")

    yheight=Float(900.0e-6).tag(unit="um", desc="real y edge of chip")

    gndplane_gap=Float(80.0e-6).tag(unit='um', desc="gap in ground plane that lets SAW through")
    gndplane_big_gap=Float(60.0e-6).tag(unit='um', desc="gap in ground plane where qubit IDT resides")
    gndplane_width=Float(30.0e-6).tag(unit='um', desc="width of ground plane fingers that block SAW")
    gndplane_testgap=Float(500.0e-6).tag(unit='um', desc="gap in ground plane for test structures")
    gndplane_side_gap=Float(30.0e-6).tag(unit='um', desc="side gap in ground plane")

    def make_teststrip(self):
        self.R(-self.gndplane_testgap/2.0, -self.ybox, self.gndplane_testgap, self.ybox-self.yheight)
        self.P([(-self.gndplane_testgap/2.0, -self.yheight),
                   (self.gndplane_testgap/2.0, -self.yheight),
                   (self.gndplane_big_gap/2.0+self.gndplane_width, -self.w/2.0-self.gap),
                   (-self.gndplane_big_gap/2.0-self.gndplane_width, -self.w/2.0-self.gap)])
        self.P([(-self.gndplane_big_gap/2.0-self.gndplane_width, -self.w/2.0-self.gap),
                  (-self.gndplane_big_gap/2.0-self.gndplane_width, -self.gndplane_gap/2.0),
                  (-self.gndplane_big_gap/2.0, -self.gndplane_gap/2.0),
                  (-self.gndplane_big_gap/2.0, -self.w/2.0-self.gap)])
        self.P([(self.gndplane_big_gap/2.0+self.gndplane_width, -self.w/2.0-self.gap),
                  (self.gndplane_big_gap/2.0+self.gndplane_width, -self.gndplane_gap/2.0),
                  (self.gndplane_big_gap/2.0, -self.gndplane_gap/2.0),
                  (self.gndplane_big_gap/2.0, -self.w/2.0-self.gap)])

    @property
    def xbox(self):
        """width from center of pattern"""
        return self.chip_width/2.0-self.blade_width/2.0

    @property
    def bcpw(self):
        return self.gap/2.0+self.w/2.0
    @property
    def ybox(self):
        """height from center of pattern"""
        return self.chip_height/2.0-self.blade_width/2.0

    Al_sec=Float(500.0e-6).tag(unit="um")
    width=Float(40.0e-6).tag(unit="um")
    height=Float(100.0e-6).tag(unit="um")

    def make_idt_conn(self):
        self.CT(0, 0, self.width/2.0, self.height/2.0)
        self.R(-self.width/2.0, -self.height/2.0, -self.Al_sec, -self.w)
        self.P([(-self.width/2.0, -self.height/2.0), (-self.width/2.0, self.height/2.0), (-3.0*self.width/2.0, -self.height/2.0)])

    @property
    def _s_bond_pad_TL(self):
        vs=self.sC(-self.xbox+self.bond_pad/2.0, self.bcpw, self.bond_pad, self.bond_pad)
        vs=self.sT(-self.xbox+self.bond_pad+self.taper_length, self.gap/2.0, self.Au_sec, self.w, vs=vs)
        vs=self.sT(-self.mb_c, 3*self.gap/2.0+self.w, self.Au_sec,
                   self.mb_c-3*self.gap/2.0-self.w, nt=30, vs=vs)
        vs=self.sT(-self.mb_c, self.mb_c, -self.xbox+self.bond_pad+self.taper_length+self.mb_c,-self.Au_sec, nt=30, ot="T", vs=vs)

        return self.sP([(-self.xbox+self.bond_pad, -self.bond_pad/2.0+self.bcpw),
                (-self.xbox+self.bond_pad, self.bond_pad/2.0+self.bcpw),
                (-self.xbox+self.bond_pad+self.taper_length, self.bcpw+self.w/2.0),
                (-self.xbox+self.bond_pad+self.taper_length, self.bcpw-self.w/2.0)], vs)


    def make_polylist(self):
        self.make_bond_pads()
        self.make_teststrip()
        #self.make_idt_conn()

    def make_bond_pads(self):
        self.extend(self._s_bond_pad_TL)
        self.extend(horiz_refl(self._s_bond_pad_TL))
        self.extend(rotate(horiz_refl(self._s_bond_pad_TL), 90))

    def _default_children(self):
        TL_mb=EBL_mark_box(name="_TL_mb", mb_type="label_box", orient="TL", x_ref=-self.mb_x, y_ref=self.mb_y, chip=self)
        BL_mb=EBL_mark_box(name="_BL_mb", orient="BL", x_ref=-self.mb_x, y_ref=-self.mb_y, chip=self)
        BR_mb=EBL_mark_box(name="_BR_mark_box", orient="BR", x_ref=self.mb_x, y_ref=-self.mb_y, chip=self)
        TR_mb=EBL_mark_box(name="_TR_mark_box", orient="TR", x_ref=self.mb_x, y_ref=self.mb_y, chip=self)

        RR_CPW=EBL_CPW(name="_R_CPW", cpw_type="R", y_ref=80.0e-6, chip=self)
        #idt_conn_l=IDT_connect(name="_L_IDT_conn", x_ref=self.l_idt_x, chip=self)
        #idt_conn_r=IDT_connect(name="_R_IDT_conn", orient="TR", x_ref=self.r_idt_x, chip=self)
        #L_CPW=CPW_strip(name="_L_CPW", y_ref=idt_conn_l.ymax/1.0e6, x_ref=idt_conn_l.xmax/1.0e6, chip=self)
        #R_CPW=CPW_strip(name="_R_CPW", y_ref=idt_conn_r.ymax/1.0e6, x_ref=idt_conn_r.x_ref-idt_conn_r.width/2.0, chip=self, orient="TR")
        return [TL_mb, BL_mb, BR_mb, TR_mb, #L_CPW, R_CPW, RR_CPW,
        #idt_conn_l, idt_conn_r,
        #EBL_test_strip(name="_test_strip"),
                Al_PADS(chip=self),
              EBL_test_pads(name="_BL_testpad", x_ref=-500.0e-6, y_ref=-1500.0e-6),
              EBL_test_pads(name="_BR_testpad", x_ref=500.0e-6, y_ref=-1500.0e-6)
    ]

class tooth_connect(EBL_Item):
    """creates a centered box with teeth"""
    tooth_size=Float(4.0e-6).tag(unit='um', desc="tooth size on CPW connection to aid contact")
    width=Float(40.0e-6).tag(unit="um")
    height=Float(100.0e-6).tag(unit="um")

    @property
    def num_teeth(self):
        """number of teeth that fit"""
        return int(self.width/(2*self.tooth_size))

    @property
    def conn_width(self):
        """width of part actually with teeth"""
        return self.tooth_size*(2*self.num_teeth-1)

    @property
    def tc_verts(self):
        vs=self.sC(0,0, self.width, self.height)
        for i in range(self.num_teeth):
            vs=self.sR(-self.conn_width/2.0+2*i*self.tooth_size, self.height/2.0, self.tooth_size, self.tooth_size, vs )
        return vs

    def make_polylist(self):
        self.extend(self.tc_verts)


class EBL_PADS(EBL_Item):
    #testpad_BL=Typed(EBL_test_pads, kwargs=dict(x_center=-500.0, y_center=-1500.0))
    #testpad_BR=Typed(EBL_test_pads, kwargs=dict(x_center=500.0, y_center=-1500.0))

    xbox=Float(2400.0).tag(unit="um", desc="real x edge of chip") #self.chip_width/2.0-self.blade_width/2.0 #set width of from center of pattern
    ybox=Float(2400.0).tag(unit="um", desc="real y edge of chip") #self.chip_height/2.0-self.blade_width/2.0 #set height from center of pattern

    """handles everything related to drawing pads."""
    pad_type=Enum('gated').tag(desc="pad types are gate")
    bond_pad=Float(200.0).tag(unit='um', desc="size of bond pad. in general, this should be above 100 um")
    bond_pad_gap=Float(500.0).tag(unit='um', desc="the bond pad gap should roughly match 50 Ohms but chip thickness effects may dominate")
    chip_height=Float(5000.0).tag(unit='um', desc="the height of the chip (in um though would be more natural in mm) as defined by the dicing saw")
    chip_width=Float(5000.0).tag(unit='um', desc="the width of the chip (in um though would be more natural in mm) as defined by the dicing saw")
    blade_width=Float(200.0).tag(unit='um', desc="width of blade used to make dicing cuts")

    w=Float(40.0).tag(unit='um', desc= "width of the center strip. should be 50 Ohm impedance matched with gap (40 um)") #50
    gap=Float(120.0).tag(unit='um', desc="gap of center strip. should be 50 Ohm impedance matched with w (120 um)") #180
    h_idt=Float(52.0).tag(unit='um', desc="height of idt electrode one is trying to connect to.")

    taper_length=Float(800.0).tag(unit='um', desc="length of taper of from bondpad to center conductor")
    idtL_x=Float(-200.0+27.7/2.0).tag(unit='um', desc="x coordinate of left idt")
    idtR_x=Float(300.0-27.7/2.0).tag(unit='um', desc="x coordinate of right idt")
    idt_y=Float(0.0).tag(unit='um', desc="y coordinateof IDT")

    gndplane_gap=Float(80.0).tag(unit='um', desc="gap in ground plane that lets SAW through")
    gndplane_big_gap=Float(60.0).tag(unit='um', desc="gap in ground plane where qubit IDT resides")
    gndplane_width=Float(30.0).tag(unit='um', desc="width of ground plane fingers that block SAW")
    gndplane_testgap=Float(500.0).tag(unit='um', desc="gap in ground plane for test structures")
    gndplane_side_gap=Float(30.0).tag(unit='um', desc="side gap in ground plane")

    gate_extension=Float(100.0).tag(unit='um', desc="length gate extends into CPW")
    idt_tooth=Float(4.0).tag(unit='um', desc="tooth size on CPW connection to aid contact")
    idt_numteeth=Int(5) #52 um, 12.5 um
    xbox=Float() #self.chip_width/2.0-self.blade_width/2.0 #set width of from center of pattern
    ybox=Float() #self.chip_height/2.0-self.blade_width/2.0 #set height from center of pattern
    #y_center=Float() #self.h_idt/2.0+self.w/2.0
    cpw_stop_x_r=Float()#self.idtR_x #self.x_center+self.w/2+self.gap
    cpw_stop_x_l=Float() #self.idtL_x#self.x_center-self.w/2-self.gap
    cpw_stop_y_t=Float() #self.y_center+self.w/2+self.gap
    cpw_stop_y_b=Float() #self.y_center-self.w/2-self.gap
    test_w=Float(500.0)

    #@property
    #def pad_type_mapped(self):
    #    return self.get_map("pad_type")

    def make_polylist(self):
        """Draws PADS depending on object parameters"""
        self.xbox=self.chip_width/2.0-self.blade_width/2.0 #set width of from center of pattern
        self.ybox=self.chip_height/2.0-self.blade_width/2.0 #set height from center of pattern
        self.y_center=self.gap/2.0+self.w/2.0

        self.cpw_stop_x_r=self.idtR_x #self.x_center+self.w/2+self.gap
        self.cpw_stop_x_l=self.idtL_x#self.x_center-self.w/2-self.gap
        self.cpw_stop_y_t=self.y_center+self.w/2+self.gap
        self.cpw_stop_y_b=self.y_center-self.w/2-self.gap

        self.get_map("pad_type")()
        #self.pad_type_mapped()

    def gated(self):
        self.mark_box_TL()
        self.mark_box_BL()
        self.mark_box_TR()
        self.mark_box_BR()
        self.cpw_L()
        self.cpw_R()
        self.cpw_T()
        self.tst_B()
        self.IDT_connect_R()
        self.IDT_connect_L()
        self.testpdr()

    def tst_B(self):
        self.test()
        self.test()
        self.test_strip()

    def testpads(self):
        self.contact_width=125.0
        self.contact_height=170.0
        self.bridge_gap_x=20.0
        self.bridge_gap_y=50.0
        self.testpad_width=400.0
        self.testpad_height=450.0
        self.poly([(self.xcenter-self.testpad_width, self.ycenter+self.testpad_height/2.0),
                   (self.x_center-self.contact_width/2.0, self.y_center+self.testpad_height/2.0),
                   (self.x_center-self.bridge_gap_x/2.0, self.y_center+self.contact_height/2.0)
                   (self.x_center-self.contact_width/2.0, self.y_center+self.contact_height/2.0)
                   ])

    def IDT_connect_R(self):
        idt_conn=self.idt_tooth*(2*self.idt_numteeth-1)
        self.poly([(self.idtR_x, self.y_center-self.w/2.0),
                   (self.idtR_x+idt_conn+self.h_idt, self.y_center-self.w/2.0),
                   (self.idtR_x+idt_conn, self.h_idt/2.0),
                   (self.idtR_x, self.h_idt/2.0)])
        self.poly([(self.idtR_x, self.y_center-self.w/2.0-self.gap),
                   (self.idtR_x+idt_conn+self.h_idt, self.y_center-self.w/2.0-self.gap),
                   (self.idtR_x+idt_conn, -self.h_idt/2.0),
                   (self.idtR_x, -self.h_idt/2.0)])
        for i in range(self.idt_numteeth):
            self.rect(self.idtR_x+2*i*self.idt_tooth, self.h_idt/2.0, self.idt_tooth, -self.idt_tooth )
            self.rect(self.idtR_x+2*i*self.idt_tooth, -self.h_idt/2.0, self.idt_tooth, self.idt_tooth )

    def IDT_connect_L(self):
        idt_conn=self.idt_tooth*(2*self.idt_numteeth-1)
        self.poly([(self.idtL_x, self.y_center-self.w/2.0),
                   (self.idtL_x-idt_conn-self.h_idt, self.y_center-self.w/2.0),
                   (self.idtL_x-idt_conn, self.h_idt/2.0),
                   (self.idtL_x, self.h_idt/2.0)])
        self.poly([(self.idtL_x, self.y_center-self.w/2.0-self.gap),
                   (self.idtL_x-idt_conn-self.h_idt, self.y_center-self.w/2.0-self.gap),
                   (self.idtL_x-idt_conn, -self.h_idt/2.0),
                   (self.idtL_x, -self.h_idt/2.0)])
        for i in range(self.idt_numteeth):
            self.rect(self.idtL_x-2*i*self.idt_tooth, self.h_idt/2.0, -self.idt_tooth, -self.idt_tooth )
            self.rect(self.idtL_x-2*i*self.idt_tooth, -self.h_idt/2.0, -self.idt_tooth, self.idt_tooth )

    def test_strip(self)          :
        self.rect(self.x_center-self.gndplane_testgap/2.0, -self.ybox, self.gndplane_testgap, self.ybox-self.mark_box_y)
        self.poly([(self.x_center-self.gndplane_testgap/2.0, -self.mark_box_y),
                   (self.x_center+self.gndplane_testgap/2.0, -self.mark_box_y),
                   (self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width, self.y_center-self.w/2.0-self.gap),
                   (self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width, self.y_center-self.w/2.0-self.gap)])
        self.poly([(self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width, self.y_center-self.w/2.0-self.gap),
                  (self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width, -self.gndplane_gap/2.0),
                  (self.x_center-self.gndplane_big_gap/2.0, -self.gndplane_gap/2.0),
                  (self.x_center-self.gndplane_big_gap/2.0, self.y_center-self.w/2.0-self.gap)])
        self.poly([(self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width, self.y_center-self.w/2.0-self.gap),
                  (self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width, -self.gndplane_gap/2.0),
                  (self.x_center+self.gndplane_big_gap/2.0, -self.gndplane_gap/2.0),
                  (self.x_center+self.gndplane_big_gap/2.0, self.y_center-self.w/2.0-self.gap)])




    def cpw_T(self):
        self.cpw_T_strip()
        self.cpw_T_left()
        self.cpw_T_right()

    def cpw_T_strip(self):
        self.rect(self.x_center-self.bond_pad/2.0, self.ybox, self.bond_pad, -self.bond_pad)
        self.poly([(self.x_center-self.bond_pad/2.0, (self.ybox-self.bond_pad)),
                   (self.x_center+self.bond_pad/2.0, (self.ybox-self.bond_pad)),
                   (self.x_center+self.w/2.0, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.x_center-self.w/2.0, (self.ybox-self.bond_pad-self.taper_length))])
        self.poly([(self.x_center-self.w/2.0, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.x_center+self.w/2.0, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.x_center+self.gndplane_width/2.0, self.cpw_stop_y_t-self.gate_extension),
                   (self.x_center-self.gndplane_width/2.0, self.cpw_stop_y_t-self.gate_extension)])

    def cpw_T_right(self):
        self.poly([( self.x_center+self.bond_pad/2.0+self.bond_pad_gap, self.ybox),
                   ( self.x_center+self.bond_pad/2.0+self.bond_pad_gap, self.ybox-self.bond_pad),
                   ( -self.mark_box_x, self.ybox-self.bond_pad),
                   ( -self.mark_box_x, self.ybox)])
        self.poly([((self.x_center+self.bond_pad/2.0+self.bond_pad_gap, self.ybox-self.bond_pad)),
                   (-self.mark_box_x, (self.ybox-self.bond_pad)),
                   (-self.mark_box_x, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.x_center+self.w/2.0+self.gap, (self.ybox-self.bond_pad-self.taper_length))])
        self.poly([(self.x_center+self.w/2.0+self.gap, (self.ybox-self.bond_pad-self.taper_length)),
                   (-self.mark_box_x, (self.ybox-self.bond_pad-self.taper_length)),
                   (-self.mark_box_x, self.cpw_stop_y_t),
                   (self.x_center+self.gndplane_big_gap/2.0, self.cpw_stop_y_t)])
        self.poly([(self.x_center+self.gndplane_big_gap+self.gndplane_width, self.y_center+self.w/2.0+self.gap),
                  (self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width, self.gndplane_gap/2.0),
                  (self.x_center+self.gndplane_big_gap/2.0, self.gndplane_gap/2.0),
                  (self.x_center+self.gndplane_big_gap/2, self.y_center+self.w/2.0+self.gap)])

    def cpw_T_left(self):
        self.poly([( self.x_center-self.bond_pad/2.0-self.bond_pad_gap, self.ybox),
                   ( self.x_center-self.bond_pad/2.0-self.bond_pad_gap, self.ybox-self.bond_pad),
                   ( self.mark_box_x, self.ybox-self.bond_pad),
                   ( self.mark_box_x, self.ybox)])
        self.poly([((self.x_center-self.bond_pad/2.0-self.bond_pad_gap, self.ybox-self.bond_pad)),
                   (self.mark_box_x, (self.ybox-self.bond_pad)),
                   (self.mark_box_x, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.x_center-self.w/2.0-self.gap, (self.ybox-self.bond_pad-self.taper_length))])
        self.poly([(self.x_center-self.w/2.0-self.gap, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.mark_box_x, (self.ybox-self.bond_pad-self.taper_length)),
                   (self.mark_box_x, self.cpw_stop_y_t),
                   (self.x_center-self.gndplane_big_gap/2.0, self.cpw_stop_y_t)])
        self.poly([(self.x_center-self.gndplane_big_gap-self.gndplane_width, self.y_center+self.w/2.0+self.gap),
                  (self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width, self.gndplane_gap/2.0),
                  (self.x_center-self.gndplane_big_gap/2.0, self.gndplane_gap/2.0),
                  (self.x_center-self.gndplane_big_gap/2.0, self.y_center+self.w/2.0+self.gap)])


    def cpw_L(self):
        self.cpw_L_strip()
        self.cpw_L_top()
        self.cpw_L_bottom()

    def cpw_L_strip(self):
        self.rect(-self.xbox, self.y_center-self.bond_pad/2.0, self.bond_pad, self.bond_pad)
        self.poly([(-(self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0),
                   (-(self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0)])
        self.poly([(-(self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0),
                   (self.cpw_stop_x_l, self.y_center+self.w/2.0),
                   (self.cpw_stop_x_l, self.y_center-self.w/2.0)])

    def cpw_L_top(self):
        self.poly([(-self.xbox, self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad),  self.mark_box_y),
                   (-self.xbox, self.mark_box_y)])
        self.poly([(-(self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad), self.mark_box_y),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.mark_box_y),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0+self.gap)])
        self.poly([(-(self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0+self.gap),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.mark_box_y),
                   (self.mark_box_x, self.mark_box_y),
                   (self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width-self.gndplane_side_gap, self.y_center+self.w/2.0+self.gap)])

    def cpw_L_bottom(self):
        self.poly([(-self.xbox, self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad),  -self.mark_box_y),
                   (-self.xbox, -self.mark_box_y)])

        self.poly([(-(self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   (-(self.xbox-self.bond_pad), -self.mark_box_y),
                   (-(self.xbox-self.bond_pad-self.taper_length), -self.mark_box_y),
                   (-(self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0-self.gap),])
        self.poly([(-(self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0-self.gap),
                   (-(self.xbox-self.bond_pad-self.taper_length), -self.mark_box_y),
                   (self.mark_box_x, -self.mark_box_y),
                   (self.x_center-self.gndplane_big_gap/2.0-self.gndplane_width-self.gndplane_side_gap, self.y_center-self.w/2.0-self.gap),])

    def cpw_R(self):
        self.cpw_R_strip()
        self.cpw_R_top()
        self.cpw_R_bottom()

    def cpw_R_strip(self):
        self.rect(self.xbox, self.y_center-self.bond_pad/2.0, -self.bond_pad, self.bond_pad)
        self.poly([((self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0),
                   ((self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0),
                   ((self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0),
                   ((self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0)])
        self.poly([((self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0),
                   ((self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0),
                   (self.cpw_stop_x_r, self.y_center+self.w/2.0),
                   (self.cpw_stop_x_r, self.y_center-self.w/2.0)])

    def cpw_R_top(self):
        self.poly([(self.xbox, self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   ((self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   ((self.xbox-self.bond_pad),  self.mark_box_y),
                   (self.xbox, self.mark_box_y)])
        self.poly([((self.xbox-self.bond_pad), self.y_center+self.bond_pad/2.0+self.bond_pad_gap),
                   ((self.xbox-self.bond_pad), self.mark_box_y),
                   ((self.xbox-self.bond_pad-self.taper_length), self.mark_box_y),
                   ((self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0+self.gap)])
        self.poly([((self.xbox-self.bond_pad-self.taper_length), self.y_center+self.w/2.0+self.gap),
                   ((self.xbox-self.bond_pad-self.taper_length), self.mark_box_y),
                   (-self.mark_box_x, self.mark_box_y),
                   (self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width+self.gndplane_side_gap, self.y_center+self.w/2.0+self.gap)])

    def cpw_R_bottom(self):
        self.poly([(self.xbox, self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   ((self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   ((self.xbox-self.bond_pad),  -self.mark_box_y),
                   (self.xbox, -self.mark_box_y)])

        self.poly([((self.xbox-self.bond_pad), self.y_center-self.bond_pad/2.0-self.bond_pad_gap),
                   ((self.xbox-self.bond_pad), -self.mark_box_y),
                   ((self.xbox-self.bond_pad-self.taper_length), -self.mark_box_y),
                   ((self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0-self.gap),])
        self.poly([((self.xbox-self.bond_pad-self.taper_length), self.y_center-self.w/2.0-self.gap),
                   ((self.xbox-self.bond_pad-self.taper_length), -self.mark_box_y),
                   (-self.mark_box_x, -self.mark_box_y),
                   (self.x_center+self.gndplane_big_gap/2.0+self.gndplane_width+self.gndplane_side_gap, self.y_center-self.w/2.0-self.gap),])

    def rect(self, xr, yr, wr, hr):
        """Adds a rectangle with bottom left corner coordinates to polylist"""
        self.R(xr, yr, wr, hr)

    def poly(self, verts):
        self.P(verts)

if __name__=="__main__":
    #a=EBL_test_pads(name="EBL_Item_test")
#    a=EBL_mark_box(name="EBL_Item_test")
    a=EBL_PADSALL(name="EBL_Item_test")
    a.show()