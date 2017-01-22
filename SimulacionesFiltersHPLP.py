import numpy as np
import matplotlib.pyplot as plt

#import PySpice.Logging.Logging as Logging
#logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *

from PySpice.Plot.BodeDiagram import bode_diagram 

from PySpiceDvTools.LTSpiceServer import enableLtSpice
from PySpiceDvTools.Filters import *
from AppliancesDetector.Filters import *

circuit = circuit = Circuit('Filter')
circuit.include('Models/BasicOpamp.cir')
circuit.include('Models/AD8619.cir')
circuit.include('Models/TL084.cir')

filter50 = HighPassFilterInverted(opAmpModel='AD8619',Fc=50)
circuit.subcircuit(filter50)
filter2 = LowPassFilterInverted(opAmpModel='AD8619', Fc=350)
circuit.subcircuit(filter2)
filter3 = WideBandPassFilterInverted(opAmpModel='AD8619')
filter3.attach(circuit)

circuit.V('1','5V',circuit.gnd,'5')
circuit.V('2','VRef',circuit.gnd,'2.5')
circuit.Sinusoidal('In', 'In', circuit.gnd, amplitude=1)
circuit.X('1',filter50.name,'In','out50','VRef','5V',circuit.gnd)
circuit.X('2',filter2.name,'In','out350','VRef','5V',circuit.gnd)
circuit.X('3',filter2.name,'out50','out','VRef','5V',circuit.gnd)
circuit.X('4',filter3.name,'In','out2','VRef','5V',circuit.gnd)

print(circuit)

simulator = circuit.simulator()
enableLtSpice(simulator, spice_command='/Applications/LTspice.app/Contents/MacOS/LTspice')

analysis = simulator.ac(start_frequency=10, stop_frequency=kilo(5), number_of_points=500,  variation='dec') 

print('Simulated, Bode plotting...')


figure1 = plt.figure(1, (20, 10))
plt.title("Bode Diagram of a Low-Pass RC Filter")
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out50)),
             #gain=np.absolute(analysis.out50),
             phase=np.angle(analysis.out50, deg=False),
             marker='',
             color='blue',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out350)),
             #gain=np.absolute(analysis.out2),
             phase=np.angle(analysis.out350, deg=False),
             marker='',
             color='red',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out)),
             #gain=np.absolute(analysis.out2),
             phase=np.angle(analysis.out, deg=False),
             marker='',
             color='magenta',
             linestyle='-',
         )
bode_diagram(axes=(plt.subplot(211), plt.subplot(212)),
             frequency=analysis.frequency,
             gain=20*np.log10(np.absolute(analysis.out2)),
             #gain=np.absolute(analysis.out2),
             phase=np.angle(analysis.out2, deg=False),
             marker='',
             color='green',
             linestyle='-',
         )
plt.tight_layout()
plt.show() 
