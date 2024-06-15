#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    This is an attempt to create horoscope based surya sidhantha meant/true position calculations
    Reference: Indian Astronomy - An Introduction - S. Balachandra Rao
    WORK STILL IN PROGRESS - NOT WORKING FOR SOME PLANETS YET
"""
import math
from hora import utils, const
from hora.panchanga import drik1 as drik
from hora.panchanga import surya_sidhantha as ss
import swisseph as swe

if __name__ == "__main__":
    place = drik.Place('Ujjain',23.1765, 75.7885,5.5)
    dt = drik.Date(1997,3,21)
    jd = swe.julday(dt[0],dt[1],dt[2],12.00)
    print('KK Ahargana',ss.ahargana_khanda_khaadyaka(jd))
    print('Graha Laghavam Ahargana',ss.ahargana_graha_laghavam(jd))