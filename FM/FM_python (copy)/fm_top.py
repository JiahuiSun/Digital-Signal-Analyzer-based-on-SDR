import sys,time
sys.path.append("..")

from fm_tx import *
from fm_rx import *
import Queue
import Q7interface

##q = Queue.Queue()
##tx_q = q
##rx_q = q

tx_q = Q7interface.tx()
rx_q = Q7interface.rx()

#get the audio data
filepath="record.wav"
wf = wave.open(filepath,'rb')
params = wf.getparams()

data = wf.readframes(params[3])
raw_data = np.fromstring(data,dtype=np.short)

FM_Tx = fm_tx(tx_q, params, raw_data)
FM_Tx.start()

FM_Rx = fm_rx(rx_q, params)
FM_Rx.start()
