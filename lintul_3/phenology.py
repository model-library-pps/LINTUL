from datetime import datetime
import numpy as np
from pcse.base import SimulationObject
from pcse.traitlets import Instance, Bool,  Float, Int
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class Phenology(SimulationObject):
    class Parameters(ParamTemplate):
        DOYEM = Int()
        PHOTTB = AfgenTrait()
        TBASE = Float()
        TSUMAN = Float()
        TSUMMT = Float()
        TSUMI = Float()
        WCWP = Float()

    class StateVariables(StatesTemplate):
        EMERG = Int()
        TSUM = Float()

    class RateVariables(RatesTemplate):
        DVS = Float()
        DTEFF = Float()
        REMERG = Int()
        RTSUM = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        p = self.params

        self.states = self.StateVariables(kiosk,
                                          EMERG = 0,
                                          TSUM = p.TSUMI,
                                          publish = ["EMERG", "TSUM"])
        self.rates = self.RateVariables(kiosk,
                                        publish = ["DVS", "DTEFF", "REMERG"])

    def calc_rates(self, day, drv, delt):
        self.calculate_development_stage(day, drv)
        self.determine_emergence_status(day, drv)
        self.calculate_growth_temperature_sum(day, drv)

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states

        s.EMERG += r.REMERG * delt
        s.TSUM += r.RTSUM * delt

    def calculate_development_stage(self, day, drv):
        p = self.params
        r = self.rates
        s = self.states

        # -----DOY
        DOY = drv.DAY.timetuple().tm_yday

        if DOY <= p.DOYEM:
            DVS1 = s.TSUM / p.TSUMAN
            DVS2 = 0.0
        elif s.TSUM <= p.TSUMAN:
            DVS1 = s.TSUM / p.TSUMAN
            DVS2 = 0.
        else:
            DVS1 = 1.0
            DVS2 = (s.TSUM - p.TSUMAN) / p.TSUMMT

        DVS = DVS1 + DVS2
        r.DVS = DVS

    def calculate_growth_temperature_sum(self, day, drv):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        DAVTMP = drv.TEMP
        DTEFF = max(0, DAVTMP - p.TBASE)
        PHOT = p.PHOTTB(k.DAYL)
        RTSUM = DTEFF * PHOT * s.EMERG

        r.DTEFF = DTEFF
        r.RTSUM = RTSUM

    def determine_emergence_status(self, day, drv):
        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        # -----DOY
        DOY = drv.DAY.timetuple().tm_yday

        if s.EMERG == 0:
            if (DOY >= p.DOYEM - 1) & (k.WC > p.WCWP):
                REMERG = 1
            else:
                REMERG = 0
        else:
            REMERG = 0

        r.REMERG = REMERG