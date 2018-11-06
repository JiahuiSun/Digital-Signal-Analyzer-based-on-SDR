from ctypes import *
import numpy as np
import math
import matplotlib.pyplot as plt
C_lib = CDLL("./resample_lib.so")

class PSTR_Upsamplefilter_para(Structure):
    _fields_ = [('os_N', c_uint),
                ('forward_sim', c_uint),
                ('filter_order', c_uint),
                ('b2_len', c_uint),
                ('b3_len', c_uint),
                ('tx_os', c_double),
                ('inter_factor', c_double),
                ('b2', POINTER(c_double)),
                ('b3', POINTER(c_double))
                ]

class PSTR_Dnsamplefilter_para(Structure):
    _fields_ = [('os_N', c_uint),
                ('filter_order', c_uint),
                ('b2_len', c_uint),
                ('b3_len', c_uint),
                ('b2', POINTER(c_double)),
                ('b3', POINTER(c_double)),
                ('forward_sim', c_uint)
                ]
    
sym_rate = 36.5e3
os_N = 32
filter_order = int(np.log2(os_N))
tx_os = 2
AD_Freq = 1.92e6
interp_factor = sym_rate*os_N*tx_os/AD_Freq
filter_len = 25
b2 = (c_double*filter_len)()
b3 = (c_double*filter_len)()
b2[:] = [0,-0.004,0,0.0111,0,-0.028,0,0.0614,0,-0.1343,0,0.4582, \
         0.7312,0.4582,0,-0.1343,0,0.0614,0,-0.028,0,0.0111,0,-0.004,0]
b3[:] = [-0.0005,-0.0047,-0.0067,0.0013,0.0205,0.029,-0.0033,-0.0685,\
         -0.0948,0.0053,0.2399,0.4944,0.6049,0.4944,0.2399,0.0053,\
         -0.0948,-0.0685,-0.0033,0.029,0.0205,0.00013,-0.0067,-0.0047,\
         -0.0005]

shape_filter_order = 33
tx_B = (c_double*shape_filter_order)()
tx_B[:] = [0.0022,-0.0028,0.0002,0.0027,-0.0041,0.0019,0.0053,-0.0082,\
           0.0014,0.0068,-0.018,0.0181,0.0404,-0.0956,-0.0599,0.4298,\
           0.7747,0.4298,-0.0599,-0.0956,0.0404,0.0181,-0.018,0.0068,\
           0.0014,-0.0082,0.0053,0.0019,-0.0041,0.0027,0.0002,-0.0028,0.0022]

Upsamplefilter_para = PSTR_Upsamplefilter_para()
Upsamplefilter_para.os_N = os_N
Upsamplefilter_para.forward_sim = 1
Upsamplefilter_para.filter_order = filter_order
Upsamplefilter_para.tx_os = c_double(tx_os)
Upsamplefilter_para.inter_factor = interp_factor
Upsamplefilter_para.b2 = b2
Upsamplefilter_para.b3 = b3
Upsamplefilter_para.b2_len = filter_len
Upsamplefilter_para.b3_len = filter_len

Dnsamplefilter_para = PSTR_Dnsamplefilter_para()
Dnsamplefilter_para.os_N = os_N
Dnsamplefilter_para.filter_order = filter_order
Dnsamplefilter_para.b2_len = filter_len
Dnsamplefilter_para.b3_len = filter_len
Dnsamplefilter_para.b2 = b2
Dnsamplefilter_para.b3 = b3
Dnsamplefilter_para.forward_sim = 1

sig_len = 4380
os_sig = (c_double*sig_len)()
t = np.linspace(0,50,sig_len)
os_sig[:] = np.cos(t)
sp_len = 2*sig_len
up_sample = (c_double*sp_len)()
up_sample[::2] = os_sig[:]
sp_output_buf = (c_double*sp_len)()
sp_filter_states = (c_double*(shape_filter_order-1))()
result0 = C_lib.shape_filter(up_sample,sig_len*2,sp_output_buf,tx_B,\
                             shape_filter_order,sp_filter_states)

itpst = [0,0,0,0]
os_len = sp_len + 4
os_sig_la = (c_double*os_len)()
os_sig_la[:] = itpst[:] + sp_output_buf[:]
itpst = os_sig_la[-4:]
fracst = 3
resample_len = int(math.floor((os_len-fracst-1)/interp_factor))
new_idx_tmp = fracst + (np.array(range(resample_len))+1)*interp_factor
max_len = (new_idx_tmp>=(os_len-1)).nonzero()[0].size
resample_len1 = resample_len-max_len+1
new_idx = (c_double*resample_len1)()
new_idx [:]= new_idx_tmp[:resample_len1]
fracst = new_idx[-1] - os_len + len(itpst)
int_sig = (c_double*resample_len1)()
la_out_len = (c_uint*1)()
lag_result = C_lib.Large_interp(os_sig_la,os_len,new_idx,resample_len1,int_sig,la_out_len)
##print lag_result,out_len[0]
##t_la = np.linspace(0,50,resample_len1)
##t_sp = np.linspace(0,50,sp_len)
##plt.plot(t,os_sig[:],t_sp,sp_output_buf[:],'r',t_la,int_sig[:],'o')
##plt.show()

states_row = filter_order
states_col = filter_len-1
filter_states = (c_double*(states_col*states_row))()
output_len = la_out_len[0]*os_N
output_buf = (c_double*output_len)()
outputlen = (c_uint*1)()
result = C_lib.unsamplefilter(int_sig, la_out_len[0], byref(Upsamplefilter_para), filter_states, \
                              states_row, states_col, output_buf, outputlen)

sig_len1 = outputlen[0]
os_sig1 = (c_double*sig_len1)()
os_sig1[:] = output_buf[:]
filter_states1 = (c_double*states_col*states_row)()
output_len1 = sig_len1/os_N
output_buf1 = (c_double*output_len1)()
outputlen1 = (c_uint*1)()
result1 = C_lib.dnsamplefilter(os_sig1, sig_len1, byref(Dnsamplefilter_para), filter_states1, \
                              states_row, states_col, output_buf1, outputlen1);

print outputlen[0], outputlen1[0]
t_up = np.linspace(0,50,outputlen[0])
t_dn = np.linspace(0,50,outputlen1[0])
plt.plot(t,os_sig[:],t_up, output_buf[:],'r',t_dn,output_buf1[:],'g')
plt.show()
