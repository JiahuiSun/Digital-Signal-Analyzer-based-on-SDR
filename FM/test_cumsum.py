import numpy as np
import matplotlib.pyplot as plt

fs = 1e3
fm = 10
##t = np.arange(0, 2*np.pi, 2*np.pi/100)
t = np.arange(0, 1./fm, 1./fs)
m = np.sin(2*np.pi*fm*t)
##plt.figure()

Kf = 3.0
cum = np.cumsum(m)/fs*Kf
plt.figure()
plt.plot(t, cum)

mod = np.exp(1j*cum)
demod = np.unwrap(np.diff(np.angle(mod)))*fs/Kf
print len(demod)
plt.figure()
plt.plot(t, m, '*')
plt.hold(True)
plt.plot(t[1:100], demod)

plt.show()
