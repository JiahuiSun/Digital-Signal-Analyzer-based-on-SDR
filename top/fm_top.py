from fm_tx import *
from fm_rx import *
import wave

fm_stop = 1

def fm_send(tx_q):
    global fm_stop
    fm_stop = 0
    
    #get the parameters and the data of 1.wav
    filepath="1.wav"
    wf = wave.open(filepath,'rb')
    params = wf.getparams()
    data = wf.readframes(params[3])
    raw_data = np.fromstring(data, dtype=np.short)
    #Transmit threading
    FM_Tx = fm_tx(tx_q, params, raw_data)
    FM_Tx.start()

def fm_recv(rx_q):
    global fm_stop
    fm_stop = 0
    FM_Rx = fm_rx(rx_q)
    FM_Rx.start()

def fm_end():
    global fm_stop
    fm_stop = 1
