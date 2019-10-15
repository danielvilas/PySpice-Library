import numpy as np
import matplotlib.pyplot as plt

#import PySpice.Logging.Logging as Logging
#logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *
from PySpiceDvTools.Loads import *
from AppliancesDetector.Appliances import *
from AppliancesDetector.Sonda import *

circuit = Circuit('Sensor Sim')
circuit.SinusoidalVoltageSource('1', 'A', circuit.gnd, amplitude=220, frequency=50)

subcir= MicroOndas1200()
circuit.subcircuit(subcir)
circuit.X('1', subcir.name, 'A', 'SIn')
subcir = Sonda()
circuit.subcircuit(subcir)
circuit.X('2', subcir.name, 'SIn',circuit.gnd,'VSense',circuit.gnd)

print (circuit)
simulator = circuit.simulator()
analysis = simulator.transient(step_time=1@u_ms, end_time=1@u_s)

current = analysis['V1']
aimax = np.amax(current.data)
aimin = np.amin(current.data)
print ('Max Current: ',aimax)
print ('Min Current: ',aimin)

figure1 = plt.figure(1, (20, 10))
plt.subplot(211)
plt.plot(analysis.time, current, '-')
plt.grid()
plt.title('Current')
plt.xlabel('time')
plt.ylabel('Amps')
plt.axhline(y=aimax,color='red')
plt.axhline(y=aimin,color='red')
yticks, ytlabels =plt.yticks()
yticks[-1]=aimax
yticks[-2]=aimin
plt.yticks(yticks)

Vsense = analysis['VSense']
plt.subplot(212)
plt.plot(analysis.time, Vsense, '-')
plt.grid()
plt.title('Current Sensed')
plt.xlabel('time')
plt.ylabel('Voltaje')
plt.show()