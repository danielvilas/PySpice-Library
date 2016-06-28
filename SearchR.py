import numpy as np
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *
from PySpiceDvTools.Loads import *
from PySpiceDvTools.LTSpiceServer import enableLtSpice

circuit = Circuit('Sensor Sim')
circuit.Sinusoidal('1', 'A', circuit.gnd, amplitude=220, frequency=50)

subcir= RlcNonLinearLoad(r=50,l=0.5,c=micro(10))
circuit.subcircuit(subcir)
circuit.X('1', subcir.name, 'A', circuit.gnd)

print (circuit)
simulator = circuit.simulator()
simulator._options['method']='gear'
simulator._options['maxord']='6'
simulator._options['reltol']='0.1'
simulator._options['pivrel']='0.1'
simulator._options['abstol']='1e-10'
analysis = simulator.transient(step_time='100us', end_time='5.2s', start_time='5s')

current = analysis['V1']
aimax = np.amax(current)
aimin = np.amin(current)
print ('Max Current: ',aimax.base)
print ('Min Current: ',aimin.base)

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