from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

class RootSenescence(SimulationObject):
    class Parameters(ParamTemplate):
        DVSDR = Float()
        RNFRT = Float()

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        RDRT = Float()
        RDRTN = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk, publish = ["RDRT", "RDRTN"])

    def calc_rates(self, day, drv, delt):
        self.calculate_death_root_dry_matter_rate()
        self.calculate_n_loss_root()

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states

    def calculate_death_root_dry_matter_rate(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        #TODO As soon as the model is built, define this variable as a parameter instead of a hard-coded value.
        RDRRT = 0.03

        if k.DVS < p.DVSDR:
            RDRT = 0
        else:
            RDRT = k.WRT * RDRRT
        r.RDRT = RDRT

    def calculate_n_loss_root(self):
        p = self.params
        r = self.rates

        RDRTN = p.RNFRT * r.RDRT
        r.RDRTN = RDRTN