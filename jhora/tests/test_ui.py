import sys
from PyQt6.QtWidgets import QApplication

def except_hook(cls, exception, traceback):
    print('exception called')
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook
App = QApplication(sys.argv)
#from hora.ui.horo_chart import ChartSimple
#chart = ChartSimple()
#chart.show()
from hora.ui.horo_chart_tabs import ChartTabbed
chart = ChartTabbed()
chart.show()
sys.exit(App.exec())
exit()
