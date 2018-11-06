from ctypes import *
import math, time
import numpy as np
from scipy import signal

resample_lib = CDLL("work/resample_lib.so")
MaxBits = 16

def param_setting():
    Params = {}

    Params['sample_freq'] = 1.92e6# unit: Hz
    Params['frame_time'] = 60e-3# unit: s
    # sample numbers per frame:115200
    Params['sample_num'] = int(Params['sample_freq']*Params['frame_time'])
    Params['sym_num'] = 3600# symbol numbers
    Params['sym_rate'] = Params['sym_num']/Params['frame_time']# symbol rate:60e3sps
    
    Params['tx_os'] = 2# overSampleRate for shape filter
    Params['sf_len'] = Params['sym_num']*Params['tx_os']# length after shape filter:7200       
    Params['os_N'] = Params['sample_num']/Params['sf_len']# overSampleRate:16
    Params['filter_order'] = int(np.log2(Params['os_N']))# 4
    
    Params['filter_len'] = 25
    Params['b2'] = (c_double*Params['filter_len'])()# firwin
    Params['b3'] = (c_double*Params['filter_len'])()

    b2_buf = signal.firwin(Params['filter_len'], 0.5)
    Params['b2'][:] = b2_buf/np.linalg.norm(b2_buf)
    b3_buf = signal.firwin(Params['filter_len'], 0.33)
    Params['b3'][:] = b3_buf/np.linalg.norm(b3_buf)

    # for shape filter and match filter
    Params['shape_filter_order'] = 33
    Params['tx_B'] = (c_double*Params['shape_filter_order'])()
    Params['tx_B'][:] = [0.0022,-0.0028,0.0002,0.0027,-0.0041,0.0019,0.0053,-0.0082,\
                       0.0014,0.0068,-0.018,0.0181,0.0404,-0.0956,-0.0599,0.4298,\
                       0.7747,0.4298,-0.0599,-0.0956,0.0404,0.0181,-0.018,0.0068,\
                       0.0014,-0.0082,0.0053,0.0019,-0.0041,0.0027,0.0002,-0.0028,0.0022]

    Params['rx_B'] = (c_double*Params['shape_filter_order'])()
    Params['rx_B'][:] = [0.0022,-0.0028,0.0002,0.0027,-0.0041,0.0019,0.0053,-0.0082,\
                       0.0014,0.0068,-0.018,0.0181,0.0404,-0.0956,-0.0599,0.4298,\
                       0.7747,0.4298,-0.0599,-0.0956,0.0404,0.0181,-0.018,0.0068,\
                       0.0014,-0.0082,0.0053,0.0019,-0.0041,0.0027,0.0002,-0.0028,0.0022]
    return Params

def init_state(Params):# why?
    State = {}
    
    State['sf_states_real'] = (c_double*(Params['shape_filter_order']-1))()# 32
    State['sf_states_imag'] = (c_double*(Params['shape_filter_order']-1))()

    states_row = Params['filter_order']# 4
    states_col = Params['filter_len']-1# 24

    State['filter_states_real'] = (c_double*(states_col*states_row))()
    State['filter_states_imag'] = (c_double*(states_col*states_row))()

    return State

def os_filter_symbol(sig_in_real, sig_in_imag, input_len, sig_out_real, sig_out_imag, Params,State):

    states_row = Params['filter_order']
    states_col = Params['filter_len']-1
    outputlen_r = (c_uint*1)()
    outputlen_i = (c_uint*1)()

    if Params['os_N'] == 1:
        memmove(sig_out_real, sig_in_real, sizeof(c_double)*input_len)
        memmove(sig_out_imag, sig_in_imag, sizeof(c_double)*input_len)
        output_len = input_len

    else:
        Upsamplefilter_para = Upsamplefilter_para_gen(Params,State)

        result_r = resample_lib.unsamplefilter(sig_in_real, input_len, byref(Upsamplefilter_para), \
                                               State['filter_states_real'], states_row, states_col, \
                                               sig_out_real, outputlen_r)

        result_i = resample_lib.unsamplefilter(sig_in_imag, input_len, byref(Upsamplefilter_para), \
                                               State['filter_states_imag'], states_row, states_col, \
                                               sig_out_imag, outputlen_i)
        output_len = outputlen_r[0]
     
    return output_len


class PSTR_Upsamplefilter_para(Structure):
    _fields_ = [('os_N', c_uint),
                ('forward_sim', c_uint),
                ('filter_order', c_uint),
                ('b2_len', c_uint),
                ('b3_len', c_uint),
                ('tx_os', c_double),
                ('inter_factor', c_double),
                ('b2', POINTER(c_double)),
                ('b3', POINTER(c_double)),
                ('delay', c_double),
                ('sig_len', c_uint)
                ]


def Upsamplefilter_para_gen(Params, State):
    
    Upsamplefilter_para = PSTR_Upsamplefilter_para()

    Upsamplefilter_para.os_N = Params['os_N']
    Upsamplefilter_para.forward_sim = 1
    Upsamplefilter_para.filter_order = Params['filter_order']
    Upsamplefilter_para.tx_os = c_double(Params['tx_os'])
    Upsamplefilter_para.inter_factor = 1
    Upsamplefilter_para.b2 = Params['b2']
    Upsamplefilter_para.b3 = Params['b3']
    Upsamplefilter_para.b2_len = Params['filter_len']
    Upsamplefilter_para.b3_len = Params['filter_len']
    Upsamplefilter_para.delay = 0
    Upsamplefilter_para.sig_len = 0
##    print Params['os_N'],1- Params['frame_type'],Params['filter_order'],Params['tx_os'],Params['interp_factor']
##    print  Params['filter_len'],State['delay'],State['sig_len']
    
    return Upsamplefilter_para
