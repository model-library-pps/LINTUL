from datetime import datetime
import numpy as np
from pcse.base import SimulationObject
from pcse.traitlets import Instance,  Float, Int
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

hPa_to_kPa = 1e-1

class Penman(SimulationObject):
    class Parameters(ParamTemplate):
        WLVGI = Float()
        SLAC = Float()

    class StateVariables(StatesTemplate):
        pass
    class RateVariables(RatesTemplate):
        PEVAP = Float()
        PTRAN = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["PEVAP", "PTRAN"])

    def calc_rates(self, day, drv, delt):
        r = self.rates
        k = self.kiosk
        p = self.params

        DAVTMP = drv.TEMP
        DTR = drv.IRRAD
        VP = drv.VAP * hPa_to_kPa
        WN = drv.WIND

        DTRJM2 = DTR
        BOLTZM = 5.668E-8
        LHVAP = 2.4E6
        PSYCH = 0.067

        BBRAD = BOLTZM * (DAVTMP + 273.) ** 4 * 86400.
        SVP = 0.611 * np.exp(17.4 * DAVTMP / (DAVTMP + 239.))
        SLOPE = 4158.6 * SVP / (DAVTMP + 239.) ** 2
        RLWN = BBRAD * max(0., 0.55 * (1. - VP / SVP))
        NRADS = DTRJM2 * (1. - 0.15) - RLWN
        NRADC = DTRJM2 * (1. - 0.25) - RLWN
        PENMRS = NRADS * SLOPE / (SLOPE + PSYCH)
        PENMRC = NRADC * SLOPE / (SLOPE + PSYCH)

        WDF = 2.63 * (1.0 + 0.54 * WN)
        PENMD = LHVAP * WDF * (SVP - VP) * PSYCH / (SLOPE + PSYCH)

        PEVAP = np.exp(-0.5 * k.LAI) * (PENMRS + PENMD) / LHVAP
        PEVAP = max(0., PEVAP)
        PTRAN = (1. - np.exp(-0.5 * k.LAI)) * (PENMRC + PENMD) / LHVAP
        PTRAN = max(0., PTRAN)

        r.PEVAP = PEVAP
        r.PTRAN = PTRAN

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states
