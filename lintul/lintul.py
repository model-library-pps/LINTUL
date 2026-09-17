# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

from pcse.traitlets import Instance
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

from lintul.astro import Astro
from lintul.biomass_partitioning import BiomassPartitioning
from lintul.crop_nitrogen_dynamics import CropNitrogenDynamics
from lintul.evapotranspiration import Evapotranspiration
from lintul.fibrous_root_growth import FibrousRootGrowth
from lintul.growth_leaf_area import GrowthLeafArea
from lintul.leaf_senescence import LeafSenescence
from lintul.light_interception_and_growth import LightInterceptionAndGrowth
from lintul.penman import Penman
from lintul.phenology import Phenology
from lintul.root_senescence import RootSenescence
from lintul.nitrogen_stress import NitrogenStress

class LINTUL(SimulationObject):
    """
    Top level object organizing the different components of LINTUL-3

    The CropSimulation object organizes the different processes of the crop
    simulation. Moreover, it contains the parameters, rate and state variables
    which are relevant at the level of the entire crop. The processes that are
    implemented as embedded simulation objects consist of:

    Astro (self.astro)
    BiomassPartitioning (self.biomass_partitioning)
    CropNitrogenDynamics (self.crop_nitrogen_dynamics)
    FibrousRootGrowth (self.fibrous_root_growth)
    GrowthLeafArea (self.growth_leaf_area)
    LeafSenescence (self.leaf_senescence)
    LightInterceptionAndGrowth (self.light_interception_and_growth)
    NitrogenStress (self.nitrogen_stress)
    Penman (self.penman)
    Phenology (self.phenology)
    RootSenescence (self.root_senescence)
    """

    astro = Instance(SimulationObject)
    biomass_partitioning = Instance(SimulationObject)
    crop_nitrogen_dynamics = Instance(SimulationObject)
    evapotranspiration = Instance(SimulationObject)
    fibrous_root_growth = Instance(SimulationObject)
    growth_leaf_area = Instance(SimulationObject)
    leaf_senescence = Instance(SimulationObject)
    light_interception_and_growth = Instance(SimulationObject)
    nitrogen_stress = Instance(SimulationObject)
    penman = Instance(SimulationObject)
    phenology = Instance(SimulationObject)
    root_senescence = Instance(SimulationObject)

    class Parameters(ParamTemplate):
        pass

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.states = self.StateVariables(kiosk)
        self.rates = self.RateVariables(kiosk)

        self.astro = Astro(day, kiosk, parvalues)
        self.penman = Penman(day, kiosk, parvalues)
        self.phenology = Phenology(day, kiosk, parvalues)
        self.fibrous_root_growth = FibrousRootGrowth(day, kiosk, parvalues)
        self.evapotranspiration = Evapotranspiration(day, kiosk, parvalues)
        self.nitrogen_stress = NitrogenStress(day, kiosk, parvalues)
        self.biomass_partitioning = BiomassPartitioning(day, kiosk, parvalues)
        self.leaf_senescence = LeafSenescence(day, kiosk, parvalues)
        self.root_senescence = RootSenescence(day, kiosk, parvalues)
        self.light_interception_and_growth = LightInterceptionAndGrowth(day, kiosk, parvalues)
        self.growth_leaf_area = GrowthLeafArea(day, kiosk, parvalues)
        self.crop_nitrogen_dynamics = CropNitrogenDynamics(day, kiosk, parvalues)

    def calc_rates(self,  day, drv, delt=1):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        self.astro.calc_rates(day, drv, delt)
        self.penman.calc_rates(day, drv, delt)
        self.phenology.calc_rates(day, drv, delt)
        self.fibrous_root_growth.calc_rates(day, drv, delt)
        self.evapotranspiration.calc_rates(day, drv, delt)
        self.nitrogen_stress.calc_rates(day, drv, delt)
        self.biomass_partitioning.calc_rates(day, drv, delt)
        self.leaf_senescence.calc_rates(day, drv, delt)
        self.root_senescence.calc_rates(day, drv, delt)
        self.light_interception_and_growth.calc_rates(day, drv, delt)
        self.growth_leaf_area.calc_rates(day, drv, delt)
        self.crop_nitrogen_dynamics.calc_rates(day, drv, delt)

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states

        self.astro.integrate(day, delt)
        self.penman.integrate(day, delt)
        self.phenology.integrate(day, delt)
        self.fibrous_root_growth.integrate(day, delt)
        self.evapotranspiration.integrate(day, delt)
        self.nitrogen_stress.integrate(day, delt)
        self.biomass_partitioning.integrate(day, delt)
        self.leaf_senescence.integrate(day, delt)
        self.root_senescence.integrate(day, delt)
        self.light_interception_and_growth.integrate(day, delt)
        self.growth_leaf_area.integrate(day, delt)
        self.crop_nitrogen_dynamics.integrate(day, delt)