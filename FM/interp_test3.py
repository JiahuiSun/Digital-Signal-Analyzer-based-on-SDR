import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
from scipy import interpolate
import pyaudio
import wave
import Queue
from ctypes import *
C_lib = CDLL("./C_lib.so")

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
frame_duration = 20e-4
sample_rate = params[2]
file_sample_num = params[3]
sdr_rate = 1.92e6
osr = int(sdr_rate/sample_rate)

frame_len = sample_rate * frame_duration
frame_num = int(np.floor(file_sample_num/frame_len))
frame_len = int(frame_len)

#allocate space for data
interp_output_len = frame_len*osr
fp_real_buf = (c_short*interp_output_len)()
fp_imag_buf = (c_short*interp_output_len)()

#modulation
m=3.1
fc=3000
cum_data = np.cumsum(raw_data) / float(framerate)

t = np.linspace(0,nframes,nframes)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
mod_data = np.cos(m*cum_data+2*np.pi*t*fc)+1j*np.sin(m*cum_data+2*np.pi*t*fc)
fp_mod_data_real = np.floor(mod_data.real*2048).astype(np.int16)
fp_mod_data_imag = np.floor(mod_data.imag*2048).astype(np.int16)

frm_idx = 0
#interpolation
f1 = interpolate.interp1d(t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len],'cubic')
f2 = interpolate.interp1d(t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len],'cubic')
fp_real_buf[:] = f1(interp_t).astype(np.int16)
fp_imag_buf[:] = f2(interp_t).astype(np.int16)

##fp_real_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)
##fp_imag_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)

#np.interp(tar_time,src_time,input_signal)    
##fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
##fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

if frm_idx==0:
    print raw_data[frm_idx*frame_len:(frm_idx+1)*frame_len]
    print fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]
    print fp_real_buf[:]
    #print fp_imag_buf[:]
    
data_rx = np.empty(frame_len, dtype = complex)
##data_rx.real = fp_real_buf[:]
##data_rx.imag = fp_imag_buf[:]
interp_real_deci = signal.decimate(fp_real_buf[:],120)
##interp_real_deci = signal.decimate(fp_imag_buf[:],2,ftype='fir')
i=0
while frm_idx<interp_output_len:
    data_rx.real[i] = fp_real_buf[frm_idx]
    data_rx.imag[i] = fp_imag_buf[frm_idx]
    frm_idx+=120
    i+=1
print data_rx.real[:]
print interp_real_deci[:]





