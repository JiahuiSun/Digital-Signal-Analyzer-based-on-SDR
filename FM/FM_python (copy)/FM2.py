import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
import pyaudio
import wave
import Queue

#open a .wav file
filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')

#get the parameters and turn into array
params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
print params
data = wf.readframes(nframes)
raw_data = np.fromstring(data,dtype=np.short)

#modulation
sig_int = np.cumsum(raw_data) / float(framerate)
m=3.1
fc=30000
t = np.arange(0, nframes) * (1.0 / framerate)
sig_mod=np.cos(m*sig_int+2*np.pi*t*fc)+1j*np.sin(m*sig_int+2*np.pi*t*fc)

#demodulation
audio_data=np.unwrap(np.diff(np.angle(sig_mod)))*10000

#Draw time Domain and frequency domain
f = np.linspace(-framerate/2,framerate/2,len(audio_data));

plta = plt.subplot(3,2,1)
plta.set_title("raw_data")
plt.plot(raw_data)
##
##raw_data_fft = np.fft.fftshift(abs(np.fft.fft(raw_data)))
##pltb = plt.subplot(3,2,2)
##pltb.set_title("raw_data_fft")
##plt.plot(raw_data_fft)
##
##plte = plt.subplot(3,2,5)
##plte.set_title("demod")
##plt.plot(audio_data)
##
##audio_data_fft = np.fft.fftshift(abs(np.fft.fft(audio_data)))
##pltf = plt.subplot(3,2,6)
##pltf.set_title("demod_fre")
##plt.plot(audio_data_fft)
##
####FIR_LP = signal.firwin(2,1/(framerate/2))
####print FIR_LP
plt.show()


###play audio
##p2 = pyaudio.PyAudio()
##stream2 = p2.open(format = p2.get_format_from_width(samplewidth),
##                channels = nchannels,
##                rate = framerate,
##                output = True)
##
##data2 = audio_data.astype(np.dtype(np.int16)).tostring()
####stream2.write(data2)
##stream2.close() 
##p2.terminate()
