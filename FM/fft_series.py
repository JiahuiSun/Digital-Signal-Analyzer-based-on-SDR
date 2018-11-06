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
t = np.arange(0,nframes)*(1.0/framerate)#generate time sampling
#draw the frequency domain waveform
fig, ax = plt.subplots()
plt.xlabel('Freq/KHz')
plt.ylabel('Amp')
plt.title('raw_data')
plt.grid(True)
freqs = np.fft.fftshift(np.fft.fftfreq(nframes,1.0/framerate))/1000
fft_raw_data = np.fft.fftshift(abs(np.fft.fft(raw_data)/len(raw_data)))
ax.plot(freqs,fft_raw_data)
#FM modulation
kf = 10
F = 3e3
fc = 0
V = np.max(abs(raw_data))
df = kf*V/2/np.pi
BW = 2*(df+F)
mf = df/F
cum_data = np.cumsum(raw_data)*(1.0/framerate)
mod_data = np.cos(kf*cum_data+2*np.pi*fc*t)+1j*np.sin(kf*cum_data+2*np.pi*fc*t)
#FM data frequency domain waveform
fig1, ax1 = plt.subplots()
plt.xlabel('Freq/KHz')
plt.ylabel('Amp')
plt.title('Mod_data')
plt.grid(True)
fft_mod_data = np.fft.fftshift(abs(np.fft.fft(mod_data)/len(mod_data)))
ax1.plot(freqs,fft_mod_data)
#bpf design and draw freqency response
#f0=framerate/2
##b,a = signal.iirdesign(7.5/8,7.9/8,2,40)
##w,h = signal.freqz(b,a)
##power = 20*np.log10(np.clip(np.abs(h),1e-8,1e100))
##fig2, ax2 = plt.subplots()
##plt.xlabel('Freq/KHz')
##plt.ylabel('dB')
##plt.title('freq response')
##plt.grid(True)
##ax2.plot(w/np.pi*8000,power)
plt.show()

#output after bpf
##out = signal.lfilter(b,a,mod_data)
##fig3, ax3 = plt.subplots()
##plt.xlabel('Freq/KHz')
##plt.ylabel('Amp')
##plt.title('bpf_out_data')
##plt.grid(True)
##fft_out = np.fft.fftshift(abs(np.fft.fft(out)/len(out)))
##ax3.plot(freqs,fft_out)
##plt.show()

#interplotation
itp_t = np.arange(0,nframes*120)*(1./framerate/120) 
interp_data = np.empty(len(mod_data)*120, dtype = complex)
interp_data.real = np.interp(interp_t,t,mod_data.real).astype(np.int16)
interp_data.imag = np.interp(interp_t,t,mod_data.imag).astype(np.int16)
#demodulation and play the audio
demod_data = np.unwrap(np.diff(np.angle(out)))*10000
audio_data = demod_data.astype(np.int16).tostring()
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)
stream.write(audio_data)
stream.close()
p.terminate()




