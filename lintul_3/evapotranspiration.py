# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Int, Float
import numpy as np

cm_to_mm = 1e1
m_to_mm = 1e3

class Evapotranspiration(SimulationObject):
    """
    Class to simulate the actual rates of transpiration and soil evapotranspiration.

    Calculates the actual rates of transpiration and soil evapotranspiration from the previously
    calculated rates of potential transpiration and potential soil evaporation (see penman.py).

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    TRANCO          Transpiration constant (crop characteristic
                    determininig drought tolerance)                 SCr     mm3 water mm-2 soil d-1
    WCFC            Soil moisture content at field capacity         SCr     mm3 water mm-2 soil
    WCAD            Soil moisture content at airdry                 SCr     mm3 water mm-2 soil
    WCST            Soil moisture content at saturation             SCr     mm3 water mm-2 soil
    WCWET           Soil moisture content above which oxygen
                    stress occurs.
    WCWP            Soil moisture content at wilting point          SCr     mm3 water m-2 soil
    WMFAC
    ==============  ==============================================  ======  ===========================

    *State variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    DSLR            Amount of days with low precipitation           N       d
    ==============  ==============================================  ======  ==============================

    *Rate variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    EVAP            Soil evaporation rate                           Y       mm3 water mm-2 soil d-1
    RDSLR           Rate of increase of days with low
                    precipitation                                   N       d d-1
    TRAN            Actual transpiration rate                       Y       mm3 water mm-2 soil d-1
    ==============  ==============================================  ======  ==============================

    *Auxiliary variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    AVAILF          Soil evaporation reduction factor               N       mm3 water mm-3 water
    EVS             Preliminary soil evaporation rate.              N       mm3 water mm-2 soil d-1
    FR              Preliminary transpiration reduction factor.     N       mm3 water mm-3 water
    TRANRF          Transpiration reduction factor.                 Y       mm3 water mm-3 water
    WAAD            Amount of water at airdry.                      N       mm3 water mm-2 water
    WAFC            Amount of water at field capacity.              Y       mm3 water mm-2 water
    WCCR            Soil moisture content below which drought
                    stress occurs.                                  N       mm3 water mm-2 water
    ==============  ==============================================  ======  ==============================
    """
    class Parameters(ParamTemplate):
        TRANCO = Float()
        WCFC = Float()
        WCAD = Float()
        WCST = Float()
        WCWET = Float()
        WCWP = Float()
        WMFAC = Int()

    class StateVariables(StatesTemplate):
        DSLR = Float()

    class RateVariables(RatesTemplate):
        AVAILF = Float()
        EVAP = Float()
        EVS = Float()
        FR = Float()
        RDSLR = Float()
        TRAN = Float()
        TRANRF = Float()
        WAAD = Float()
        WAFC = Float()
        WCCR = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        DSLRI = 1

        self.states = self.StateVariables(kiosk,
                                          DSLR = DSLRI)
        self.rates = self.RateVariables(kiosk,
                                          publish = ["EVAP", "TRAN", "TRANRF", "WAFC"])

    def calc_rates(self, day, drv, delt=1):

        self.calculate_water_amount_at_airdry()
        self.calculate_water_amount_at_field_capacity()
        self.calculate_growth_rate_DSLR(drv, delt)
        self.calculate_soil_evaporation_corrected_for_dry_days(drv)
        self.calculate_critical_soil_moisture_content()
        self.calculate_preliminary_transpiration_reduction_factor()
        self.calculate_evapotranspiration_reduction_factor(delt)
        self.calculate_actual_transpiration_rate()
        self.calculate_actual_soil_evaporation_rate()
        self.calculate_transpiration_reduction_factor()

    def integrate(self, day, drv, delt=1):
        r = self.rates
        s = self.states

        s.DSLR += r.RDSLR

    def calculate_actual_soil_evaporation_rate(self):
        r = self.rates

        r.EVAP = r.AVAILF * r.EVS

    def calculate_actual_transpiration_rate(self):
        k = self.kiosk
        r = self.rates

        r.TRAN = r.FR * r.AVAILF * k.PTRAN

    def calculate_critical_soil_moisture_content(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        WCCR1 = p.WCWP + 0.01
        WCCR2 = p.WCWP + (k.PTRAN / (k.PTRAN + p.TRANCO)) * (p.WCFC - p.WCWP)
        WCCR = max(WCCR1, WCCR2)
        r.WCCR = WCCR

    def calculate_evapotranspiration_reduction_factor(self, delt):
        k = self.kiosk
        r = self.rates

        if r.EVS + r.FR * k.PTRAN == 0:
            AVAILF = 0.
        else:
            WAV = k.WA - r.WAAD
            AVAILF = min(1, WAV / (r.EVS + r.FR * k.PTRAN)) / delt

        r.AVAILF = AVAILF

    def calculate_growth_rate_DSLR(self, drv, delt):
        r = self.rates
        s = self.states

        if drv.RAIN  * cm_to_mm >= 0.5:
            r.RDSLR = (- s.DSLR + 1) / delt
        else:
            r.RDSLR = 1 / delt

    def calculate_preliminary_transpiration_reduction_factor(self):
        p = self.params
        if p.WMFAC == 1:
            self.calculate_preliminary_transpiration_reduction_factor_flooded_rice()
        else:
            self.calculate_preliminary_transpiration_reduction_factor_without_flooded_rice()

    def calculate_soil_evaporation_corrected_for_dry_days(self, drv):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        if drv.RAIN * cm_to_mm >= 0.5:
            EVS = k.PEVAP
        else:
            EVSMXT = k.PEVAP * (np.sqrt(s.DSLR + r.RDSLR) - np.sqrt(s.DSLR + r.RDSLR - 1))
            EVS = min(k.PEVAP, EVSMXT + drv.RAIN * cm_to_mm)

        r.EVS = EVS

    def calculate_transpiration_reduction_factor(self):
        k = self.kiosk
        r = self.rates

        if k.PTRAN == 0.:
            TRANRF = 0.
        else:
            TRANRF = r.TRAN / k.PTRAN
        r.TRANRF = TRANRF

    def calculate_preliminary_transpiration_reduction_factor_without_flooded_rice(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        FR1 = 0
        FR3 = 1.

        if k.WC > r.WCCR:
            FR2 = (p.WCST - k.WC) / (p.WCST - p.WCWET)
        else:
            FR2 = (k.WC - p.WCWP) / (r.WCCR - p.WCWP)
        FR = min(FR3, max(FR1, FR2))

        r.FR = FR

    def calculate_preliminary_transpiration_reduction_factor_flooded_rice(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.WC > r.WCCR:
            FR = 1.
        else:
            FR1 = 0.
            FR2 = (k.WC - p.WCWP) / (r.WCCR - p.WCWP)
            FR3 = 1.
            FR = min(FR3, max(FR1, FR2))

        r.FR = FR

    def calculate_water_amount_at_airdry(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        WAAD = p.WCAD * k.ROOTD * m_to_mm
        r.WAAD = WAAD

    def calculate_water_amount_at_field_capacity(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        WAFC = p.WCFC * k.ROOTD * m_to_mm
        r.WAFC = WAFC
