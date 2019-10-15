import numpy as np
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *
from PySpiceDvTools.Loads import *
#from PySpiceDvTools.LTSpiceServer import enableLtSpice

circuit = Circuit('Sensor Sim')
circuit.SinusoidalVoltageSource('1', 'A', circuit.gnd, amplitude=220, frequency=50)

#subcir= RlcNonLinearLoadFullSerie(r=50,l=.35,c=nano(35))
subcir= RlcNonLinearLoadFullParallel(r=200,l=150,c=pico(200))
circuit.subcircuit(subcir)
circuit.X('1', subcir.name, 'A', circuit.gnd)

print (circuit)
simulator = circuit.simulator()
simulator._options['method']='gear'
simulator._options['maxord']='6'
simulator._options['reltol']='0.1'
simulator._options['pivrel']='0.1'
simulator._options['abstol']='1e-10'
analysis = simulator.transient(step_time=100@u_us, end_time=5.2@u_s, start_time=5@u_s)

current = analysis['V1']
aimax = np.amax(current.data)
aimin = np.amin(current.data)
print ('Max Current: ',aimax)
print ('Min Current: ',aimin)

figure1 = plt.figure(1, (20, 10))
#plt.subplot(211)
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

plt.show()