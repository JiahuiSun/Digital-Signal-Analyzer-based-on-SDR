import Parameter as P
from Tkinter import *
from common import *
from initWindow import *
import numpy as np


def updateCd(data):
    '''Update function for Constellationdiagram'''
    global line_cd
    
    mean = np.sqrt(np.mean(np.abs(P.data)**2))
    if mean == 0:
        mean = 1
    data_mean = P.data / mean
    data_mean = data_mean*np.exp(1j*P.Params['phase'])
    r_data = data_mean.real[P.Params['cd_idx']]
    i_data = data_mean.imag[P.Params['cd_idx']]             
    line_cd.set_xdata(r_data)
    line_cd.set_ydata(i_data)
    return line_cd,


def setupCdTl():
    '''Set up constellationdiagram window'''
    global line_cd
    
    #add window    
    P.cdTl = initTl(Toplevel(), P.viewMenu, flag='cdFlag', size='500x550', title='Constellation Diagram', icon=P.logoIcon)
    
    #add frames
    cd_toolFrame = Frame(P.cdTl.root, height=40, bg='#D9D9D9')
    cd_toolFrame.grid(row=0, column=0, sticky=W)

    fig_cd, ax_cd = plt.subplots(figsize=(5,5) ,dpi=100, facecolor='#D9D9D9')
    fig_cd.subplots_adjust(left=0.04, right=0.96, bottom=0.03, top=0.96)
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    #设置轴的刻度和标签
    ax_cd.set_xticks(np.linspace(-2, 2, 11))
    ax_cd.set_xticklabels(['']*10)
    ax_cd.set_yticks(np.linspace(-2, 2, 11))
    ax_cd.set_yticklabels(['']*10)
    #移动轴到中间位置
    ax_cd.spines['right'].set_color('none')
    ax_cd.spines['top'].set_color('none')
    ax_cd.xaxis.set_ticks_position('bottom')
    ax_cd.spines['bottom'].set_position(('data', 0))
    ax_cd.yaxis.set_ticks_position('left')
    ax_cd.spines['left'].set_position(('data', 0))

    line_cd, = ax_cd.plot(np.array(0), np.array(0), 'o')    
    ax_cd.grid(True)

    canvas_cd = fig_cd.canvas
    canvas_cd = FigureCanvasTkAgg(fig_cd, master=P.cdTl.root)
    canvas_cd.show()
    canvas_cd.get_tk_widget().grid(row=1, column=0)
    
    toolbar = NavigationToolbar2TkAgg(canvas_cd, cd_toolFrame)
    toolbar.pack()
    toolbar.update()
    # 动画延时
##    ani_cd = animation.FuncAnimation(fig_cd, updateCd, inputData, interval=500, repeat=False)
    ani_cd = animation.FuncAnimation(fig_cd, updateCd, inputData, repeat=False)

    P.cdTl.root.mainloop()
