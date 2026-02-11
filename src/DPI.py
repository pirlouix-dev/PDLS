import sys
from PyQt5.QtWidgets import QApplication

Cache = None

def GetDPI():
    global Cache
    if Cache: return Cache
    
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    screen = app.primaryScreen()
    dpi = screen.physicalDotsPerInch()
    app.quit()
    Cache = dpi
    return dpi