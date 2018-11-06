# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import pyaudio
import wave
from scipy import fftpack
from scipy import signal
####################画图函数#######################
def tfplot(signal_input,framerate,name,title):
    t = np.arange(0, len(signal_input)) * (1.0 / framerate);       #设定时间范围
    f = np.linspace(-framerate/2,framerate/2,len(signal_input));   #设定频率范围
    #傅立叶变换
    signal_fft = np.fft.fft(signal_input)
    #时域波形
    plt.subplot(2,1,1)
    plt.plot(t,signal_input)
    plt.xlabel('t[s]')
    plt.ylabel(name)
    plt.title(title)
    #频域波形
    plt.subplot(2,1,2)
    plt.plot(f,np.fft.fftshift(abs(signal_fft)))
    plt.xlabel('f[Hz]')
    plt.ylabel(name)
    plt.show()
#####################开始############################
filepath="/home/sjh/Desktop/FM/1.wav"
wf = wave.open(filepath,'rb')
wf2 = wave.open(filepath,'rb')
#读取音频信息:声道数,量化位数,采样频率,采样点数
params = wf.getparams()
nchannels,samplewidth,framerate,nframes = params[:4]
print params

'''
#播放音频
chunk = 1024
p = pyaudio.PyAudio()
stream = p.open(format = p.get_format_from_width(samplewidth),
                channels = nchannels,
                rate = framerate,
                output = True)
data = wf.readframes(chunk)
while data != '':
      stream.write(data)
      data = wf.readframes(chunk)
stream.close() 
p.terminate()
wf.close()
'''
'''
#显示音频
indata = wf2.readframes(nframes)
outdata = np.fromstring(indata,dtype=np.short)
#wenti:显示和播放用不同的wf
tfplot(outdata,framerate,'Vfm','1.wav')
#调制,求信号x(t)的积分
fc = 2e4
kf = 10000
t = np.arange(0, nframes) * (1.0 / framerate)
sig_int = np.cumsum(outdata) / float(framerate)
sig_mod=np.cos(2*np.pi*fc*t+2*np.pi*kf*sig_int)
tfplot(sig_mod,framerate,'Vfm','sig_mod')

sig_diff = np.diff(sig_mod)/(1.0/framerate)                #进行微分
sig_diff2 = abs(fftpack.hilbert(sig_diff)) #希尔伯特变换，求绝对值得到瞬时幅度（包络检波）
sig_diff3 = sig_diff2-np.mean(sig_diff2)
sig_demod = sig_diff3/2/np.pi/kf   #调整幅度
tfplot(sig_demod,framerate,'sig','sig_demod')
sig_demod*=1e4
'''
'''
angle_data=np.angle(sig_mod)
audioda=np.diff(angle_data)
audiodata=np.unwrap(audioda)
#audiodata=signal.decimate(audiodata,DOWN_FACTOR,ftype="fir")
plt.plot(audiodata)
plt.show()
#audiodata = signal.fftconvolve(FIR_LP, audiodata)
#audiodata_amp=audiodata*1e4
#snd_data = audiodata_amp.astype(np.dtype('<i2')).tostring()
'''
'''
#write .wav
# 打开WAV文档
f = wave.open(r"sweep.wav", "wb")
# 配置声道数、量化位数和取样频率
f.setnchannels(nchannels)
f.setsampwidth(samplewidth)
f.setframerate(framerate)
# 将wav_data转换为二进制数据写入文件
f.writeframes(sig_demod.astype(np.dtype('<i2')).tostring())
#f.writeframes()
f.close()
'''
