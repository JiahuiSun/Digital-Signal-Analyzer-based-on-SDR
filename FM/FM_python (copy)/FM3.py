import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
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
print params


frame_duration = 20e-3
sample_rate = params[2]
file_sample_num = params[3]
frame_len = sample_rate * frame_duration
frame_num = int(np.floor(file_sample_num/frame_len))
frame_len = int(frame_len)

interp_output_len = frame_len
interp_real_buf = (c_double*interp_output_len)()
interp_imag_buf = (c_double*interp_output_len)()
fp_real_buf = (c_short*interp_output_len)()
fp_imag_buf = (c_short*interp_output_len)()

input_sample_len = frame_len
pInput_real = (c_double*input_sample_len)()
pInput_imag = (c_double*input_sample_len)()

#print frame_duration, sample_rate, file_sample_num, frame_len, frame_num

#modulation
cum_data = np.cumsum(raw_data) / float(framerate)
m=3.1
fc=3000
t = np.arange(0, nframes) * (1.0 / framerate)
mod_data = np.cos(m*cum_data+2*np.pi*t*fc)+1j*np.sin(m*cum_data+2*np.pi*t*fc)
fp_mod_data_real = np.floor(mod_data.real*2048).astype(np.int16)
fp_mod_data_imag = np.floor(mod_data.imag*2048).astype(np.int16)

for frm_idx in range(frame_num):
    fp_buf = (c_short*(interp_output_len*2))()
    fp_real_buf[:] = fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]
    fp_imag_buf[:] = fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]
    
    of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
    tx_q.put(fp_buf)
    
##    data_tx = np.empty(input_sample_len, dtype = complex)
##    data_tx.real = fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]
##    data_tx.imag = fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]
##    tx_q.put(data_tx)

p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)
last_sam = 0
frm_idx = 0
data_rx = np.empty(input_sample_len, dtype = complex)
while not rx_q.empty():

    data_buf = rx_q.get()
    ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)

    data_rx.real = pInput_real[:]
    data_rx.imag = pInput_imag[:]

    diff_data = np.diff(np.angle(data_rx));

    audio_data = np.unwrap(diff_data)*10000
    audio_data = audio_data.astype(np.dtype('<i2')).tostring()
    stream.write(audio_data)

stream.close()
p.terminate()
