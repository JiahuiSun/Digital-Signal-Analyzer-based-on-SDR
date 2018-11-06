import numpy as np
import Queue
import ImageTk
import Q7interface
from Tkinter import *


def cfspanReset():
    '''Reset Params when span or center_freq change'''
    global Params
    span_half = int(Params['input_sample_len']*Params['span']*1e3/Params['sample_freq']/2)
    start = Params['input_sample_len']/2 - span_half
    end = Params['input_sample_len']/2 + span_half

    Params['span_half'] = span_half
    Params['start'] = start
    Params['end'] = end
    Params['base_start'] = Params['freqs'][start]
    Params['base_end'] = Params['freqs'][end]
    Params['cf_start'] = Params['center_freq'] + Params['base_start']
    Params['cf_end'] = Params['center_freq'] + Params['base_end']

    spec_idx = Params['freqs'][start:end] + Params['center_freq']
    Params['spec_idx'] = spec_idx


def offphaseReset():
    '''Reset Params when phase or offset change'''
    global Params
    eye_start = Params['input_sample_len']/2 + Params['offset'] + Params['interval']/2
    wave_idx = Params['input_sample_len']/2 + Params['offset'] + np.arange(Params['sample_num'])
    cd_idx = Params['input_sample_len']/2 + Params['offset'] + Params['sym_idx']

    Params['eye_start'] = eye_start
    Params['wave_idx'] = wave_idx
    Params['cd_idx'] = cd_idx


Params = {}

Params['sample_freq'] = 1.92e6
Params['osr'] = 64
Params['sym_num_display'] = 20
Params['input_sample_len'] = 115200
Params['mod_order'] = 1

Params['interval'] = int(Params['osr'])
Params['data_duration'] = Params['input_sample_len'] / Params['sample_freq']
Params['time_step'] = 1 / Params['sample_freq']
Params['sample_num'] = np.round(Params['sym_num_display']*Params['osr']).astype(int)
Params['sample_idx'] = Params['input_sample_len'] / 2 + np.arange(Params['sample_num'])
Params['sym_idx'] = np.round(np.arange(Params['sym_num_display'])*Params['osr']).astype(int)

Params['phase'] = 0
Params['offset'] = 0
Params['center_freq'] = 2000
Params['span'] = 200 #unit: KHz
Params['input_freq'] = 2000.0

freqs = np.fft.fftshift(np.fft.fftfreq(Params['input_sample_len'], \
                                       Params['time_step']))/1e6 #unit: MHz
Params['freqs'] = freqs

cfspanReset()
offphaseReset()

Flags = {}

Flags['specFlag'] = 0
Flags['eyeFlag'] = 0
Flags['cdFlag'] = 0
Flags['wfFlag'] = 0
Flags['fmFlag'] = 0
Flags['paramFlag'] = 0

q = Queue.Queue()
tx_q = q
rx_q = q
##tx_q = Q7interface.tx()
##rx_q = Q7interface.rx()
fm_q = Queue.Queue()

data = np.zeros(Params['input_sample_len'], dtype=complex)
PSD = np.zeros(Params['input_sample_len'])

root = Tk()

cursorIcon = ImageTk.PhotoImage(file='icon/cursor.ico')
logoIcon = ImageTk.PhotoImage(file='icon/logo.ico')
cfspanIcon = ImageTk.PhotoImage(file='icon/cfspan.ico')
FMcover = ImageTk.PhotoImage(file='icon/FM.jpg')

cdTl = None
paramTl = None
wfTl = None
eyeTl = None
fmTl = None

viewMenu = None
paramMenu = None
runMenu = None
editMenu = None
helpMenu = None
fileMenu = None

bwLabel = None
CFLabel = None
spanEntry = None
spanlabel = None
CFEntry = None
line_spec = None
ax_spec = None

cursor_Checkbutton = None
cursorEntry = None
cursor_xyLabel = None
reminder = None
reminderCanvas = None
