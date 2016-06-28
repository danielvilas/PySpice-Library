import numpy as np
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit.Units import *
from PySpice.Spice.BasicElement import *
from PySpice.Spice.HighLevelElement import *
from PySpice.Spice.Simulation import *

circuit = Circuit('NonLineal Load Sim')


'''
V1 A 0 SINE(0 220 50)
D1 0 N001 Def
D2 A N001 Def
D3 N003 A Def
D4 N003 0 Deg
R1 N001 N002 27.5
L1 N002 N003 0.5
.MODEL Def D
'''

circuit.Sinusoidal('1', 'A', circuit.gnd, amplitude=220, frequency=50)
circuit.D('1',circuit.gnd,'N001', model='Def')
circuit.D('2','A','N001',model='Def')
circuit.D('3','N003','A',model='Def')
circuit.D('4','N003',circuit.gnd,model='Def')
circuit.R('1','N001','N002',27.5)
circuit.L('1','N002','N003',0.5)
circuit.model('Def', 'D')


print(circuit)

simulator = circuit.simulator()
analysis = simulator.transient(step_time='1ms', end_time='1s')

current = analysis['V1']
aimax = np.amax(current)
aimin = np.amin(current)
print ('Max Current: ',aimax.base)
print ('Min Current: ',aimin.base)

figure1 = plt.figure(1, (20, 10))
plt.plot(analysis.time, current, '-')
plt.grid()
plt.title('Current')
plt.xlabel('time')
plt.ylabel('Amps')
plt.axhline(y=aimax,color='red')
plt.axhline(y=aimin,color='red')
yticks, ytlabels =plt.yticks()
yticks[-1]=aimax
yticks[-1]=aimin
plt.yticks(yticks)
plt.show()
