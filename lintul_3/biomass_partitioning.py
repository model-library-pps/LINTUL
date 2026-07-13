import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

FPAR = 0.5
J_to_MJ = 1e-6

class BiomassPartitioning(SimulationObject):
    class Parameters(ParamTemplate):
        FLVTB = AfgenTrait()
        FRTTB = AfgenTrait()
        FSTTB = AfgenTrait()
        FSOTB = AfgenTrait()
        NPART = Float()
        WLVGI = Float()
        WRTLI = Float()
        WSOI = Float()
        WSTI = Float()

    class StateVariables(StatesTemplate):
        pass

    class RateVariables(RatesTemplate):
        FLV = Float()
        FST = Float()
        FRT = Float()
        FSO = Float()
        FLVMOD = Float()
        FRTMOD = Float()
        FSH = Float()
        FSHMOD = Float()
        MODIF = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk, publish = ["FLV", "FRT","FSO", "FST"])
        self.states = self.StateVariables(kiosk)

    def calc_rates(self, day, drv, delt):
        self.calculate_biomass_partitioning_fractions()

    def calculate_biomass_partitioning_fractions(self):
        k = self.kiosk

        if k.NNI >= k.TRANRF:
            self.calculate_biomass_partitioning_fraction_to_roots()
            self.calculate_biomass_partitioning_fraction_to_shoots()
            self.calculate_biomass_partitioning_fraction_to_leaves()
            self.calculate_biomass_partitioning_fraction_to_stems()
            self.calculate_biomass_partitioning_fraction_to_storage_organs()
        else:
            self.calculate_biomass_partitioning_fraction_to_leaves_nlimited()
            self.calculate_biomass_partitioning_fraction_to_roots_nlimited()
            self.calculate_biomass_partitioning_fraction_to_stems_nlimited()
            self.calculate_biomass_partitioning_fraction_to_storage_organs_nlimited()

    def calculate_biomass_partitioning_fraction_to_leaves(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        FLVWET = p.FLVTB(k.DVS)
        FLV = FLVWET * r.FSHMOD
        r.FLV = FLV

    def calculate_biomass_partitioning_fraction_to_leaves_nlimited(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        FLVWET = p.FLVTB(k.DVS)
        FLVMOD = np.exp(-p.NPART * (1.0 - k.NNI))
        FLV = FLVWET * FLVMOD
        MODIF = (1. - FLV) / (1. - (FLV / FLVMOD))
        r.FLV = FLV
        r.FLVMOD = FLVMOD
        r.MODIF = MODIF

    def calculate_biomass_partitioning_fraction_to_roots(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        FRTWET = p.FRTTB(k.DVS)
        FRTMOD = max(1., 1. / (k.TRANRF + 0.5))
        FRT = FRTWET * FRTMOD
        r.FRT = FRT
        r.FRTMOD = FRTMOD

    def calculate_biomass_partitioning_fraction_to_roots_nlimited(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        FRTWET = p.FRTTB(k.DVS)
        FRT = FRTWET * r.MODIF
        r.FRT = FRT

    def calculate_biomass_partitioning_fraction_to_shoots(self):
        r = self.rates
        FSHMOD = (1. - r.FRT) / (1. - r.FRT / r.FRTMOD)
        r.FSHMOD = FSHMOD

    def calculate_biomass_partitioning_fraction_to_stems(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        FSTWET = p.FSTTB(k.DVS)
        FST = FSTWET * r.FSHMOD
        r.FST = FST

    def calculate_biomass_partitioning_fraction_to_stems_nlimited(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        FSTWET = p.FSTTB(k.DVS)
        FST = FSTWET * r.MODIF
        r.FST = FST

    def calculate_biomass_partitioning_fraction_to_storage_organs(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        FSOWET = p.FSOTB(k.DVS)
        FSO = FSOWET * r.FSHMOD
        r.FSO = FSO

    def calculate_biomass_partitioning_fraction_to_storage_organs_nlimited(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        FSOWET = p.FSOTB(k.DVS)
        FSO = FSOWET * r.MODIF
        r.FSO = FSO

    def integrate(self, day, drv, delt = 1):
        r = self.rates
        s = self.states

