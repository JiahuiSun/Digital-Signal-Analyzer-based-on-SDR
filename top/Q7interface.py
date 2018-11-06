from ctypes import *
import time


class Q7:
	def __init__(self):
		fn =	'/tmp/' + 'libQ7.so'
		print fn
		self.lib = CDLL(fn)

		self.blk = 4096                         #???
##		frame_len = 1920*120*2*2
##		pdu_num = 16/16
##		self.blk = frame_len/pdu_num
		self.offset = 0L                        #???
		self.cnt = 0                            #???

	def _off( self ):
		t_offset = (c_long*1)()
		self.lib.offset( self.h, t_offset )
		return long(t_offset[0]) 

	def empty( self ):
		return False

	def full( self ):
		return False
		
	def state( self ):
		pos = long(self.start+self.offset)
		print "space",self._off()-pos
	
class rx(Q7):
	def __init__(self):
		Q7.__init__(self)
		self.h = self.lib.attachQ7Mem('rx_udp.d')
	
		self.lib.dumpQ7Mem( self.h )
		self.cap_size = self.lib.mSize( self.h )
		print "Capture Mem Size",self.cap_size
		self.start = self._off()
		
##	def read( self, l, off ):
##		pos = long(self.start+off)
##		while self._off()<long(pos+self.blk*2):
##			time.sleep(0.001)
##			self.cnt += 1
##			if (self.cnt%1000)==0:
##				print "time out, no packet recv",self._off(),pos
##				break
##		self.lib.getAddr.restype = c_void_p
##		addr = self.lib.getAddr( self.h, c_long(pos) )
##		vbuf = cast( addr, POINTER(c_short*(l/2)) )
##		return vbuf.contents
## 
##	def get( self ):
##		self.offset += self.blk
##		buf = self.read( self.blk, self.offset )
##
##		return buf

        # modified by GAO 20151111
	def read( self, l, off ):
		pos = long(self.start+off)
		while self._off()<long(pos+l):
			time.sleep(0.001)
			self.cnt += 1
			if self.cnt == 1000:
				print "time out, no packet recv",self._off(),pos
				break

		self.cnt = 0

		self.lib.getAddr.restype = c_void_p
		addr = self.lib.getAddr( self.h, c_long(pos) )
		vbuf = cast( addr, POINTER(c_short*(l/2)) )

		return vbuf.contents
	
	def get( self, blk_len ):
		#self.offset += blk_len
		buf = self.read( blk_len, self.offset )
		self.offset += blk_len
		return buf
	

class tx(Q7):
	def __init__(self):
		Q7.__init__(self)
		self.h = self.lib.attachQ7Mem('tx_udp.d')
		self.lib.dumpQ7Mem( self.h )

		self.sendbuf_size = self.lib.mSize( self.h )
		print "Send Mem Size",self.sendbuf_size
		self.start = self._off()
		
	def put( self, buf ):
		#print buf
		self.write( buf, len(buf)*2, self.offset )
		self.offset += len(buf)*2
		
	def write( self, buf, l, off ):
		pos = long(self.start+off)
		read_head = long(self._off())
		while read_head<long(pos-self.blk*10):
			time.sleep(0.001)
			read_head = long(self._off())
			self.cnt += 1
			if (self.cnt==1000):
				print "time out, no packet send",self._off(),pos
				break
		self.cnt = 0
		#if long(read_head)>long(pos):
		#	print "send buf lose",'pos=',pos,'head=',read_head,'diff=',read_head-pos

		self.lib.Q7write( self.h, byref(buf), l, c_long(pos) )
