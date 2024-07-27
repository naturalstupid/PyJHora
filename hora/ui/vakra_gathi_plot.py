from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QGridLayout, QComboBox
import pyqtgraph as pg
from hora import utils, const

""" mars(2),mercury(3),jupiter(4),venus(5),saturn(6),uranus(9), neptune(10), pluto(12), 
    earth(-1). Ceres (99) added just for reference and not to be used. """
_starting_planet_index = 2
retrogression_planets_periods = {2:(686.97959,18),3:(87.96926,9),4:(4332.8201,12),5:(224.7008,8),6:(10755.699,59),
                                 9:(20687.153,60),10:(60190.03,165),11:(90582.03,360),99:(1680.22107,50),-1:(365.25636,1)}

dist = lambda T : T**(2/3) # Kepler
from numpy import linspace, sin, cos, pi
def get_retrogression_orbit_data(planet):
    periods = retrogression_planets_periods[planet][1]
    T1 = retrogression_planets_periods[planet][0]
    T2 = retrogression_planets_periods[-1][0]
    d1 = dist(T1)
    d2 = dist(T2)

    theta = linspace(0, 2*pi*periods, 1000)
    x = d1*cos(T2*theta/T1) - d2*cos(theta)
    y = d1*sin(T2*theta/T1) - d2*sin(theta)
    return x,y
class VakraGathiPlot(QtWidgets.QMainWindow):
    def __init__(self,planet=6,color=(255,0,255),axis_off=True,title='',plot_width=500,plot_height=500):
        super().__init__()
        self.title = title
        self.color = color
        self.plot_width = plot_width; self.plot_height = plot_height; self.axis_off = axis_off
        # Temperature vs time plot
        self.plot_graph = pg.PlotWidget()
        widget = QWidget()
        layout = QGridLayout()
        self._planet_combo = QComboBox()
        _planet_list = utils.PLANET_NAMES[2:7]+utils.PLANET_NAMES[9:12]
        self._planet_combo.addItems(_planet_list)
        self._planet_combo.currentIndexChanged.connect(self._update_chart)
        self._planet_combo.setCurrentIndex(planet-_starting_planet_index)
        layout.addWidget(self._planet_combo,0,0)
        layout.addWidget(self.plot_graph,0,1,3,1)
        widget.setLayout(layout)
        #self.setCentralWidget(self.plot_graph)
        self.setCentralWidget(widget)
    def _update_chart(self):
        self.plot_graph.clear()
        planet = self._planet_combo.currentIndex()+_starting_planet_index
        if self._planet_combo.currentIndex()>4: planet = self._planet_combo.currentIndex()+_starting_planet_index+2
        self.title = utils.resource_strings['retrograde_as_seen_from_earth_str_1']+' '+utils.PLANET_NAMES[planet]+' '+utils.resource_strings['retrograde_as_seen_from_earth_str_2']
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=self.color)
        self.plot_graph.setTitle(self.title,color=(0,0,0))
        self.plot_graph.setMinimumSize(self.plot_width,self.plot_height)
        if self.axis_off:
            self.plot_graph.getPlotItem().hideAxis('left');self.plot_graph.getPlotItem().hideAxis('bottom')
        x,y=get_retrogression_orbit_data(planet)
        self.plot_graph.plot(x, y, pen=pen)
        T1 = retrogression_planets_periods[planet][0]; T2 = retrogression_planets_periods[-1][0]
        d1 = dist(T1); d2 = dist(T2)
        theta = linspace(0, 2*pi, 13)
        labels = utils.RAASI_LIST+[utils.RAASI_LIST[0]]
        label_factor = 0.85
        lbl = pg.TextItem(utils.resource_strings['earth_str'],color=(0,0,0))
        self.plot_graph.addItem(lbl); lbl.setPos(0.0,0.0)
        for i,t in enumerate(theta[:-1]):
            lbl = pg.TextItem(labels[i],color=(0,0,0))
            self.plot_graph.addItem(lbl)
            th = 0.5*(theta[i]+theta[i+1])
            x = (d1+d2)*cos(t)*label_factor; y = (d1+d2)*sin(t)*label_factor
            xh = (d1+d2)*cos(th)*label_factor; yh = (d1+d2)*sin(th)*label_factor
            lbl.setPos(xh,yh)
            #line = pg.LineSegmentROI([(0,0),(x,y)])
            line = pg.LineROI(pos1=(0,0),pos2=(x,y),width=0.5,pen = pg.mkPen(color=(255,0,0)),movable=False)
            self.plot_graph.addItem(line)
            line.setPos(0,0)
        
import sys
#const._TROPICAL_MODE = False
utils.set_language('ta')
app = QtWidgets.QApplication(sys.argv)
planet = 6
w = VakraGathiPlot(planet=planet)
w.show()
app.exec()

