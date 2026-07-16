# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class LeafSenescence(SimulationObject):
    """
    Class to simulate leaf senescence

    Simulates senescence of leaves and its effects on the leaf area index and the amount. Under
    potential growth conditions, leaf senescence either takes place due to self-shading or due
    to ageing. Leaf senescence leads to a reduction of the leaf area index as well. Under nitrogen
    limited growth conditions, leaf ageing is enhanced. It is assumed that the concentration of
    nitrogen in senescenced leaves equals the residual nitrogen concentration of that leaf.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    LAICR           Leaf area index above which senescence due to
                    self-shading occurs.                            SCr      m2 leaf m-2 ground
    NSLA            Parameter in function that describes the
                    relationship between Nitrogen Nutrition Index
                    and the specific leaf nitrogen under nitrogen
                    limited conditions.                             SCr     -
    RDRT            Relative death rate of leaves due to ageing
                    once the temperature sum from emergence
                    exceeds a TSUMAG under potential growth
                    conditions.                                     SCr      d-1
    RDRSHM          Relative death rate of leaves due to self-
                    shading.                                        SCr      d-1
    RNFLV           Residual leaf nitrogen concentration            SCr      g N g-1 DM
    SLACF           Modificaiton factor of specific leaf area under
                    potential growth  conditions as a function of
                    development stage                               TCr     -
    SLAC            Reference specific leaf area                    SCr     m2 leaf g-1 leaf
    TSUMAG          Temperature sum from emergence above which
                    leaf senescence due to ageing occurs.           SCr     degC d
    ==============  ==============================================  ======  ===========================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RDLAI           Death rate leaf area index                      SCr     m2 leaf m-2 ground d-1
    RDLN            Nitrogen loss rate due to leaf senescence       SCr     g N m-2 ground d-1
    RDLV            Death rate leaf dry matter                      SCr     g DM m-2 ground d-1
    RDLVNS          Death rate leaf dry matter                      SCr     g DM m-2 ground d-1
    ==============  ==============================================  ======  ==============================

    """

    class Parameters(ParamTemplate):
        LAICR = Float()
        NSLA = Float()
        RDRT = AfgenTrait()
        RDRSHM = Float()
        RNFLV = Float()
        SLAC = Float()
        SLACF = AfgenTrait()
        TSUMAG = Float()

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        RDLAI = Float()
        RDLV = Float()
        RDLN = Float()
        RDLVNS = Float()
        RRDLV = Float()
        RRDLVAG = Float()
        RRDLVSH = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["RDLVNS", "RDLAI", "RDLN"])

    def calc_rates(self, day, drv, delt):
        self.calculate_relative_leaf_dry_matter_death_rate_due_ageing(drv)
        self.calculate_relative_leaf_dry_matter_death_due_self_shading()
        self.calculate_relative_leaf_dry_matter_death_rate_without_nstress()
        self.calculate_leaf_death_dry_matter_rate_without_nstress()
        self.calculate_leaf_dry_matter_death_rate()
        self.calculate_leaf_area_death_rate()
        self.calculate_leaf_n_loss_rate()

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states

    def calculate_leaf_dry_matter_death_rate(self):
        r = self.rates
        k = self.kiosk

        #TODO change this into a parameter once the model is ready.
        r.RDRNS = 0.03

        if k.EMERG == 0:
            DLVNS = 0.
        else:
            DLVNS = k.WLVG * r.RDRNS * (1. - k.NNI)
        RDLVNS = DLVNS + r.RDLV
        r.RDLVNS = RDLVNS

    def calculate_leaf_area_death_rate(self):
        p = self.params
        r = self.rates
        k = self.kiosk

        #TODO change this into a parameter once the model is ready.
        r.RDRNS = 0.03

        SLACF = p.SLACF(k.DVS)
        SLA = p.SLAC * SLACF * np.exp(-p.NSLA * (1.0 - k.NNI))

        DLAIS = r.RRDLV * k.LAI
        if k.EMERG == 0:
            DLAINS = 0
        else:
            DLAINS = k.WLVG * r.RDRNS * (1. - k.NNI) * SLA
        RDLAI = DLAIS + DLAINS
        r.RDLAI = RDLAI

    def calculate_leaf_death_dry_matter_rate_without_nstress(self):
        r = self.rates
        k = self.kiosk
        r.RDLV = r.RRDLV * k.WLVG

    def calculate_relative_leaf_dry_matter_death_rate_without_nstress(self):
        r = self.rates
        RRDLV = max(r.RRDLVAG, r.RRDLVSH)
        r.RRDLV = RRDLV

    def calculate_relative_leaf_dry_matter_death_rate_due_ageing(self, drv):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.TSUM < p.TSUMAG:
            RRDLVAG = 0
        else:
            RRDLVAG = p.RDRT(drv.TEMP)
        r.RRDLVAG = RRDLVAG

    def calculate_relative_leaf_dry_matter_death_due_self_shading(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        RRDLVSH1 = 0
        RRDLVSH2 = p.RDRSHM * (k.LAI - p.LAICR) / p.LAICR
        RRDLVSH = max(RRDLVSH1, RRDLVSH2)
        r.RRDLVSH = RRDLVSH

    def calculate_leaf_n_loss_rate(self):
        p = self.params
        r = self.rates

        RDLN = r.RDLVNS * p.RNFLV
        r.RDLN = RDLN