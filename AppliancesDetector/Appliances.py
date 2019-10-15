from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Unit import *

from PySpiceDvTools.Loads import *

"""
ILabels = {'Microondas 1200Wh' 'Nevera 250Wh' 'Pequeño 15Wh' 'Horno 4000Wh' 'Picos 20A'};
listaRl = [27.5 130.625 2942.5 7.305 6.445];
listaLl = [0.5 2 5 0.5 0.5];
"""

class MicroOndas1200(BasicNonLinearLoad):
    """MicroOndas 1200w"""
    __name__ = 'MicroOndas1200'

    def __init__(self, diodeModel=None):
        super().__init__(diodeModel=diodeModel,r= 27.5, l=0.5)

class Nevera250(BasicNonLinearLoad):
    """Nevera 250w"""
    __name__ = 'Nevera250'

    def __init__(self, diodeModel=None):
        super().__init__(diodeModel=diodeModel,r= 130.625, l=2)


class Pequeno15(BasicNonLinearLoad):
    """Pequeño 15Wh"""
    __name__ = 'Pequeno15'

    def __init__(self, diodeModel=None):
        super().__init__(diodeModel=diodeModel,r= 2942.5, l=5)

class Horno4000(BasicNonLinearLoad):
    """Horno 4000Wh"""
    __name__ = 'Horno4000'

    def __init__(self, diodeModel=None):
        super().__init__(diodeModel=diodeModel,r= 7.305, l=0.5)

class Picos20A(BasicNonLinearLoad):
    """Picos 20A"""
    __name__ = 'Picos20A'

    def __init__(self, diodeModel=None):
        super().__init__(diodeModel=diodeModel,r= 6.445, l=0.5)

