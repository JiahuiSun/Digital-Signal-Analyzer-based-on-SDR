import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pyaudio
import wave
import Queue
import time
from ctypes import *
C_lib = CDLL("./C_lib.so")#load DLL

q = Queue.Queue()
plt_q = Queue.Queue()
tx_q = q
rx_q = q

#get the raw data
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
Kf=3.1
fc=0
cum_data = np.cumsum(raw_data)*(1.0/framerate)
t = np.linspace(0,nframes-1,nframes)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
mod_data = np.cos(Kf*cum_data+2*np.pi*t*fc)+1j*np.sin(Kf*cum_data+2*np.pi*t*fc)

#fix point, move eleven bits to the left and turn into int16
fp_mod_data_real = np.int16(mod_data.real*2048)
fp_mod_data_imag = np.int16(mod_data.imag*2048)

#put each frame into buffer
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

b,a = signal.iirdesign(4./8,5./8,1,40)
FIR_LPF = signal.firwin(2,2./16000)
data_rx = np.empty(frame_len*osr, dtype = complex)
##pre_data = 0

while not rx_q.empty():
    data_buf = rx_q.get()
    ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)

    #decimation
    data_rx.real = np.ctypeslib.as_array(pInput_real).astype(np.int16)
    data_rx.imag = np.ctypeslib.as_array(pInput_imag).astype(np.int16)

    dec_data = signal.decimate(data_rx,120,ftype='fir')

##    out = signal.lfilter(b,a,dec_data)
    out = signal.fftconvolve(FIR_LPF,dec_data)
    #demodulation
    dem_data = np.unwrap(np.diff(np.angle(out)))*1e4
    plt_q.put(dem_data)
##    dem_data = np.unwrap(np.diff(np.angle(dec_data)))*1e4
    play_data = dem_data.astype(np.int16).tostring()
    
##    data_delay = np.insert(dec_data,0,pre_data)
##    pre_data = data_delay[-1]
##    data_delay = np.delete(data_delay,-1)
##    diff_data = dec_data*np.conj(data_delay)
##    ang_data = np.angle(diff_data)
##    audio_data = np.unwrap(ang_data)*1e4
##    play_data = audio_data.astype(np.int16).tostring()
    #plot    
    stream.write(play_data)

while not plt_q.empty():
    data_buf = plt_q.get()
    plt.plot(t[0:frame_len],data_buf)
    plt.show()

stream.close()
p.terminate()

