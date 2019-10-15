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
#from PySpiceDvTools.LTSpiceServer import enableLtSpice
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

circuit.SinusoidalVoltageSource('1', 'A', circuit.gnd, amplitude=220, frequency=50)

subcir= BasicNonLinearLoad(r=27.5,l=0.5)
circuit.subcircuit(subcir)
circuit.X('1', 'BasicNonLinearLoad', 'A', circuit.gnd)


print(circuit)

print(subcir.getRValue())
print(subcir.getLValue())


simulator = circuit.simulator()
#enableLtSpice(simulator)
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

valsr = np.linspace(10,40,61)
valsc05 = []
valsc10 = []

for val in valsr:
    print(val)
    subcir.setLValue(0.5) 
    subcir.setRValue(val)
    analysis = simulator.transient(step_time=1@u_ms, end_time=1@u_s)
    current = analysis['V1']
    max = np.amax(current.data)
    valsc05 = np.append(valsc05, max)
    subcir.setLValue(1) 
    subcir.setRValue(val)
    analysis = simulator.transient(step_time=1@u_ms, end_time=1@u_s)
    current = analysis['V1']
    max = np.amax(current.data)
    valsc10 = np.append(valsc10, max)

plt.subplot(212)
plt.plot(valsr,valsc05,valsr, valsc10)
plt.title('Max Current')
plt.xlabel('Resistance')
plt.ylabel('Amps')
plt.show()
