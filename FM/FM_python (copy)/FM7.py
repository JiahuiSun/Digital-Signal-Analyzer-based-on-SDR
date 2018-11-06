import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
from scipy import interpolate
import pyaudio
import wave
import Queue
from ctypes import *#ctypes library,same with C
C_lib = CDLL("./C_lib.so")#load DLL

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
frame_num = np.floor(file_sample_num/frame_len).astype(np.int16)
frame_len = int(frame_len)

#allocate space for data
interp_output_len = frame_len*osr
fp_real_buf = (c_short*interp_output_len)()
fp_imag_buf = (c_short*interp_output_len)()

input_sample_len = frame_len*osr
pInput_real = (c_double*input_sample_len)()
pInput_imag = (c_double*input_sample_len)()

#modulation
Kf=3.1
fc=3000
cum_data = np.cumsum(raw_data) / float(framerate)
t = np.linspace(0,nframes,nframes)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
mod_data = np.cos(Kf*cum_data+2*np.pi*t*fc)+1j*np.sin(Kf*cum_data+2*np.pi*t*fc)

#fix point, move eleven bits to the left and turn into int16
fp_mod_data_real = np.floor(mod_data.real*2048).astype(np.int16)
fp_mod_data_imag = np.floor(mod_data.imag*2048).astype(np.int16)

#put each frame into buffer
for frm_idx in range(frame_num):
    fp_buf = (c_short*(interp_output_len*2))()
    
    #interpolation
##    #plan 1:
##    f1 = interpolate.interp1d(t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len],'quadratic')
##    f2 = interpolate.interp1d(t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len],'quadratic')
##    interp_data_real = f1(interp_t)
##    interp_data_imag = f2(interp_t)
##    fp_real_buf[:] = interp_data_real.astype(np.int16)
##    fp_imag_buf[:] = interp_data_imag.astype(np.int16)
    
#   plan 2:
    fp_real_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)
    fp_imag_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)
    
###   plan 3: np.interp(tar_time,src_time,input_signal)    
##    fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
##    fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

    #combine real and image to one
    of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
    tx_q.put(fp_buf)

#set the audio stream
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)

last_sam = 0
data_rx = np.empty(frame_len, dtype = complex)
##data_rx = np.empty(frame_len+1, dtype = complex)

while not rx_q.empty():
    data_buf = rx_q.get()
    ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)

##    #decimation
    #plan 1:
    data_rx.real = pInput_real[::120]
    data_rx.imag = pInput_imag[::120]

##    data_rx.real[1:] = pInput_real[::120]
##    data_rx.imag[1:] = pInput_imag[::120]
##    data_rx[0] = last_sam
##    last_sam = data_rx[frame_len]
    
##    #plan 2:
##    data_rx.real = signal.decimate(pInput_real[:],120,ftype='fir')
##    data_rx.imag = signal.decimate(pInput_imag[:],120,ftype='fir')
    
##    if last_sam==0:
##        print fp_mod_data_real[:frame_len]
##        print fp_mod_data_imag[:frame_len]
##        print data_rx
##        last_sam+=1

    #demodulation and play audio
##    audio_data = np.unwrap(np.diff(np.angle(data_rx)))*10000
    delta = data_rx[0:-1]*data_rx[1:].conj()
    angs = np.angle(delta)*10000
    audio_data = angs.astype(np.int16).tostring()
    stream.write(audio_data)

stream.close()
p.terminate()
