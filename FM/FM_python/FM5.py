import matplotlib.pyplot as plt
import numpy as np
from scipy import fftpack
from scipy import signal
from scipy import interpolate
import pyaudio
import wave
import Queue
from ctypes import *
import threading
C_lib = CDLL("./C_lib.so")

class th(threading.Thread):
    def __init__(self,func):
        super(th,self).__init__()
        self.func = func
    def run(self):
        self.func()

def send(frame_len,mod_data):
    global tx_q
    interp_output_len = frame_len*osr
    fp_real_buf = (c_short*interp_output_len)()
    fp_imag_buf = (c_short*interp_output_len)()
    fp_mod_data_real = np.floor(mod_data.real*2048).astype(np.int16)
    fp_mod_data_imag = np.floor(mod_data.imag*2048).astype(np.int16)
    while True:
        for frm_idx in range(frame_num):
            fp_buf = (c_short*(interp_output_len*2))()
            fp_real_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)
            fp_imag_buf[:] = interpolate.spline(t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len],interp_t).astype(np.int16)
            of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
            tx_q.put(fp_buf)

def sound(frame_len,samplewidth,nchannels,framerate):
    global qs
    audio = qs.get()
    audio_play = np.empty(frame_len-1,dtype=np.int16)
    for i in range(frame_len-1):
        audio_play[i] = audio[i]
    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)
    while True:
        stream.write(audio_play.tostring())

def defm(frame_len):
    global rx_q
    input_sample_len = frame_len*osr
    pInput_real = (c_double*input_sample_len)()
    pInput_imag = (c_double*input_sample_len)()
    while True:
        audio_data = (c_short*(frame_len))()
        data_rx = np.empty(frame_len, dtype = complex)
        data_buf = rx_q.get()
        ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)
        data_rx.real = pInput_real[::120]
        data_rx.imag = pInput_imag[::120]
        audio_data = (np.unwrap(np.diff(np.angle(data_rx)))*10000).astype(np.int16)
        qs.put(audio_data)

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

#modulation
Kf=3.1
fc=3000
cum_data = np.cumsum(raw_data) / float(framerate)
t = np.linspace(0,nframes,nframes)
interp_t = np.linspace(0,frame_len-1,frame_len*osr)
mod_data = np.cos(Kf*cum_data+2*np.pi*t*fc)+1j*np.sin(Kf*cum_data+2*np.pi*t*fc)

q = Queue.Queue()
qs = Queue.Queue()
tx_q = q
rx_q = q

t2 = th(send(frame_len,mod_data))
t2.start()

t1 = th(defm(frame_len))
t1.start()

t = th(sound(frame_len,samplewidth,nchannels,framerate))
t.start()
