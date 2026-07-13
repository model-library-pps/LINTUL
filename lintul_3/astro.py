import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

class Astro(SimulationObject):
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

        # -----DOY
        DOY = drv.DAY.timetuple().tm_yday

        # -----PI VALUE
        PI = 3.1415926

        # SINE AND COSINE OF LATITUDE
        SINLAT = np.sin(PI * drv.LAT / 180.)
        COSLAT = np.cos(PI * drv.LAT / 180.)

        # MAXIMAL SINE OF DECLINATION
        SINDCM = np.sin(PI * 23.45 / 180.)

        # SINE AND COSINE OF DECLINATION(EQUATIONS 3.4, 3.5)
        SINDEC = -SINDCM * np.cos(2. * PI * (DOY + 10.) / 365.)
        COSDEC = np.sqrt(1. - SINDEC * SINDEC)

        # THE  TERMS A AND B ACCORDING TO EQUATION 3.3
        A = SINLAT * SINDEC
        B = COSLAT * COSDEC

        # DAYLENGTH ACCORDING TO EQUATION 3.6
        r.DAYL = 12. * (1. + (2. / PI) * np.arcsin(A / B))

    def integrate(self, day, delt = 1):
        r = self.rates
        s = self.states
