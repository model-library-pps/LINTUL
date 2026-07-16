# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Float
from pcse.util import AfgenTrait

class SoilNitrogenDynamics(SimulationObject):
    """
    Class to simulate the dynamics of available nitrogen in the soil

    Simulates the amount of nitrogen in the soil that is available for uptake. Sources for available
    nitrogen are nitrogen fertilization and mineralization. The only sink for available nitrogen is
    root uptake.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    DVSNLT          Development stage above which there is no
                    net mineralization.                             SCr     -
    FERTAB          Nitrogen fertilization rate as a function of
                    day of the year                                 TCr     g N m-2 ground d-1
    NERTAB          Fraction of applied nitrogen that becomes
                    available as a function of year                 TCr     g N g-1 N
    ==============  ==============================================  ======  ===========================

    *State variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    NAVAIL          Amount of available nitrogen in next time step  Y       g N m-2 ground
    TNSOIL          Amount of available nitrogen                    N       g N m-2 ground
    ==============  ==============================================  ======  ==============================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RFERTN          Effective fertilization rate                    N       g N m-2 ground d-1
    RNUPT           Root nitrogen uptake                            N       g N m-2 ground d-1
    RTMIN           Net nitrogen mineralization rate                N       g N m-2 ground d-1
    ==============  ==============================================  ======  ==============================

    *Auxiliary variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    NRF             Fraction of applied nitrogen that becomes
                    available                                       N       -
    ==============  ==============================================  ======  ==============================
    """

    class Parameters(ParamTemplate):
        DVSNLT = Float()
        FERTAB = AfgenTrait()
        NRFTAB = AfgenTrait


    class StateVariables(StatesTemplate):
        NAVAIL = Float()
        TNSOIL = Float()

    class RateVariables(RatesTemplate):
        RFERTN = Float()
        RNUPT = Float()
        RTMIN = Float()
        NRF = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        TNSOILI = 0.

        self.states = self.StateVariables(kiosk,
                                          publish = ["NAVAIL"],
                                          TNSOIL = TNSOILI,
                                          NAVAIL = TNSOILI)
        self.rates = self.RateVariables(kiosk)

    def calc_rates(self, day, drv, delt=1):
        self.calculate_net_mineralization_rate()
        self.calculate_total_n_fertilization_rate(drv)
        self.calculate_recovery_fraction(drv)
        self.calculate_effective_n_fertilization_rate()

    def integrate(self, day, drv, delt=1):
        k = self.kiosk
        r = self.rates
        s = self.states

        s.TNSOIL += (r.RTMIN + r.FERTNS - k.RNUPTOT) * delt
        s.NAVAIL = s.TNSOIL

    def calculate_effective_n_fertilization_rate(self):
        r = self.rates
        FERTNS = r.NRF * r.FERTNTOT
        r.FERTNS = FERTNS

    def calculate_net_mineralization_rate(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.EMERG == 0:
            RTMIN = 0.
        elif k.DVS <= p.DVSNLT:
            #TODO As soon as the model is fully built, replace this hard coded value of 0.10 g N d-1 with a parameter
            RTMIN = 0.10
        else:
            RTMIN = 0.
        r.RTMIN = RTMIN

    def calculate_recovery_fraction(self, drv):
        p = self.params
        r = self.rates
        DOY = drv.DAY.timetuple().tm_yday
        NRF = p.NRFTAB(DOY)
        r.NRF = NRF

    def calculate_total_n_fertilization_rate(self, drv):
        p = self.params
        r = self.rates

        DOY = drv.DAY.timetuple().tm_yday
        FERTNTOT = p.FERTAB(DOY)
        r.FERTNTOT = FERTNTOT