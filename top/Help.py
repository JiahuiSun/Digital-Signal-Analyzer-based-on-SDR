from Tkinter import *
from tkMessageBox import *


def aboutus():
    message = "本软件是在天津大学自动化学院高镇副教授指导下，\
由郭亭佚、毛岩、孙嘉徽、武建鹏、章倩编写完成。\
比较简陋，多多包涵！"        
    showinfo("About us", message)

def instruction():
    winInstru = Toplevel()
    textInstru = Text(winInstru, width=50, height=30)
    textInstru.pack()
    information = """基础知识：
1.通信原理，包括星座图、眼图、符号同步、相位、信噪比等
2.数字信号处理，包括FFT、时频变换等
3.Python编程，熟练Tkinter库、matplotlib库和numpy库

操作方法：
1.点击run开始发送并接受数据，点击stop停止发送和接受数据
2.点击view可以查看星座图、眼图、波形图和收听FM广播
"""
    textInstru.insert(END, information)
