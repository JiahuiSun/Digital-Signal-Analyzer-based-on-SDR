from ctypes import *
import math, time
import numpy as np
import threading
import fm_top
C_lib = CDLL("work/C_lib.so")


class update_data(threading.Thread):
    rx_stop = 1
    
    def __init__(self, rxq, fm_q, sample_freq, sample_len, data):
        threading.Thread.__init__(self)
        self.sf = sample_freq
        self.sl = sample_len
        self.rxq = rxq
        self.fm_q = fm_q
        self.data = data

    def run(self):
        data_duration = self.sl/self.sf
        pInput_real = (c_double*self.sl)()
        pInput_imag = (c_double*self.sl)()

##        print 'update data start'
        while update_data.rx_stop == 0:
            data_buf = self.rxq.get(self.sl*4)# *4是因为一个double占4个字节            
            if fm_top.fm_stop == 0:
                self.fm_q.put(data_buf)
            else:
                time.sleep(data_duration)
                ok_separater = C_lib.CSM_data_separater(data_buf,pInput_real,pInput_imag,self.sl)
                self.data.real = pInput_real[:]
                self.data.imag = pInput_imag[:]

##        print 'update data ended'
