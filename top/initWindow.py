import Parameter as P
import sys
import fm_top
from common import *


class initWindow:
    def __init__(self, parent, flag='specFlag', size='900x635', title='SDR', icon=None):
        self.root = parent
        self.flag = flag
        self.size = size
        self.title = title
        self.icon = icon
        
        self.root.title(self.title)
        self.root.geometry(self.size)
        self.root.resizable(0, 0)
        
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.icon)
        self.root.protocol('WM_DELETE_WINDOW', self._destroy)
##        self.root.bind_all('<Control-q>', self.destroy)

        P.Flags[self.flag] = 1
        
    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()

    def _destroy(self):
        P.Flags[self.flag] = 0
        self.root.quit()
        self.root.destroy()

    def destroy(self, event):
        P.Flags[self.flag] = 0
        self.root.quit()
        self.root.destroy()
        

class initmainWindow(initWindow):
    def __init__(self, parent, flag='specFlag', size='900x635', title='SDR', icon=None):
        self.root = parent
        self.flag = flag
        self.size = size
        self.title = title
        self.icon = icon
        
        self.root.bind_all('<Control-q>', self.destroy)
        
        initWindow.__init__(self, parent, flag, size, title, icon)

    def _destroy(self):
        symbol_tx.SYMBOL_TX.sym_tx_stop = 1
        update_data.update_data.rx_stop = 1
        
        initWindow._destroy(self)
        sys.exit()

    def destroy(self, event):
        symbol_tx.SYMBOL_TX.sym_tx_stop = 1
        update_data.update_data.rx_stop = 1
        
        initWindow.destroy(self, event)
        sys.exit()


class initTl(initWindow):
    def __init__(self, parent, menu, flag='eyeFlag', size='900x635', title='SDR', icon=None):
        self.root = parent
        self.menu = menu
        self.title = title
        self.flag = flag
        self.size = size
        self.icon = icon
        
        self.menu.entryconfig(self.title, state='disabled')

        initWindow.__init__(self, parent, flag, size, title, icon)
        P.reminderCanvas.itemconfig(P.reminder, text=self.title+' is set up.')
    #????绑定的是父类的destroy，为什么点击×时调用子类的destroy函数
    def _destroy(self):
        self.menu.entryconfig(self.title, state='normal')
        initWindow._destroy(self)
        P.reminderCanvas.itemconfig(P.reminder, text=self.title+' is destroyed.')
        
    def destroy(self, event):
        self.menu.entryconfig(self.title, state='normal')
        initWindow.destroy(self, event)


class initFM(initTl):
    def __init__(self, parent, menu, flag='eyeFlag', size='900x635', title='SDR', icon=None):
        self.root = parent
        self.menu = menu
        self.flag = flag
        self.size = size
        self.title = title
        self.icon = icon
        
        self.menu.entryconfig('Eye Diagram', state='disabled')
        self.menu.entryconfig('Constellation Diagram', state='disabled')
        self.menu.entryconfig('Waveform', state='disabled')
        
        initTl.__init__(self, parent, menu, flag, size, title, icon)

        symbol_tx.SYMBOL_TX.sym_tx_stop = 1
        fm_top.fm_send(P.tx_q)
        fm_top.fm_recv(P.fm_q)
        
    def _destroy(self):
        self.menu.entryconfig('Eye Diagram', state='normal')
        self.menu.entryconfig('Constellation Diagram', state='normal')
        self.menu.entryconfig('Waveform', state='normal')
        
        fm_top.fm_end()
        symbol_tx.SYMBOL_TX.sym_tx_stop = 0
        qamSend()
        
        initTl._destroy(self)
        
    def destroy(self, event):
        self.menu.entryconfig('Eye Diagram', state='normal')
        self.menu.entryconfig('Constellation Diagram', state='normal')
        self.menu.entryconfig('Waveform', state='normal')

        fm_top.fm_end()
        symbol_tx.SYMBOL_TX.sym_tx_stop = 0
        qamSend()
        
        initTl.destroy(self, event)
