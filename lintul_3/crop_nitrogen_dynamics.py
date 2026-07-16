# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class CropNitrogenDynamics(SimulationObject):
    """
    Class to simulate the dynamics of nitrogen in the leaves, roots, storage organs, and stems.

    Simulates the amount of N in leaves, roots, storage organs, and stems. The source for N uptake by
    vegetative organs (leaves, roots, stems) are N uptake from the soil. The source for N uptake by
    the storage organs is N translocation from the vegetative organs. Thus, N translocation is a sink
    for the vegetative organs. Furthermore, another sink of N for leaves and roots in N loss due to
    senescence.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    DVSNLT          Development stage above which there is no
                    more N uptake from the soil.                    SCr     -
    DVSNT           Development stage below which there is no N
                    translocation from vegetative organs to
                    storage organs.                                 SCr     -
    FNTRT           Fraction of root to stem and leaf
                    translocatable amount of N.                     SCr     g N g-1 N
    NFRLVI          Initial N concentration in leaves               SCr     g N g-1 DM
    NFRRTI          Initial N concentration in roots                SCr     g N g-1 DM
    NFRSTI          Initial N concentration in stems                SCr     g N g-1 DM
    NMAXSO          Maximum N concentration in storage organs       SCr     g N g-1 DM
    RNFLV           Residual fraction of N in leaves                SCr     g N g-1 DM
    RNFRT           Residual fraction of N in roots                 SCr     g N g-1 DM
    RNFST           Residual fraction of N in stems                 SCr     g N g-1 DM
    TCNT            Time coefficient for N translocation to the
                    storage organs                                  SCr     d
    WLVGI           Initial dry weight leaves                       SCr     g DM m-2 ground
    WRTLI           Initial dry weight roots                        SCr     g DM m-2 ground
    WSTI            Initial dry weight stems                        SCr     g DM m-2 ground
    WCWP            Soil moisture content at wilting point          SCr     mm3 water m-2 soil
    ==============  ==============================================  ======  ===========================

    *State variables*
    ==============  ==============================================  ======  ===========================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ===========================
    ANLV            Amount of N in leaves                           Y       g N m-2 ground
    ANRT            Amount of N in roots                            Y       g N m-2 ground
    ANSO            Amount of N in storage organs                   Y       g N m-2 ground
    ANST            Amount of N in stems                            Y       g N m-2 ground
    ==============  ==============================================  ======  ===========================

    *Rate variables*
    ==============  ==============================================  ======  ===========================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ===========================
    RNSO            Translocation rate of N to storage organs       N       g N m-2 ground d-1
    RNTLV           Translocation rate of N from leaves             N       g N m-2 ground d-1
    RNTRT           Translocation rate of N from roots              N       g N m-2 ground d-1
    RNTST           Translocation rate of N from stems              N       g N m-2 ground d-1
    RNULV           N uptake rate by leaves                         N       g N m-2 ground d-1
    RNURT           N uptake rate by roots                          N       g N m-2 ground d-1
    RNUST           N uptake rate by stems                          N       g N m-2 ground d-1
    RNUPTOT         Total N uptake rate                             Y       g N m-2 ground d-1
    ==============  ==============================================  ======  ===========================

    *Auxiliary variables*
    ==============  ==============================================  ======  ===========================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ===========================
    ATN             Total amount of translocatable N                N       g N m-2 ground
    ATNLV           Amount of translocatable N in leaves            N       g N m-2 ground
    ATNRT           Amount of translocatable N in roots             N       g N m-2 ground
    ATNST           Amount of translocatable N in stems             N       g N m-2 ground
    NDEML           N demand of leaves                              N       g N m-2 ground
    NDEMR           N demand of roots                               N       g N m-2 ground
    NDEMS           N demand of stems                               N       g N m-2 ground
    NDEMSO          Source limited N demand of storage organs       N       g N m-2 ground
    NDEMTO          Total N demand                                  N       g N m-2 ground
    NSUPSO          Supply limited N demand of storage organs       N       g N m-2 ground
    ==============  ==============================================  ======  ===========================
    """

    class Parameters(ParamTemplate):
        DVSNLT = Float()
        DVSNT = Float()
        FNTRT = Float()
        NFRLVI = Float()
        NFRRTI = Float()
        NFRSTI = Float()
        NMAXSO = Float()
        RNFLV = Float()
        RNFRT = Float()
        RNFST = Float()
        TCNT = Float()
        WLVGI = Float()
        WRTLI = Float()
        WSTI = Float()
        WCWP = Float()

    class StateVariables(StatesTemplate):
        ANLV = Float()
        ANRT = Float()
        ANSO = Float()
        ANST = Float()

    class RateVariables(RatesTemplate):
        ATN = Float()
        ATNLV = Float()
        ATNRT = Float()
        ATNST = Float()
        NDEML = Float()
        NDEMR = Float()
        NDEMS = Float()
        NDEMSO = Float()
        NDEMTO = Float()
        NSUPSO = Float()

        RNSO = Float()
        RNTLV = Float()
        RNTRT = Float()
        RNTST = Float()
        RNULV = Float()
        RNURT = Float()
        RNUST = Float()
        RNUPTOT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)

        p = self.params
        ANLVI = p.NFRLVI * p.WLVGI
        ANRTI = p.NFRSTI * p.WRTLI
        ANSTI = p.NFRSTI * p.WSTI
        ANSOI = 0.

        self.states = self.StateVariables(kiosk,
                                          publish = ["ANLV", "ANRT", "ANSO", "ANST"],
                                          ANLV = ANLVI,
                                          ANRT = ANRTI,
                                          ANSO = ANSOI,
                                          ANST = ANSTI,
                                          )
        self.rates = self.RateVariables(kiosk,
                                        publish = ["RNUPTOT"])

    def calc_rates(self, day, drv, delt):
        # self.calculate_actual_n_concentration_green_parts_crop()

        self.calculate_n_demand_leaves()
        self.calculate_n_demand_roots()
        self.calculate_n_demand_stems()
        self.calculate_n_demand_storage_organs()
        self.calculate_n_demand_crop()

        self.calculate_n_uptake_total_rate(delt)
        self.calculate_n_uptake_leaves_rate()
        self.calculate_n_uptake_roots_rate()
        self.calculate_n_uptake_stems_rate()

        self.calculate_translocatable_n_leaves()
        self.calculate_translocatable_n_stems()
        self.calculate_translocatable_n_roots()
        self.calculate_translocatable_n_crop()

        self.calculate_maximum_translocation_rate_to_storage_organs()
        self.calculate_translocation_rate_to_storage_organs()
        self.calculate_translocation_rate_leaves()
        self.calculate_translocation_rate_roots()
        self.calculate_translocation_rate_stems()

    def integrate(self, day, drv, delt = 1):
        k = self.kiosk
        r = self.rates
        s = self.states

        s.ANLV += (r.RNULV - r.RNTLV - k.RDLN) * delt
        s.ANRT += (r.RNURT - r.RNTRT - k.RDRTN) * delt
        s.ANST += (r.RNUST - r.RNTST) * delt
        s.ANSO += r.RNSO * delt

    def calculate_n_demand_crop(self):
        r = self.rates

        NDEMTO = r.NDEML + r.NDEMR + r.NDEMS
        r.NDEMTO = NDEMTO

    def calculate_n_demand_leaves(self):
        k = self.kiosk
        r = self.rates
        s = self.states

        NDEML = max(0, k.NMAXLV * k.WLVG - s.ANLV)
        r.NDEML = NDEML

    def calculate_n_demand_roots(self):
        k = self.kiosk
        r = self.rates
        s = self.states

        NDEMR = max(0, k.NMAXRT * k.WRT - s.ANRT)
        r.NDEMR = NDEMR

    def calculate_n_demand_stems(self):
        k = self.kiosk
        r = self.rates
        s = self.states

        NDEMS = max(0, k.NMAXST * k.WST - s.ANST)
        r.NDEMS = NDEMS

    def calculate_n_demand_storage_organs(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        NDEMSO = max(0, p.NMAXSO * k.WSO - s.ANSO) / p.TCNT
        r.NDEMSO = NDEMSO

    def calculate_n_uptake_leaves_rate(self):
        r = self.rates

        if r.NDEMTO == 0:
            RNULV = 0
        else:
            RNULV = (r.NDEML / r.NDEMTO) * r.RNUPTOT
        r.RNULV = RNULV

    def calculate_n_uptake_roots_rate(self):
        r = self.rates

        if r.NDEMTO == 0:
            RNURT = 0
        else:
            RNURT = (r.NDEMR / r.NDEMTO) * r.RNUPTOT
        r.RNURT = RNURT

    def calculate_n_uptake_stems_rate(self):
        r = self.rates

        if r.NDEMTO == 0:
            RNUST = 0
        else:
            RNUST = (r.NDEMS / r.NDEMTO) * r.RNUPTOT
        r.RNUST = RNUST

    def calculate_n_uptake_total_rate(self, delt):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.EMERG == 0:
            RNUPTOT = 0
        elif k.DVS > p.DVSNLT:
            RNUPTOT = 0
        elif k.WC <= p.WCWP:
            RNUPTOT = 0
        else:
            RNUPTOT = min(k.NAVAIL, r.NDEMTO) / delt
        r.RNUPTOT = RNUPTOT

    def calculate_translocatable_n_crop(self):
        r = self.rates

        ATN = r.ATNLV + r.ATNRT + r.ATNST

        r.ATN = ATN

    def calculate_translocatable_n_leaves(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        ATNLV1 = 0.
        ATNLV2 = s.ANLV - k.WLVG * p.RNFLV
        ATNLV = max(ATNLV1, ATNLV2)

        r.ATNLV = ATNLV

    def calculate_translocatable_n_roots(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        ATNRT1 = (r.ATNLV + r.ATNST) * p.FNTRT
        ATNRT2 = s.ANRT - k.WRT * p.RNFRT
        ATNRT = min(ATNRT1, ATNRT2)

        r.ATNRT = ATNRT

    def calculate_translocatable_n_stems(self):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        ATNST1 = 0.
        ATNST2 = s.ANST - k.WST * p.RNFST
        ATNST = max(ATNST1, ATNST2)

        r.ATNST = ATNST

    def calculate_translocation_rate_leaves(self):
        r = self.rates

        if r.ATN == 0:
            RNTLV = 0
        else:
            RNTLV = r.RNSO * (r.ATNLV / r.ATN)

        r.RNTLV = RNTLV

    def calculate_translocation_rate_roots(self):
        r = self.rates

        if r.ATNRT == 0:
            RNTRT = 0
        else:
            RNTRT = r.RNSO * (r.ATNRT / r.ATN)

        r.RNTRT = RNTRT

    def calculate_translocation_rate_stems(self):
        r = self.rates

        if r.ATNST == 0:
            RNTST = 0
        else:
            RNTST = r.RNSO * (r.ATNST / r.ATN)

        r.RNTST = RNTST

    def calculate_maximum_translocation_rate_to_storage_organs(self):
        p = self.params
        r = self.rates

        NSUPSO = r.ATN / p.TCNT
        r.NSUPSO = NSUPSO

    def calculate_translocation_rate_to_storage_organs(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.DVS <= p.DVSNT:
            RNSO = 0.
        else:
            RNSO = min(r.NDEMSO, r.NSUPSO)
        r.RNSO = RNSO