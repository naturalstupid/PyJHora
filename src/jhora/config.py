#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# py -- routines for computing tithi, vara, etc.
#
# Copyright (C) 2013 Satish BD  <bdsatish@gmail.com>
# Downloaded from https://github.com/bdsatish/drik-panchanga
#
# This file is part of the "drik-panchanga" Python library
# for computing Hindu luni-solar calendar based on the Swiss ephemeris
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
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora
"""Unified configuration backend for PyJHora.

This version keeps the single-JSON / metadata-driven design but avoids the
old grouped hardcoded apply path. Instead, it uses a generic binding engine
with a small set of reusable binding kinds and adapters.

Binding kinds
-------------
- attr          : direct attribute assignment on jhora.const
- setter        : call a const setter with a converted value
- enum_attr     : store enum member name, assign enum value/member to const attr
- enum_setter   : store enum member name, pass enum value/member to const setter

Adapters
--------
Adapters handle the few value patterns that are *not* plain bool/int/float/string,
for example:
- language code <-> display label
- database engine symbolic name <-> runtime integer/IntEnum value
- bhava/house method string key <-> runtime int-or-str value
- empty string <-> None

Adding a new setting usually means adding only one metadata entry, not changing
apply/save/restore code.
"""

from __future__ import annotations

import configparser
import copy
import json
import os
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from jhora import const


# ============================================================
# FILE PATHS
# ============================================================
CONFIG_DIR = const._DATA_DIR
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Legacy files (best-effort migration if present)
USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.ini")
ADVANCED_SETTINGS_FILE = os.path.join(CONFIG_DIR, "advanced_settings.json")
from jhora.place_db import _ENGINE_DISPLAY_LABELS
CONFIG_VERSION = 1


# ============================================================
# ERRORS / STATE
# ============================================================
class ConfigError(Exception):
    pass


_CONFIG_CACHE: Dict[str, Any] = {"version": CONFIG_VERSION, "settings": {}}
_SETTINGS_LOADED = False


# ============================================================
# BASIC HELPERS
# ============================================================
def _ensure_config_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default

    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on", "y", "t"):
        return True
    if text in ("0", "false", "no", "off", "n", "f"):
        return False
    return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


# ============================================================
# ENUM HELPERS (CONFIG-LAYER ONLY)
# ============================================================
def _enum_names(enum_class: Any, preferred: Optional[Iterable[str]] = None, exclude: Optional[Iterable[str]] = None) -> List[str]:
    preferred = list(preferred or [])
    exclude = set(exclude or [])

    names: List[str] = []

    if hasattr(enum_class, "__members__"):
        for name in enum_class.__members__.keys():
            if name not in exclude:
                names.append(name)
    else:
        for attr, value in vars(enum_class).items():
            if attr.startswith("_") or attr in exclude:
                continue
            if isinstance(value, int):
                names.append(attr)

    return [x for x in preferred if x in names] + [x for x in names if x not in preferred]


def _enum_name_to_value(enum_class: Any, name: Any, default: Any = None, exclude: Optional[Iterable[str]] = None) -> Any:
    exclude = set(exclude or [])

    if name is None:
        return default
    if not isinstance(name, str):
        return name

    name = str(name).strip()
    if name in exclude:
        return default

    if hasattr(enum_class, "__members__"):
        member = enum_class.__members__.get(name)
        if member is not None:
            return member
    else:
        if hasattr(enum_class, name):
            return getattr(enum_class, name)

    return default


def _enum_value_to_name(enum_class: Any, value: Any, default: Any = None, exclude: Optional[Iterable[str]] = None) -> Any:
    exclude = set(exclude or [])

    if value is None:
        return default
    if isinstance(value, str):
        return default if value in exclude else value

    if hasattr(enum_class, "__members__"):
        for name, member in enum_class.__members__.items():
            if name in exclude:
                continue
            if member == value:
                return name
    else:
        for attr, attr_value in vars(enum_class).items():
            if attr.startswith("_") or attr in exclude:
                continue
            if attr_value == value:
                return attr

    return default


# ============================================================
# ADAPTERS / CHOICE PROVIDERS
# ============================================================
# ---- language adapters --------------------------------------
def _language_choices() -> List[Tuple[str, str]]:
    return [(code, label) for label, code in const.available_languages.items()]


def _language_to_storage(value: Any, default: str = "en") -> str:
    if value is None:
        return default

    value = str(value).strip()
    reverse = {v: k for k, v in const.available_languages.items()}

    if value in reverse:
        return value
    if value in const.available_languages:
        return const.available_languages[value]
    return default


def _language_to_runtime(value: Any, default: Optional[str] = None) -> str:
    return _language_to_storage(value, default=getattr(const, "_DEFAULT_LANGUAGE", "en") if default is None else default)


def _language_to_display(value: Any, default: str = "English") -> str:
    if value is None:
        return default

    value = str(value).strip()
    reverse = {v: k for k, v in const.available_languages.items()}
    if value in reverse:
        return reverse[value]
    if value in const.available_languages:
        return value
    return default


# ---- engine adapters ----------------------------------------
def _engine_names() -> List[str]:
    names: List[str] = []
    for attr, value in vars(const.PLACE_DATABASE_ENGINE).items():
        if attr.startswith("_"):
            continue
        if isinstance(value, int):
            names.append(attr)

    preferred = [
        "CSV_5K",       #"CSV (Population > 5000)",
        "SQLITE_5K",    #"SQLITE (Population > 5000)",
        "PICKLE_5K",    #"PICKLE (Population > 5000)",

        "CSV_5K_IN",    #"CSV (Population > 5000, India >= 0)",
        "PICKLE_5K_IN", #"PICKLE (Population > 5000, India >= 0)",
        "SQLITE_5K_IN", #"SQLITE (Population > 5000, India >= 0)",

        "CSV_500",      #"CSV (Population > 500)",
        "PICKLE_500",   #"PICKLE (Population > 500)",
        "SQLITE_500",   #"SQLITE (Population > 500)",

        "CSV_500_IN",   #"CSV (Population > 500, India >= 0)",
        "PICKLE_500_IN",#"PICKLE (Population > 500, India >= 0)",
        "SQLITE_500_IN",#"SQLITE (Population > 500, India >= 0)",

        "NONE",
    ]

    return [x for x in preferred if x in names] + [x for x in names if x not in preferred]

def _engine_choices() -> List[Tuple[str, str]]:
    """
    Returns:
        [
            ("SQLITE_5K", "SQLITE (Population > 5000)"),
            ...
        ]

    stored value  -> first item
    visible label -> second item
    """
    choices: List[Tuple[str, str]] = []

    for name in _engine_names():
        label = _ENGINE_DISPLAY_LABELS.get(name, name)
        choices.append((name, label))

    return choices

def _engine_to_storage(value: Any, default: str = "NONE") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return str(value).strip().upper()

    for attr, attr_value in vars(const.PLACE_DATABASE_ENGINE).items():
        if attr.startswith("_"):
            continue
        if attr_value == value:
            return attr

    return default


def _engine_to_runtime(value: Any, default: Any = None) -> Any:
    if default is None:
        default = getattr(const, "database_engine", 0)

    if value is None:
        return default
    if not isinstance(value, str):
        return value

    name = str(value).strip().upper()
    for attr, attr_value in vars(const.PLACE_DATABASE_ENGINE).items():
        if attr.startswith("_"):
            continue
        if attr == name and isinstance(attr_value, int):
            return attr_value

    return default


# ---- ayanamsa adapters --------------------------------------
def _ayanamsa_choices() -> List[Tuple[str, str]]:
    return [(key, key) for key in const.available_ayanamsa_modes.keys()]


def _ayanamsa_to_storage(value: Any, default: Optional[str] = None) -> str:
    if default is None:
        default = getattr(const, "_DEFAULT_AYANAMSA_MODE", "TRUE_PUSHYA")
    if value is None:
        return default
    value = str(value).strip()
    return value if value in const.available_ayanamsa_modes else default


def _ayanamsa_to_runtime(value: Any, default: Optional[str] = None) -> str:
    return _ayanamsa_to_storage(value, default=default)


def _ayanamsa_to_display(value: Any, default: Optional[str] = None) -> str:
    return _ayanamsa_to_storage(value, default=default)


# ---- bhava/house-method adapters ----------------------------
def _house_method_choices() -> List[Tuple[str, str]]:
    try:
        hs = const.available_house_systems()
    except Exception:
        hs = {}
    return [(str(k), str(v)) for k, v in hs.items()]


def _house_method_to_storage(value: Any, default: Any = None) -> str:
    if value is None:
        if default is None:
            default = getattr(const, "bhaava_madhya_method", 1)
        return str(default)
    return str(value).strip()


def _house_method_to_runtime(value: Any, default: Any = None) -> Any:
    if value is None:
        if default is None:
            return getattr(const, "bhaava_madhya_method", 1)
        value = default

    text = str(value).strip()
    try:
        return int(text)
    except Exception:
        return text


def _house_method_to_display(value: Any, default: Any = None) -> str:
    key = _house_method_to_storage(value, default=default)
    try:
        hs = const.available_house_systems()
    except Exception:
        hs = {}

    for raw_key, label in hs.items():
        if str(raw_key) == key:
            return str(label)
    return key


# ---- misc adapters ------------------------------------------
def _int_list_to_runtime(value: Any, default: Optional[List[int]] = None) -> List[int]:
    if value is None:
        return list(default or [])
    if isinstance(value, (list, tuple)):
        result: List[int] = []
        for item in value:
            try:
                result.append(int(item))
            except Exception:
                pass
        return result
    return list(default or [])


def _empty_string_to_none(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _none_to_empty_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


CHOICE_PROVIDERS: Dict[str, Callable[[], List[Tuple[Any, Any]]]] = {
    "language": _language_choices,
    "database_engine": _engine_choices,
    "ayanamsa": _ayanamsa_choices,
    "house_method": _house_method_choices,
    "dhasa_year_duration": lambda: [(name, name) for name in _enum_names(
        const.DHASA_YEAR_DURATION,
        preferred=[
            "TRUE_SIDEREAL_YEAR",
            "MEAN_SIDEREAL_YEAR",
            "MEAN_TROPICAL_YEAR",
            "TRUE_TROPICAL_YEAR",
            "SAVANA_YEAR",
            "MEAN_LUNAR_YEAR",
            "TRUE_LUNAR_YEAR",
            "GREGORIAN_YEAR",
        ],
        exclude=["JHORA_DEFAULT", "DEFAULT"],
    )],
    "savana_year_method": lambda: [(name, name) for name in _enum_names(
        const.SAVANA_YEAR_METHOD,
        preferred=["PROSPECTIVE_0_to_360_JHORA", "MIDPOINT", "RETROSPECTIVE_360_to_0"],
        exclude=["DEFAULT"],
    )],
    "true_lunar_year_method": lambda: [(name, name) for name in _enum_names(
        const.TRUE_LUNAR_YEAR_METHOD,
        preferred=["TITHI_BOUNDARY", "TITHI_AT_DOB"],
        exclude=["DEFAULT"],
    )],
    "retrogression_method": lambda: [(1, "1"), (2, "2")],
    "tamil_month_method": lambda: [(0, "0"), (1, "1"), (2, "2"), (3, "3")],
    "kali_start_year": lambda: [(1, "1"), (13, "13")],
}

ADAPTERS: Dict[str, Dict[str, Callable[..., Any]]] = {
    "language_code": {
        "to_storage": _language_to_storage,
        "to_runtime": _language_to_runtime,
        "to_display": _language_to_display,
    },
    "engine_name": {
        "to_storage": _engine_to_storage,
        "to_runtime": _engine_to_runtime,
        "to_display": _engine_to_storage,
    },
    "ayanamsa_name": {
        "to_storage": _ayanamsa_to_storage,
        "to_runtime": _ayanamsa_to_runtime,
        "to_display": _ayanamsa_to_display,
    },
    "house_method_key": {
        "to_storage": _house_method_to_storage,
        "to_runtime": _house_method_to_runtime,
        "to_display": _house_method_to_display,
    },
    "optional_string": {
        "to_storage": _none_to_empty_string,
        "to_runtime": _empty_string_to_none,
        "to_display": _none_to_empty_string,
    },
    "int_list": {
        "to_storage": lambda value, default=None: list(value or []),
        "to_runtime": _int_list_to_runtime,
        "to_display": lambda value, default=None: ", ".join(str(x) for x in (value or [])),
    },
}


# ============================================================
# METADATA BUILDERS
# ============================================================
def _meta(
    *,
    label: str,
    type_: str,
    tab: str,
    section: str,
    default: Any,
    binding: Optional[Dict[str, Any]] = None,
    value: Any = None,
    visible: bool = True,
    order: int = 0,
    description: str = "",
    choices: Optional[List[Any]] = None,
    choices_provider: Optional[str] = None,
    min_value: Any = None,
    max_value: Any = None,
    read_only: bool = False,
    nullable: bool = False,
) -> Dict[str, Any]:
    meta = {
        "label": label,
        "type": type_,
        "tab": tab,
        "section": section,
        "group": section,
        "default": _deepcopy(default),
        "value": _deepcopy(default if value is None else value),
        "visible": bool(visible),
        "order": int(order),
        "description": description,
        "read_only": bool(read_only),
        "nullable": bool(nullable),
        "binding": _deepcopy(binding or {}),
    }

    if choices is not None:
        meta["choices"] = _deepcopy(choices)
    if choices_provider:
        meta["choices_provider"] = str(choices_provider)
    if min_value is not None:
        meta["min"] = min_value
    if max_value is not None:
        meta["max"] = max_value

    return meta


def _binding(kind: str, *, target: Optional[str] = None, setter: Optional[str] = None,
             adapter: Optional[str] = None, enum_class: Optional[str] = None,
             exclude: Optional[List[str]] = None) -> Dict[str, Any]:
    data: Dict[str, Any] = {"kind": kind}
    if target:
        data["target"] = target
    if setter:
        data["setter"] = setter
    if adapter:
        data["adapter"] = adapter
    if enum_class:
        data["enum_class"] = enum_class
    if exclude:
        data["exclude"] = list(exclude)
    return data


def build_default_settings_data() -> Dict[str, Any]:
    data = {"version": CONFIG_VERSION, "settings": {}}
    s = data["settings"]

    # -------------------------
    # User / General
    # -------------------------
    s["language"] = _meta(
        label="Language",
        type_="choice",
        tab="User",
        section="general",
        order=10,
        default=_language_to_storage(getattr(const, "_DEFAULT_LANGUAGE", "en")),
        choices_provider="language",
        binding=_binding("attr", target="_DEFAULT_LANGUAGE", adapter="language_code"),
    )
    s["include_uranus_to_pluto"] = _meta(
        label="Include Uranus / Neptune / Pluto",
        type_="bool",
        tab="User",
        section="general",
        order=20,
        default=bool(getattr(const, "_INCLUDE_URANUS_TO_PLUTO", False)),
        binding=_binding("attr", target="_INCLUDE_URANUS_TO_PLUTO"),
    )
    s["include_islamic_calendar"] = _meta(
        label="Include Islamic Calendar",
        type_="bool",
        tab="User",
        section="general",
        order=30,
        default=bool(getattr(const, "include_islamic_calendar", False)),
        binding=_binding("attr", target="include_islamic_calendar"),
    )
    s["use_24hour_format_in_to_dms"] = _meta(
        label="Use 24-hour format",
        type_="bool",
        tab="User",
        section="general",
        order=40,
        default=bool(getattr(const, "use_24hour_format_in_to_dms", True)),
        binding=_binding("attr", target="use_24hour_format_in_to_dms"),
    )

    s["apply_daylight_savings_correction"] = _meta(
        label="Apply Daylight Savings Correction",
        type_="bool",
        tab="User",
        section="calculation",
        order=75,
        default=bool(getattr(const, "apply_daylight_savings_correction", True)),
        binding=_binding("attr", target="apply_daylight_savings_correction"),
    )

    # -------------------------
    # User / Location
    # -------------------------
    s["database_engine"] = _meta(
        label="Place Database Engine",
        type_="choice",
        tab="User",
        section="location",
        order=10,
        default=_engine_to_storage(getattr(const, "database_engine", 0), default="NONE"),
        choices_provider="database_engine",
        binding=_binding("setter", target="database_engine", setter="set_place_database_engine", adapter="engine_name"),
    )
    s["check_database_for_world_cities"] = _meta(
        label="Check database for world cities",
        type_="bool",
        tab="User",
        section="location",
        order=20,
        default=bool(getattr(const, "check_database_for_world_cities", True)),
        binding=_binding("attr", target="check_database_for_world_cities"),
    )
    s["get_place_elevation_from_internet"] = _meta(
        label="Get place elevation from internet",
        type_="bool",
        tab="User",
        section="location",
        order=30,
        default=bool(getattr(const, "get_place_elevation_from_internet", False)),
        visible=False,
        binding=_binding("attr", target="get_place_elevation_from_internet"),
    )
    s["use_internet_for_location_check"] = _meta(
        label="Use internet for location check",
        type_="bool",
        tab="User",
        section="location",
        order=40,
        default=bool(getattr(const, "use_internet_for_location_check", True)),
        visible=False,
        binding=_binding("attr", target="use_internet_for_location_check"),
    )

    # -------------------------
    # User / Calculation
    # -------------------------
    s["default_ayanamsa_mode"] = _meta(
        label="Default Ayanamsa Mode",
        type_="choice",
        tab="User",
        section="calculation",
        order=10,
        default=_ayanamsa_to_storage(getattr(const, "_DEFAULT_AYANAMSA_MODE", "TRUE_PUSHYA")),
        choices_provider="ayanamsa",
        binding=_binding("attr", target="_DEFAULT_AYANAMSA_MODE", adapter="ayanamsa_name"),
    )
    s["dhasa_year_duration_default"] = _meta(
        label="Dhasa Year Duration",
        type_="choice",
        tab="User",
        section="calculation",
        order=20,
        default=_enum_value_to_name(
            const.DHASA_YEAR_DURATION,
            getattr(const, "dhasa_year_duration_default", getattr(const.DHASA_YEAR_DURATION, "TRUE_SIDEREAL_YEAR", None)),
            default="TRUE_SIDEREAL_YEAR",
            exclude=["JHORA_DEFAULT", "DEFAULT"],
        ),
        choices_provider="dhasa_year_duration",
        binding=_binding("enum_attr", target="dhasa_year_duration_default", enum_class="DHASA_YEAR_DURATION", exclude=["JHORA_DEFAULT", "DEFAULT"]),
    )
    s["savana_year_method_default"] = _meta(
        label="Savana Year Method",
        type_="choice",
        tab="User",
        section="calculation",
        order=30,
        default=_enum_value_to_name(
            const.SAVANA_YEAR_METHOD,
            getattr(const, "savana_year_method_default", getattr(const.SAVANA_YEAR_METHOD, "PROSPECTIVE_0_to_360_JHORA", None)),
            default="PROSPECTIVE_0_to_360_JHORA",
            exclude=["DEFAULT"],
        ),
        choices_provider="savana_year_method",
        binding=_binding("enum_attr", target="savana_year_method_default", enum_class="SAVANA_YEAR_METHOD", exclude=["DEFAULT"]),
    )
    s["true_lunar_year_method_default"] = _meta(
        label="True Lunar Year Method",
        type_="choice",
        tab="User",
        section="calculation",
        order=40,
        default=_enum_value_to_name(
            const.TRUE_LUNAR_YEAR_METHOD,
            getattr(const, "true_lunar_year_method_default", getattr(const.TRUE_LUNAR_YEAR_METHOD, "TITHI_AT_DOB", None)),
            default="TITHI_AT_DOB",
            exclude=["DEFAULT"],
        ),
        choices_provider="true_lunar_year_method",
        binding=_binding("enum_attr", target="true_lunar_year_method_default", enum_class="TRUE_LUNAR_YEAR_METHOD", exclude=["DEFAULT"]),
    )
    s["bhaava_madhya_method"] = _meta(
        label="Bhava Madhya Method",
        type_="choice",
        tab="User",
        section="calculation",
        order=50,
        default=_house_method_to_storage(getattr(const, "bhaava_madhya_method", 1)),
        choices_provider="house_method",
        binding=_binding("attr", target="bhaava_madhya_method", adapter="house_method_key"),
    )
    s["tamil_month_method"] = _meta(
        label="Tamil Month Method",
        type_="choice",
        tab="User",
        section="calculation",
        order=60,
        default=int(getattr(const, "tamil_month_method", 3)),
        choices_provider="tamil_month_method",
        binding=_binding("attr", target="tamil_month_method"),
    )
    s["use_planet_speed_for_panchangam_end_timings"] = _meta(
        label="Use planet speed for Panchangam end timings",
        type_="bool",
        tab="User",
        section="calculation",
        order=70,
        default=bool(getattr(const, "use_planet_speed_for_panchangam_end_timings", True)),
        binding=_binding("attr", target="use_planet_speed_for_panchangam_end_timings"),
    )

    # -------------------------
    # User / Charts
    # -------------------------
    s["include_special_and_arudha_lagna_in_charts"] = _meta(
        label="Include special & arudha lagna in charts",
        type_="bool",
        tab="User",
        section="charts",
        order=10,
        default=bool(getattr(const, "include_special_and_arudha_lagna_in_charts", True)),
        binding=_binding("attr", target="include_special_and_arudha_lagna_in_charts"),
    )
    s["include_maandhi_in_charts"] = _meta(
        label="Include Maandhi in charts",
        type_="bool",
        tab="User",
        section="charts",
        order=20,
        default=bool(getattr(const, "include_maandhi_in_charts", True)),
        binding=_binding("attr", target="include_maandhi_in_charts"),
    )
    s["include_charts_only_for_western_type"] = _meta(
        label="Include charts only for western type",
        type_="bool",
        tab="User",
        section="charts",
        order=30,
        default=bool(getattr(const, "include_charts_only_for_western_type", False)),
        binding=_binding("attr", target="include_charts_only_for_western_type"),
    )

    # -------------------------
    # Advanced / Nodes
    # -------------------------
    s["use_true_nodes_for_rahu_ketu"] = _meta(
        label="Use true nodes for Rahu / Ketu",
        type_="bool",
        tab="Advanced",
        section="nodes",
        order=10,
        default=bool(getattr(const, "_use_true_nodes_for_rahu_ketu", True)),
        binding=_binding("setter", target="_use_true_nodes_for_rahu_ketu", setter="set_node_mode"),
    )

    # -------------------------
    # Advanced / Calculation Variants
    # -------------------------
    s["use_saravali_formula_for_uccha_bala"] = _meta(
        label="Use Saravali formula for Uccha Bala",
        type_="bool",
        tab="Advanced",
        section="calculation_variants",
        order=10,
        default=bool(getattr(const, "use_saravali_formula_for_uccha_bala", True)),
        binding=_binding("attr", target="use_saravali_formula_for_uccha_bala"),
    )
    s["hora_chart_by_pvr_method"] = _meta(
        label="Hora chart by PVR method",
        type_="bool",
        tab="Advanced",
        section="calculation_variants",
        order=20,
        default=bool(getattr(const, "hora_chart_by_pvr_method", True)),
        binding=_binding("attr", target="hora_chart_by_pvr_method"),
    )
    s["ashtottari_bhukthi_starts_from_dhasa_lord"] = _meta(
        label="Ashtottari Bhukthi starts from Dhasa lord",
        type_="bool",
        tab="Advanced",
        section="calculation_variants",
        order=30,
        default=bool(getattr(const, "ashtottari_bhukthi_starts_from_dhasa_lord", True)),
        binding=_binding("attr", target="ashtottari_bhukthi_starts_from_dhasa_lord"),
    )
    s["planet_retrogression_calculation_method"] = _meta(
        label="Planet retrogression calculation method",
        type_="choice",
        tab="Advanced",
        section="calculation_variants",
        order=40,
        default=int(getattr(const, "planet_retrogression_calculation_method", 1)),
        choices_provider="retrogression_method",
        binding=_binding("attr", target="planet_retrogression_calculation_method"),
    )

    # -------------------------
    # Advanced / Tradition Overrides
    # -------------------------
    s["force_kali_start_year_for_years_before_kali_year_4009"] = _meta(
        label="Force Kali start year before Kali year 4009",
        type_="bool",
        tab="Advanced",
        section="tradition_overrides",
        order=10,
        default=bool(getattr(const, "force_kali_start_year_for_years_before_kali_year_4009", True)),
        binding=_binding("attr", target="force_kali_start_year_for_years_before_kali_year_4009"),
    )
    s["kali_start_year"] = _meta(
        label="Kali start year",
        type_="choice",
        tab="Advanced",
        section="tradition_overrides",
        order=20,
        default=int(getattr(const, "kali_start_year", 13)),
        choices_provider="kali_start_year",
        binding=_binding("attr", target="kali_start_year"),
    )
    s["ritu_per_solar_tamil_month"] = _meta(
        label="Ritu per solar Tamil month",
        type_="bool",
        tab="Advanced",
        section="tradition_overrides",
        order=30,
        default=bool(getattr(const, "ritu_per_solar_tamil_month", True)),
        binding=_binding("attr", target="ritu_per_solar_tamil_month"),
    )
    s["use_aharghana_for_vaara_calcuation"] = _meta(
        label="Use aharghana for vaara calculation",
        type_="bool",
        tab="Advanced",
        section="tradition_overrides",
        order=40,
        default=bool(getattr(const, "use_aharghana_for_vaara_calcuation", False)),
        binding=_binding("attr", target="use_aharghana_for_vaara_calcuation"),
    )
    s["scorpio_owner_for_dhasa_calculations"] = _meta(
        label="Scorpio owner for dhasa calculations",
        type_="string",
        tab="Advanced",
        section="tradition_overrides",
        order=50,
        default=_none_to_empty_string(getattr(const, "scorpio_owner_for_dhasa_calculations", None)),
        visible=False,
        nullable=True,
        binding=_binding("attr", target="scorpio_owner_for_dhasa_calculations", adapter="optional_string"),
    )
    s["aquarius_owner_for_dhasa_calculations"] = _meta(
        label="Aquarius owner for dhasa calculations",
        type_="string",
        tab="Advanced",
        section="tradition_overrides",
        order=60,
        default=_none_to_empty_string(getattr(const, "aquarius_owner_for_dhasa_calculations", None)),
        visible=False,
        nullable=True,
        binding=_binding("attr", target="aquarius_owner_for_dhasa_calculations", adapter="optional_string"),
    )
    s["use_kp_dictionary_for_lords_calculation"] = _meta(
        label="Use KP dictionary for lords calculation",
        type_="bool",
        tab="Advanced",
        section="tradition_overrides",
        order=70,
        default=bool(getattr(const, "use_kp_dictionary_for_lords_calculation", False)),
        binding=_binding("attr", target="use_kp_dictionary_for_lords_calculation"),
    )

    # -------------------------
    # Advanced / Compatibility
    # -------------------------
    s["skip_using_girls_varna_for_minimum_tamil_porutham"] = _meta(
        label="Skip girl's varna for minimum Tamil porutham",
        type_="bool",
        tab="Advanced",
        section="compatibility",
        order=10,
        default=bool(getattr(const, "skip_using_girls_varna_for_minimum_tamil_porutham", True)),
        binding=_binding("attr", target="skip_using_girls_varna_for_minimum_tamil_porutham"),
    )
    s["mandatory_compatibility_south_list"] = _meta(
        label="Mandatory compatibility south list",
        type_="int_list",
        tab="Advanced",
        section="compatibility",
        order=20,
        default=list(getattr(const, "mandatory_compatibility_south_list", [1, 2, 3, 5])),
        visible=False,
        binding=_binding("attr", target="mandatory_compatibility_south_list", adapter="int_list"),
    )
    s["compatibility_minimum_score_north"] = _meta(
        label="Compatibility minimum score north",
        type_="float",
        tab="Advanced",
        section="compatibility",
        order=30,
        default=float(getattr(const, "compatibility_minimum_score_north", 18.0)),
        visible=False,
        binding=_binding("attr", target="compatibility_minimum_score_north"),
    )
    s["compatibility_minimum_score_south"] = _meta(
        label="Compatibility minimum score south",
        type_="float",
        tab="Advanced",
        section="compatibility",
        order=40,
        default=float(getattr(const, "compatibility_minimum_score_south", 6.0)),
        visible=False,
        binding=_binding("attr", target="compatibility_minimum_score_south"),
    )
    s["compatibility_maximum_score_north"] = _meta(
        label="Compatibility maximum score north",
        type_="float",
        tab="Advanced",
        section="compatibility",
        order=50,
        default=float(getattr(const, "compatibility_maximum_score_north", 36.0)),
        visible=False,
        binding=_binding("attr", target="compatibility_maximum_score_north"),
    )
    s["compatibility_maximum_score_south"] = _meta(
        label="Compatibility maximum score south",
        type_="float",
        tab="Advanced",
        section="compatibility",
        order=60,
        default=float(getattr(const, "compatibility_maximum_score_south", 10.0)),
        visible=False,
        binding=_binding("attr", target="compatibility_maximum_score_south"),
    )

    return data


# ============================================================
# FILE I/O
# ============================================================
def _save_json(data: Dict[str, Any], file_path: str = SETTINGS_FILE) -> None:
    _ensure_config_dir()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_json(file_path: str = SETTINGS_FILE) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "settings" not in data or not isinstance(data["settings"], dict):
        raise ConfigError("Invalid settings JSON structure")

    data.setdefault("version", CONFIG_VERSION)
    return data


# ============================================================
# CHOICE / ADAPTER RESOLUTION
# ============================================================
def _resolve_choices(meta: Dict[str, Any]) -> List[Any]:
    if "choices" in meta:
        return _deepcopy(meta.get("choices", []))

    provider_name = meta.get("choices_provider")
    if provider_name:
        provider = CHOICE_PROVIDERS.get(provider_name)
        if provider:
            return _deepcopy(provider())

    return []


def _adapter_fn(adapter_name: Optional[str], direction: str) -> Optional[Callable[..., Any]]:
    if not adapter_name:
        return None
    adapter = ADAPTERS.get(adapter_name)
    if not adapter:
        return None
    return adapter.get(direction)


# ============================================================
# NORMALIZATION / VALIDATION
# ============================================================
def _normalize_choice_storage(meta: Dict[str, Any], value: Any) -> Any:
    binding = meta.get("binding", {})
    fn = _adapter_fn(binding.get("adapter"), "to_storage")
    if fn:
        return fn(value, default=meta.get("default"))

    choices = _resolve_choices(meta)
    if choices:
        for choice in choices:
            if isinstance(choice, (tuple, list)) and len(choice) == 2:
                stored, label = choice
                if value == stored or str(value) == str(stored):
                    return stored
                if value == label or str(value) == str(label):
                    return stored
            else:
                if value == choice or str(value) == str(choice):
                    return choice

    return value


def _coerce_value(meta: Dict[str, Any], value: Any) -> Any:
    type_ = str(meta.get("type", "string")).strip().lower()
    nullable = bool(meta.get("nullable", False))

    if value is None and nullable:
        return None

    if type_ == "bool":
        return _to_bool(value, default=bool(meta.get("default", False)))
    if type_ == "int":
        return _to_int(value, default=int(meta.get("default", 0)))
    if type_ == "float":
        return _to_float(value, default=float(meta.get("default", 0.0)))
    if type_ == "string":
        return "" if value is None else str(value)
    if type_ == "choice":
        return _normalize_choice_storage(meta, value)
    if type_ == "int_list":
        return _int_list_to_runtime(value, default=meta.get("default", []))

    return value


def _validate_against_choices(meta: Dict[str, Any], value: Any) -> Any:
    if str(meta.get("type", "string")).strip().lower() != "choice":
        return value

    choices = _resolve_choices(meta)
    if not choices:
        return value

    valid_values = []
    for choice in choices:
        if isinstance(choice, (tuple, list)) and len(choice) == 2:
            valid_values.append(choice[0])
        else:
            valid_values.append(choice)

    if value in valid_values:
        return value

    for vv in valid_values:
        if str(vv) == str(value):
            return vv

    raise ConfigError(f"Invalid choice value '{value}' for setting '{meta.get('label', '')}'")


def _validate_range(meta: Dict[str, Any], value: Any) -> Any:
    if isinstance(value, (int, float)):
        if "min" in meta and value < meta["min"]:
            raise ConfigError(f"Value for '{meta.get('label', '')}' must be >= {meta['min']}")
        if "max" in meta and value > meta["max"]:
            raise ConfigError(f"Value for '{meta.get('label', '')}' must be <= {meta['max']}")
    return value


def _normalize_and_validate(meta: Dict[str, Any], value: Any) -> Any:
    value = _coerce_value(meta, value)
    value = _validate_against_choices(meta, value)
    value = _validate_range(meta, value)
    return value


# ============================================================
# BINDING ENGINE
# ============================================================
def _runtime_default_for_binding(meta: Dict[str, Any]) -> Any:
    binding = meta.get("binding", {})
    target = binding.get("target")
    if target and hasattr(const, target):
        return getattr(const, target)
    return meta.get("default")


def _read_runtime_value_from_binding(meta: Dict[str, Any]) -> Any:
    binding = meta.get("binding", {})
    kind = binding.get("kind")
    target = binding.get("target")

    if not target:
        return meta.get("default")

    runtime_value = getattr(const, target, meta.get("default"))

    # enum runtime -> symbolic storage
    if kind in ("enum_attr", "enum_setter"):
        enum_class_name = binding.get("enum_class")
        enum_class = getattr(const, enum_class_name, None)
        if enum_class is not None:
            return _enum_value_to_name(
                enum_class,
                runtime_value,
                default=meta.get("default"),
                exclude=binding.get("exclude", []),
            )

    # adapter-driven runtime -> storage
    fn = _adapter_fn(binding.get("adapter"), "to_storage")
    if fn:
        return fn(runtime_value, default=meta.get("default"))

    return runtime_value


def read_runtime_value(key: str, fallback: Any = None) -> Any:
    meta = get_setting_def(key)
    if not meta:
        return fallback
    return _read_runtime_value_from_binding(meta)


def _apply_bound_value(meta: Dict[str, Any], value: Any) -> None:
    binding = meta.get("binding", {})
    kind = binding.get("kind")
    target = binding.get("target")
    setter_name = binding.get("setter")

    runtime_value = value

    # Adapter-driven storage -> runtime
    fn = _adapter_fn(binding.get("adapter"), "to_runtime")
    if fn:
        runtime_value = fn(runtime_value, default=_runtime_default_for_binding(meta))

    # Enum symbolic storage -> enum/int runtime
    if kind in ("enum_attr", "enum_setter"):
        enum_class_name = binding.get("enum_class")
        enum_class = getattr(const, enum_class_name, None)
        if enum_class is not None:
            runtime_value = _enum_name_to_value(
                enum_class,
                runtime_value,
                default=_runtime_default_for_binding(meta),
                exclude=binding.get("exclude", []),
            )

    if kind == "setter":
        if setter_name and hasattr(const, setter_name):
            getattr(const, setter_name)(runtime_value)
        return

    if kind == "enum_setter":
        if setter_name and hasattr(const, setter_name):
            getattr(const, setter_name)(runtime_value)
        return

    # attr / enum_attr fallback
    if target:
        setattr(const, target, runtime_value)


def apply_setting(key: str) -> None:
    meta = get_setting_def(key)
    if not meta:
        return
    if not meta.get("binding"):
        return
    value = meta.get("value", meta.get("default"))
    _apply_bound_value(meta, value)


def apply_all_settings() -> None:
    for key in list(_CONFIG_CACHE.get("settings", {}).keys()):
        apply_setting(key)


# ============================================================
# ACCESSORS / MUTATORS
# ============================================================
def get_setting_def(key: str) -> Optional[Dict[str, Any]]:
    return _CONFIG_CACHE.get("settings", {}).get(key)


def get_all_setting_defs() -> Dict[str, Dict[str, Any]]:
    return _CONFIG_CACHE.get("settings", {})


def has_setting(key: str) -> bool:
    return key in _CONFIG_CACHE.get("settings", {})


def get_value(key: str, fallback: Any = None) -> Any:
    meta = get_setting_def(key)
    if not meta:
        return fallback
    return _deepcopy(meta.get("value", meta.get("default", fallback)))


def set_value(key: str, value: Any, *, apply: bool = True, save: bool = False) -> Any:
    meta = get_setting_def(key)
    if not meta:
        raise KeyError(f"Unknown setting: {key}")
    if meta.get("read_only", False):
        raise ConfigError(f"Setting '{key}' is read-only")

    normalized = _normalize_and_validate(meta, value)
    meta["value"] = normalized

    if apply:
        apply_setting(key)
    if save:
        save_all_settings()

    return normalized


def set_values(values_by_key: Dict[str, Any], *, apply: bool = True, save: bool = False) -> None:
    if not isinstance(values_by_key, dict):
        raise TypeError("values_by_key must be a dict")

    for key, value in values_by_key.items():
        set_value(key, value, apply=False, save=False)

    if apply:
        apply_all_settings()
    if save:
        save_all_settings()


def reset_setting(key: str, *, apply: bool = True, save: bool = False) -> Any:
    meta = get_setting_def(key)
    if not meta:
        raise KeyError(f"Unknown setting: {key}")

    meta["value"] = _deepcopy(meta.get("default"))
    if apply:
        apply_setting(key)
    if save:
        save_all_settings()
    return _deepcopy(meta["value"])


def reset_all(*, apply: bool = True, save: bool = False) -> Dict[str, Any]:
    for meta in _CONFIG_CACHE.get("settings", {}).values():
        meta["value"] = _deepcopy(meta.get("default"))

    if apply:
        apply_all_settings()
    if save:
        save_all_settings()

    return snapshot_values()


def snapshot_values() -> Dict[str, Any]:
    return {key: _deepcopy(meta.get("value", meta.get("default"))) for key, meta in _CONFIG_CACHE.get("settings", {}).items()}


# ============================================================
# DEVELOPER API
# ============================================================
def add_setting(
    key: str,
    meta: Optional[Dict[str, Any]] = None,
    *,
    label: Optional[str] = None,
    type_: Optional[str] = None,
    tab: str = "User",
    section: str = "general",
    default: Any = None,
    value: Any = None,
    visible: bool = True,
    order: int = 0,
    description: str = "",
    choices: Optional[List[Any]] = None,
    choices_provider: Optional[str] = None,
    min_value: Any = None,
    max_value: Any = None,
    read_only: bool = False,
    nullable: bool = False,
    binding: Optional[Dict[str, Any]] = None,
    save: bool = True,
    apply: bool = False,
    overwrite: bool = False,
) -> Dict[str, Any]:
    if has_setting(key) and not overwrite:
        raise ConfigError(f"Setting '{key}' already exists")

    if meta is None:
        meta = _meta(
            label=label or key,
            type_=type_ or "string",
            tab=tab,
            section=section,
            default=default,
            value=value,
            visible=visible,
            order=order,
            description=description,
            choices=choices,
            choices_provider=choices_provider,
            min_value=min_value,
            max_value=max_value,
            read_only=read_only,
            nullable=nullable,
            binding=binding,
        )
    else:
        meta = _deepcopy(meta)
        meta.setdefault("label", label or key)
        meta.setdefault("type", type_ or "string")
        meta.setdefault("tab", tab)
        meta.setdefault("section", section)
        meta.setdefault("group", section)
        meta.setdefault("visible", visible)
        meta.setdefault("order", order)
        meta.setdefault("description", description)
        meta.setdefault("read_only", read_only)
        meta.setdefault("nullable", nullable)
        meta.setdefault("binding", binding or {})
        if "value" not in meta:
            meta["value"] = _deepcopy(meta.get("default"))

    meta["value"] = _normalize_and_validate(meta, meta.get("value", meta.get("default")))
    _CONFIG_CACHE.setdefault("settings", {})[key] = meta

    if apply:
        apply_setting(key)
    if save:
        save_all_settings()

    return _deepcopy(meta)


def remove_setting(key: str, *, save: bool = True) -> bool:
    settings = _CONFIG_CACHE.get("settings", {})
    if key not in settings:
        return False
    del settings[key]
    if save:
        save_all_settings()
    return True


# ============================================================
# UI MODEL
# ============================================================
def get_ui_model(*, tab: Optional[str] = None, visible_only: bool = True) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for key, meta in _CONFIG_CACHE.get("settings", {}).items():
        if visible_only and not meta.get("visible", True):
            continue
        if tab is not None and str(meta.get("tab", "")).lower() != str(tab).lower():
            continue

        item = _deepcopy(meta)
        item["key"] = key
        item["choices"] = _resolve_choices(meta)
        items.append(item)

    items.sort(key=lambda item: (
        str(item.get("tab", "")),
        str(item.get("section", "")),
        int(item.get("order", 0)),
        str(item.get("label", "")),
    ))
    return items


def get_ui_tabs() -> List[str]:
    tabs: List[str] = []
    for meta in _CONFIG_CACHE.get("settings", {}).values():
        tab = str(meta.get("tab", "")).strip()
        if tab and tab not in tabs:
            tabs.append(tab)
    return tabs


def get_ui_sections(tab: Optional[str] = None, *, visible_only: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in get_ui_model(tab=tab, visible_only=visible_only):
        section = str(item.get("section", "general"))
        grouped.setdefault(section, []).append(item)
    return grouped


# ============================================================
# LEGACY MIGRATION
# ============================================================
def _find_setting_key_by_section_and_name(section: str, key: str) -> Optional[str]:
    for setting_key, meta in _CONFIG_CACHE.get("settings", {}).items():
        if str(meta.get("section", "")) == str(section) and setting_key == key:
            return setting_key
    return None


def _migrate_from_legacy_files() -> bool:
    migrated = False

    if os.path.exists(USER_SETTINGS_FILE):
        parser = configparser.ConfigParser()
        parser.read(USER_SETTINGS_FILE, encoding="utf-8")
        for section in parser.sections():
            for key, raw_value in parser[section].items():
                setting_key = _find_setting_key_by_section_and_name(section, key)
                if not setting_key:
                    continue
                try:
                    set_value(setting_key, raw_value, apply=False, save=False)
                    migrated = True
                except Exception:
                    pass

    if os.path.exists(ADVANCED_SETTINGS_FILE):
        try:
            with open(ADVANCED_SETTINGS_FILE, "r", encoding="utf-8") as f:
                advanced = json.load(f)
        except Exception:
            advanced = {}

        if isinstance(advanced, dict):
            for section, section_values in advanced.items():
                if not isinstance(section_values, dict):
                    continue
                for key, raw_value in section_values.items():
                    setting_key = _find_setting_key_by_section_and_name(section, key)
                    if not setting_key:
                        continue
                    try:
                        set_value(setting_key, raw_value, apply=False, save=False)
                        migrated = True
                    except Exception:
                        pass

    return migrated


# ============================================================
# LOAD / SAVE / INITIALIZE
# ============================================================
def load_all_settings(*, create_if_missing: bool = True, apply: bool = True) -> Dict[str, Any]:
    global _CONFIG_CACHE

    _ensure_config_dir()

    if os.path.exists(SETTINGS_FILE):
        try:
            _CONFIG_CACHE = _load_json(SETTINGS_FILE)
        except Exception as exc:
            raise ConfigError(f"Failed to load settings JSON: {exc}")

        # Normalize loaded values without hardcoding setting names.
        for key, meta in list(_CONFIG_CACHE.get("settings", {}).items()):
            try:
                if "value" not in meta:
                    meta["value"] = _deepcopy(meta.get("default"))
                meta["value"] = _normalize_and_validate(meta, meta.get("value"))
            except Exception as exc:
                raise ConfigError(f"Invalid setting '{key}': {exc}")

        if apply:
            apply_all_settings()
        return _deepcopy(_CONFIG_CACHE)

    _CONFIG_CACHE = build_default_settings_data()
    _migrate_from_legacy_files()

    if create_if_missing:
        save_all_settings()
    if apply:
        apply_all_settings()

    return _deepcopy(_CONFIG_CACHE)


def save_all_settings(file_path: str = SETTINGS_FILE) -> None:
    _save_json(_CONFIG_CACHE, file_path=file_path)


def initialize_runtime(*, force_reload: bool = False, create_if_missing: bool = True, silent: bool = True) -> Optional[Dict[str, Any]]:
    global _SETTINGS_LOADED

    if _SETTINGS_LOADED and not force_reload:
        return None

    try:
        data = load_all_settings(create_if_missing=create_if_missing, apply=True)
        _SETTINGS_LOADED = True
        return data
    except Exception:
        if silent:
            return None
        raise


def reset_to_defaults(*, apply: bool = True, save: bool = False) -> Dict[str, Any]:
    global _CONFIG_CACHE
    _CONFIG_CACHE = build_default_settings_data()
    if apply:
        apply_all_settings()
    if save:
        save_all_settings()
    return _deepcopy(_CONFIG_CACHE)


# ============================================================
# CONVENIENCE ALIASES
# ============================================================
def get_settings_dict() -> Dict[str, Any]:
    return _deepcopy(_CONFIG_CACHE)


def get_current_settings() -> Dict[str, Any]:
    return _deepcopy(_CONFIG_CACHE)


def save_settings() -> None:
    save_all_settings()

def _normalize_runtime_for_compare(meta: Dict[str, Any], runtime_value: Any) -> Any:
    """
    Convert an actual runtime const value back into the storage-style value
    so we can compare expected-vs-actual consistently.
    """
    binding = meta.get("binding", {})
    kind = binding.get("kind")

    # enum runtime -> enum name
    if kind in ("enum_attr", "enum_setter"):
        enum_class_name = binding.get("enum_class")
        enum_class = getattr(const, enum_class_name, None)
        if enum_class is not None:
            return _enum_value_to_name(
                enum_class,
                runtime_value,
                default=meta.get("default"),
                exclude=binding.get("exclude", []),
            )

    # adapter runtime -> storage
    fn = _adapter_fn(binding.get("adapter"), "to_storage")
    if fn:
        return fn(runtime_value, default=meta.get("default"))

    return runtime_value


def _expected_runtime_from_storage(meta: Dict[str, Any], storage_value: Any) -> Any:
    """
    Convert a stored config value into the runtime value that should be applied to const.
    """
    binding = meta.get("binding", {})
    kind = binding.get("kind")

    runtime_value = storage_value

    # adapter storage -> runtime
    fn = _adapter_fn(binding.get("adapter"), "to_runtime")
    if fn:
        runtime_value = fn(runtime_value, default=_runtime_default_for_binding(meta))

    # enum name -> enum value/member
    if kind in ("enum_attr", "enum_setter"):
        enum_class_name = binding.get("enum_class")
        enum_class = getattr(const, enum_class_name, None)
        if enum_class is not None:
            runtime_value = _enum_name_to_value(
                enum_class,
                runtime_value,
                default=_runtime_default_for_binding(meta),
                exclude=binding.get("exclude", []),
            )

    return runtime_value


def debug_dump_runtime_bindings(keys: Optional[List[str]] = None, apply_first: bool = True) -> None:
    """
    Print a detailed diagnostic report:
      - stored config value
      - expected runtime value
      - actual const target value
      - actual value re-normalized into storage form
      - match status
    """
    if apply_first:
        apply_all_settings()

    settings = get_all_setting_defs()
    selected_keys = keys or list(settings.keys())

    print("=" * 120)
    print("CONFIG -> CONST RUNTIME BINDING REPORT")
    print("=" * 120)

    for key in selected_keys:
        meta = settings.get(key)
        if not meta:
            print(f"[MISSING] {key}")
            continue

        binding = meta.get("binding", {})
        target = binding.get("target")
        kind = binding.get("kind")
        stored_value = meta.get("value", meta.get("default"))

        if not binding:
            print(f"[NO-BINDING] {key} | stored={stored_value!r}")
            continue

        expected_runtime = _expected_runtime_from_storage(meta, stored_value)

        if target and hasattr(const, target):
            actual_runtime = getattr(const, target)
        else:
            actual_runtime = None

        actual_storage = _normalize_runtime_for_compare(meta, actual_runtime)

        runtime_match = (actual_runtime == expected_runtime)
        storage_match = (str(actual_storage) == str(stored_value))

        status = "OK" if (runtime_match or storage_match) else "MISMATCH"

        print(f"KEY            : {key}")
        print(f"  kind         : {kind}")
        print(f"  target       : {target}")
        print(f"  stored       : {stored_value!r}")
        print(f"  expected_rt  : {expected_runtime!r}")
        print(f"  actual_rt    : {actual_runtime!r}")
        print(f"  actual_store : {actual_storage!r}")
        print(f"  status       : {status}")
        print("-" * 120)


def validate_runtime_bindings(keys: Optional[List[str]] = None, apply_first: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Return a structured validation result instead of only printing.

    Useful for programmatic checks:
        result = validate_runtime_bindings()
        bad = {k:v for k,v in result.items() if not v["ok"]}
    """
    if apply_first:
        apply_all_settings()

    settings = get_all_setting_defs()
    selected_keys = keys or list(settings.keys())

    report: Dict[str, Dict[str, Any]] = {}

    for key in selected_keys:
        meta = settings.get(key)
        if not meta:
            report[key] = {
                "ok": False,
                "reason": "missing_setting",
            }
            continue

        binding = meta.get("binding", {})
        target = binding.get("target")
        kind = binding.get("kind")
        stored_value = meta.get("value", meta.get("default"))

        if not binding:
            report[key] = {
                "ok": True,
                "reason": "no_binding",
                "stored": stored_value,
            }
            continue

        expected_runtime = _expected_runtime_from_storage(meta, stored_value)

        if target and hasattr(const, target):
            actual_runtime = getattr(const, target)
        else:
            actual_runtime = None

        actual_storage = _normalize_runtime_for_compare(meta, actual_runtime)

        runtime_match = (actual_runtime == expected_runtime)
        storage_match = (str(actual_storage) == str(stored_value))

        report[key] = {
            "ok": bool(runtime_match or storage_match),
            "kind": kind,
            "target": target,
            "stored": stored_value,
            "expected_runtime": expected_runtime,
            "actual_runtime": actual_runtime,
            "actual_storage": actual_storage,
            "runtime_match": runtime_match,
            "storage_match": storage_match,
        }

    return report

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("Loading unified settings...")
    data = load_all_settings(create_if_missing=True, apply=True)
    print("Loaded successfully.")
    print(debug_dump_runtime_bindings())
