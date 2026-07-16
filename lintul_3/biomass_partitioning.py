import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

FPAR = 0.5
J_to_MJ = 1e-6

class BiomassPartitioning(SimulationObject):
    """
    Class to simulate the biomass partitioning fractions to leaves, roots, stems, and storage organs.

    Simulates the fraction of newly produced dry matter that is partitioned to different organs. Under
    potential growth conditions, each of these fractions depends on the development stage. Under
    water-limited growth conditions, the fraction of newly produced dry matter that is partitioned to
    the roots increases at the cost of the newly produced dry matter that is partitioned to the shoot
    (i.e. shoot, stems, storage organs). Under N-limited conditions, there is a decreased dry matter
    partitioning to the leaves compared to potential conditions.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    FLVTB           Partitioning fraction to leaves as a function   TCr     g DM g-1 DM
                    of development stage under potential growth
                    conditions.
    FRTTB           Partitioning fraction the to roots as a         TCr     g DM g-1 DM
                    function of development stage under potential
                    growth ocnditions
    FSOTB           Partitioning fraction to the storage organs as
                    a function of development stage under potential TCr     g DM g-1 DM
                    growth conditions.
    FSTTB           Partitioning fraction to the stems as a
                    function of development stage under potential   TCr     g DM g-1 DM
                    growth conditions.
    NPART           Parameter that describes the decrease of the
                    dry matter partitioning to the leaves as a
                    function of the Nitrogen Nutrition Index.       SCr     -
    ==============  ==============================================  ======  ===========================

    *Auxiliary variables

    ==============  ==============================================  ======  ===========================
     Name            Description                                     Pbl     Unit
    ==============  ==============================================  ======  ===========================
    FLV             Fraction of dry matter partitioned to leaves    Y       g DM g-1 DM
    FRT             Fraction of dry matter partitioned to roots     Y       g DM g-1 DM
    FST             Fraction of dry matter partitioned to stems     Y       g DM g-1 DM
    FSO             Fraction of dry matter pratitioned to storage
                    organs.                                         Y       g DM g-1 DM
    ==============  ==============================================  ======  ===========================
    """

    class Parameters(ParamTemplate):
        FLVTB = AfgenTrait()
        FRTTB = AfgenTrait()
        FSTTB = AfgenTrait()
        FSOTB = AfgenTrait()
        NPART = Float()

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

