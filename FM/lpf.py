from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

##b,a = signal.iirdesign(3./8,4./8,2,40)
b,a = signal.iirdesign([1./8,3./8],[0.5/8,3.5/8],2,40)
w,h = signal.freqz(b,a)
power = 20*np.log10(np.clip(np.abs(h),1e-8,1e100))
fig2, ax2 = plt.subplots()
plt.xlabel('Freq/KHz')
plt.ylabel('dB')
plt.title('freq response')
plt.grid(True)
ax2.plot(w/np.pi*8000,power)
plt.show()
