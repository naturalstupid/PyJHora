#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #
#  PyJHora - Based on the book Vedic Astrology - An Integrated Approach, PVR Narasimha Rao        #
#  Copyright © 2022 Sundar Sundaresan <Sundaram.Sundaresan@gmail.com>.                           #
#                                                                                                #
#  This program is free software: you can redistribute it and/or modify it under the terms of    #
#  the GNU General Public License as published by the Free Software Foundation, either version   #
#  3 of the License, or (at your option) any later version.                                      #
#                                                                                                #
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;     #
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#  See the GNU General Public License for more details.                                          #
#  																								 #
#  Vedic Astrology was givem to us by our ancient sages without any commerical benefits.         #
#  Let us also do the same without any commercial benfits and distribute this free. THANK YOU    #
#  You should have received a copy of the GNU General Public License along with this program.    #
#  If not, see <http://www.gnu.org/licenses/>.                                                   #
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #

name = "PyJHora"

version = "3.7.4"

author = "Sundar Sundaresan"

author_email = "Sundaram.Sundaresan@gmail.com"

description = "A Python package for generating Indian style calendar, panchang, horoscope and compatibility"

url = "https://github.com/naturalstupid/PyJHora"

project_urls = {
    "Source Code": "https://github.com/naturalstupid/PyJHora",
    "Documentation": "https://github.com/naturalstupid/PyJHora",
}

#install_requires = ['itertools', "configparser", 'operator', 'collections', 'enum', 'csv', 'numpy', 'scamp', 'math', 're', 'regex', 'random',]
install_requires = ['swisseph', 'geopy','pytz','PyQt6' ]

#extras_require = { }

package_data = {
    'horoscope': ["data/*",'lang/*','images/*']
}

classifiers = [
    "Programming Language :: Python :: 3.6",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]
