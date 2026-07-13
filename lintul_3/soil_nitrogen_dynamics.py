from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Float
from pcse.util import AfgenTrait

class SoilNitrogenDynamics(SimulationObject):
    class Parameters(ParamTemplate):
        DVSNLT = Float()
        NRFTAB = AfgenTrait
        FERTAB = AfgenTrait()

    class StateVariables(StatesTemplate):
        NAVAIL = Float()
        TNSOIL = Float()

    class RateVariables(RatesTemplate):
        RFERTN = Float()
        RFERTNTOT = Float()
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