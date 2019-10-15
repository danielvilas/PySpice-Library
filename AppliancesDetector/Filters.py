import numpy as np
from PySpice.Spice.Netlist import SubCircuitFactory

#import PySpice.Logging.Logging as Logging
#logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *

class Adder(SubCircuitFactory):
    __nodes__ = ('In50', 'In150', 'In250', 'Out', 'Ref', 'V+','V-')
    __name__  = 'Adder'

    def __init__(self, opAmpModel=None):
        super().__init__()
        self.X('1',opAmpModel,'Ref','N001','V+','V-','Out')
        self.R('1','In50','N001',kilo(6))
        self.R('2','In150','N001',kilo(3))
        self.R('3','In250','N001',kilo(2))
        self.R('4','Out','N001',kilo(2))