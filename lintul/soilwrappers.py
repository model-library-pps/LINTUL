from pcse.base import SimulationObject
from pcse.traitlets import Instance
from lintul.soil_water_dynamics import SoilWaterDynamics, SoilWaterDynamicsPP
from lintul.soil_nitrogen_dynamics import SoilNitrogenDynamics, SoilNitrogenDynamicsPP

class BaseSoilWrapper(SimulationObject):
    """Base class for wrapping soil water and nutrient/carbon balances.
    """
    waterbalance_class = None
    nutrientbalance_class = None
    waterbalance = Instance(SimulationObject)
    nutrientbalance = Instance(SimulationObject)

    def initialize(self, day, kiosk, parvalues):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        if self.waterbalance_class is not None:
            self.waterbalance = self.waterbalance_class(day, kiosk, parvalues)
        if self.nutrientbalance_class is not None:
            self.nutrientbalance = self.nutrientbalance_class(day, kiosk, parvalues)

    def calc_rates(self, day, drv):
        if self.waterbalance_class is not None:
            self.waterbalance.calc_rates(day, drv)
        if self.nutrientbalance_class is not None:
            self.nutrientbalance.calc_rates(day, drv)

    def integrate(self, day, delt=1.0):
        if self.waterbalance_class is not None:
            self.waterbalance.integrate(day, delt)
        if self.nutrientbalance_class is not None:
            self.nutrientbalance.integrate(day, delt)

class Lintul_original_PP_SoilWrapper(BaseSoilWrapper):
    waterbalance_class = SoilWaterDynamicsPP
    nutrientbalance_class = SoilNitrogenDynamicsPP

class Lintul_original_WLP_SoilWrapper(BaseSoilWrapper):
    waterbalance_class = SoilWaterDynamics
    nutrientbalance_class = SoilNitrogenDynamicsPP

class Lintul_original_WNLP_SoilWrapper(BaseSoilWrapper):
    waterbalance_class = SoilWaterDynamics
    nutrientbalance_class = SoilNitrogenDynamics
