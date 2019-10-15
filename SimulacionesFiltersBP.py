import numpy as np
import matplotlib.pyplot as plt

#import PySpice.Logging.Logging as Logging
#logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *

from PySpice.Plot.BodeDiagram import bode_diagram 

#from PySpiceDvTools.LTSpiceServer import enableLtSpice
from PySpiceDvTools.Filters import *
from AppliancesDetector.Filters import *


circuit = circuit = Circuit('Filter')
#circuit.include('Models/BasicOpamp.cir')
circuit.include('Models/AD8619.cir')
filter50 = NarrowBandPassFilterInverted(opAmpModel='AD8619', Fc=50)
circuit.subcircuit(filter50)

filter150 = NarrowBandPassFilterInverted(opAmpModel='AD8619', Fc=150)
circuit.subcircuit(filter150)

filter250 = NarrowBandPassFilterInverted(opAmpModel='AD8619', Fc=250)
circuit.subcircuit(filter250)

adder = Adder(opAmpModel='AD8619')
circuit.subcircuit(adder)


circuit.V('1','5V',circuit.gnd,'5')
circuit.V('2','VRef',circuit.gnd,'2.5')
circuit.SinusoidalVoltageSource('In', 'In', circuit.gnd, amplitude=1)
circuit.X('1',filter50.name,'In','out50','VRef','5V',circuit.gnd)
circuit.X('2',filter150.name,'In','out150','VRef','5V',circuit.gnd)
circuit.X('3',filter250.name,'In','out250','VRef','5V',circuit.gnd)
circuit.X('4',adder.name,'out50','out150','out250','out','VRef','5V',circuit.gnd)


print(circuit)

_C=nano(100)

simulator = circuit.simulator()
#enableLtSpice(simulator)

analysis = simulator.ac(start_frequency=10@u_Hz, stop_frequency=1@u_kHz, number_of_points=200,  variation='dec') 

print('Simulated, Bode plotting...')

figure1 = plt.figure(1, (20, 10))
plt.title("Bode Diagram of a Low-Pass RC Filter")
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out50)),
             phase=np.angle(analysis.out50, deg=False),
             marker='',
             color='blue',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out150)),
             phase=np.angle(analysis.out150, deg=False),
             marker='',
             color='green',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out250)),
             phase=np.angle(analysis.out250, deg=False),
             marker='',
             color='red',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out)),
             phase=np.angle(analysis.out, deg=False),
             marker='',
             color='magenta',
             linestyle='-',
         )
plt.tight_layout()
plt.show() 