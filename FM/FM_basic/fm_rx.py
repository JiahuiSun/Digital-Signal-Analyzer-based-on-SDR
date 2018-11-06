import numpy as np
from scipy import signal
from ctypes import *
import pyaudio
import threading, time

C_lib = CDLL("./C_lib.so")

class fm_rx(threading.Thread):
    def __init__(self,rx_q,params):
        threading.Thread.__init__(self)
        self.rx_q = rx_q
        self.params = params

    def run(self):
        #set the audio stream
        nchannels,samplewidth,framerate = self.params[:3]
        p = pyaudio.PyAudio()
        stream = p.open(format = p.get_format_from_width(samplewidth),
                        channels = nchannels,
                        rate = framerate,
                        output = True)

        frame_duration = 20e-3
        sdr_rate = 1.92e6
        osr = int(sdr_rate/framerate)
        frame_len = int(framerate * frame_duration)#960
        
        input_sample_len = frame_len*osr#38400
        pInput_real = (c_double*input_sample_len)()
        pInput_imag = (c_double*input_sample_len)()
        
        data_rx = np.empty(frame_len, dtype = complex)
        while True:
            start_time = time.time()

            data_buf = self.rx_q.get(input_sample_len*4)
            ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,input_sample_len)

            t0 = time.time()
            
            #decimation
            tmp_real = np.ctypeslib.as_array(pInput_real).astype(np.int16)
            tmp_imag = np.ctypeslib.as_array(pInput_imag).astype(np.int16)
            
##            data_rx.real = signal.decimate(tmp_real,osr,ftype='fir')
##            data_rx.imag = signal.decimate(tmp_real,osr,ftype='fir')
            
            data_rx.real = tmp_real[::osr]
            data_rx.imag = tmp_imag[::osr]
            
            t1 = time.time()
            
            #demodulation and play audio
            audio_data = np.unwrap(np.diff(np.angle(data_rx)))*framerate/3.1
            audio_data = audio_data.astype(np.int16).tostring()
            
            t2 = time.time()
            
            stream.write(audio_data)
            
            end_time = time.time()
            print 'all', end_time-start_time, 'sepa', t0-start_time, \
                  'down', t1-t0, 'demod', t2-t1           
        stream.close()
        p.terminate()
