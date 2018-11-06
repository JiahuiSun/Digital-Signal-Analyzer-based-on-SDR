import Parameter as P
from initWindow import *
from Tkinter import *

   
def setupFMTl():
    '''Listening FM radio''' 
    if P.Flags['eyeFlag']:
        P.eyeTl._destroy()
    if P.Flags['cdFlag']:
        P.cdTl._destroy()
    if P.Flags['wfFlag']:
        P.wfTl._destroy()
    if P.Flags['paramFlag']:
        P.paramTl._destroy()
        
    P.fmTl = initFM(Toplevel(), P.viewMenu, flag='fmFlag', size='500x500', title='FM', icon=P.logoIcon)
    
    img = Label(P.fmTl.root, image=P.FMcover)
    img.pack()

    P.fmTl.root.mainloop()
