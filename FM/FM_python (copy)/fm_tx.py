import threading, time
import wave
import numpy as np
from ctypes import *

C_lib = CDLL("./C_lib.so")
class fm_tx(threading.Thread):
    def __init__(self,tx_q,params,raw_data):
        threading.Thread.__init__(self)
        self.txq = tx_q
        self.params = params
        self.raw_data = raw_data

    def run(self):
        #set the buffer size
        frame_duration = 20e-3
        sample_rate = self.params[2]
        file_sample_num = self.params[3]*self.params[0]
        sdr_rate = 1.92e6
        osr = int(sdr_rate/sample_rate)

        frame_len = sample_rate * frame_duration
        frame_num = np.int16(file_sample_num/frame_len)
        frame_len = int(frame_len)

        #allocate space for data
        interp_output_len = frame_len*osr
        fp_real_buf = (c_short*interp_output_len)()
        fp_imag_buf = (c_short*interp_output_len)()

        #modulation
        Kf=3.1
        fc=0
        cum_data = np.cumsum(self.raw_data) / float(sample_rate)
        t = np.linspace(0,file_sample_num-1,file_sample_num)
        interp_t = np.linspace(0,frame_len-1,frame_len*osr)
        mod_data = np.cos(Kf*cum_data+2*np.pi*t*fc)+1j*np.sin(Kf*cum_data+2*np.pi*t*fc)

        #fix point, move eleven bits to the left and turn into int16
        fp_mod_data_real = np.int16(mod_data.real*2048)
        fp_mod_data_imag = np.int16(mod_data.imag*2048)

        #put each frame into buffer
        for frm_idx in range(frame_num):
            start_time = time.time()
            fp_buf = (c_short*(interp_output_len*2))()
            
            #interpolation    
            fp_real_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_real[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)
            fp_imag_buf[:] = np.interp(interp_t,t[:frame_len],fp_mod_data_imag[frm_idx*frame_len:(frm_idx+1)*frame_len]).astype(np.int16)

            #combine real and image to one
            of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)
            self.txq.put(fp_buf)
            end_time = time.time()
            
##            print 'tx frame time is ', end_time - start_time
