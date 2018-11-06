import Parameter as P
from Tkinter import *
from common import *
from initWindow import *
import numpy as np
import spectrum
import ParaSetCliSock


def updateSpectrum(data):
    '''Power spectrum density'''    
    if not update_data.update_data.rx_stop:
        p = spectrum.Periodogram(P.data, sampling=P.Params['sample_freq'], window='hann')
        p.run()

        if sum(p.psd) == 0:
            P.PSD = np.zeros(np.size(p.psd))
            P.line_spec.set_ydata(P.PSD[P.Params['start']:P.Params['end']])
        else:
            P.PSD = np.fft.fftshift(10*np.log10(p.psd))
            P.line_spec.set_ydata(P.PSD[P.Params['start']:P.Params['end']])
            P.line_spec.set_xdata(P.Params['spec_idx'])
            
            y = np.array(P.PSD[:])
            ymax = max(y)
            idx = np.where(y>ymax*0.9)
            ave = np.mean(y[idx[0][0]:idx[0][-1]])
            threshold = ave/np.sqrt(2)
            x = np.where(y>threshold)

            bw = (x[0][-1]-x[0][0]+1)*P.Params['sample_freq']/1e3/P.Params['input_sample_len']#unit: KHz
            bandwidth = 'Bandwidth: {:.2f}KHz'.format(bw)
            P.bwLabel['text'] = bandwidth

        updateCursor()
        
    return P.line_spec,


def setParamSpec():
    '''Set span and center frequency'''    
    try:
        span_tmp = float(P.spanEntry.get())
    except:
        span_tmp = P.Params['span']
        P.spanEntry.delete(0, END)
    try:
        center_freq_tmp = float(P.CFEntry.get())
    except:
        center_freq_tmp = P.Params['center_freq']
        CFEntry.delete(0, END)
        
    if span_tmp <= 1920 and span_tmp >0 and center_freq_tmp <= 6000 and center_freq_tmp >=70:
        if P.Params['center_freq'] != center_freq_tmp:
            P.Params['center_freq'] = round(center_freq_tmp, 4)#最多保留4位小数
            ParaSetCliSock.set_param('rx_freq', P.Params['center_freq'])
            
        P.Params['span'] = span_tmp
        P.cfspanReset()

        P.as_spec.set_xlim(P.Params['cf_start'], P.Params['cf_end'])
        P.as_spec.set_xticks(np.linspace(P.Params['cf_start'], P.Params['cf_end'], 11))
        P.as_spec.set_xticklabels(['']*11)
        P.as_spec.grid(True, color='k', linewidth='1.5')

        # CF
        CF_label = ' CF: {}MHz'.format(P.Params['center_freq'])
        P.CFLabel['text'] = CF_label

        # span
        span_label = ' Span: {}KHz'.format(P.Params['span'])
        P.spanLabel['text'] = span_label
    elif  span_tmp > 1920 or span_tmp <= 0:
        P.spanEntry.delete(0, END)
        P.spanEntry.insert(0, P.Params['span'])
        showerror('error', 'The span is out of range! Please enter again.')
    else:
        P.CFEntry.delete(0, END)
        P.CFEntry.insert(0, P.Params['center_freq'])
        showerror('error', 'The center frequency is out of range! Please enter again.')

