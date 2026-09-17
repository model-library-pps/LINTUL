# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from lintul.drunir import Drunir
from pcse.base import ParamTemplate, RatesTemplate, SimulationObject, StatesTemplate
from pcse.traitlets import Float, Instance

cm_to_mm = 1e1
m_to_mm = 1e3

class SoilWaterDynamicsPP(SimulationObject):
    """
    Class to simulate soil water dynamics under potential growth conditions

    This class simulates a fake water balance in which the soil moisture content is always at field capacity.
    
    ** Simulation parameters **

    =================  ==============================================  ======  ===========================
    Name               Description                                     Type    Unit
    =================  ==============================================  ======  ===========================
    ROOTDI             Initial rooting depth                           SCr     mm3 water mm-2 ground d-1
    ROOTDM             Maximum rooting depth                           SCr     m soil
    WCFC               Soil moisture content at field capacity         SCr     m3 water m-3 soil
    =================  ==============================================  ======  ===========================

    ** State variables **

    =================  ==============================================  ======  ===========================
    Name               Description                                     Pbl     Unit
    =================  ==============================================  ======  ===========================
    WA                 Amount of water in rooted soil                  Y       mm3 water mm-2 ground
    WC                 Soil moisture content in rooted soil            Y       mm3 water mm-3 ground
    =================  ==============================================  ======  ===========================

    """

    class Parameters(ParamTemplate):
        WCFC = Float()
        ROOTDI = Float()
        ROOTDM = Float()

    class StateVariables(StatesTemplate):
        WA = Float()
        WC = Float()

    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parameters):
        self.kiosk = kiosk
        self.rates = self.RateVariables(kiosk)
        self.params = self.Parameters(parameters)
        p = self.params
        WAI = p.ROOTDI * p.WCFC * m_to_mm
        WCI = WAI / p.ROOTDI
        self.states = self.StateVariables(kiosk,
                                          publish = ["WA", "WC"],
                                          WA = WAI,
                                          WC = WCI
                                          )
    def calc_rates(self, day, drv):
        pass

    def integrate(self, day, drv):
        k = self.kiosk
        p = self.params
        s = self.states
        WA = k.ROOTD * p.WCFC * m_to_mm
        WC = WA / (k.ROOTD * m_to_mm)
        s.WA = WA
        s.WC = WC

class SoilWaterDynamics(SimulationObject):
    """
    Class to simulate the dynamics of water in the rooted soil

    Simulates the amount of water in the rooted soil. Sources for water in the rooted soil include
    rain and irrigation. Another source consists of root exploration; i.e. more water come available
    due to roots that grow deeper in the rootable soil. Sinks of water are evaporation, transpiration,
    drainage, and surface run-off.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    ROOTDI          Initial rooted depth                            SCr     m soil
    WCI             Initial soil moisture content of rooted soil    SCr     mm3 water mm-3 soil
    WCSUBS          Soil moisture content of subsoil                SCr     mm3 water mm-3 soil
    ==============  ==============================================  ======  ===========================

    *State variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    TDRAIN          Total amount of water removed by drainage       N       mm3 water mm-2 soil
    TEVAP           Total amount of water removed by soil
                    evaporation                                     N       mm3 water mm-2 soil
    TEXPLOR         Total amount of water added by root exploration N       mm3 water mm-2 soil
    TIRRIG          Total amount of water added by irrigation       N       mm3 water mm-2 soil
    TRAIN           Total amount of rain added by precipitation     N       mm3 water mm-2 soil
    TRUNOFF         Total amount of water removed by surface runoff N       mm3 water mm-2 soil
    TTRAN           Total amount of water transpired                N       mm3 water mm-2 soil
    WA              Amount of water in rooted soil                  Y       mm3 water mm-2 soil
    WATBAL          Water balance                                   N       mm3 water mm-2 soil
    WC              Soil moisture content of rooted soil            Y       mm3 water mm-3 soil
    ==============  ==============================================  ======  ==============================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    REVAP           Rate of soil evaporation                        N       mm3 water mm-2 soil d-1
    REXPLOR         Rate of root exploration                        N       mm3 water mm-2 soil d-1
    RTRAN           Rate of actual transpiration                    N       mm3 water mm-2 soil d-1
    RTDRAIN         Rate of change total amount of water lost by
                    drainage                                        N       mm3 water mm-2 soil d-1
    RTEVAP          Rate of change total amount of water lost by
                    soil evaporation                                N       mm3 water mm-2 soil d-1
    RTEXPLOR        Rate of change total amount of water added by
                    root exploration                                N       mm3 water mm-2 soil d-1
    RTIRRIG         Rate of change total amount of water added by
                    root irrigation                                 N       mm3 water mm-2 soil d-1
    RTRAIN          Rate of change total amount of water added by
                    precipitation                                   N       mm3 water mm-2 soil d-1
    RTTRAN          Rate of change total amount of water lost by
                    transpiration                                   N       mm3 water mm-2 soil d-1
    RTRUNOF         Rate of change total amount of water lost by
                    surface run-off                                 N       mm3 water mm-2 soil d-1
    RWA             Rate of change water in rooted soil             N       mm3 water mm-2 soil d-1
    ==============  ==============================================  ======  ==============================
    """

    drunir = Instance(SimulationObject)

    class Parameters(ParamTemplate):
        ROOTDI = Float()
        WCI = Float()
        WCSUBS = Float()

    class StateVariables(StatesTemplate):
        WA = Float()
        WC = Float()

        TDRAIN = Float()
        TEVAP = Float()
        TEXPLOR = Float()
        TIRRIG = Float()
        TTRAN = Float()
        TRUNOFF = Float()
        TRAIN = Float()
        WATBAL = Float()

    class RateVariables(RatesTemplate):
        RWA = Float()
        REVAP = Float()
        REXPLOR = Float()
        RRAIN = Float()
        RTRAN = Float()

        RTDRAIN = Float()
        RTEVAP = Float()
        RTEXPLOR = Float()
        RTIRRIG = Float()
        RTRAIN = Float()
        RTTRAN = Float()
        RTRUNOFF = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        self.rates = self.RateVariables(kiosk, publish = ["REVAP", "RRAIN", "RTRAN"])

        p = self.params
        WAI = m_to_mm * p.ROOTDI * p.WCI

        self.states = self.StateVariables(
            kiosk,
            publish = ["WA", "WC"],
            WA = WAI,
            WC = p.WCI,
            TDRAIN = 0,
            TEVAP = 0,
            TEXPLOR = 0,
            TIRRIG = 0,
            TTRAN = 0,
            TRUNOFF = 0,
            TRAIN = 0,
            WATBAL = 0.
        )

        self.drunir = Drunir(day, kiosk, parvalues)

    def calc_rates(self,  day, drv, delt=1):
        self.calculate_precipitation_rate(drv)
        self.calculate_exploration_rate()
        self.get_soil_evaporation_rate()
        self.get_transpiration_rate()
        self.drunir.calc_rates(day, drv, delt)
        self.calculate_cummulative_rates()
        self.calculate_net_rate_water_amount()

    def integrate(self, day, drv, delt = 1):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        s.WA += r.RWA * delt

        s.TDRAIN += r.RTDRAIN * delt
        s.TEVAP += r.RTEVAP * delt
        s.TEXPLOR += r.RTEXPLOR * delt
        s.TIRRIG += r.RTIRRIG * delt
        s.TTRAN += r.RTTRAN * delt
        s.TRUNOFF += r.RTRUNOFF * delt
        s.TRAIN += r.RTRAIN * delt

        if k.ROOTD == 0.:
            s.WC = 0.
        else:
            s.WC = s.WA / (k.ROOTD * m_to_mm)

        WAI = m_to_mm * p.ROOTDI * p.WCI
        s.WATBAL = s.WA - WAI - s.TRAIN - s.TEXPLOR - s.TIRRIG + s.TRUNOFF + s.TTRAN + s.TEVAP + s.TDRAIN

    def calculate_cummulative_rates(self):
        k = self.kiosk
        r = self.rates

        r.RTDRAIN = k.RDRAIN
        r.RTEVAP = r.REVAP
        r.RTEXPLOR = r.REXPLOR
        r.RTIRRIG = k.RIRRIG
        r.RTTRAN = r.RTRAN
        r.RTRUNOFF = k.RRUNOFF
        r.RTRAIN = r.RRAIN

    def calculate_exploration_rate(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        REXPLOR = m_to_mm * k.RROOTD * p.WCSUBS
        r.REXPLOR = REXPLOR

    def calculate_net_rate_water_amount(self):
        k = self.kiosk
        r = self.rates

        RWA = (r.RRAIN + r.REXPLOR + k.RIRRIG) - (k.RRUNOFF + r.RTRAN + r.REVAP + k.RDRAIN)
        r.RWA = RWA

    def calculate_precipitation_rate(self, drv):
        r = self.rates

        RRAIN = drv.RAIN * cm_to_mm
        r.RRAIN = RRAIN

    def get_soil_evaporation_rate(self):
        k = self.kiosk
        r = self.rates

        REVAP = k.EVAP
        r.REVAP = REVAP

    def get_transpiration_rate(self):
        k = self.kiosk
        r = self.rates

        RTRAN = k.TRAN
        r.RTRAN = RTRAN