# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class NitrogenStress(SimulationObject):
    """
    Class to simulate the Nitrogen Nutrition Index

    Simulates the daily value of the Nitrogen Nutrition Index (NNI). This index varies from 0 to 1. If
    NNI = 1.0, there is no nitrogen stress. If NNI = 0.0, the degree of nitrogen stress is maximum.
    NNI can drop below 1, once the N concentration in the green parts of the plant drop below an
    optimum concentration. If the NNI value is smaller than 1, various crop variables are affected:
    - The LAI reduces during juvenile growth stages (see light_interception_and_growth.py)
    - The SLA the LAI reduces during mature growth stages (see light_interception_and_growth.py)
    - The partitioning of newly produced dry matter to leaves is reduced (see biomass_partitioning.py)
    - Leaf senescence is enhanced (see leaf_senescence.py)

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    FRNX            Fraction of optimum N concentration and
                    maximum N concentration in leaves and stems     SCr     -
    LRNR            Fraction of maximum N concentration in roots
                    and maximum N concentration in leaves           SCr     -
    LSNR            Fraction of maximum N concentration in stems    SCr     -
                    and maximum N concentration in leaves           SCr     -
    NMXLV           Maximum N concentration in leaves as a
                    function of development stage                   TCr     g N g-1 DM
    RNFLV           Residual N concentration in leaves              SCr     g N g-1 DM
    RNFST           Residual N concentration in stems               SCr     g N g-1 DM
    ==============  ==============================================  ======  ===========================

    *Auxiliary variables*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ===========================
    NFGMR           N concentration of green dry matter (i.e. in
                    leaves and stems)                               N       g N g-1 DM
    NNI             Nitrogen Nutrition Index                        Y       -
    NMAXLV          Maximum N concentration in leaves               Y       g N g-1 DM
    NMAXRT          Maximum N concentration in roots                Y       g N g-1 DM
    NMAXST          Maximum N concentration in stems                Y       g N g-1 DM
    NOPTL           Optimum N concentration in leaves               N       g N g-1 DM
    NOPTLV          Optimum N amount in leaves                      N       g N m-2 ground
    NOPTMR          Optimum N concentration in green dry matter
                    (i.e. in stems and leaves).                     N       g N g-1 DM
    NOPTS           Optimum N concentration in stems                N       g N g-1 DM
    NOPTST          Optimum N amount in stems                       N       g N m-2 ground
    NRMR            Residual N concentration in green dry matter
                    (i.e. in leaves and stems)                      N       g N g-1 DM
    ==============  ==============================================  ======  ===========================

    """
    class Parameters(ParamTemplate):
        FRNX = Float()
        LRNR = Float()
        LSNR = Float()
        NMXLV = AfgenTrait()
        RNFLV = Float()
        RNFST = Float()

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        NFGMR = Float()
        NNI = Float()
        NMAXLV = Float()
        NMAXRT = Float()
        NMAXST = Float()
        NOPTL = Float()
        NOPTLV = Float()
        NOPTMR = Float()
        NOPTS = Float()
        NOPTST = Float()
        NRMR = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["NMAXLV", "NMAXRT", "NMAXST", "NNI"])

    def calc_rates(self, day, drv, delt):
        k = self.kiosk
        r = self.rates
        s = self.states

        self.calculate_maximum_n_concentration_leaves()
        self.calculate_maximum_n_concentration_roots()
        self.calculate_maximum_n_concentration_stems()
        self.calculate_optimum_n_concentration_leaves()
        self.calculate_optimum_n_concentration_stems()
        self.calculate_optimum_n_content_leaves()
        self.calculate_optimum_n_content_stems()
        self.calculate_optimum_n_concentration_green_parts_crop()
        self.calculate_actual_n_concentration_green_parts_crop()
        self.calculate_residual_n_concentration_green_parts_crop()
        self.calculate_nitrogen_nutrition_index(drv)

    def integrate(self, day, drv, delt = 1):
        pass

    def calculate_actual_n_concentration_green_parts_crop(self):
        k = self.kiosk
        r = self.rates

        TBGMR = k.WLVG + k.WST

        if TBGMR == 0:
            NFGMR = 0.
        else:
            NFGMR = (k.ANLV + k.ANST) / TBGMR
        r.NFGMR = NFGMR

    def calculate_maximum_n_concentration_leaves(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        NMAXLV = p.NMXLV(k.DVS)
        r.NMAXLV = NMAXLV

    def calculate_maximum_n_concentration_roots(self):
        p = self.params
        r = self.rates
        NMAXRT = p.LRNR * r.NMAXLV
        r.NMAXRT = NMAXRT

    def calculate_maximum_n_concentration_stems(self):
        p = self.params
        r = self.rates
        NMAXST = p.LSNR * r.NMAXLV
        r.NMAXST = NMAXST

    def calculate_nitrogen_nutrition_index(self, drv):
        k = self.kiosk
        r = self.rates

        tiny = 0.001

        if k.EMERG == 0:
            NNI = 0.
        else:
            NNI1 = (r.NFGMR - r.NRMR)/(r.NOPTMR - r.NRMR)
            NNI2 = tiny
            NNI3 = 1.0
            NNI = min(NNI3, max(NNI1, NNI2))
        r.NNI = NNI

    def calculate_optimum_n_concentration_leaves(self):
        p = self.params
        r = self.rates

        NOPTLV = p.FRNX * r.NMAXLV
        r.NOPTLV = NOPTLV

    def calculate_optimum_n_concentration_stems(self):
        p = self.params
        r = self.rates

        NOPTST = p.FRNX * r.NMAXST
        r.NOPTST = NOPTST

    def calculate_optimum_n_concentration_green_parts_crop(self):
        k = self.kiosk
        r = self.rates
        TBGMR = k.WLVG + k.WST

        if TBGMR == 0:
            NOPTMR = 0.
        else:
            NOPTMR = (r.NOPTL + r.NOPTS) / TBGMR
        r.NOPTMR = NOPTMR

    def calculate_optimum_n_content_leaves(self):
        k = self.kiosk
        r = self.rates

        NOPTL = r.NOPTLV * k.WLVG
        r.NOPTL = NOPTL

    def calculate_optimum_n_content_stems(self):
        k = self.kiosk
        r = self.rates

        NOPTS = r.NOPTST * k.WST
        r.NOPTS = NOPTS

    def calculate_residual_n_concentration_green_parts_crop(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        TBGMR = k.WLVG + k.WST

        if TBGMR == 0:
            NRMR = 0.
        else:
            NRMR = (k.WLVG * p.RNFLV + k.WST * p.RNFST) / TBGMR
        r.NRMR = NRMR