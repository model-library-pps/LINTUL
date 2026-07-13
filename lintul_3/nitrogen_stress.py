import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class NitrogenStress(SimulationObject):

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