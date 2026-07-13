import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

FPAR = 0.5
J_to_MJ = 1e-6

class LightInterceptionAndGrowth(SimulationObject):
    class Parameters(ParamTemplate):
        K = Float()
        LUE = Float()
        NLUE = Float()
        WLVGI = Float()
        WRTLI = Float()
        WSOI = Float()
        WSTI = Float()

    class StateVariables(StatesTemplate):
        WLVG = Float()
        WRT = Float()
        WSO = Float()
        WST = Float()
        WTOT = Float()

    class RateVariables(RatesTemplate):
        FINT = Float()
        PARINT = Float()
        RGWRT = Float()
        RGWLVG = Float()
        RGWSO = Float()
        RGWST = Float()
        RGWTOT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk,
                                        publish = ["RGWTOT", "RGWLVG", "RGWRT", "RGWSO", "RGWST"])

        p = self.params
        WTOTI = p.WLVGI + p.WRTLI + p.WSOI + p.WSTI
        self.states = self.StateVariables(kiosk,
                                          publish = ["WLVG", "WRT", "WSO", "WST"],
                                          WLVG = p.WLVGI,
                                          WRT = p.WRTLI,
                                          WSO = p.WSOI,
                                          WST = p.WSTI,
                                          WTOT = WTOTI)

    def calc_rates(self, day, drv, delt):
        self.calculate_light_interception_rate(drv)
        self.calculate_total_dry_matter_production()
        self.calculate_root_dry_matter_production()
        self.calculate_leaf_dry_matter_production()
        self.calculate_storage_organ_dry_matter_production()
        self.calculate_stem_dry_matter_production()
        self.calculate_storage_organ_dry_matter_production()

    def integrate(self, day, drv, delt = 1):
        k = self.kiosk
        r = self.rates
        s = self.states

        s.WTOT += r.RGWTOT * delt
        s.WLVG += (r.RGWLVG - k.RDLVNS) * delt
        s.WRT += (r.RGWRT - k.RDRT) * delt
        s.WST += r.RGWST * delt
        s.WSO += r.RGWSO * delt

    def calculate_leaf_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWLVG = k.FLV * r.RGWTOT
        r.RGWLVG = RGWLVG

    def calculate_light_interception_rate(self, drv):
        k = self.kiosk
        p = self.params
        r = self.rates

        RAD = drv.IRRAD * J_to_MJ
        FINT =  (1 - np.exp(-p.K * k.LAI))
        PARINT = FPAR * FINT * RAD
        r.FINT = FINT
        r.PARINT = PARINT

    def calculate_root_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWRT = k.FRT * r.RGWTOT
        r.RGWRT = RGWRT

    def calculate_stem_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWST = k.FST * r.RGWTOT
        r.RGWST = RGWST

    def calculate_storage_organ_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWSO = k.FSO * r.RGWTOT
        r.RGWSO = RGWSO

    def calculate_total_dry_matter_production(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.EMERG == 1:
            if k.TRANRF <= k.NNI:
                RGWTOT = k.TRANRF * r.PARINT * p.LUE
            else:
                RGWTOT = r.PARINT * p.LUE * np.exp(-p.NLUE * (1.0 - k.NNI))
        else:
            RGWTOT = 0.
        r.RGWTOT = RGWTOT



