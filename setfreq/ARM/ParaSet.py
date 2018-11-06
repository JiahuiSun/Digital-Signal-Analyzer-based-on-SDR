import threading
import struct,socket,time
from ctypes import *
import os
#test_lib = CDLL('./test_freq_power.so')

addr = ('10.0.77.112', 10000)
#addr = ('localhost',12345)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(addr)

class SerSocket(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global sock
        
        rx_len = 7+9 # lable + '1995.0000'
        tx_freq = '2000 0000'
        rx_freq = '2000 0000'
        while True:
            msg, CliAddr = sock.recvfrom(rx_len)
            if msg[:7] == 'tx_freq':
                #tx_freq_str, = struct.unpack('f',msg[7:])
                tx_freq_str = str(msg[7:])
		tx_freq_str_list = tx_freq_str.split('.')
		tx_freq = tx_freq_str_list[0] + ' ' + tx_freq_str_list[1]
		#a = "./test_freq.sh 1995 0000 %s %s"%(tx_freq_str_list[0],tx_freq_str_list[1])
		a = './test_freq.sh' + ' ' + rx_freq + ' ' + tx_freq
		os.system(a)
                print 'set frequency!!!', 'tx_freq', tx_freq, 'rx_freq', rx_freq

            elif msg[:7] == 'rx_freq':
                rx_freq_str = str(msg[7:])
		rx_freq_str_list = rx_freq_str.split('.')
		rx_freq = rx_freq_str_list[0] + ' ' + rx_freq_str_list[1]
		a = './test_freq.sh' + ' ' + rx_freq + ' ' + tx_freq 
		os.system(a)
                print 'set frequency!!!', 'tx_freq', tx_freq, 'rx_freq', rx_freq

            elif msg[:7] == 't_power':
                tx_power, = struct.unpack('f',msg[7:])
                #test_lib.test_power(int(rx_power))
                print 'set tx power!!!', tx_power

rx = SerSocket()
rx.start()
