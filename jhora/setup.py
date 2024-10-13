#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #
#  PyJHora - Based on the book Vedic Astrology - An Integrated Approach, PVR Narasimha Rao        #
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #
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

import setuptools
import os
from types import SimpleNamespace

# load _package_info.py into a SimpleNamespace, without having to import the whole carnatic package
# (this is similar to the way scamp handles things)
package_info_file_path = os.path.join(os.path.dirname(__file__), "./", "_package_info.py")
with open(package_info_file_path, "r") as f:
    file_contents_string = f.read()
package_info_dict: dict = {}
exec(file_contents_string, None, package_info_dict)
package_info = SimpleNamespace(**package_info_dict)


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=package_info.name,
    version=package_info.version,
    author=package_info.author,
    author_email=package_info.author_email,
    description=package_info.description,
    #include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=package_info.url,
    project_urls=package_info.project_urls,
    packages=setuptools.find_packages(),
    install_requires=package_info.install_requires,
    #extras_require=package_info.extras_require,
    package_data=package_info.package_data,
    classifiers=package_info.classifiers,
)
