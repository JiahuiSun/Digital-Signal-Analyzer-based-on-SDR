import Parameter as P
from Tkinter import *
from common import *
from initWindow import *
import numpy as np


def updateEyediagram(data):
    '''Update function for eye diagram'''
    global subfig3, subfig4
    
    mean = np.sqrt(np.mean(np.abs(P.data)**2))
    if mean == 0:
        mean = 1
    data_mean = P.data / mean
    data_mean = data_mean*np.exp(1j*P.Params['phase'])

    for eye_idx in range(P.Params['sym_num_display']):
        interval = int(P.Params['osr'])
        start = P.Params['eye_start'] + eye_idx*interval
        subfig3.plot(range(interval), data_mean.real[start+np.arange(interval)])
        subfig4.plot(range(interval), data_mean.imag[start+np.arange(interval)])

    if len(subfig3.lines) >= 41:
        del subfig3.lines[1:21]
        del subfig4.lines[1:21]


def setupEyeTl():
    '''Set up eye diagram window'''
    global subfig3, subfig4

    P.eyeTl = initTl(Toplevel(), P.viewMenu, flag='eyeFlag', size='500x550', title='Eye Diagram', icon=P.logoIcon)

    eye_toolFrame = Frame(P.eyeTl.root, height=40, bg='#D9D9D9')
    eye_toolFrame.grid(row=0, column=0, sticky=W)

    fig_eye = plt.figure(figsize=(5,5), dpi=100, facecolor='#D9D9D9')
    fig_eye.subplots_adjust(left=0.04, right=0.96, bottom=0.04, top=0.97, hspace=0.2)
    subfig3 = plt.subplot(211)  # real eyediagram
    subfig4 = plt.subplot(212)  # imag eyediagram
    
    line3 = subfig3.plot(100*[int(P.Params['osr'])/2], np.linspace(-2,2,100), 'k--')
    line4 = subfig4.plot(100*[int(P.Params['osr'])/2], np.linspace(-2,2,100), 'k--')
    
    subfig3.set_xlim(0, P.Params['osr']-1)
    subfig4.set_xlim(0, P.Params['osr']-1)

    subfig3.set_yticks([])
    subfig4.set_yticks([])

    canvas_eye = fig_eye.canvas
    canvas_eye = FigureCanvasTkAgg(fig_eye, master=P.eyeTl.root)
    canvas_eye.show()
    canvas_eye.get_tk_widget().grid(row=1, column=0)

    toolbar = NavigationToolbar2TkAgg(canvas_eye, eye_toolFrame)
    toolbar.pack()
    toolbar.update()
    # 动画延时
##    ani = animation.FuncAnimation(fig_eye, updateEyediagram, inputData, interval=500, repeat=False)
    ani = animation.FuncAnimation(fig_eye, updateEyediagram, inputData, repeat=False)

    P.eyeTl.root.mainloop()
