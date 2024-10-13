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
import sys
from PyQt6.QtWidgets import QApplication

def except_hook(cls, exception, traceback):
    print('exception called')
    sys.__excepthook__(cls, exception, traceback)
sys.excepthook = except_hook
App = QApplication(sys.argv)
#from jhora.ui.horo_chart import ChartSimple
#chart = ChartSimple()
#chart.show()
from jhora.ui.horo_chart_tabs import ChartTabbed
chart = ChartTabbed()
chart.show()
sys.exit(App.exec())
exit()
