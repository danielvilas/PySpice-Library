from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit.Units import *


class NonLinearLoad(SubCircuitFactory):
    """Non Linear Load Subcircuit"""
    __name__ = 'NonLinearLoad'
    __nodes__ = ('Live', 'Neutral')
    __diodeModel__= None
    ##############################################
    def __init__(self,
                 diodeModel=None
             ):

        super().__init__()
        if(diodeModel==None):
            diodeModel = 'DefaultD'
            self.model('DefaultD', 'D')
        __diodeModel__=diodeModel

        self.D('1','Neutral','NPOS', model=diodeModel)
        self.D('2','Live','NPOS',model=diodeModel)
        self.D('3','NNEG','Live',model=diodeModel)
        self.D('4','NNEG','Neutral',model=diodeModel)

class BasicNonLinearLoad(NonLinearLoad):
    """Non Linear Load Subcircuit"""
    __name__ = 'BasicNonLinearLoad'

    def __init__(self, r, l,
                 diodeModel=None
             ):

        super().__init__(diodeModel=diodeModel)
        self.R('1','NPOS','N001',r)
        self.L('1','N001','NNEG',l)

    def setRValue(self,r):
        self['R1'].resistance=r
    def getRValue(self):
        return self['R1'].resistance
    def setLValue(self,l):
        self['L1'].inductance=l
    def getLValue(self):
        return self['L1'].inductance

class RlcNonLinearLoad(NonLinearLoad):
    """Non Linear Load Subcircuit"""
    __name__ = 'RlcNonLinearLoad'

    def __init__(self, r, l, c, 
                 diodeModel=None
             ):

        super().__init__(diodeModel=diodeModel)
        self.R('1','NPOS','N001',r)
        self.L('1','N001','NNEG',l)
        self.C('1','NPOS','NNEG',c)

    def setRValue(self,r):
        self['R1'].resistance=r
    def getRValue(self):
        return self['R1'].resistance
    def setLValue(self,l):
        self['L1'].inductance=l
    def getLValue(self):
        return self['L1'].inductance
    def setCValue(self,c):
        self['C1'].capacitance=l
    def getCValue(self):
        return self['C1'].capacitance

class RlcNonLinearLoadFullSerie(NonLinearLoad):
    """Non Linear Load Subcircuit"""
    __name__ = 'RlcNonLinearLoadFullSerie'

    def __init__(self, r, l, c, 
                 diodeModel=None
             ):

        super().__init__(diodeModel=diodeModel)
        self.R('1','NPOS','N001',r)
        self.L('1','N001','N002',l)
        self.C('1','N002','NNEG',c)

    def setRValue(self,r):
        self['R1'].resistance=r
    def getRValue(self):
        return self['R1'].resistance
    def setLValue(self,l):
        self['L1'].inductance=l
    def getLValue(self):
        return self['L1'].inductance
    def setCValue(self,c):
        self['C1'].capacitance=l
    def getCValue(self):
        return self['C1'].capacitance


class RlcNonLinearLoadFullParallel(NonLinearLoad):
    """Non Linear Load Subcircuit"""
    __name__ = 'RlcNonLinearLoadFullParallel'

    def __init__(self, r, l, c, 
                 diodeModel=None
             ):

        super().__init__(diodeModel=diodeModel)
        self.R('1','NPOS','NNEG',r)
        self.L('1','NPOS','NNEG',l)
        self.C('1','NPOS','NNEG',c)

    def setRValue(self,r):
        self['R1'].resistance=r
    def getRValue(self):
        return self['R1'].resistance
    def setLValue(self,l):
        self['L1'].inductance=l
    def getLValue(self):
        return self['L1'].inductance
    def setCValue(self,c):
        self['C1'].capacitance=l
    def getCValue(self):
        return self['C1'].capacitance