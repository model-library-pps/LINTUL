import numpy as np
from pcse.traitlets import Float
from pcse.base import SimulationObject, ParamTemplate, StatesTemplate, RatesTemplate
from pcse.util import AfgenTrait

class CropNitrogenDynamics(SimulationObject):
    class Parameters(ParamTemplate):
        DVSNLT = Float()
        DVSNT = Float()
        FRNX = Float()
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