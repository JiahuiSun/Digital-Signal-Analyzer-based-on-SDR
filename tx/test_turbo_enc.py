import random
import ctypes
from ctypes import *

turbo_enc_dll = ctypes.CDLL('/home/alex/Desktop/TT1_py/turbo_enc.so')
iodat_pll = ctypes.CDLL('/home/alex/Desktop/TT1_py/iodat.so')

length = 336
code_rate = 3
tmp = [ random.randint(0,1) for i in range(length)]
turbo_in = (c_byte*length)()
turbo_in[:] = tmp
iodat_pll.write_char(turbo_in,length,'turbo_in.dat')

turbo_out = (c_byte*(length*3+12))()
turbo_enc_dll.turbo_enc(turbo_in, turbo_out, length, code_rate, 1)
iodat_pll.write_char(turbo_out, (length*3+12), 'turbo_out.dat')

