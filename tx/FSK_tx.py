from ctypes import *
import math, time
import numpy as np
import threading
#from spectrum import *
import matplotlib.pyplot as plt

#from param_setting import *
#from tx.init_state import *
from tx.function import *


C_lib = CDLL("work/C_lib.so")
resample_lib = CDLL("work/resample_lib.so")


class FSK_TX(threading.Thread):
    def __init__(self, mod_order, txq):
        threading.Thread.__init__(self)
        self.mod_order = mod_order
        self.txq = txq

    def run(self):

        sampling_rate = 1.92e6
        frm_len = 60e-3
        sym_num = 200
        sample_per_frm = int(sampling_rate*frm_len)
        sample_per_sym = int(sample_per_frm/sym_num)
        print sym_num, sample_per_sym, sample_per_frm

        f1 = data_cosine(N = sample_per_sym, A = 0, sampling = sampling_rate, freq = 20e3)
        f2 = data_cosine(N = sample_per_sym, A = 0, sampling = sampling_rate, freq = 40e3)
        f3 = data_cosine(N = sample_per_sym, A = 0, sampling = sampling_rate, freq = 60e3)
        f4 = data_cosine(N = sample_per_sym, A = 0, sampling = sampling_rate, freq = 80e3)

        freq_addr = (c_long*4)()
        freq_addr[0],flag = f1.__array_interface__['data']
        freq_addr[1],flag = f2.__array_interface__['data']
        freq_addr[2],flag = f3.__array_interface__['data']
        freq_addr[3],flag = f4.__array_interface__['data']

        bits_len = sym_num*self.mod_order
        tx_bits = (c_uint*bits_len)()
        
        interp_real_buf = (c_double*sample_per_frm)()
        interp_imag_buf = (c_double*sample_per_frm)()
        fp_real_buf = (c_short*sample_per_frm)()
        fp_imag_buf = (c_short*sample_per_frm)()
        fp_buf = (c_short*(sample_per_frm*2))()

        tx_bits[:] = [1,1,0,0,1,0,0,1]*(bits_len/8)
        if self.mod_order == 1:
            for bit_idx in range(bits_len):
                addr = addressof(interp_real_buf) + bit_idx*sample_per_sym*sizeof(c_double)
                memmove(addr, freq_addr[tx_bits[bit_idx]],sample_per_sym*sizeof(c_double))
        elif self.mod_order == 2:
            for (bit_idx,sym_idx) in zip(range(0,bits_len,2),range(sym_num)):
                f_idx = tx_bits[bit_idx+1]*2 + tx_bits[bit_idx]
                addr = addressof(interp_real_buf) + sym_idx*sample_per_sym*sizeof(c_double)
                memmove(addr, freq_addr[f_idx],sample_per_sym*sizeof(c_double))
            
        #C_lib.ModFSK(tx_bits,freq_addr,sample_per_sym,interp_real_buf,bits_len,self.mod_order)
            
        '''fix point'''
        ok_amplifier = C_lib.CSM_amplifier(interp_real_buf, interp_imag_buf, sample_per_frm,\
                                           fp_real_buf, fp_imag_buf, c_double(2048), 16, 1)

        of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,sample_per_frm)
        
        while True:
            self.txq.put(fp_buf)
            time.sleep(frm_len)
