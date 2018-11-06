import numpy as np
from scipy import signal
from scipy import interpolate
from scipy import fftpack
import pyaudio
import wave
import Queue
import time
from ctypes import *
C_lib = CDLL("./C_lib.so")#load DLL
import matplotlib.pyplot as plt

q = Queue.Queue()
tx_q = q
rx_q = q

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

#modulation
##Kf=3.1
Kf=5*8e3/max(raw_data)
print Kf

fc=30000
cum_data = np.cumsum(raw_data)*(1.0/framerate)
t = np.linspace(0,nframes-1,nframes)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
mod_data = np.cos(Kf*cum_data+2*np.pi*t*fc)+1j*np.sin(Kf*cum_data+2*np.pi*t*fc)

#fix point, move eleven bits to the left and turn into int16
fp_mod_data_real = np.int16(mod_data.real*2048)
fp_mod_data_imag = np.int16(mod_data.imag*2048)

time1 = time.time()

#put each frame into buffer
for frm_idx in range(frame_num):
    fp_buf = (c_short*(interp_output_len*2))()
    
    #interpolation:np.interp(tar_time,src_time,input_signal)
    fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
    fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

    #combine real and image to one
    of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
    tx_q.put(fp_buf)
        
time4 = time.time()
print "interp_time",time4 - time1

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
    

    #demodulation and play audio
    audio_data = np.unwrap(np.diff(np.angle(data_rx)))*framerate/Kf
    play_audio = audio_data.astype(np.int16)

    stream.write(play_audio.tostring())


time5 = time.time()
print "bofangshjian",time5-time4
plt.figure()
plt.plot(np.arange(0, len(play_audio))/framerate, play_audio, 'o')
plt.hold(True)
plt.plot(np.arange(0, len(cum_data))/framerate, cum_data)
plt.show()
stream.close()
p.terminate()
