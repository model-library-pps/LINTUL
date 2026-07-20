# -*- coding: utf-8 -*-
# Herman Berghuijs (herman.berghuijs@wur.nl)
# July 2026

import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate

FPAR = 0.5
J_to_MJ = 1e-6

class LightInterceptionAndGrowth(SimulationObject):
    """
    Class to calculate the daily light interception and dry matter production.

    Simulates the daily light interception and the dry matter production rates for each organ (i.e.
    leaves, roots, storage organs, and stems). Light interception is simulated according to Lambert
    Beer's law. The total dry matter production under potential conditions is calculated as the
    product of the light use efficiency and the amount of intercepted PAR. Under water- or
    nitrogen-limited conditions, the total dry matter production is reduced. The newly produced dry
    matter that is assigned to an organ is calculated by mulitplying the total dry matter production
    with the dry partitioning fraction of dry of that organ that was previously (see
    biomass_partitioning.py) calculated.

    *Simulation parameters*

    ==============  ==============================================  ======  ===========================
     Name            Description                                    Type     Unit
    ==============  ==============================================  ======  ===========================
    K               Light extinction coefficient                    SCr     m2 ground m-2 leaf
    LUE             Light use efficiency                            SCr     g DM MJ-1 PAR
    NLUE            Parameter in function that describes the
                    relationship between Nitrogen Nutrition Index
                    and the total dry matter production under
                    nitrogen-limited conditions.                    SCr     -
    WLVGI           Inital leaf dry matter weight                   SCr     g DM m-2 ground
    WRTLI           Inital root matter weight                       SCr     g DM m-2 ground
    WSOI            Inital storage organ dry matter weight          SCr     g DM m-2 ground
    WSTI            Inital stem dry matter weight                   SCr     g DM m-2 ground
    ==============  ==============================================  ======  ===========================

    *State variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    CBAL            Dry weight balance                              N       g DM m-2 ground
    WDRT            Dead root dry matter weight                     N       g DM m-2 ground
    WLVD            Dead leaf dry matter weight                     N       g DM m-2 ground
    WLVG            Green leaf dry matter weight                    Y       g DM m-2 ground
    WLV             Living and dead leaf dry matter weight          Y       g DM m-2 ground
    WRT             Living root dry matter weight                   Y       g DM m-2 ground
    WSO             Storage organ dry matter weight                 Y       g DM m-2 ground
    WST             Stem dry matter weight                          Y       g DM m-2 ground
    WTOT            Total weight of dry matter produced (including
                    dry matter that died).                          N       g DM m-2 ground
    ==============  ==============================================  ======  ==============================

    *Rate variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    RGWRT           Growth rate root dry matter                     Y       g DM m-2 ground d-1
    RGWLVG          Growth rate leaf dry matter                     Y       g DM m-2 ground d-1
    RGWSO           Growth rate storage organ dry matter            Y       g DM m-2 ground d-1
    RGWST           Growth rate stem dry matter                     Y       g DM m-2 ground d-1
    RGWTOT          Total growth rate dry matter                    Y       g DM m-2 ground d-1
    ==============  ==============================================  ======  ==============================

     *Auxiliary variables*

    ==============  ==============================================  ======  ==============================
     Name            Description                                    Pbl     Unit
    ==============  ==============================================  ======  ==============================
    FINT            Fraction of PAR intercepted                     N       MJ radiation MJ-1 radiation
    PARINT          Amount of PAR intercepted                       N       MJ PAR m-2 ground d-1
    ==============  ==============================================  ======  ==============================
    """

    class Parameters(ParamTemplate):
        K = Float()
        LUE = Float()
        NLUE = Float()
        WLVGI = Float()
        WRTLI = Float()
        WSOI = Float()
        WSTI = Float()

    class StateVariables(StatesTemplate):
        CBAL = Float()
        WDRT = Float()
        WLV = Float()
        WLVD = Float()
        WLVG = Float()
        WRT = Float()
        WSO = Float()
        WST = Float()
        WTOT = Float()

    class RateVariables(RatesTemplate):
        FINT = Float()
        PARINT = Float()
        RGWRT = Float()
        RGWLVG = Float()
        RGWSO = Float()
        RGWST = Float()
        RGWTOT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk,
                                        publish = ["RGWTOT", "RGWLVG", "RGWRT", "RGWSO", "RGWST"])

        p = self.params
        self.states = self.StateVariables(kiosk,
                                          publish = ["WLVG", "WRT", "WSO", "WST"],
                                          CBAL = 0.,
                                          WDRT = 0.,
                                          WLV = p.WLVGI,
                                          WLVD = 0.,
                                          WLVG = p.WLVGI,
                                          WRT = p.WRTLI,
                                          WSO = p.WSOI,
                                          WST = p.WSTI,
                                          WTOT = 0.)

    def calc_rates(self, day, drv, delt):
        self.calculate_light_interception_rate(drv)
        self.calculate_total_dry_matter_production()
        self.calculate_root_dry_matter_production()
        self.calculate_leaf_dry_matter_production()
        self.calculate_storage_organ_dry_matter_production()
        self.calculate_stem_dry_matter_production()
        self.calculate_storage_organ_dry_matter_production()

    def integrate(self, day, drv, delt = 1):
        k = self.kiosk
        p = self.params
        r = self.rates
        s = self.states

        s.WTOT += r.RGWTOT * delt
        s.WLV += r.RGWLVG * delt
        s.WLVG += (r.RGWLVG - k.RDLVNS) * delt
        s.WLVD += k.RDLVNS * delt
        s.WDRT += k.RDRT * delt
        s.WRT += (r.RGWRT - k.RDRT) * delt
        s.WST += r.RGWST * delt
        s.WSO += r.RGWSO * delt

        s.CBAL = s.WTOT + (p.WRTLI + p.WLVGI + p.WSTI + p.WSOI) - (s.WLV + s.WST + s.WSO + s.WRT + s.WDRT)
        print(s.CBAL)

    def calculate_leaf_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWLVG = k.FLV * r.RGWTOT
        r.RGWLVG = RGWLVG

    def calculate_light_interception_rate(self, drv):
        k = self.kiosk
        p = self.params
        r = self.rates

        RAD = drv.IRRAD * J_to_MJ
        FINT =  (1 - np.exp(-p.K * k.LAI))
        PARINT = FPAR * FINT * RAD
        r.FINT = FINT
        r.PARINT = PARINT

    def calculate_root_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWRT = k.FRT * r.RGWTOT
        r.RGWRT = RGWRT

    def calculate_stem_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWST = k.FST * r.RGWTOT
        r.RGWST = RGWST

    def calculate_storage_organ_dry_matter_production(self):
        r = self.rates
        k = self.kiosk

        RGWSO = k.FSO * r.RGWTOT
        r.RGWSO = RGWSO

    def calculate_total_dry_matter_production(self):
        k = self.kiosk
        p = self.params
        r = self.rates

        if k.EMERG == 1:
            if k.TRANRF <= k.NNI:
                RGWTOT = k.TRANRF * r.PARINT * p.LUE
            else:
                RGWTOT = r.PARINT * p.LUE * np.exp(-p.NLUE * (1.0 - k.NNI))
        else:
            RGWTOT = 0.
        r.RGWTOT = RGWTOT



