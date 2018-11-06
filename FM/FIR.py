import scipy.signal as signal
import numpy as np
import pylab as pl
import wave
import pyaudio
def h_ideal(n,fc):
    return 2*fc*np.sinc(2*fc*np.arange(-n,n,1.0))

b = h_ideal(30,0.25)#fixpoint:0.25=fc/fs
b2 = signal.firwin(len(b),0.5)#cutoff = fc/(fs/2)
w,h = signal.freqz(b)#w/(2*pi)=f/fs
w2,h2 = signal.freqz(b2)

pl.figure(figsize=(8,6))
pl.subplot(211)
pl.plot(w/2/np.pi,20*np.log10(np.abs(h)),label=u"h_ideal")
pl.plot(w/2/np.pi,20*np.log10(np.abs(h2)),label=u"firwin")
pl.xlabel("Freq")
pl.ylabel("Amp/dB")
pl.legend()
pl.subplot(212)
pl.plot(b,label=u"h_ideal")
pl.plot(b2,label=u"firwin")
pl.legend()
pl.show()
'''
#get the audio data
filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')
params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
data = wf.readframes(nframes)
raw_data = np.fromstring(data,dtype=np.short)

#set the buffer size
frame_duration = 20e-3
sample_rate = params[2]
file_sample_num = params[3]
sdr_rate = 1.92e6
osr = int(sdr_rate/sample_rate)

audio_data = signal.fftconvolve(b2,raw_data)

#set the audio stream
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = int(framerate),
                output = True)

play_data = audio_data.astype(np.int16).tostring()
stream.write(play_data)
    
stream.close()
p.terminate()
'''
