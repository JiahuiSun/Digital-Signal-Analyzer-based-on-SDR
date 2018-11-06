'''
2018/3/28 21:46
1.菜单栏添加快捷键绑定
2.改变输入参数布局方式

2018/3/29 16:00
1.改变了toolbar布局
2.改变了参数和reminder布局

2018/3/30 14:00
1.解决了参数调用问题
2.解决了Label更新问题

3.亟待解决grid问题 done
4.warning问题 done
5.纵轴坐标显示问题 done
6.save布局问题 done
7.动静态显示span done
8.save的位置 done
9.带宽问题 done

2018/3/31
1.关闭主窗口时，子窗口仍未关闭 done
2.星座图一打开显示问题，星座图和run谁先打开 done

2018/4/4
1.run后线画在星座图上 done
2.同时启动发送和接收时，updateSpectrum会报错 done

2018/4/8
1.加入眼图 done
2.加入波形图 done
3.加入FM done

2018/4/9
1.眼图没清除，因为更新间隔太快所以太卡 done

2018/4/10
1.动画函数更新延长间隔来缓解卡顿问题 done
2.没加光标，不知道加哪 
3.程序实时性问题
4.频谱grid问题 done
5.FM接收处理时间太长，播放卡 done
6.星座图坐标轴 done

1.快捷键都要加上
'''
# system module
import sys, time
sys.path.append('..')
import warnings
warnings.filterwarnings('ignore')
import Queue
import numpy as np
import spectrum

# Tkinter module
from Tkinter import *
from tkMessageBox import *
import ImageTk, Image
from Dialog import *

# matplotlib module
import sjhmatplotlib
sjhmatplotlib.use('TkAgg')
from sjhmatplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sjhmatplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
import sjhmatplotlib.pyplot as plt
from sjhmatplotlib.figure import Figure
import sjhmatplotlib.animation as animation

# self module
from tx import symbol_tx
from tx.FSK_tx import *
import Q7interface
import update_data
import ParaSetCliSock
import fm_top
from Help import *

#############################__common_function__############################
def _destroyRoot():
    '''Quit GUI application cleanly'''
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1
    update_data.update_data.rx_stop = 1
    
    if tl_cd != None:
        _destroyCdWindow()#同时关闭星座图
    if tl_param != None:
        _destroyParamtl()#同时关闭星座图设置参数的窗口
    if waveformTl != None:
        _destroyWfWindow()#同时关闭波形图
    if eyeTl != None:
        _destroyEyeWindow()#同时关闭眼图
    if fmTl != None:
        _destroyFMWindow()#同时关闭FM
        
    root.quit()
    root.destroy()
    sys.exit()#关闭所有进程


def destroyRoot(event):
    '''Quit GUI application cleanly in the way of Ctrl+Q'''
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1
    update_data.update_data.rx_stop = 1
    
    if tl_cd != None:
        _destroyCdWindow()#同时关闭星座图
    if tl_param != None:
        _destroyParamtl()#同时关闭星座图设置参数的窗口
    if waveformTl != None:
        _destroyWfWindow()#同时关闭波形图
    if eyeTl != None:
        _destroyEyeWindow()#同时关闭眼图
    if fmTl != None:
        _destroyFMWindow()#同时关闭FM
        
    root.quit()
    root.destroy()
    sys.exit()#关闭所有进程


def mousePosition(event):
    '''Display the position of mouse'''
    global pos_xy
    
    posXdata = event.xdata
    posYdata = event.ydata
    if posXdata == None and posYdata == None:
        pos_xy = ''
    else:
        pos_xy = ' X: {0:.3f}   Y: {1:.3f} '.format(posXdata, posYdata)
    #对象是字典类型，直接赋值    
    posLabel['text'] = pos_xy

    
def qamSend(mod_order, tx_q):
    '''Set tx threading'''
    send_task = symbol_tx.SYMBOL_TX(mod_order, tx_q)
    send_task.start()


def updateData():
    '''Set rx threading'''
    new_data = update_data.update_data(rx_q, fm_q, sample_freq, input_sample_len, data)
    new_data.start()


def _run():
    '''Start the receive threading'''
    symbol_tx.SYMBOL_TX.sym_tx_stop = 0#点击run开启发送线程
    qamSend(mod_order, tx_q)
    update_data.update_data.rx_stop = 0#点击run开启接收线程
    updateData()
    runMenu.entryconfig('Run', state='disabled')#禁用run
    viewMenu.entryconfig('FM', state='normal')


def run(event):
    '''Start the receive threading'''
    symbol_tx.SYMBOL_TX.sym_tx_stop = 0#点击run开启发送线程
    qamSend(mod_order, tx_q)
    update_data.update_data.rx_stop = 0#点击run开启接收线程
    updateData()
    runMenu.entryconfig('Run', state='disabled')#禁用run
    viewMenu.entryconfig('FM', state='normal')

    
def _stop():
    '''Stop the receive threading'''
    update_data.update_data.rx_stop = 1#点击stop结束接收线程
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1#点击stop结束发送线程
    if fmFlag:
        _destroyFMWindow()
    runMenu.entryconfig('Run', state='normal')#启用run
    viewMenu.entryconfig('FM', state='disabled')


def stop(event):
    '''Stop the receive threading'''
    update_data.update_data.rx_stop = 1#点击stop结束接收线程
    symbol_tx.SYMBOL_TX.sym_tx_stop = 1#点击stop结束发送线程
    if fmFlag:
        _destroyFMWindow()
    runMenu.entryconfig('Run', state='normal')#启用run
    viewMenu.entryconfig('FM', state='disabled')

    
def inputData():
    '''Receive data'''
    global data
    while True:
        time.sleep(data_duration)
        print 'sunnnnnnnnn'
        yield data


def _saveFig():
    fig_spec.savefig('example.png')

#######################__Spectrum__#####################################
def updateSpectrum(data):
    '''Power spectrum density'''
    global start, end
    global line_spec
    global PSD
    global bandwidth, bwLabel

    if not update_data.update_data.rx_stop:#接收数据才更新，否则不更新
        p = spectrum.Periodogram(data, sampling=sample_freq, window='hann')
        p.run()

        if sum(p.psd) == 0:
            PSD = np.zeros(np.size(p.psd))
            line_spec.set_ydata(PSD[start:end])
        else:
            PSD = np.fft.fftshift(10*np.log10(p.psd))
            line_spec.set_ydata(PSD[start:end])

            y = np.array(PSD[:])
            ymax = max(y)
    ##        print 'ymax=', ymax
            idx = np.where(y>ymax*0.9)
            ave = np.mean(y[idx[0][0]:idx[0][-1]])
    ##        print 'ave=', ave
            threshold = ave/np.sqrt(2)
            x = np.where(y>threshold)

            bw = (x[0][-1]-x[0][0]+1)*sample_freq/1e3/input_sample_len#unit: KHz
            bandwidth = 'Bandwidth: {:.2f}KHz'.format(bw)
            bwLabel['text'] = bandwidth

        updateCursor()
    return line_spec,


def updateCursor():
    '''cursor'''
    global center_freq, span_half, input_freq

    if cursor_Checkbutton.get()==0:
        if len(ax_spec.lines)==2:
            del ax_spec.lines[1]
        cursor_xy = ''
        cursor_icon = ''
        
    if cursor_Checkbutton.get()==1:
        try:input_freq_tmp = float(cursorEntry.get())
        except:
            input_freq = 2000.0

        if input_freq_tmp <= center_freq+freqs[end] and input_freq_tmp >= center_freq+freqs[start]:
            input_freq = input_freq_tmp
            g = (input_freq-center_freq) / freqs[end]
            k = input_sample_len/2+g*span_half
            h, = ax_spec.plot(input_freq, PSD[k], 'rD')
            
            cursor_xy= ' Cursor:  ({0:.2f}  ,  {1:.2f}) '.format(input_freq, PSD[k])
            cursor_icon = cf_span_icon
        else:
            cursorEntry.delete(0, END)
            cursorEntry.insert(0, input_freq)          
            showerror('error', 'The input frequency cannot be displayed!')
            cursor_xy = ''
            cursor_icon = ''
            
        if len(ax_spec.lines)==3:
            del ax_spec.lines[1]
            
    cursor_xyLabel['image'] = cursor_icon    
    cursor_xyLabel['text'] = cursor_xy
        

def setParamSpec():
    '''Set span and center frequency'''
    global span, center_freq
    global start, end, span_half
    global ax_spec, line_spec
    global CFLabel, spanLabel
    global PSD
    
    try:
        span_tmp = float(spanEntry.get())
    except:
        span_tmp = 200
        spanEntry.delete(0, END)
    try:
        center_freq_tmp = float(CFEntry.get())
    except:
        center_freq_tmp = 2000
        CFEntry.delete(0, END)
        
    if span_tmp <= 1920 and span_tmp >0 and center_freq_tmp <= 6000 and center_freq_tmp >=70:
        if center_freq != center_freq_tmp:
            center_freq = center_freq_tmp
            print 'center freq changed!'
            
        span = span_tmp  
        span_half = int(input_sample_len*span*1e3/sample_freq/2)
        start = input_sample_len/2 - span_half
        end = input_sample_len/2 + span_half

        ax_spec.cla()#清空指定axes
        plt.sca(ax_spec)#回到指定axes，防止画到别的图上
        line_spec, = ax_spec.plot(freqs[start:end]+center_freq, PSD[start:end])
        ax_spec.set_ylim(y_min, y_max)
        ax_spec.set_xlim(freqs[start]+center_freq, freqs[end]+center_freq)
        ax_spec.set_ylabel('PSD / dB')
        
        ax_spec.set_xticks(np.linspace(freqs[start]+center_freq, freqs[end]+center_freq, 11))
        ax_spec.set_xticklabels(['']*11)
        ax_spec.grid(True, color='k', linewidth='1.5')

        # CF
        CF_label = ' CF: {}MHz'.format(center_freq)
        CFLabel['text'] = CF_label

        # span
        span_label = ' Span: {}KHz'.format(span)
        spanLabel['text'] = span_label
    elif  span_tmp > 1920 or span_tmp <= 0:
        spanEntry.delete(0, END)
        spanEntry.insert(0, span)
        showerror('error', 'The span is out of range! Please enter again.')
    else:
        CFEntry.delete(0, END)
        CFEntry.insert(0, center_freq)
        showerror('error', 'The center frequency is out of range! Please enter again.')


###########################__param_setting__###################################
def _destroyParamtl():
    '''Destroy tl_param window'''
    global tl_param
    paramMenu.entryconfig('Parameter Setting...', state='normal')#启用param top level
    tl_param.quit()
    tl_param.destroy()    


def parameter_toplevel():
    '''Set up param window including offset and phase'''
    global tl_param, offsetEntry, phaseEntry
    global offset, phase
    
    tl_param = Toplevel()
    paramMenu.entryconfig('Parameter Setting...', state='disabled')#禁用param top level
    
    tl_param.title('Parameter Setting')
    icon = ImageTk.PhotoImage(file='myicon.ico')
    tl_param.tk.call('wm', 'iconphoto', tl_param._w, icon)# 设置窗口logo
    tl_param.withdraw()
    tl_param.protocol('WM_DELETE_WINDOW', _destroyParamtl)

    #save button
    paramButton = Button(tl_param, text='Save', command=phase_offset_Set, font='Times')
    paramButton.grid(row=1, column=5)

    #add label
    Label(tl_param, text='    ').grid(row=1, column=4)
    Label(tl_param, text='Constellation & Eye diagram & Waveform').grid(row=0, column=0,columnspan=6)
    
    offsetLabel = Label(tl_param, text='offset:', font='Times')
    offsetLabel.grid(row=1, column=0)

    offsetEntry = Entry(tl_param, width=6)
    offsetEntry.grid(row=1, column=1)
    offsetEntry.insert(0, offset)

    phasesetLabel = Label(tl_param, text='  phase:', font='Times')
    phasesetLabel.grid(row=1, column=2)

    phaseEntry = Entry(tl_param, width=6)
    phaseEntry.grid(row=1, column=3)
    phaseEntry.insert(0, phase)

    tl_param.update()
    tl_param.deiconify()
    tl_param.mainloop()
    

def phase_offset_Set():
    '''Get the input of phase and offset'''
    global phase, offset
    global offsetEntry, phaseEntry
    
    try:offset_tmp = int(offsetEntry.get())
    except:
        offset_tmp = 0
        offsetEntry.delete(0,END)
        
    try:phase_tmp = float(phaseEntry.get())
    except:
        phase_tmp = 0
        phaseEntry.delete(0,END)

    if phase_tmp >= -(np.pi) and phase_tmp <= np.pi and offset_tmp >= 0 and offset_tmp < osr:
        phase = phase_tmp
        offset = offset_tmp
    elif phase_tmp < -(np.pi) or phase_tmp > np.pi:
        phaseEntry.delete(0, END)
        phaseEntry.insert(0, phase)
        showerror('error', 'The phase is out of range! Please enter again.')
    else:
        offsetEntry.delete(0, END)
        offsetEntry.insert(0, offset)         
        showerror('error', 'The offset is out of range! Please enter again.')
        
    print 'phase', phase
    print 'offset', offset


###########################__constellationdiagram__###################################
def updateConstellationdiagram(data):
    '''Update function for Constellationdiagram'''
    global line_cd
    global phase, offset
    
    mean = np.sqrt(np.mean(np.abs(data)**2))
    if mean == 0:
        mean = 1
    data_mean = data / mean
    data_mean = data_mean*np.exp(1j*phase)
    r_data = data_mean.real[input_sample_len/2+offset+sym_idx]
    i_data = data_mean.imag[input_sample_len/2+offset+sym_idx]             
    line_cd.set_xdata(r_data)
    line_cd.set_ydata(i_data)
    return line_cd,


def _destroyCdWindow():
    '''Destroy tl_cd'''
    global tl_cd, cdFlag
    cdFlag = 0
    
    if not pause:
        viewMenu.entryconfig('Constellation', state='normal')#启用Constellation
    tl_cd.quit()
    tl_cd.destroy()


def constellationdiagram_window():
    '''Set up constellationdiagram window'''
    global tl_cd, cdFlag
    global offsetEntry, phaseEntry
    global phase, offset
    global line_cd, data
    cdFlag = 1
    
    #add window    
    tl_cd = Toplevel()
    viewMenu.entryconfig('Constellation', state='disabled')#禁用Constellation
    
    tl_cd.title('Constellation diagram')
    tl_cd.geometry("500x550")
    tl_cd.resizable(0, 0)
    
    icon = ImageTk.PhotoImage(file='myicon.ico')
    tl_cd.tk.call('wm', 'iconphoto', tl_cd._w, icon)# 设置窗口logo

    tl_cd.withdraw()
    tl_cd.protocol('WM_DELETE_WINDOW', _destroyCdWindow)
    
    #add frames
    cd_toolFrame = Frame(tl_cd, height=40, bg='#D9D9D9')
    cd_toolFrame.grid(row=0, column=0, sticky=W)
    #cd_toolFrame.grid_propagate(True)#固定frame大小用的

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
    canvas_cd = FigureCanvasTkAgg(fig_cd, master=tl_cd)
    canvas_cd.show()
    canvas_cd.get_tk_widget().grid(row=1, column=0)
    
    toolbar = NavigationToolbar2TkAgg(canvas_cd, cd_toolFrame)# constellationdiagram的canvas
    toolbar.pack()
    toolbar.update()
    # 动画延时
##    ani_cd = animation.FuncAnimation(fig_cd, updateConstellationdiagram, inputData, interval=500, repeat=False)
    ani_cd = animation.FuncAnimation(fig_cd, updateConstellationdiagram, inputData, repeat=False)
    
    tl_cd.update()
    tl_cd.deiconify()
    tl_cd.mainloop()


##############################__waveform__#################################
def updateWaveform(data):
    '''Update function for wavaform'''
    global phase, offset
    global line1, line2
    
    mean = np.sqrt(np.mean(np.abs(data)**2))
    if mean == 0:
        mean = 1
    data_mean = data / mean
    data_mean = data_mean*np.exp(1j*phase)
    idx = input_sample_len/2 + offset + np.arange(sample_num)
    r_data = data_mean.real[idx]
    i_data = data_mean.imag[idx]
    line1.set_ydata(r_data)
    line2.set_ydata(i_data)
    return [line1,line2]
    

def _destroyWfWindow():
    '''destroy waveform window'''
    global waveformTl, waveFlag
    waveFlag = 0
    
    if not pause:
        viewMenu.entryconfig('Waveform', state='normal')#启用waveform
    waveformTl.quit()
    waveformTl.destroy()

    
def ToplevelWaveform(): #选择view菜单点击waveform出现
    global line1, line2
    global waveformTl, waveFlag
    global phase, offset
    global data
    waveFlag = 1
    
    waveformTl = Toplevel()
    viewMenu.entryconfig('Waveform', state='disabled')#禁用waveform

    waveformTl.title('Waveform')
    waveformTl.geometry("500x550")
    waveformTl.resizable(0, 0)
    
    icon = ImageTk.PhotoImage(file='myicon.ico')
    waveformTl.tk.call('wm', 'iconphoto', waveformTl._w, icon)# 设置窗口logo

    waveformTl.withdraw()
    waveformTl.protocol('WM_DELETE_WINDOW', _destroyWfWindow)

    #add frames
    wf_toolFrame = Frame(waveformTl, height=40, bg='#D9D9D9')
    wf_toolFrame.grid(row=0, column=0, sticky=W)
    
    fig_wf = plt.figure(figsize=(5,5), dpi=100, facecolor='#D9D9D9')
    fig_wf.subplots_adjust(left=0.1, right=0.94, top=0.97, bottom=0.04, hspace=0.2)
    
    subfig1 = plt.subplot(211)  # real waveform
    subfig2 = plt.subplot(212)  # imag waveform
        
    line1, = subfig1.plot(sample_idx, np.zeros(sample_num))
    line2, = subfig2.plot(sample_idx, np.zeros(sample_num))

    subfig1.set_xlim(sample_idx[1], sample_idx[-1])
    subfig2.set_xlim(sample_idx[1], sample_idx[-1])
    subfig1.set_ylim(-2, 2)
    subfig2.set_ylim(-2, 2)
    subfig1.grid(True)
    subfig2.grid(True)
    
    canvas_wf = fig_wf.canvas
    canvas_wf = FigureCanvasTkAgg(fig_wf, master=waveformTl)
    canvas_wf.show()
    canvas_wf.get_tk_widget().grid(row=1, column=0)

    toolbar = NavigationToolbar2TkAgg(canvas_wf, wf_toolFrame)
    toolbar.pack()
    toolbar.update()
    # 动画
##    ani = animation.FuncAnimation(fig_wf, updateWaveform, inputData, interval=500, repeat=False)
    ani = animation.FuncAnimation(fig_wf, updateWaveform, inputData, repeat=False)
    
    waveformTl.update()
    waveformTl.deiconify()
    waveformTl.mainloop()


#################################__eye__#####################################
def update_eyediagram(data):#eyediagram更新函数
    '''Update function for eye diagram'''
    global subfig3, subfig4
    global phase, offset
    
    mean = np.sqrt(np.mean(np.abs(data)**2))
    if mean == 0:
        mean = 1
    data_mean = data / mean
    data_mean = data_mean*np.exp(1j*phase)

    for eye_idx in range(sym_num_display):
        interval = int(osr)
        start = input_sample_len/2 + offset + interval/2 + eye_idx*interval
        subfig3.plot(range(interval), data_mean.real[start+np.arange(interval)])
        subfig4.plot(range(interval), data_mean.imag[start+np.arange(interval)])

    if len(subfig3.lines) >= 41:
        del subfig3.lines[1:21]
        del subfig4.lines[1:21]


def _destroyEyeWindow():
    '''Destroy eye diagram window'''
    global eyeTl, eyeFlag
    eyeFlag = 0
    
    if not pause:
        viewMenu.entryconfig('Eye diagram', state='normal')#启用waveform
    eyeTl.quit()
    eyeTl.destroy()


def eyeWindow():
    '''Set up eye diagram window'''
    global eyeTl, eyeFlag
    global phase, offset
    global data
    global subfig3, subfig4
    eyeFlag = 1
    
    eyeTl = Toplevel()
    viewMenu.entryconfig('Eye diagram', state='disabled')

    eyeTl.title('Eye diagram')
    eyeTl.geometry('500x550')
    eyeTl.resizable(0, 0)
    icon = ImageTk.PhotoImage(file='myicon.ico')
    eyeTl.tk.call('wm', 'iconphoto', eyeTl._w, icon)

    eyeTl.withdraw()
    eyeTl.protocol('WM_DELETE_WINDOW', _destroyEyeWindow)

    eye_toolFrame = Frame(eyeTl, height=40, bg='#D9D9D9')
    eye_toolFrame.grid(row=0, column=0, sticky=W)

    fig_eye = plt.figure(figsize=(5,5), dpi=100, facecolor='#D9D9D9')
    fig_eye.subplots_adjust(left=0.04, right=0.96, bottom=0.04, top=0.97, hspace=0.2)
    subfig3 = plt.subplot(211)  # real eyediagram
    subfig4 = plt.subplot(212)  # imag eyediagram
    
    line3 = subfig3.plot(100*[int(osr)/2], np.linspace(-2,2,100), 'k--')
    line4 = subfig4.plot(100*[int(osr)/2], np.linspace(-2,2,100), 'k--')
    
    subfig3.set_xlim(0, osr-1)
    subfig4.set_xlim(0, osr-1)

    subfig3.set_yticks([])
    subfig4.set_yticks([])

    canvas_eye = fig_eye.canvas
    canvas_eye = FigureCanvasTkAgg(fig_eye, master=eyeTl)
    canvas_eye.show()
    canvas_eye.get_tk_widget().grid(row=1, column=0)

    toolbar = NavigationToolbar2TkAgg(canvas_eye, eye_toolFrame)
    toolbar.pack()
    toolbar.update()
    # 动画延时
##    ani = animation.FuncAnimation(fig_eye, update_eyediagram, inputData, interval=500, repeat=False)
    ani = animation.FuncAnimation(fig_eye, update_eyediagram, inputData, repeat=False)
    
    eyeTl.update()
    eyeTl.deiconify()
    eyeTl.mainloop()


############################__FM__############################
def _destroyFMWindow():
    '''Destroy FM window'''
    global fmTl, fmFlag
    global pause, eyeFlag, cdFlag, waveFlag
    pause = False
    fmFlag = 0
    
    fm_top.fm_end()
    symbol_tx.SYMBOL_TX.sym_tx_stop = 0
    qamSend(mod_order, tx_q)
    viewMenu.entryconfig('FM', state='normal')
    if not eyeFlag:
        viewMenu.entryconfig('Eye diagram', state='normal')
    if not cdFlag:
        viewMenu.entryconfig('Constellation', state='normal')
    if not waveFlag:
        viewMenu.entryconfig('Waveform', state='normal')
    
    fmTl.quit()
    fmTl.destroy()

    
def FM_play():
    '''Listening FM radio'''
    global fmTl, fmFlag
    global pause
    pause = True
    fmFlag = 1
    
    fmTl = Toplevel()
    viewMenu.entryconfig('FM', state='disabled')
    viewMenu.entryconfig('Eye diagram', state='disabled')
    viewMenu.entryconfig('Constellation', state='disabled')
    viewMenu.entryconfig('Waveform', state='disabled')
    
    fmTl.title('FM radio')
    fmTl.geometry('512x512')
    fmTl.resizable(0, 0)
    
    icon = ImageTk.PhotoImage(file='myicon.ico')
    fmTl.tk.call('wm', 'iconphoto', fmTl._w, icon)

##    fmTl.withdraw()
    fmTl.protocol('WM_DELETE_WINDOW', _destroyFMWindow)

    pic = ImageTk.PhotoImage(file='FM.jpg')
    img = Label(fmTl, image=pic)
    img.pack()

    symbol_tx.SYMBOL_TX.sym_tx_stop = 1
    fm_top.fm_send(tx_q)
    fm_top.fm_recv(fm_q)

    fmTl.update()
##    fmTl.deiconify()
    fmTl.mainloop()

    
#############################__main__#############################
sample_freq = 1.92e6
osr = 64
sym_num_display = 20
input_sample_len = 115200
mod_order = 1
time_step = 1. / sample_freq
data_duration = input_sample_len / sample_freq
sample_num = int(np.round(sym_num_display*osr))
sample_idx = input_sample_len / 2 + np.arange(sample_num)#
sym_idx = np.round(np.arange(sym_num_display)*osr).astype(int)

phase = 0
offset = 0
center_freq = 2000#unit: MHz
span = 200#unit: KHz

q = Queue.Queue()
tx_q = q
rx_q = q
fm_q = Queue.Queue()

pause = False
eyeFlag = 0
cdFlag = 0
waveFlag = 0
fmFlag = 0
tl_cd = None
tl_param = None
waveformTl = None
eyeTl = None
fmTl = None

data = np.zeros(input_sample_len, dtype=complex)
PSD = np.zeros(input_sample_len)

##qamSend(mod_order, tx_q)# 启动发送线程

#########################__set_top_window__#######################################
root = Tk()
root.withdraw()
root.protocol('WM_DELETE_WINDOW', _destroyRoot)

root.title("Digital Signal Analyzer Based on SDR")
root.geometry("900x635")
root.resizable(0, 0)
icon = ImageTk.PhotoImage(file='myicon.ico')
cf_span_icon = ImageTk.PhotoImage(file='cursor.ico')# 设置span/cf的logo
root.tk.call('wm', 'iconphoto', root._w, icon)# 设置窗口logo

###########################__spectrum_initial__######################################
fig_spec, ax_spec = plt.subplots(figsize=(9,5), dpi=100, facecolor='#D9D9D9')#D9D9D9
fig_spec.subplots_adjust(left=0.08, right=0.96, bottom=0.01, top=0.96)
y_min = 0
y_max = 100
plt.ylim(y_min, y_max)
plt.ylabel('PSD / dB')

canvas_spec = fig_spec.canvas
canvas_spec = FigureCanvasTkAgg(fig_spec, master=root)
canvas_spec.mpl_connect('motion_notify_event', mousePosition)
canvas_spec.show()
canvas_spec.get_tk_widget().grid(row=1, column=0)

freqs = np.fft.fftshift(np.fft.fftfreq(input_sample_len, time_step))/1e6 #MHz
span_half = int(input_sample_len*span*1e3/sample_freq/2)
start = input_sample_len/2 - span_half
end = input_sample_len/2 + span_half

ax_spec.set_xticks(np.linspace(freqs[start]+center_freq, freqs[end]+center_freq, 11))
ax_spec.set_xticklabels(['']*11)
ax_spec.grid(True, color='k', linewidth='1.5')

line_spec, = ax_spec.plot(freqs[start:end]+center_freq, PSD[start:end])
##plt.vlines(np.linspace(freqs[start]+center_freq, freqs[end]+center_freq, 11), y_min, y_max, hold=None, color='k', linestyle='--')
##plt.hlines(np.linspace(y_min, y_max, 11), freqs[start]+center_freq, freqs[end]+center_freq, hold=None, color='k', linestyle='--')    

ani = animation.FuncAnimation(fig_spec, updateSpectrum, inputData, interval=500, repeat=False)
##ani = animation.FuncAnimation(fig_spec, updateSpectrum, inputData, repeat=False)

###########################__menubar__#####################################
menuBar = Menu(root)
root.config(menu=menuBar)
# add logo
menuBar.add_cascade(label=None, menu=None, image=icon)
# file menu
fileMenu = Menu(menuBar)
fileMenu.add_command(label="Open", accelerator="Ctrl+N", command=None)
fileMenu.add_command(label="Save", accelerator="Ctrl+S", command=_saveFig)
fileMenu.add_command(label="Save as...", accelerator="Ctrl+Shift+S", command=None)
fileMenu.add_command(label="Exit", accelerator="Ctrl+Q", command=_destroyRoot)
menuBar.add_cascade(label="File", menu=fileMenu)
# edit menu
editMenu = Menu(menuBar)
editMenu.add_command(label="Undo", accelerator="Ctrl+Z", command=None)
editMenu.add_command(label="Redo", accelerator="Ctrl+Alt+Z", command=None)
editMenu.add_separator()
editMenu.add_command(label="Copy", accelerator="Ctrl+C", command=None)
editMenu.add_command(label="Paste", accelerator="Ctrl+C", command=None)
editMenu.add_command(label="Cut", accelerator="Ctrl+X", command=None)
editMenu.add_command(label="Select all", accelerator="Ctrl+A", command=None)
editMenu.add_separator()
editMenu.add_command(label="Find...", accelerator="Ctrl+F", command=None)
menuBar.add_cascade(label="Edit", menu=editMenu)
# view menu
viewMenu = Menu(menuBar)
##viewMenu.add_radiobutton(label="Waveform", command=ToplevelWaveform, indicatoron=False)
viewMenu.add_command(label="Waveform", command=ToplevelWaveform)
viewMenu.add_radiobutton(label="Eye diagram", command=eyeWindow, indicatoron=False)
viewMenu.add_radiobutton(label="Constellation", command=constellationdiagram_window, indicatoron=False)
viewMenu.add_separator()
viewMenu.add_radiobutton(label="FM", command=FM_play, indicatoron=False)
menuBar.add_cascade(label="View", menu=viewMenu)
viewMenu.entryconfig('FM', state='disabled')
# run menu
runMenu = Menu(menuBar)
runMenu.add_radiobutton(label="Run", accelerator="Alt+R", command=_run, indicatoron=False)
runMenu.add_radiobutton(label="Stop", accelerator="Alt+S", command=_stop, indicatoron=False)
menuBar.add_cascade(label="Run", menu=runMenu)
# param menu
paramMenu = Menu(menuBar)
paramMenu.add_command(label="Parameter Setting...", command=parameter_toplevel)
menuBar.add_cascade(label="Param", menu=paramMenu)
# help menu
helpMenu = Menu(menuBar)
helpMenu.add_command(label="Instruction", command=instruction)
helpMenu.add_separator()
helpMenu.add_command(label="About us...", command=aboutus, image=icon, compound='left')
menuBar.add_cascade(label="Help", menu=helpMenu)

########################__frames__####################################
#
toolFrame = Frame(root, height=40, bg='#D9D9D9')
toolFrame.grid(row=0, column=0, sticky=W)

toolbar = NavigationToolbar2TkAgg(canvas_spec, toolFrame)# 主界面的canvas
toolbar.pack()
toolbar.update()
#
paramFrame = Frame(root, height=40, bg='#D9D9D9')
paramFrame.grid(row=0, column=0)

CFLabel = Label(paramFrame, text='Center Frequency:', font='Times')
CFLabel.grid(row=0, column=0, sticky=W)

CFEntry = Entry(paramFrame, width=6)
CFEntry.grid(row=0, column=1)
CFEntry.insert(0, 2000)

CFUnit = Label(paramFrame, text='MHz', font='Times')
CFUnit.grid(row=0, column=2)

Label(paramFrame, text='    ').grid(row=0, column=3)

spanLabel = Label(paramFrame, text='Span:', font='Times')
spanLabel.grid(row=0, column=4)

spanEntry = Entry(paramFrame, width=6)
spanEntry.grid(row=0, column=5)
spanEntry.insert(0, 200)

spanUnit = Label(paramFrame, text='KHz', font='Times')
spanUnit.grid(row=0, column=6)

Label(paramFrame, text='    ').grid(row=0, column=7)

saveButton = Button(paramFrame, text='Save', command=setParamSpec, font='Times')
saveButton.grid(row=0, column=8)
#
bwFrame = Frame(root, height=40, bg='#D9D9D9')
bwFrame.grid(row=0, column=0, sticky=E)

bandwidth = 'Bandwidth: {0:>6}KHz'.format(' ')
bwLabel = Label(bwFrame, text=bandwidth, font='Times')
bwLabel.grid(row=0, column=0, padx=40)

#####################__Label__####################################
# CF
CF_label = ' CF: {}MHz'.format(center_freq)
CFLabel = Label(root, text=CF_label, font='Times', image=cf_span_icon, compound='left')
CFLabel.grid(row=2, column=0, padx=10, pady=6, sticky=W)

# position
pos_xy = ''
posLabel = Label(root, text=pos_xy, font='Times')
posLabel.grid(row=2, column=0, padx=10, pady=6)

# span
span_label = ' Span: {}KHz'.format(span)
spanLabel = Label(root, text=span_label, font='Times', image=cf_span_icon, compound='left')
spanLabel.grid(row=2, column=0, padx=10, pady=6, sticky=E)

#cursor
cursorFrame = Frame(root, height=40, bg='#D9D9D9')
cursorFrame.grid(row=3, column=0,sticky=W)
cursorFrame2 = Frame(root, height=40, bg='#D9D9D9')
cursorFrame2.grid(row=3, column=0,sticky=E)
cursorLabel1=Label(cursorFrame,text='  Frequency:',font='Times',image=icon, compound='left').grid(row=0,column=0,padx=10, pady=6,sticky=W)
cursorEntry=Entry(cursorFrame,width=10)
cursorEntry.grid(row=0,column=1)
cursorEntry.insert(0,'2000.0')
cursorLabel2=Label(cursorFrame,text='MHz',font='Times').grid(row=0,column=2,padx=10, pady=6)
cursor_Checkbutton = IntVar()
cursorCheckbutton = Checkbutton(cursorFrame,command=updateCursor, text='Capture',font='Times',width=8,height=1,indicatoron=0,variable = cursor_Checkbutton, onvalue =1, offvalue = 0)
cursorCheckbutton.grid(row=0,column=3,padx=10, pady=6, sticky=W)

cursor_xyLabel = Label(cursorFrame2, text=None, font='Times', image=None, fg='blue', compound='left')
cursor_xyLabel.grid(row=0,column=0,padx=10, pady=6)
###################################################################
# reminder
reminderFrame = Frame(root, height=40, bg='#A3A3A3')
reminderFrame.grid(row=4, column=0, sticky=EW)

####################__accelerator__####################################
root.bind_all("<Control-q>", destroyRoot)
root.bind_all("<Alt-r>", run)
root.bind_all("<Alt-s>", stop)

root.update()
root.deiconify()
root.mainloop()
