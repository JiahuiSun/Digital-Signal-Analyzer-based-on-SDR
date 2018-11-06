import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pyaudio
import wave
import Queue
import time
from ctypes import *
C_lib = CDLL("./C_lib.so")

filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')
params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
str_data = wf.readframes(nframes)
wf.close()

raw_data = np.fromstring(str_data,dtype=np.short)
##t = np.arange(0,nframes)*(1.0/framerate)#generate time sampling
t = np.linspace(0,nframes-1,nframes)

q = Queue.Queue()
tx_q = q
rx_q = q

#set the buffer size
frame_duration = 20e-3
sample_rate = params[2]
file_sample_num = params[3]
sdr_rate = 1.92e6
osr = int(sdr_rate/sample_rate)

frame_len = sample_rate * frame_duration
frame_num = np.int16(file_sample_num/frame_len)
frame_len = int(frame_len)

#allocate space for data
interp_output_len = frame_len*osr
fp_real_buf = (c_short*interp_output_len)()
fp_imag_buf = (c_short*interp_output_len)()

input_sample_len = frame_len*osr
pInput_real = (c_double*input_sample_len)()
pInput_imag = (c_double*input_sample_len)()

#FM modulation and FM data frequency domain waveform
kf = 10
F = 3e3
fc = 0
V = np.max(abs(raw_data))
df = kf*V/2/np.pi
BW = 2*(df+F)
mf = df/F
cum_data = np.cumsum(raw_data)*(1.0/framerate)
mod_data = np.cos(kf*cum_data+2*np.pi*fc*t)+1j*np.sin(kf*cum_data+2*np.pi*fc*t)
freqs = np.fft.fftshift(np.fft.fftfreq(nframes,1.0/framerate))/1000 
fig1, ax1 = plt.subplots()
plt.xlabel('Freq/KHz')
plt.ylabel('Amp')
plt.title('Mod_data')
plt.grid(True)
fft_mod_data = np.fft.fftshift(abs(np.fft.fft(mod_data)/len(mod_data)))
ax1.plot(freqs,fft_mod_data)

#fix point, move eleven bits to the left and turn into int16
fp_mod_data_real = np.int16(mod_data.real*2048)
fp_mod_data_imag = np.int16(mod_data.imag*2048)

##interp_t = np.arange(0,frame_len*osr)*(1./framerate/osr)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
for frm_idx in range(frame_num):
    fp_buf = (c_short*(interp_output_len*2))()
    
    #interpolation:np.interp(tar_time,src_time,input_signal)
    fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
    fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

    #combine real and image to one
    of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
    tx_q.put(fp_buf)

#set the audio stream
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)

data_rx = np.empty(frame_len, dtype = complex)
while not rx_q.empty():
    
    data_buf = rx_q.get()
    ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)

    #decimation
    tmp_real = np.ctypeslib.as_array(pInput_real).astype(np.int16)
    tmp_imag = np.ctypeslib.as_array(pInput_imag).astype(np.int16)
    data_rx.real = signal.decimate(tmp_real,osr,ftype='fir')
    data_rx.imag = signal.decimate(tmp_imag,osr,ftype='fir')

    #bpf design and draw freqency response
    #f0=framerate/2
    b,a = signal.iirdesign(7./8,7.9/8,2,40)
    out = signal.lfilter(b,a,data_rx)
    
    #demodulation and play audio
    audio_data = np.unwrap(np.diff(np.angle(out)))*10000
    play_audio = audio_data.astype(np.int16).tostring()
    stream.write(play_audio)

##w,h = signal.freqz(b,a)
##power = 20*np.log10(np.clip(np.abs(h),1e-8,1e100))
##fig2, ax2 = plt.subplots()
##plt.xlabel('Freq/KHz')
##plt.ylabel('dB')
##plt.title('freq response')
##plt.grid(True)
##ax2.plot(w/np.pi*8000,power)
plt.show()





