from datetime import datetime
import numpy as np
from pcse.base import SimulationObject
from pcse.traitlets import Instance,  Float, Int
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

cm_to_mm = 1e1
m_to_mm = 1e3

class Drunir(SimulationObject):
    """
    Class to simulate the rates of drainage, irrigation, and surface run-off.

    Simulate the rates of drainage, irrigation, and surface run-off. The amount of water that is
    removed by drainage during one time step is the minimum of two potential amounts. The first
    potential amount is the difference between the actual amount of water in the rooted soil and the
    amount of water at field capacity in the rooted soil. The second potential amount is a maximum
    amount that can be removed during one time step. If the amount of water in the rooted soil is
    still above the amount of field capacity, the amount of water that is removed by surface-runoff
    equals the amount required to bring the amount of water in the soil at the amount at field capcity.
    Irrigation rates are calculated as a fraction of the amount of water that is required to bring the
    soil moisture content to field capacity after one timestep.

    *Simulation parameters*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ==============================
    DRATE           Maximum drainage rate of the rooted soil.       SCr     mm3 water m-2 rooted soil d-1
    IRRIGF          Fraction of the amount of water that is
                    required to bring the soil moisture content
                    to field capacity that is applied by
                    irrigation.                                     SCr     -
    WCFC            Soil moistore content at field capacity.        SCr     mm3 water m-3 rooted soil
    WCST            Soil moisture content at saturation.            SCr     mm3 water m-3 rooted soil
    WMFAC           Switch to determine whether (=1) or not (=0)
                    the simulated system is flooded rice.           SCr     -
    ==============  ==============================================  ======  ==============================

    *Rate variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RIRRIG          Irrigation rate                                 Y       mm3 water m-2 rooted soil d-1
    RDRAIN          Drainage rate                                   Y       mm3 water m-2 rooted soil d-1
    RRUNOFF         Surface run-off-rate                            Y       mm3 water m-2 rooted soil d-1
    ==============  ==============================================  ======  ==============================

    *Auxiliary variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    WAST            Amount of water in rooted soil at saturation    N       mm3 water m-2 rooted soil
    ==============  ==============================================  ======  ==============================

    """
    class Parameters(ParamTemplate):
        DRATE = Float()
        IRRIGF = Float()
        WCFC = Float()
        WCST = Float()
        WMFAC = Float()

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        RIRRIG = Float()
        RDRAIN = Float()
        RRUNOFF = Float()
        WAST = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["RDRAIN", "RIRRIG", "RRUNOFF"])

    def calc_rates(self, day, drv, delt):
        self.calculate_water_amount_at_saturation()
        self.calculate_drainage_rate(delt)
        self.calculate_surface_runoff_rate(delt)
        self.calculate_irrigation_rate(delt)

    def integrate(self, day, drv, delt = 1):
        pass

    def calculate_drainage_rate(self, delt):
        k = self.kiosk
        p = self.params
        r = self.rates

        RDRAIN1 = 0.
        RDRAIN2 = ((k.WA - k.WAFC) / delt) + (k.RRAIN - k.REVAP - k.RTRAN)
        RDRAIN3 = p.DRATE
        RDRAIN = max(RDRAIN1, min(RDRAIN2, RDRAIN3))
        r.RDRAIN = RDRAIN

    def calculate_irrigation_rate(self, delt):
        p = self.params

        if p.WMFAC == 1.0:
            self.calculate_irrigation_rate_flooded_rice(delt)
        else:
            self.calculate_irrigation_rate_no_flooded_rice(delt)

    def calculate_irrigation_rate_flooded_rice(self, delt):
        k = self.kiosk
        p = self.params
        r = self.rates

        RIRRIG1 = 0
        RIRRIG2 =  ((r.WAST-k.WA)/delt) - (r.RRAIN - r.REVAP - r.RTRAN - r.RDRAIN - r.RRUNOFF)
        RIRRIG = p.IRRIGF * max(RIRRIG1, RIRRIG2)
        r.RIRRIG = RIRRIG

    def calculate_irrigation_rate_no_flooded_rice(self, delt):
        k = self.kiosk
        p = self.params
        r = self.rates

        RIRRIG1 = 0
        RIRRIG2 = ((k.WAFC-k.WA)/delt) - (k.RRAIN - k.REVAP - k.RTRAN - r.RDRAIN - r.RRUNOFF)
        RIRRIG = p.IRRIGF * max(RIRRIG1, RIRRIG2)
        r.RIRRIG = RIRRIG
        return 0

    def calculate_surface_runoff_rate(self, delt):
        k = self.kiosk
        r = self.rates

        RRUNOFF1 = 0.
        RRUNOFF2 = ((k.WA-r.WAST)/delt) + (k.RRAIN - k.REVAP - k.RTRAN - r.RDRAIN)
        RRUNOFF = max(RRUNOFF1, RRUNOFF2)
        r.RRUNOFF = RRUNOFF

    def calculate_water_amount_at_saturation(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        WAST = p.WCST * k.ROOTD * m_to_mm
        r.WAST = WAST

