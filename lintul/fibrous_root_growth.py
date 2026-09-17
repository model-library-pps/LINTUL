# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Float

class FibrousRootGrowth(SimulationObject):
    """
    Class to calculate the growth of the rooting depth.

    Simulates the growth of the rooting depth. From emergence rooting depth increases with a constant
    rate, unless there is severe drought. Once the maximum rooting depth is reached, the rooting depth
    does not longer increase.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    ROOTDI          Initial rooting depth                           SCr     m rooted soil
    ROOTDM:         Maximum rooting depth                           SCr     m rooted soil
    RRDMAX          Maximum growth of rooting depth                 SCr     m rooted soil d-1
    ==============  ==============================================  ======  ===========================

     *State variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    ROOTD           Rooting depth                                   Y       m  rooted soil
    ==============  ==============================================  ======  ==============================

    *Rate variables*
    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RROOTD          Growth rate rooting depth                       Y       m rooted soil d-1
    ==============  ==============================================  ======  ==============================
    """

    class Parameters(ParamTemplate):
        ROOTDI = Float()
        ROOTDM = Float()
        RRDMAX = Float()
        WCWP = Float()

    class StateVariables(StatesTemplate):
        ROOTD = Float()

    class RateVariables(RatesTemplate):
        RROOTD = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        p = self.params

        self.states = self.StateVariables(kiosk,
                                          ROOTD = p.ROOTDI,
                                          publish = ["ROOTD"])
        self.rates = self.RateVariables(kiosk,
                                        publish = ["RROOTD"])

    def calc_rates(self, day, drv, delt=1):
        self.calculate_root_growth_rate()

    def calculate_root_growth_rate(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        if k.EMERG == 0:
            RROOTD = 0.
        elif k.WC - p.WCWP <= 0:
            RROOTD = 0.
        else:
            RROOTD = min(p.RRDMAX, p.ROOTDM - s.ROOTD)

        r.RROOTD = RROOTD

    def integrate(self, day, drv, delt=1):
        r = self.rates
        s = self.states

        s.ROOTD += r.RROOTD * delt