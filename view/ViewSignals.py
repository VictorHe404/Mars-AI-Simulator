from PyQt6.QtCore import QObject, pyqtSignal

class ViewSignals(QObject):
    #Main map update signal
    main_map_signal = pyqtSignal(str)
    mini_map_signal = pyqtSignal(str)