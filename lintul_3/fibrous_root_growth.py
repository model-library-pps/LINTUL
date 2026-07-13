from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Float

class FibrousRootGrowth(SimulationObject):
    class Parameters(ParamTemplate):
        ROOTDI = Float()
        RRDMAX = Float()
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