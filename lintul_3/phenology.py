# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from datetime import datetime
import numpy as np
from pcse.base import SimulationObject
from pcse.traitlets import Instance, Bool,  Float, Int
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class Phenology(SimulationObject):
    """
    Class to simulate phenological development

    Simulates the phenological development of the crop. The development state is determined by the
    effectve, accumulated amount of heat. The development rate is determined by the effective
    temperature which is, in turn, determined by the base temperature daily minimium and maximum
    tmeperature. It can also be reduced under suboptimal daylengths.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    DOYEM           Day of emergence                                SCr     d
    PHOTTB          Reduction factor of the development rate as
                    a function of daylength                         TSCr    d
    TBASE           Base temperature (i.e. temperature below
                    which there is no development)                  SCr     degC
    TSUMAN          Temperature sum from emergence to anthesis      SCr     degC d
    TSUMMT          Temperature sum from anthesis to maturity       SCr     degC d
    TSUMI           Initial  tmeperature sum from emergence.        SCr     degC d
    WCWP            Soil moisture content at wilting point          SCr     degC d
    ==============  ==============================================  ======  ===========================

    *State variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    EMERG           Indicates whether (=1) or not (=0) the crop
                    has emerged.                                    Y       -
    TSUM            Temperature sum from emergence                  Y       -
    ==============  ==============================================  ======  ==============================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    REMERG          Equals 1 at the day that the crop emerges       Y       -
    RTSUM           Growth rate temperature sum from emergence      Y       degC
    ==============  ==============================================  ======  ==============================

    *Auxiliary variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    DVS             Development stage                               Y       -
    DTEFF           Effective temperature                           Y       degC
    ==============  ==============================================  ======  ==============================

    """
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