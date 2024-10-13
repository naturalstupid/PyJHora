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
from PyQt6.QtGui import QPixmap, QFont, QPainter
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication, QLabel

class LabelGrid(QWidget):
    def __init__(self,rows=2,columns=2,has_header=True,has_index=True,show_as_grid=True,data=None):
        QWidget.__init__(self)
        if data != None and len(data)>0:
            rows = len(data); columns = len(data[0])
        else:
            data = [['' for _ in range(columns)] for _ in range(rows)]
        self._rows = rows; self._columns = columns; self._has_header = has_header; self._has_index=has_index
        self.labels = [[QLabel(data[r][c]) for c in range(columns)] for r in range(rows)]
        self._label_styles = [['' for _ in range(columns)] for _ in range(rows)]
        self._header_style = "font-weight: bold"
        self._border_style = "border: 1px solid black"
        [[self.labels[r][c].setStyleSheet(self._border_style) for r in range(self._rows)] for c in range(self._columns)]
        [self.labels[r][0].setStyleSheet(self._header_style+';'+self._border_style) for r in range(self._rows)]
        [self.labels[0][c].setStyleSheet(self._header_style+';'+self._border_style) for c in range(self._columns)]
        self._grid_layout = QGridLayout()
        self.setLayout(self._grid_layout)
        [[self._grid_layout.addWidget(self.labels[r][c],r,c) for c in range(columns)] for r in range(rows)]
        self._grid_layout.setSpacing(0)
    def setSize(self,rows=2,columns=2):
        self._rows = rows; self._columns = columns
        self.labels = [[QLabel('') for _ in range(columns)] for _ in range(rows)]
        [[self.labels[r][c].setStyleSheet(self._border_style) for r in range(self._rows)] for c in range(self._columns)]
        [self.labels[r][0].setStyleSheet(self._header_style+';'+self._border_style) for r in range(self._rows)]
        [self.labels[0][c].setStyleSheet(self._header_style+';'+self._border_style) for c in range(self._columns)]
    def setData(self,data=None):
        if data==None: data = [['' for _ in range(self._columns)] for _ in range(self._rows)]
        [[self.labels[r][c].setText(data[r][c]) for c in range(self._columns)] for r in range(self._rows)]
        [[self._grid_layout.addWidget(self.labels[r][c],r,c) for c in range(self._columns)] for r in range(self._rows)]
        [[self.labels[r][c].setStyleSheet(self._border_style) for r in range(self._rows)] for c in range(self._columns)]
        [self.labels[r][0].setStyleSheet(self._header_style+';'+self._border_style) for r in range(self._rows)]
        [self.labels[0][c].setStyleSheet(self._header_style+';'+self._border_style) for c in range(self._columns)]

if __name__ == "__main__":
    import sys
    def except_hook(cls, exception, traceback):
        print('exception called')
        sys.__excepthook__(cls, exception, traceback)
    sys.excepthook = except_hook
    App = QApplication(sys.argv)
    data = [['('+str(r)+','+str(c)+')' for c in range(3)] for r in range(3)]
    label_grid = LabelGrid(data=data)
    label_grid.show()
    sys.exit(App.exec())
    
    