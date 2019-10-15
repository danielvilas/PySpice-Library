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
from PySpiceDvTools.SkFilters import *
#from AppliancesDetector.Filters import *

def createCircuit(filter1o,filter2o):
    circuit = Circuit('Filter')
    circuit.include('Models/BasicOpamp.cir')
    circuit.include('Models/AD8619.cir')
    circuit.include('Models/TL084.cir')
    circuit.subcircuit(filter1o)
    circuit.subcircuit(filter2o)

    circuit.V('1','5V',circuit.gnd,'5')
    circuit.V('2','VRef',circuit.gnd,'2.5')
    circuit.SinusoidalVoltageSource('In', 'In', 'VRef', amplitude=1)
    circuit.X('1',filter1o.name,'In','out1o','VRef','5V',circuit.gnd)
    circuit.X('2',filter2o.name,'In','out2o','VRef','5V',circuit.gnd)

    print(circuit)
    return circuit

def simulateAndPrint(figure1, ax1, ax2, circuit, fc0, fc1=None):
    simulator = circuit.simulator()
 #   enableLtSpice(simulator, spice_command='/Applications/LTspice.app/Contents/MacOS/LTspice')

    analysis = simulator.ac(start_frequency=10@u_Hz, stop_frequency=5@u_kHz, number_of_points=500,  variation='dec') 

    print('Simulated, Bode plotting...')

    bode_diagram(axes=(figure1.add_subplot(ax1), figure1.add_subplot(ax2)),
                 frequency=analysis.frequency,
                 gain=20*np.log10(np.absolute(analysis.out1o)),
                 #gain=np.absolute(analysis.out50),
                 phase=np.angle(analysis.out1o, deg=False),
                 marker='',
                 color='blue',
                 linestyle='-',
             )
    bode_diagram(axes=(figure1.add_subplot(ax1), figure1.add_subplot(ax2)),
                 frequency=analysis.frequency,
                 gain=20*np.log10(np.absolute(analysis.out2o)),
                 #gain=np.absolute(analysis.out50),
                 phase=np.angle(analysis.out2o, deg=False),
                 marker='',
                 color='red',
                 linestyle='-',
                 )
    figure1.add_subplot(ax1)
    plt.axvline(x=fc0, linewidth=0.5, color='k')
    if fc1 != None:
        plt.axvline(x=fc1, linewidth=0.5, color='k')
    figure1.add_subplot(ax2)
    plt.axvline(x=fc0, linewidth=0.5, color='k')
    if fc1 != None:
        plt.axvline(x=fc1, linewidth=0.5, color='k')

def testModel(model):
    figure1 = plt.figure(1, (20, 10))
    plt.title('Bode Diagram of Salen Key vs 1 Order ({})'.format(model))

    filterL1 = SKLowPassFilterInverted(opAmpModel=model, Fc=350)
    filterL2 = SKLowPassFilter(opAmpModel=model,R1=470,R2=kilo(3), C1=micro(1),C2=nano(100),name='sklpfi_400')
    circuit = createCircuit(filterL1,filterL2)
    simulateAndPrint(figure1,231,234, circuit,350)

    filterH1 = SKHighPassFilterInverted(opAmpModel=model, Fc=50)
    filterH2 = SKHighPassFilter(opAmpModel=model, R1=kilo(1), R2=kilo(33), C1=micro(4.7),C2=nano(100),name='skhpfi_40')
    circuit = createCircuit(filterH1,filterH2)
    simulateAndPrint(figure1,232,235,circuit,50)

    filter1o = CascadeFilter(fa=filterL1,fb=filterH1,name='wide_50_350')
    filter2o = CascadeFilter(fa=filterL2,fb=filterH2,name='wide_40_400')
    circuit = createCircuit(filter1o,filter2o)
    filter1o.attach(circuit)
    filter2o.attach(circuit)
    simulateAndPrint(figure1,233,236,circuit,50,350)

    plt.tight_layout()
    plt.show()
testModel(model='BasicOpamp')
testModel(model='AD8619')
testModel(model='TL084')
