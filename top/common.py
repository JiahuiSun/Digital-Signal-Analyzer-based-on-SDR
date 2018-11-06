import Parameter as P
from tx import symbol_tx
import update_data
from Tkinter import *
from tkMessageBox import *
from Dialog import *

# matplotlib module used by eye/waveform/constellation/spectrum
import sjhmatplotlib
sjhmatplotlib.use('TkAgg')
from sjhmatplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sjhmatplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
import sjhmatplotlib.pyplot as plt
from sjhmatplotlib.figure import Figure
import sjhmatplotlib.animation as animation


def qamSend():
    '''Set tx threading'''
    send_task = symbol_tx.SYMBOL_TX(P.Params['mod_order'], P.tx_q)
    send_task.start()


def updateData():
    '''Set rx threading'''
    new_data = update_data.update_data(P.rx_q, P.fm_q, P.Params['sample_freq'], P.Params['input_sample_len'], P.data)
    new_data.start()


def inputData():
    '''Update data'''
    while True:
        yield P.data


def drun():
    '''Start the receive threading'''
    symbol_tx.SYMBOL_TX.sym_tx_stop = 0
    qamSend()
    update_data.update_data.rx_stop = 0
    updateData()
    P.runMenu.entryconfig('Run', state='disabled')
    P.viewMenu.entryconfig('FM', state='normal')
    P.reminderCanvas.itemconfig(P.reminder, text='Running...')


def run(event):
    '''Start the receive threading'''
    if symbol_tx.SYMBOL_TX.sym_tx_stop and update_data.update_data.rx_stop:
        symbol_tx.SYMBOL_TX.sym_tx_stop = 0
        qamSend()
        update_data.update_data.rx_stop = 0
        updateData()
        P.runMenu.entryconfig('Run', state='disabled')
        P.viewMenu.entryconfig('FM', state='normal')
        P.reminderCanvas.itemconfig(P.reminder, text='Running...')
        
    
def dstop():
    '''Stop the receive threading'''
    update_data.update_data.rx_stop = 1
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1
    
    if P.Flags['fmFlag']:
        P.fmTl._destroy()
    P.runMenu.entryconfig('Run', state='normal')
    P.viewMenu.entryconfig('FM', state='disabled')
    P.reminderCanvas.itemconfig(P.reminder, text='Stop')


def stop(event):
    '''Stop the receive threading'''
    update_data.update_data.rx_stop = 1
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1
    if P.Flags['fmFlag']:
        P.fmTl._destroy()
    P.runMenu.entryconfig('Run', state='normal')
    P.viewMenu.entryconfig('FM', state='disabled')
    P.reminderCanvas.itemconfig(P.reminder, text='Stop')
    

def mousePosition(event):
    '''Display the position of mouse'''    
    posXdata = event.xdata
    posYdata = event.ydata
    if posXdata == None and posYdata == None:
        pos_xy = ''
    else:
        pos_xy = ' X: {0:.3f}   Y: {1:.3f} '.format(posXdata, posYdata)
        
    P.posLabel['text'] = pos_xy


def updateCursor():
    '''Display the positon of cursor'''    
    if P.cursor_Checkbutton.get()==0:
        if len(P.as_spec.lines)==2:
            del P.as_spec.lines[1]
        cursor_xy = ''
        cursor_icon = ''
        
    if P.cursor_Checkbutton.get()==1:
        try:input_freq_tmp = float(P.cursorEntry.get())
        except:
            P.Params['input_freq'] = P.Params['center_freq']
            
        if input_freq_tmp <= P.Params['cf_end'] and input_freq_tmp >= P.Params['cf_start']:
            P.Params['input_freq'] = input_freq_tmp
            g = (P.Params['input_freq']-P.Params['center_freq']) / P.Params['base_end']
            k = P.Params['input_sample_len']/2+g*P.Params['span_half']
            h, = P.as_spec.plot(P.Params['input_freq'], P.PSD[k], 'rD')

            cursor_xy= ' Cursor:  ({0:.2f}  ,  {1:.2f}) '.format(P.Params['input_freq'], P.PSD[k])
            cursor_icon = P.cursorIcon
        else:
            P.cursorEntry.delete(0, END)
            P.cursorEntry.insert(0, P.Params['center_freq'])
            showerror('error', 'The input frequency cannot be displayed!')
            cursor_xy = ''
            cursor_icon = ''
            
        if len(P.as_spec.lines)==3:
            del P.as_spec.lines[1]
            
    P.cursor_xyLabel['image'] = cursor_icon    
    P.cursor_xyLabel['text'] = cursor_xy
