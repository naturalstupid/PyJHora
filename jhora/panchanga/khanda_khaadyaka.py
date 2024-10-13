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
"""
    This is an attempt to create horoscope based surya sidhantha meant/true position calculations
    Reference: Indian Astronomy - An Introduction - S. Balachandra Rao
    WORK STILL IN PROGRESS - NOT WORKING FOR SOME PLANETS YET
"""
import math
from jhora import utils, const
from jhora.panchanga import drik1 as drik
from jhora.panchanga import surya_sidhantha as ss
import swisseph as swe

if __name__ == "__main__":
    place = drik.Place('Ujjain',23.1765, 75.7885,5.5)
    dt = drik.Date(1997,3,21)
    jd = swe.julday(dt[0],dt[1],dt[2],12.00)
    print('KK Ahargana',ss.ahargana_khanda_khaadyaka(jd))
    print('Graha Laghavam Ahargana',ss.ahargana_graha_laghavam(jd))