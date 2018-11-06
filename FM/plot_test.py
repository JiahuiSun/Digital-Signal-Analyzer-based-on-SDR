import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
import pyaudio
import wave
import Queue

filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')

params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
str_data = wf.readframes(nframes)
wf.close()
raw_data = np.fromstring(str_data,dtype=np.short)

t = np.linspace(0,nframes-1,nframes)
f = np.linspace(-framerate/2,framerate/2,len(raw_data))
freqs = np.fft.fftshift(np.fft.fftfreq(nframes, 1.0/framerate))/1000 #KHz

#the time domain figure of input
plt.subplot(421)
plt.plot(t,raw_data)
raw_data_fft = np.fft.fftshift(abs(np.fft.fft(raw_data)))
plt.subplot(422)
plt.plot(freqs,raw_data_fft)
plt.show()
'''
##freq1 = fftpack.fft(raw_data,raw_data.size)
##freq_plot1 = np.abs(freq1)[0:freq1.size/2+1]
##plt.subplot(422)
##plt.plot(freq_plot1)

kf = 10
F = 3e3
fc = 0
V = np.max(abs(raw_data))
df = kf*V/2/np.pi
BW = 2*(df+F)
mf = df/F
#df= 31601.8055003  BW= 69203.6110007  mf= 10.5339351668

cum_data = np.cumsum(raw_data)*(1.0/framerate)
mod_data = np.cos(kf*cum_data+2*np.pi*fc*t)+1j*np.sin(kf*cum_data+2*np.pi*fc*t)

##mod_data.real = np.int16(mod_data.real*2048)
##mod_data.imag = np.int16(mod_data.imag*2048)

plt.subplot(423)
plt.plot(t,mod_data.real)
plt.subplot(424)
plt.plot(t,mod_data.imag)

freq = fftpack.fft(mod_data,mod_data.size)
freq_plot = np.abs(freq)[0:freq.size/2+1]
plt.subplot(425)
plt.plot(freq_plot)
plt.show()

mod_data_fft = np.fft.fftshift(abs(np.fft.fft(mod_data)))
plt.subplot(424)
plt.plot(freqs,mod_data_fft)

interp_t = np.linspace(0,nframes-1,nframes*120)

interp_data = np.empty(len(mod_data)*120, dtype = complex)
interp_data.real = np.interp(interp_t,t,mod_data.real).astype(np.int16)
interp_data.imag = np.interp(interp_t,t,mod_data.imag).astype(np.int16)

##freqs = np.fft.fftshift(np.fft.fftfreq(nframes, 1.0/framerate/120))/1000 #KHz
##plt.subplot(425)
##plt.plot(interp_t,interp_data)
##interp_data_fft = np.fft.fftshift(abs(np.fft.fft(interp_data)))
##plt.subplot(426)
##plt.plot(freqs,interp_data_fft)
##plt.show()

wp = [(fc-BW/2)/(1.92e6/2),(fc+BW/2)/(1.92e6/2)]
ws = [(fc-BW/2-F)/(1.92e6/2),(fc+BW/2+F)/(1.92e6/2)]
b,a = signal.iirdesign(wp,ws,1,40)
bpf_data = signal.lfilter(b,a,interp_data)

w,h = signal.freqz(b,a)
power = 20*np.log10(np.clip(np.abs(h),1e-8,1e100))
plt.subplot(4,2,7)
plt.plot(w/np.pi*(1.92e6/2),power)

##plt.subplot(4,2,8)
##plt.plot(interp_t,bpf_data)


dec_data = signal.decimate(bpf_data,120,ftype='fir')
##dec_data = signal.decimate(interp_data,120,ftype='fir')
demod_data = np.unwrap(np.diff(np.angle(dec_data)))*10000
audio_data = demod_data.astype(np.int16).tostring()

##plt.subplot(4,2,8)
##plt.plot(demod_data)
##bpf_data_fft = np.fft.fftshift(abs(np.fft.fft(bpf_data)))
##plt.subplot(4,2,8)
##plt.plot(f,bpf_data_fft)
##plt.show()

plt.show()
'''
'''
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)
stream.write(audio_data)
stream.close()
p.terminate()
'''
