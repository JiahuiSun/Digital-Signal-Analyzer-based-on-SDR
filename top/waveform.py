import Parameter as P
from Tkinter import *
from common import *
from initWindow import *
import numpy as np


def updateWaveform(data):
    '''Update function for wavaform'''
    global line1, line2
    
    mean = np.sqrt(np.mean(np.abs(P.data)**2))
    if mean == 0:
        mean = 1
    data_mean = P.data / mean
    data_mean = data_mean*np.exp(1j*P.Params['phase'])
    r_data = data_mean.real[P.Params['wave_idx']]
    i_data = data_mean.imag[P.Params['wave_idx']]
    line1.set_ydata(r_data)
    line2.set_ydata(i_data)
    return [line1,line2]

    
def setupWfTl():
    global line1, line2

    P.wfTl = initTl(Toplevel(), P.viewMenu, flag='wfFlag', size='500x550', title='Waveform', icon=P.logoIcon)

    #add frames
    wf_toolFrame = Frame(P.wfTl.root, height=40, bg='#D9D9D9')
    wf_toolFrame.grid(row=0, column=0, sticky=W)
    
    fig_wf = plt.figure(figsize=(5,5), dpi=100, facecolor='#D9D9D9')
    fig_wf.subplots_adjust(left=0.1, right=0.94, top=0.97, bottom=0.04, hspace=0.2)
    
    subfig1 = plt.subplot(211)  # real waveform
    subfig2 = plt.subplot(212)  # imag waveform
        
    line1, = subfig1.plot(P.Params['sample_idx'], np.zeros(P.Params['sample_num']))
    line2, = subfig2.plot(P.Params['sample_idx'], np.zeros(P.Params['sample_num']))

    subfig1.set_xlim(P.Params['sample_idx'][1], P.Params['sample_idx'][-1])
    subfig2.set_xlim(P.Params['sample_idx'][1], P.Params['sample_idx'][-1])
    subfig1.set_ylim(-2, 2)
    subfig2.set_ylim(-2, 2)
    subfig1.grid(True)
    subfig2.grid(True)
    
    canvas_wf = fig_wf.canvas
    canvas_wf = FigureCanvasTkAgg(fig_wf, master=P.wfTl.root)
    canvas_wf.show()
    canvas_wf.get_tk_widget().grid(row=1, column=0)

    toolbar = NavigationToolbar2TkAgg(canvas_wf, wf_toolFrame)
    toolbar.pack()
    toolbar.update()
    # 动画
##    ani = animation.FuncAnimation(fig_wf, updateWaveform, inputData, interval=500, repeat=False)
    ani = animation.FuncAnimation(fig_wf, updateWaveform, inputData, repeat=False)

    P.wfTl.root.mainloop()
