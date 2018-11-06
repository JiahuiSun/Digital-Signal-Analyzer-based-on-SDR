import threading
import struct,socket
from ctypes import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr_arm = ('10.0.77.112',10000)
#addr_arm = ('localhost',12345)

# para_str: 'tx_freq', 'rx_freq', 't_power'
def set_para(rx_freq,f_value):
    freq = str(f_value)
    if '.' in freq:
        tmp_str = freq.split('.')
        zero_num = 4-len(tmp_str[1])
        freq = freq + zero_num*'0'
    else:
        freq = freq + '.0000'
    return freq

def set_param(para_str, f_value):
    #pkt = para_str + struct.pack('f',f_value)
    f_value=set_para(para_str,f_value)
    pkt = para_str + str(f_value)
    send_size = sock.sendto(pkt,addr_arm)
  
