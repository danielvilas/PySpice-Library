from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit.Units import *

class Sonda(SubCircuitFactory):
    __name__ = 'Sonda'
    __nodes__ = ('CIn', 'COut','VSense', 'VRef')
    
    def __init__(self,
                 turn_ratio=1/500,
                 primary_inductance=100e-6,
                 coupling=1,
                 RShunt=68,
             ):

        super().__init__()
        secondary_inductance = primary_inductance / float(turn_ratio**2)
        primary_inductor = self.L('primary', 'CIn', 'COut', primary_inductance)
        secondary_inductor = self.L('secondary', 'VSense', 'VRef', secondary_inductance)
        self.CoupledInductor('coupling', primary_inductor.name, secondary_inductor.name, coupling)
        self.R('shunt','VSense', 'VRef',RShunt)
