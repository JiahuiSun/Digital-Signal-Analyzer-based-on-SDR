from Tkinter import *
import Parameter as P
from initWindow import *
import numpy as np


def setupParamTl():
    '''Set up param window including offset and phase'''
    global offsetEntry, phaseEntry
    
    P.paramTl = initTl(Toplevel(), P.paramMenu, flag='paramFlag', size='300x55', title='Parameter Setting', icon=P.logoIcon)
    
    #save button
    paramButton = Button(P.paramTl.root, text='Save', command=phase_offset_set, font='Times')
    paramButton.grid(row=1, column=5)

    #add label
    Label(P.paramTl.root, text='    ').grid(row=1, column=4)
    Label(P.paramTl.root, text='Constellation & Eye diagram & Waveform').grid(row=0, column=0,columnspan=6)
    
    offsetLabel = Label(P.paramTl.root, text='offset:', font='Times', padx=4)
    offsetLabel.grid(row=1, column=0)

    offsetEntry = Entry(P.paramTl.root, width=6)
    offsetEntry.grid(row=1, column=1)
    offsetEntry.insert(0, P.Params['offset'])

    phasesetLabel = Label(P.paramTl.root, text='  phase:', font='Times')
    phasesetLabel.grid(row=1, column=2)

    phaseEntry = Entry(P.paramTl.root, width=6)
    phaseEntry.grid(row=1, column=3)
    phaseEntry.insert(0, P.Params['phase'])

    P.paramTl.root.mainloop()
    

def phase_offset_set():
    '''Get the input of phase and offset'''
    global offsetEntry, phaseEntry
    
    try:offset_tmp = int(offsetEntry.get())
    except:
        offset_tmp = 0
        offsetEntry.delete(0,END)
        
    try:phase_tmp = float(phaseEntry.get())
    except:
        phase_tmp = 0
        phaseEntry.delete(0,END)

    if phase_tmp >= -(np.pi) and phase_tmp <= np.pi and offset_tmp >= 0 and offset_tmp < P.Params['osr']:
        P.Params['phase'] = phase_tmp
        P.Params['offset'] = offset_tmp
        P.offphaseReset()
        
    elif phase_tmp < -(np.pi) or phase_tmp > np.pi:
        phaseEntry.delete(0, END)
        phaseEntry.insert(0, P.Params['phase'])
        showerror('error', 'The phase is out of range! Please enter again.')
    else:
        offsetEntry.delete(0, END)
        offsetEntry.insert(0, P.Params['offset'])         
        showerror('error', 'The offset is out of range! Please enter again.')
        
##    print 'phase', P.Params['phase']
##    print 'offset', P.Params['offset']
    
