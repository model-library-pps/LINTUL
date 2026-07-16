# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class GrowthLeafArea(SimulationObject):
    """
    Class to simulate the growth of the leaf area

    Simulates the growth of the leaf area index. During the juvenile phase, the leaf area index grows
    exponential, given that there is no water or nitrogen stress. After the juvenile phase, the growth
    of the leaf area index is proportional to the growth of the leaf dry matter.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    NLAI            Parameter that describes the decrease in the
                    growth rate of the leaf area index and the
                    Nitrogen Nutrition Index during the juvenile
                    phase.                                          TCr     -
    NSLA            Parameter that describes the reduction in the
                    specific leaf area as a function of the
                    Nitrogen Nutrition Index.                       SCr     -
    RGRL            Relative growth rate of the leaf area index
                    during the juvenile growth phase.               SCr     (C d)-1
    SLACF           Modificaiton factor of specific leaf area under
                    potential growth  conditions as a function of
                    development stage                               TCr     -
    SLAC            Reference specific leaf area                    SCr     m2 leaf g-1 leaf
    TSUMAN          Temperature sum between emergence and
                    anthesis.                                       SCr     degC d
    TSUMI           Initial temperature sum from emergence.         SCr     degC d
    WLVGI           Initial leaf dry weight                         SCr     g DM m-2
    ==============  ==============================================  ======  ===========================

     *State variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    LAI             Leaf area index                                 Y       m2 leaf m-2 ground
    ==============  ==============================================  ======  ==============================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RGLAI            Growth rate leaf area index                    Y       m2 leaf m-2 ground d-1
    ==============  ==============================================  ======  ==============================
    """


    class Parameters(ParamTemplate):
        NLAI = Float()
        NSLA = Float()
        RGRL = Float()
        SLACF = AfgenTrait()
        SLAC = Float()
        TSUMAN = Float()
        TSUMI = Float()
        WLVGI = Float()

    class StateVariables(StatesTemplate):
        LAI = Float()
    class RateVariables(RatesTemplate):
        RGLAI = Float()
        SLA = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        p = self.params
        DVS = p.TSUMI / p.TSUMAN
        SLACFI = p.SLACF(DVS)
        ISLA = p.SLAC * SLACFI
        LAII = p.WLVGI * ISLA

        self.states = self.StateVariables(kiosk,
                                          publish = ["LAI"],
                                          LAI = LAII)

        self.rates = self.RateVariables(kiosk)

    def calc_rates(self, day, drv, delt):
        self.calculate_specific_leaf_area()
        self.calculate_growth_leaf_area(delt)

    def integrate(self, day, drv, delt = 1):
        k = self.kiosk
        r = self.rates
        s = self.states

        s.LAI += (r.RGLAI - k.RDLAI) * delt

    def calculate_growth_leaf_area(self, delt):
        k = self.kiosk
        r = self.rates
        s = self.states

        if k.EMERG == 0:
            r.RGLAI = 0.
        elif k.REMERG == 1:
            self.calculate_growth_leaf_area_at_emergence(delt)
        elif (k.DVS < 0.20) & (s.LAI < 0.75):
            self.calculate_growth_leaf_area_juvenile_leaves(delt)
        else:
            self.calculate_growth_leaf_area_mature_leaves()

    def calculate_growth_leaf_area_at_emergence(self, delt):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        DVS = p.TSUMI / p.TSUMAN
        SLACFI = p.SLACF(DVS)
        ISLA = p.SLAC * SLACFI
        LAII = k.WLVG * ISLA
        RGLAI = LAII / delt
        r.RGLAI = RGLAI

    def calculate_growth_leaf_area_juvenile_leaves(self, delt):
        r = self.rates
        k = self.kiosk
        p = self.params
        s = self.states

        RGLAI = (s.LAI * (np.exp(p.RGRL * k.DTEFF * delt) - 1.) / delt) * k.TRANRF * np.exp(-p.NLAI * (1.0 - k.NNI))
        r.RGLAI = RGLAI

    def calculate_growth_leaf_area_mature_leaves(self):
        r = self.rates
        k = self.kiosk
        RGLAI = k.RGWLVG * r.SLA
        r.RGLAI = RGLAI

    def calculate_specific_leaf_area(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        SLACF = p.SLACF(k.DVS)
        SLA = p.SLAC * SLACF * np.exp(-p.NSLA * (1.0 - k.NNI))
        r.SLA = SLA