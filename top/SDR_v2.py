__version__ = "$Revision: SDR_v2.0 $"

import sys
sys.path.append('..')
import warnings
import numpy as np
import spectrum
from Tkinter import *

# self module
import update_data
import ParaSetCliSock
import Parameter as P
from initWindow import *
from Help import *
from FM import *
from eye import *
from waveform import *
from constellation import *
from spec import *
from phase_offset import *
from common import *


title = "Digital Signal Analyzer Based on Software Defined Radio"
mainInterface = initmainWindow(P.root, flag='specFlag', size='900x635', title=title, icon=P.logoIcon)

fig_spec, P.as_spec = plt.subplots(figsize=(9,5), dpi=100, facecolor='#D9D9D9')
fig_spec.subplots_adjust(left=0.08, right=0.96, bottom=0.01, top=0.96)
y_min = 0
y_max = 100
plt.ylim(y_min, y_max)
plt.ylabel('PSD / dB')

P.as_spec.set_xticks(np.linspace(P.Params['cf_start'], P.Params['cf_end'], 11))
P.as_spec.set_xticklabels(['']*11)
P.as_spec.grid(True, color='k', linewidth='1.5')
P.line_spec, = P.as_spec.plot(P.Params['spec_idx'], P.PSD[P.Params['start']:P.Params['end']])

canvas_spec = fig_spec.canvas
canvas_spec = FigureCanvasTkAgg(fig_spec, master=mainInterface.root)
canvas_spec.mpl_connect('motion_notify_event', mousePosition)
canvas_spec.show()
canvas_spec.get_tk_widget().grid(row=1, column=0)

menuBar = Menu(mainInterface.root)
mainInterface.root.config(menu=menuBar)
# add logo
menuBar.add_cascade(label=None, menu=None, image=P.logoIcon)
# file menu
P.fileMenu = Menu(menuBar)
P.fileMenu.add_command(label="Open", accelerator="Ctrl+N", command=None)
P.fileMenu.add_command(label="Save", accelerator="Ctrl+S", command=None)
P.fileMenu.add_command(label="Save as...", accelerator="Ctrl+Shift+S", command=None)
P.fileMenu.add_command(label="Exit", accelerator="Ctrl+Q", command=mainInterface._destroy)
menuBar.add_cascade(label="File", menu=P.fileMenu)
# edit menu
P.editMenu = Menu(menuBar)
P.editMenu.add_command(label="Undo", accelerator="Ctrl+Z", command=None)
P.editMenu.add_command(label="Redo", accelerator="Ctrl+Alt+Z", command=None)
P.editMenu.add_separator()
P.editMenu.add_command(label="Copy", accelerator="Ctrl+C", command=None)
P.editMenu.add_command(label="Paste", accelerator="Ctrl+C", command=None)
P.editMenu.add_command(label="Cut", accelerator="Ctrl+X", command=None)
P.editMenu.add_command(label="Select all", accelerator="Ctrl+A", command=None)
P.editMenu.add_separator()
P.editMenu.add_command(label="Find...", accelerator="Ctrl+F", command=None)
menuBar.add_cascade(label="Edit", menu=P.editMenu)
# view menu
P.viewMenu = Menu(menuBar)
P.viewMenu.add_command(label="Waveform", command=setupWfTl)
P.viewMenu.add_command(label="Eye Diagram", command=setupEyeTl)
P.viewMenu.add_command(label="Constellation Diagram", command=setupCdTl)
P.viewMenu.add_separator()
P.viewMenu.add_command(label="FM", command=setupFMTl)
menuBar.add_cascade(label="View", menu=P.viewMenu)
P.viewMenu.entryconfig('FM', state='disabled')
# run menu
P.runMenu = Menu(menuBar)
P.runMenu.add_command(label="Run", accelerator="Alt+R", command=drun)
P.runMenu.add_command(label="Stop", accelerator="Alt+S", command=dstop)
menuBar.add_cascade(label="Run", menu=P.runMenu)
# param menu
P.paramMenu = Menu(menuBar)
P.paramMenu.add_command(label="Parameter Setting", command=setupParamTl)
menuBar.add_cascade(label="Param", menu=P.paramMenu)
# help menu
P.helpMenu = Menu(menuBar)
P.helpMenu.add_command(label="Instruction", command=instruction)
P.helpMenu.add_separator()
P.helpMenu.add_command(label=" About us", command=aboutus, image=P.logoIcon, compound='left')
menuBar.add_cascade(label="Help", menu=P.helpMenu)

# tool frame
toolFrame = Frame(mainInterface.root, height=40, bg='#D9D9D9')
toolFrame.grid(row=0, column=0, sticky=W)

toolbar = NavigationToolbar2TkAgg(canvas_spec, toolFrame)
toolbar.pack()
toolbar.update()
# parameter frame
paramFrame = Frame(mainInterface.root, height=40, bg='#D9D9D9')
paramFrame.grid(row=0, column=0)

P.CFLabel = Label(paramFrame, text='Center Frequency:', font='Times')
P.CFLabel.grid(row=0, column=0, sticky=W)

P.CFEntry = Entry(paramFrame, width=8)
P.CFEntry.grid(row=0, column=1)
P.CFEntry.insert(0, 2000)

CFUnit = Label(paramFrame, text='MHz', font='Times')
CFUnit.grid(row=0, column=2)

Label(paramFrame, text='    ').grid(row=0, column=3)

P.spanLabel = Label(paramFrame, text='Span:', font='Times')
P.spanLabel.grid(row=0, column=4)

P.spanEntry = Entry(paramFrame, width=6)
P.spanEntry.grid(row=0, column=5)
P.spanEntry.insert(0, 200)

spanUnit = Label(paramFrame, text='KHz', font='Times')
spanUnit.grid(row=0, column=6)

Label(paramFrame, text='    ').grid(row=0, column=7)

saveButton = Button(paramFrame, text='Save', command=setParamSpec, font='Times')
saveButton.grid(row=0, column=8)
# bandwidth frame
bwFrame = Frame(mainInterface.root, height=40, bg='#D9D9D9')
bwFrame.grid(row=0, column=0, sticky=E)

bandwidth = 'Bandwidth: {0:>6}KHz'.format(' ')
P.bwLabel = Label(bwFrame, text=bandwidth, font='Times')
P.bwLabel.grid(row=0, column=0, padx=10)

# CF label
CF_label = ' CF: {}MHz'.format(P.Params['center_freq'])
P.CFLabel = Label(mainInterface.root, text=CF_label, font='Times', image=P.cfspanIcon, compound='left')
P.CFLabel.grid(row=2, column=0, padx=10, pady=6, sticky=W)

# position label
P.posLabel = Label(mainInterface.root, text='', font='Times')
P.posLabel.grid(row=2, column=0, padx=10, pady=6)

# span label
span_label = ' Span: {}KHz'.format(P.Params['span'])
P.spanLabel = Label(mainInterface.root, text=span_label, font='Times', image=P.cfspanIcon, compound='left')
P.spanLabel.grid(row=2, column=0, padx=10, pady=6, sticky=E)

# cursor frame
cursorFrame = Frame(mainInterface.root, height=40, bg='#D9D9D9')
cursorFrame.grid(row=3, column=0, sticky=W)
cursorFrame2 = Frame(mainInterface.root, height=40, bg='#D9D9D9')
cursorFrame2.grid(row=3, column=0, sticky=E)

cursorLabel1=Label(cursorFrame, text=' Frequency:', font='Times', image=P.cfspanIcon, compound='left')
cursorLabel1.grid(row=0,column=0, padx=10, sticky=W)
P.cursorEntry=Entry(cursorFrame, width=10)
P.cursorEntry.grid(row=0, column=1)
P.cursorEntry.insert(0, '2000.0')
cursorLabel2=Label(cursorFrame, text='MHz', font='Times')
cursorLabel2.grid(row=0, column=2, padx=10)

P.cursor_Checkbutton = IntVar()
cursorCheckbutton = Checkbutton(cursorFrame, command=updateCursor, text='Capture', font='Times', width=8,\
                                height=1, indicatoron=0, variable=P.cursor_Checkbutton, onvalue=1, offvalue=0)
cursorCheckbutton.grid(row=0, column=3, padx=10, sticky=W)

P.cursor_xyLabel = Label(cursorFrame2, text=None, font='Times', image=None, fg='red', compound='left')
P.cursor_xyLabel.grid(row=0,column=0,padx=10)

# reminder canvas
P.reminderCanvas = Canvas(mainInterface.root, height=30, bg='#3E3E3A')
P.reminder = P.reminderCanvas.create_text(10, 15, font='System', fill='white', activefill='red', anchor=W)
P.reminderCanvas.grid(row=4, column=0, pady=10, sticky=EW)
P.reminderCanvas.itemconfig(P.reminder, text='Software initializition is completed.')

##################################__socket thread__########################################
##ParaSetCliSock.set_param('rx_freq', P.Params['center_freq'])
##ParaSetCliSock.set_param('tx_freq', P.Params['center_freq'])

mainInterface.root.bind_all("<Alt-r>", run)
mainInterface.root.bind_all("<Alt-s>", stop)
ani = animation.FuncAnimation(fig_spec, updateSpectrum, inputData, interval=500, repeat=False)

warnings.filterwarnings('ignore')

mainInterface.root.mainloop()
