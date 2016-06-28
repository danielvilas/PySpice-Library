import numpy as np
from PySpice.Spice.Netlist import SubCircuitFactory

#import PySpice.Logging.Logging as Logging
#logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *

class NarrowBandPassFilterInverted(SubCircuitFactory):
    _Gain = None
    _Fc = None
    _BW = None
    _C = None
    
    _Q = None
    _R3 = None
    _Req = None
    _a = None
    _R2 = None
    _R1 = None

    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')

    def _calc_values(self):
        """
        Q=Fc/Bw
        𝑅3=𝑄/(𝜋 𝐶 𝐹𝑐)
        𝑅𝑒𝑞=𝑅3/(4 𝑄^2)
        𝛼=(2𝑄^2)/𝐺
        𝑅2=𝑅𝑒𝑞*((1+𝛼)/𝛼)
        𝑅1=𝛼𝑅2
        """
        self._Q =self._Fc/self._BW
        self._R3 = self._Q/(np.pi*self._C*self._Fc)
        self._Req=self._R3/(4*pow(self._Q,2) )
        self._a=(2*pow(self._Q,2))/self._Gain
        self._R2=self._Req*(1+self._a)/self._a
        self._R1=self._a*self._R2

    def __init__(self, opAmpModel=None, C=nano(100), Gain=1, Fc=50, BW=10, name = None):
        super().__init__()

        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        self._C=float(C)
        self._Gain =float(Gain)
        self._Fc=float(Fc)
        self._BW=float(BW)

        if name == None:
            name = 'nbpfi_{}_{}_{}'.format(Fc,BW,Gain)
        self.__name__= name
        self.name = name
        self._calc_values()
        self.X('1',opAmpModel,'Ref','N002','V+','V-','Out')
        self.C('1','N001','Out',self._C)
        self.C('2','N001','N002',self._C)
        self.R('1','N001','In',self._R1)
        self.R('2','V-','N001',self._R2)
        self.R('3','N002','Out',self._R3)

class HighPassFilterInverted(SubCircuitFactory):
    _Gain = None
    _Fc = None
    _C = None
    
    _R2 = None
    _R1 = None

    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')

    def _calc_values(self):
        """
        R1=1/(2πFc*C1 )
        R2=G*R1
        """
        self._R1 = 1/(2*np.pi*self._C*self._Fc)
        self._R2=self._Gain*self._R1


    def __init__(self, opAmpModel=None, C=nano(100), Gain=1, Fc=50, name = None):
        super().__init__()

        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        self._C=float(C)
        self._Gain =float(Gain)
        self._Fc=float(Fc)
        
        if name == None:
            name = 'hpfi_{}_{}'.format(Fc,Gain)
        self.__name__= name
        self.name = name
        self._calc_values()
        self.X('1',opAmpModel,'Ref','N002','V+','V-','Out')
        self.C('1','N001','N002',self._C)
        self.R('1','N001','In',self._R1)
        self.R('2','N002','Out',self._R2)

class LowPassFilterInverted(SubCircuitFactory):
    _Gain = None
    _Fc = None
    _C = None
    
    _R2 = None
    _R1 = None

    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')

    def _calc_values(self):
        """
        R1=1/(2πFc*C1 )
        R2=R1/G
        """
        self._R1 = 1/(2*np.pi*self._C*self._Fc)
        self._R2=self._R1/self._Gain


    def __init__(self, opAmpModel=None, C=nano(100), Gain=1, Fc=350, name = None):
        super().__init__()

        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        self._C=float(C)
        self._Gain =float(Gain)
        self._Fc=float(Fc)
        
        if name == None:
            name = 'lpfi_{}_{}'.format(Fc,Gain)
        self.__name__= name
        self.name = name
        self._calc_values()
        self.X('1',opAmpModel,'Ref','N001','V+','V-','Out')
        self.C('1','N001','Out',self._C)
        self.R('1','N001','Out',self._R1)
        self.R('2','In','N002',self._R2)
        self.C('2','N002','N001',micro(10))

class WideBandPassFilterInverted(SubCircuitFactory):
    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')
    _lp=None
    _hp=None

    def attach(self, circuit):
        circuit.subcircuit(self)
        circuit.subcircuit(self._lp)
        circuit.subcircuit(self._hp)
        
    def __init__(self, opAmpModel=None, C=nano(100), Gain=1, Finf=50, Fsup=350, name = None):
        super().__init__()

        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        if name == None:
            name = 'wbpfi_{}_{}_{}'.format(Finf,Fsup,Gain)
        self.__name__= name
        self.name = name
        self._lp=LowPassFilterInverted(opAmpModel=opAmpModel,C=C,Gain=Gain,Fc=Fsup)
        self._hp=HighPassFilterInverted(opAmpModel=opAmpModel,C=C,Gain=Gain,Fc=Finf)
        self.X('1',self._hp.name,'In','N001','Ref','V+','V-')
        self.X('2',self._lp.name,'N001','Out','Ref','V+','V-')

