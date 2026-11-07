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

"""JHoraWeb entry point.

Sets up the settings and the language, registers all pages (each page module registers its own route
when imported) and starts the NiceGUI server.

Environment variables (a .env file next to this file is loaded first):
  JHORA_PUBLIC=1     per-browser settings mode (see web_settings.py)
  STORAGE_SECRET     secret that signs the browser cookie; when unset, one is generated and saved
                     in .jhora_secret next to this file
  JHORA_CONFIG_DIR   folder holding factory_settings.json and user_settings.json
  JHORA_IMAGES_DIR   folder served at /img
  JHORA_PLACES_DB    places database (see components.py)
  PORT               server port (default 8080)
"""
import os
# Load .env before web_settings is imported (it reads JHORA_PUBLIC at import).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_storage_secret():
    """Returns the secret that signs the browser cookie.

    Order: the STORAGE_SECRET environment variable (or .env); otherwise the contents of .jhora_secret
    next to this file; otherwise a new random secret, saved to that file so it stays the same across
    restarts.
    """
    secret = os.environ.get('STORAGE_SECRET', '').strip()
    if secret and secret != 'jhora-dev-secret-change-me':
        return secret
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.jhora_secret')
    try:
        with open(path, encoding='utf-8') as f:
            secret = f.read().strip()
        if secret:
            return secret
    except FileNotFoundError:
        pass
    import secrets
    secret = secrets.token_urlsafe(32)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(secret)
    print(f"[main] STORAGE_SECRET not set - generated one and saved it to {path}")
    return secret
from nicegui import ui, app
from jhora import const, utils, config
from jhora.panchanga import vratha
drik = utils.hora_engine_proxy
drik.set_planet_list() #### <<< This is required to first setup planet list and flags

from engine_sync import apply_current_language
# JHORA_CONFIG_DIR: optional folder holding factory_settings.json and user_settings.json.
_cfg_dir = os.environ.get('JHORA_CONFIG_DIR')
if _cfg_dir:
    config.CONFIG_DIR = _cfg_dir
    config.FACTORY_SETTINGS_FILE = os.path.join(_cfg_dir, 'factory_settings.json')
    config.USER_SETTINGS_FILE = os.path.join(_cfg_dir, 'user_settings.json')
# create_if_missing=False: the web server never writes user_settings.json.
config.initialize_runtime(force_reload=True, create_if_missing=False, silent=False)
apply_current_language()
import web_settings
web_settings.install()
IMAGES_PATH = os.path.abspath(os.environ.get('JHORA_IMAGES_DIR') or const._IMAGES_PATH)
app.add_static_files('/img', IMAGES_PATH)
try:
    vratha.load_festival_data(const._FESTIVAL_FILE)
except Exception:
    pass
if __name__ in {"__main__", "__mp_main__"}:
    import panchangam_tab  # noqa: F401  (registers the / page on import)
    import calendar_tab  # noqa: F401  (registers the /calendar page on import)
    import kundali_chart  # noqa: F401  (registers the /kundali page on import)
    import dhasa_tab  # noqa: F401  (registers the /dhasa page on import)
    import bhava_tab  # noqa: F401  (registers the /bhava page on import)
    import chakra_tab  # noqa: F401  (registers the /chakra page on import)
    import amsa_ruler_tab  # noqa: F401  (registers the /amsa_ruler page on import)
    import sphuta_tab  # noqa: F401  (registers the /sphuta page on import)
    import saham_tab  # noqa: F401  (registers the /saham page on import)
    import drishti_tab  # noqa: F401  (registers the /drishti page on import)
    import arudha_tab  # noqa: F401  (registers the /arudha page on import)
    import vimsopaka_bala_tab  # noqa: F401  (registers the /vimsopaka_bala page on import)
    import vaiseshikamsa_bala_tab  # noqa: F401  (registers the /vaiseshikamsa_bala page on import)
    import other_bala_tab  # noqa: F401  (registers the /other_bala page on import)
    import shad_bala_tab  # noqa: F401  (registers the /shad_bala page on import)
    import bhava_bala_tab  # noqa: F401  (registers the /bhava_bala page on import)
    import ashtakavarga_tab  # noqa: F401  (registers the /ashtakavarga page on import)
    import argala_tab  # noqa: F401  (registers the /argala page on import)
    import shodhaya_pinda_tab  # noqa: F401  (registers the /shodhaya_pinda page on import)
    import yoga_tab  # noqa: F401  (registers the /yoga page on import)
    import dosha_tab  # noqa: F401  (registers the /dosha page on import)
    import prediction_tab  # noqa: F401  (registers the /prediction page on import)
    import compatibility_tab  # noqa: F401  (registers the /compatibility page on import)
    import pancha_pakshi_tab  # noqa: F401  (registers the /pancha_pakshi page on import)
    import kpinfo_tab  # noqa: F401  (registers the /kpinfo page on import)
    import transit_tab  # noqa: F401  (registers the /transit page on import)
    import vratha_tab # noqa: F401 (registers the /vratha page on import)
    import about_tab  # noqa: F401  (registers the /about page on import)
    _secret = _get_storage_secret()
    ui.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')), title=const._APP_NAME_VERSION,
           reload=False, show=False,
           storage_secret=_secret)
