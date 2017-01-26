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

class SKHighPassFilter(SubCircuitFactory):
    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')
    
    _Gain = None
    _Fc = None
    _C1 = None
    _C2 = None
    
    _R2 = None
    _R1 = None
    _R3 = None
    _R4 = None
    
    _Q = None
    
    def __init__(self, opAmpModel=None, R1=None, R2= None, R3=None, R4=None, C1=None,C2=None, name = None):
        super().__init__()
        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")
        
        if self._C1==None:
            self._C1=C1
        if self._C2==None:
            self._C2=C2
        
        if self._R1==None:
            self._R1=R1
        if self._R2==None:
            self._R2=R2
        if self._R3==None:
            self._R3=R3
        if self._R4==None:
            self._R4=R4
        if self.__name__==None:
            self.__name__=name
            self.name = name
        if self.__name__==None:
            self.__name__='skhpfi'
            self.name = name
    
        self.R('1','N001','Out',self._R1)
        self.R('2','N002','Ref',self._R2)
        self.C('1','N001','In',self._C1)
        self.C('2','N002','N001',self._C2)
        
        if (R3 == None) & (R4 == None):
            self._Gain=1;
            # + - Vp Vn out
            self.X('1',opAmpModel,'N002','Out','V+','V-','Out')
        elif(R3 != None) & (R4 != None):
            self.R('3','N003','Ref',self._R3)
            self.R('4','N003','Out',self._R4)
            self.X('1',opAmpModel,'N002','N003','V+','V-','Out')
            self._Gain=1+R4/R3
        else:
            raise NotImplementedError("R3 and R4 goes in tandem")


class SKHighPassFilterInverted(SKHighPassFilter):
    def _calc_values(self):
        """
            K= - 1, Solve R
            C1=C2
            
            Gain = 1
            W0=2πFc;
            R1= 1/(2Q W0 C)
            R2= 2Q/(W0 C)
        """
        w0=2*np.pi*self._Fc
        self._R1 = 1/(2*self._Q*w0*self._C1)
        self._R2=(2*self._Q)/(self._C1 * w0)


    def __init__(self, opAmpModel=None, C=nano(100), Fc=50, Q=1, name = None):

        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")
        Gain=1;
        self._C1=float(C)
        self._C2=float(C)
        self._Gain =float(Gain)
        self._Fc=float(Fc)
        self._Q=float(Q)
        
        if name == None:
            name = 'skhpfi_{}_{}'.format(Fc,Gain)
        self.__name__= name
        self.name = name
        self._calc_values()
        super().__init__(opAmpModel=opAmpModel)


class SKLowPassFilter(SubCircuitFactory):
    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')
    
    _Gain = None
    _Fc = None
    _C1 = None
    _C2 = None
    
    _R2 = None
    _R1 = None
    _R3 = None
    _R4 = None
    
    _Q = None

    def __init__(self, opAmpModel=None, R1=None, R2= None, R3=None, R4=None, C1=None,C2=None, name = None):
        super().__init__()
        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        if self._C1==None:
            self._C1=C1
        if self._C2==None:
            self._C2=C2
                        
        if self._R1==None:
            self._R1=R1
        if self._R2==None:
            self._R2=R2
        if self._R3==None:
            self._R3=R3
        if self._R4==None:
            self._R4=R4
        if self.__name__==None:
            self.__name__=name
            self.name = name
        if self.__name__==None:
            self.__name__='sklpfi'
            self.name = name

        self.R('1','N001','In',self._R1)
        self.R('2','N002','N001',self._R2)
        self.C('1','N001','Out',self._C1)
        self.C('2','N002','Ref',self._C2)

        if (R3 == None) & (R4 == None):
            self._Gain=1;
            # + - Vp Vn out
            self.X('1',opAmpModel,'N002','Out','V+','V-','Out')
        elif(R3 != None) & (R4 != None):
            self.R('3','N003','Ref',self._R3)
            self.R('4','N003','Out',self._R4)
            self.X('1',opAmpModel,'N002','N003','V+','V-','Out')
            self._Gain=1+R4/R3
        else:
            raise NotImplementedError("R3 and R4 goes in tandem")


class SKLowPassFilterInverted(SKLowPassFilter):

    def _calc_values(self):
        """
        K= - 1, Solve C
        Gain = 1
        W0=2πFc;
        C1= (Q/W0)*(1/R1+1/R2)
        C2= 1/(Q W0 (R1+R2))
        """
        w0=2*np.pi*self._Fc
        self._C1=(self._Q/w0)*(1/self._R1+1/self._R2)
        self._C2=1/(self._Q*w0 *(self._R1+self._R2))


    def __init__(self, opAmpModel=None, R1=kilo(100), R2= kilo(100), Fc=350, Q=1, name = None):
        self._R1=float(R1)
        self._R2=float(R2)
        self._Fc=float(Fc)
        self._Q=float(Q)
        if name == None:
            name = 'sklpfi_{}_{}'.format(Fc,1)
        self.__name__= name
        self.name = name
        self._calc_values()
        super().__init__(opAmpModel=opAmpModel)


class SKWideBandPassFilterInverted(SubCircuitFactory):
    __nodes__ = ('In', 'Out', 'Ref', 'V+','V-')
    _lp=None
    _hp=None

    def attach(self, circuit):
        circuit.subcircuit(self)
        circuit.subcircuit(self._lp)
        circuit.subcircuit(self._hp)
        
    def __init__(self, opAmpModel=None, C=nano(100), R1=kilo(100), R2= kilo(100), Finf=50, Fsup=350, name = None):
        super().__init__()
        Gain=1
        if opAmpModel == None:
            raise NotImplementedError("This Filters needs An Operational Model")

        if name == None:
            name = 'skwbpfi_{}_{}_{}'.format(Finf,Fsup,Gain)
        self.__name__= name
        self.name = name
        self._lp=SKLowPassFilterInverted(opAmpModel=opAmpModel, R1=R1, R2=R2,Fc=Fsup)
        self._hp=SKHighPassFilterInverted(opAmpModel=opAmpModel,C=C,Fc=Finf)
        self.X('1',self._hp.name,'In','N001','Ref','V+','V-')
        self.X('2',self._lp.name,'N001','Out','Ref','V+','V-')

