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
from AppliancesDetector.Appliances import *
from AppliancesDetector.Sonda import *
from PySpiceDvTools.SkFilters import *
from PySpiceDvTools.Filters import CascadeFilter
from scipy.fftpack import fft,fftfreq
from scipy.signal import resample

circuit = Circuit('Sensor Sim')

model = 'BasicOpamp'

circuit.include('Models/BasicOpamp.cir')
circuit.include('Models/AD8619.cir')
circuit.include('Models/TL084.cir')

microwave= MicroOndas1200()
sonda = Sonda()
vRef = VoltageReference (opAmpModel=model)

filterL = SKLowPassFilter(opAmpModel=model,R1=470,R2=kilo(3), C1=micro(1),C2=nano(100),name='sklpfi_400')
filterH = SKHighPassFilter(opAmpModel=model, R1=kilo(1), R2=kilo(33), C1=micro(4.7),C2=nano(100),name='skhpfi_40')
filter2o = CascadeFilter(fa=filterL,fb=filterH,name='wide_40_400')

circuit.subcircuit(microwave)
circuit.subcircuit(sonda)
circuit.subcircuit(vRef)
circuit.subcircuit(filter2o)
filter2o.attach(circuit)

circuit.SinusoidalVoltageSource('1', 'A', circuit.gnd, amplitude=220, frequency=50)
circuit.V('2','5V',circuit.gnd,'5')
circuit.X('1', microwave.name, 'A', 'SIn')
circuit.X('2', vRef.name, '5V', 'VRef',circuit.gnd)
circuit.X('3', sonda.name, 'SIn',circuit.gnd,'VSense','VRef')
circuit.X('4',filter2o.name,'VSense','VFilter','VRef','5V',circuit.gnd)

print (circuit)
simulator = circuit.simulator()
#enableLtSpice(simulator, spice_command='/Applications/LTspice.app/Contents/MacOS/LTspice')
analysis = simulator.transient(step_time=1@u_ms, end_time=1@u_s)

current = analysis['V1']
aimax = np.amax(current.data)
aimin = np.amin(current.data)
print ('Max Current: ',aimax)
print ('Min Current: ',aimin)

figure1 = plt.figure(1, (20, 10))
plt.subplot(321)
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
plt.subplot(322)
nTime=np.linspace(0.0, 1.0, num=5000);
yf = np.interp(nTime,analysis.time,current)
yf = fft(yf)
x =fftfreq(yf.size,1.0/yf.size)
plt.plot(x[1:500], np.abs(yf[1:500]), '-')
plt.grid()
plt.title('Frec Current Sensed PF ({})'.format(model))
plt.xlabel('Freq')
plt.ylabel('Pos-Filter')

Vsense = analysis['VSense']
plt.subplot(323)
plt.plot(analysis.time, Vsense, '-')
plt.grid()
plt.title('Current Sensed')
plt.xlabel('time')
plt.ylabel('Voltaje')

plt.subplot(324)
nTime=np.linspace(0.0, 1.0, num=5000);
yf = np.interp(nTime,analysis.time,Vsense)
yf = fft(yf)
x =fftfreq(yf.size,1.0/yf.size)
plt.plot(x[1:500], np.abs(yf[1:500]), '-')
plt.grid()
plt.title('Frec Current Sensed PF ({})'.format(model))
plt.xlabel('Freq')
plt.ylabel('Pos-Filter')

Vsense = analysis['VFilter']
plt.subplot(325)
plt.plot(analysis.time,Vsense, '-')
plt.grid()
plt.title('Current Sensed PF ({})'.format(model))
plt.xlabel('time')
plt.ylabel('Pos-Filter')

plt.subplot(326)
nTime=np.linspace(0.0, 1.0, num=5000);
yf = np.interp(nTime,analysis.time,Vsense)
yf = fft(yf)
x =fftfreq(yf.size,1.0/yf.size)
plt.plot(x[1:500], np.abs(yf[1:500]), '-')
plt.grid()
plt.title('Frec Current Sensed PF ({})'.format(model))
plt.xlabel('Freq')
plt.ylabel('Pos-Filter')

plt.show()
