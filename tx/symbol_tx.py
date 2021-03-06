﻿from ctypes import *
import math, time
import numpy as np
import threading

#from param_setting import *
#from tx.init_state import *
from tx.function import *

C_lib = CDLL("work/C_lib.so")
resample_lib = CDLL("work/resample_lib.so")

class SYMBOL_TX(threading.Thread):
    sym_tx_stop = 0
    
    def __init__(self, mod_order, txq):
        threading.Thread.__init__(self)
        self.mod_order = mod_order
        self.txq = txq

    def run(self):
        param = param_setting()
        state = init_state(param)
        
        shape_filter_flag = 1
        interp_output_len = param['sample_num']# 115200

        bits_len = param['sym_num']*self.mod_order# 生成原始比特数：115200*1
        tx_bits = (c_uint*bits_len)()# 申请空间115200个uint
        
        frm_real_buf = (c_double* param['sym_num'])()# 申请一帧数据空间：3600个double
        frm_imag_buf = (c_double* param['sym_num'])()
        sf_real_buf = (c_double*param['sf_len'])()# 7200
        sf_imag_buf = (c_double*param['sf_len'])()
        
        interp_real_buf = (c_double*interp_output_len)()# 申请全部数据空间：115200个double
        interp_imag_buf = (c_double*interp_output_len)()
        
        fp_real_buf = (c_short*interp_output_len)()# 定点化空间申请：115200个short
        fp_imag_buf = (c_short*interp_output_len)()

##        if self.mod_order == 1 or self.mod_order == 2:
##            tx_bits[:] = [1,0,0,0,1,0,0,0]*(bits_len/8)#115200
##
##        elif self.mod_order == 4:
##            tx_bits[:] = [0,0,0,0,0,0,0,1,0,0,1,0,0,0,1,1,\
##                          0,1,0,0,0,1,0,1,0,1,1,0,0,1,1,1,\
##                          1,0,0,0,1,0,0,1,1,0,1,0,1,0,1,1,\
##                          1,1,0,0,1,1,0,1,1,1,1,0,1,1,1,1]*112 \
##                        + [0,0,0,0,0,0,0,1,0,0,1,0,0,0,1,1,\
##                          1,0,0,0,1,0,0,1,1,0,1,0,1,0,1,1]#7200
        
##        print 'sym_tx start'
        while SYMBOL_TX.sym_tx_stop == 0:
##            time.sleep(1)
            
            fp_buf = (c_short*(interp_output_len*2))()
            tx_bits[:] = np.random.randint(0,2,bits_len)# 产生115200个原始比特

            #memmove(tx_bits, addressof(input_buf), sizeof(c_uint)*bits_len)

            ok_qpsk = C_lib.modulate(tx_bits, frm_real_buf, frm_imag_buf, bits_len,  self.mod_order)
            #print 'ok_qpsk',ok_qpsk,bits_len,self.mod_order1
            
            '''shape filter'''
            if shape_filter_flag:
                sf_real_tmp = (c_double*param['sf_len'])()# 申请经过sf后的数据空间
                sf_imag_tmp = (c_double*param['sf_len'])()
                
                sf_real_tmp[::2] = frm_real_buf[:]
                sf_imag_tmp[::2] = frm_imag_buf[:]
                result_sf_r = resample_lib.shape_filter(sf_real_tmp,param['sf_len'],sf_real_buf,param['tx_B'],\
                                                         param['shape_filter_order'],state['sf_states_real'])
                result_sf_i = resample_lib.shape_filter(sf_imag_tmp,param['sf_len'],sf_imag_buf,param['tx_B'],\
                                                         param['shape_filter_order'],state['sf_states_imag'])

                '''Interpolation'''
                #os_len = ov_filter(sf_real_buf,sf_imag_buf, interp_real_buf,interp_imag_buf,param, state)
                os_len = os_filter_symbol(sf_real_buf,sf_imag_buf, param['sf_len'],interp_real_buf,interp_imag_buf,param, state)
            else:
                osr = param['os_N']*2
                interp_output_len = param['sym_num']*osr
                os_real = np.array(frm_real_buf[:]).repeat(osr)
                os_imag = np.array(frm_imag_buf[:]).repeat(osr)
                interp_real_buf[:interp_output_len] = os_real
                interp_imag_buf[:interp_output_len] = os_imag
                #print 'over sample rate is', osr
            
            '''fix point'''
            ok_amplifier = C_lib.CSM_amplifier(interp_real_buf, interp_imag_buf, interp_output_len,\
                                               fp_real_buf, fp_imag_buf, c_double(2048), \
                                               MaxBits, 1)

            of_combiner = C_lib.CSM_data_combiner(fp_real_buf,fp_imag_buf,fp_buf,interp_output_len)

            self.txq.put(fp_buf)

##        self.txq.queue.clear()
##        fp_buf = 0
##        self.txq.put(fp_buf)
##        print 'sym_tx ended'
