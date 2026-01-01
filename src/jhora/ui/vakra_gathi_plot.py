#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QComboBox
from PyQt6.QtGui import QCursor
import pyqtgraph as pg
from jhora import utils, const
from jhora.panchanga import drik

""" mars(2),mercury(3),jupiter(4),venus(5),saturn(6),uranus(9), neptune(10), pluto(11), 
    earth(-1). Ceres (99) added just for reference and not to be used. """
_starting_planet_index = 2
retrogression_planets_periods = {2:(686.97959,18),3:(87.96926,9),4:(4332.8201,12),5:(224.7008,8),6:(10755.699,59),
                                 9:(20687.153,60),10:(60190.03,165),11:(90582.03,248),99:(1680.22107,50),-1:(365.25636,1)}
_track_mouse_coordinates = False
dist = lambda T : T**(2/3) # Kepler
from numpy import linspace, sin, cos, pi
def get_planet_entry_data(start_jd,place):
    npe_data = {}
    for planet in list(retrogression_planets_periods.keys())[:5]:
        npe_data[planet]={}
        jd_utc = start_jd - place.timezone/24.
        p_long = drik.sidereal_longitude(jd_utc, planet)
        y,m,d,_ = utils.jd_to_gregorian(start_jd)
        p_date = drik.Date(y,m,d)
        rasi = p_long//30
        theta = linspace(0, 2*pi, 13)
        for i,t in enumerate(theta[:-1]):
            r = int(rasi+i)%12
            npe = drik.next_planet_entry_date(planet, start_jd, place,raasi=None,direction=1) # V4.5.0
            y,m,d,_ = utils.jd_to_gregorian(npe[0]); p_long = npe[1]
            npe_data[planet][r]=((y,m,d),p_long)
            start_jd = npe[0]+0.1
            #print(planet,'next raasi',p_date,p_long,p_long//30)
    return npe_data 
def get_retrogression_orbit_data(planet,start_angle=0):
    #print('planet',planet,retrogression_planets_periods[planet],'periods',periods)
    periods = retrogression_planets_periods[planet][1]
    T1 = retrogression_planets_periods[planet][0]
    T2 = retrogression_planets_periods[-1][0]
    d1 = dist(T1)
    d2 = dist(T2)

    theta = linspace(start_angle, 2*pi*periods+start_angle, 1000)
    x = d1*cos(T2*theta/T1) - d2*cos(theta)
    y = d1*sin(T2*theta/T1) - d2*sin(theta)
    return x,y
class VakraGathiPlot(QtWidgets.QMainWindow):
    def __init__(self,start_jd=None,place=None,planet=6,color=(255,0,255),axis_off=True,title='',plot_width=500,plot_height=500,
                 language='Tamil'):
        super().__init__()
        self._start_jd = start_jd
        self._place = place
        self.title = title
        self.color = color
        self.plot_width = plot_width; self.plot_height = plot_height; self.axis_off = axis_off
        self._next_planet_entry_data = {}
        if self._start_jd  is not None and self._place  is not None:
            self._next_planet_entry_data = get_planet_entry_data(start_jd,place)
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
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(const.available_languages.keys())
        self._lang_combo.setCurrentText(language)
        self._language = const.available_languages[language]
        self._lang_combo.activated.connect(self._change_language)
        layout.addWidget(self._lang_combo,1,0)
        layout.addWidget(self.plot_graph,0,1,3,1)
        widget.setLayout(layout)
        self._change_language()
        self.setCentralWidget(widget)
    def _change_language(self):
        _language_index = self._lang_combo.currentIndex()
        self._language = list(const.available_languages.values())[_language_index]
        #print('self._language',self._language)
        utils.set_language(self._language)
        msgs = utils.resource_strings
        self._lang_combo.clear()
        self._lang_combo.addItems([msgs[l.lower()+'_str'] for l in const.available_languages.keys()])
        self._lang_combo.setCurrentIndex(_language_index)

        _planet_list = utils.PLANET_NAMES[2:7]+utils.PLANET_NAMES[9:12]
        _current_planet_index = self._planet_combo.currentIndex()
        self._planet_combo.clear()
        self._planet_combo.addItems(_planet_list)
        self._planet_combo.setCurrentIndex(_current_planet_index)
    def onMouseMoved(self, evt):
        #print('mouse moved',evt.x(),evt.y())
        if self.plot_graph.plotItem.vb.mapSceneToView(evt) and self.line.cursor()==Qt.CursorShape.PointingHandCursor:
            point =self.plot_graph.plotItem.vb.mapSceneToView(evt)
            print(point.x(),point.y())
            #self.mouse_label.setPos(-560,560)
            self.mouse_label.setText("Date： {0} \nLongitude: {1}".format(point.x(), point.y()),color='b')
    def _update_chart(self):
        self.plot_graph.clear()
        planet = self._planet_combo.currentIndex()+_starting_planet_index
        if self._planet_combo.currentIndex()>4: planet = self._planet_combo.currentIndex()+_starting_planet_index+2
        if planet not in retrogression_planets_periods.keys(): return
        # Draw retrograde graph
        self.title = utils.resource_strings['retrograde_as_seen_from_earth_str_1']+' '+utils.PLANET_NAMES[planet]+' '+utils.resource_strings['retrograde_as_seen_from_earth_str_2']
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=self.color)
        self.plot_graph.setTitle(self.title,color=(0,0,0))
        self.plot_graph.setMinimumSize(self.plot_width,self.plot_height)
        T1 = retrogression_planets_periods[planet][0]; T2 = retrogression_planets_periods[-1][0]
        d1 = dist(T1); d2 = dist(T2)
        label_factor = 0.85
        if self.axis_off:
            self.plot_graph.getPlotItem().hideAxis('left');self.plot_graph.getPlotItem().hideAxis('bottom')
        p_long = 0
        if self._start_jd  is not None and self._place  is not None:
            jd_utc = self._start_jd - self._place.timezone/24.
            p_long = drik.sidereal_longitude(jd_utc, planet)
            y,m,d,_ = utils.jd_to_gregorian(self._start_jd)
            date_str = str(y)+'-'+str(m)+'-'+str(d)
            lbl = pg.TextItem(date_str,color=(0,0,0))
            self.plot_graph.addItem(lbl)
            th = p_long*pi/180.0
            x_label = (d1+d2)*cos(th)*0.5; y_label = (d1+d2)*sin(th)*0.5
            lbl.setPos(x_label,y_label)
            # Draw DOB Line
            x_line = x_label; y_line = y_label
            line = pg.LineROI(pos1=(0,0),pos2=(x_line,y_line),width=1,pen = pg.mkPen(color=(0,0,255)),movable=False)
            self.plot_graph.addItem(line)
        #print(utils.PLANET_NAMES[planet],utils.to_dms(p_long,is_lat_long='plong'))
        x,y=get_retrogression_orbit_data(planet,p_long)
        self.line = self.plot_graph.plot(x, y, pen=pen)
        self.line.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        if _track_mouse_coordinates:
            #track mouse coordinates 
            self.mouse_label = pg.TextItem(text="Date: {} \nLongitude: {}".format(0, 0))
            self.mouse_label.setPos(-560,560)
            self.plot_graph.addItem(self.mouse_label)
            self.setMouseTracking(True)
            self.plot_graph.scene().sigMouseMoved.connect(self.onMouseMoved)
        # Write Earth Label
        labels = utils.RAASI_LIST+[utils.RAASI_LIST[0]]
        lbl = pg.TextItem(utils.resource_strings['earth_str'],color=(0,0,0))
        self.plot_graph.addItem(lbl); lbl.setPos(0.0,0.0)
        y,m,d,_ = utils.jd_to_gregorian(self._start_jd)
        p_date = drik.Date(y,m,d)
        raasi = p_long//30
        theta = linspace(0, 2*pi, 13)
        for i,t in enumerate(theta[:-1]):
            r = i;date_str = ''
            if planet <=6:
                r = int(raasi+i-1)%12
                #npe = drik.next_planet_entry_date(planet, p_date, place,raasi=None,direction=1)
                npe = self._next_planet_entry_data[planet][r]
                y,m,d = npe[0]; p_long = utils.to_dms(npe[1],is_lat_long='plong')
                date_str = str(y)+'-'+str(m)+'-'+str(d)
                p_date = drik.Date(y,m,d)
            # Write Raasi Label
            lbl = pg.TextItem(labels[r]+'\n'+date_str,color=(0,0,0))
            self.plot_graph.addItem(lbl)
            th = 0.5*(theta[r]+theta[r+1])
            x_label = (d1+d2)*cos(th)*label_factor; y_label = (d1+d2)*sin(th)*label_factor
            lbl.setPos(x_label,y_label)
            # Draw Raasi Separation Line
            x_line = (d1+d2)*cos(t)*label_factor; y_line = (d1+d2)*sin(t)*label_factor
            line = pg.LineROI(pos1=(0,0),pos2=(x_line,y_line),width=0.5,pen = pg.mkPen(color=(255,0,0)),movable=False)
            self.plot_graph.addItem(line)
            line.setPos(0,0)
        
if __name__ == '__main__':
    import sys
    from _datetime import datetime
    from jhora import utils
    from jhora.panchanga import drik
    #const._TROPICAL_MODE = False
    utils.set_language('ta')
    app = QtWidgets.QApplication(sys.argv)
    planet = 6 # 2 = Mars,3=Merc,4-Jup,5=Ven,6=Sat,7=Ura,8=Nep,9=Plu
    current_date_str,current_time_str = datetime.now().strftime('%Y,%m,%d;%H:%M:%S').split(';')
    dob = tuple(map(int,current_date_str.split(',')))
    tob = tuple(map(int,current_time_str.split(':')))
    loc = utils.get_place_from_user_ip_address(); place = drik.Place(loc[0],loc[1],loc[2],loc[3])
    jd = utils.julian_day_number(dob, tob)
    """
    npe = get_planet_entry_data(jd,place)
    print(npe)
    exit()
    """
    w = VakraGathiPlot(jd,place,planet=planet)
    w.show()
    app.exec()

