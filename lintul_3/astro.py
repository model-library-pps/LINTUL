import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

class Astro(SimulationObject):
    """
    Class to simulate the daylength

    Simulates the daylength for a given combination of latitude and day of the year

    **Auxiliary variable**

    ==============  ==============================================  ======  ===========================
     Name           Description                                     Pbl     Unit
    ==============  ==============================================  ======  ===========================
    DAYL            Daylength                                       Y       h
    ==============  ==============================================  ======  ===========================
    """

    class Parameters(ParamTemplate):
        pass
    class StateVariables(StatesTemplate):
        pass
    class RateVariables(RatesTemplate):
        DAYL = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["DAYL"])

    def calc_rates(self, day, drv, delt):
        r = self.rates

        DOY = drv.DAY.timetuple().tm_yday
        PI = 3.1415926
        SINLAT = np.sin(PI * drv.LAT / 180.)
        COSLAT = np.cos(PI * drv.LAT / 180.)
        SINDCM = np.sin(PI * 23.45 / 180.)
        SINDEC = -SINDCM * np.cos(2. * PI * (DOY + 10.) / 365.)
        COSDEC = np.sqrt(1. - SINDEC * SINDEC)
        A = SINLAT * SINDEC
        B = COSLAT * COSDEC
        DAYL = 12. * (1. + (2. / PI) * np.arcsin(A / B))
        r.DAYL = DAYL

    def integrate(self, day, delt = 1):
        r = self.rates
        s = self.states
