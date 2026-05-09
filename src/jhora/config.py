import os
import json
import copy
import configparser

from jhora import const


# ============================================================
# FILE PATHS
# ============================================================
CONFIG_DIR = const._DATA_DIR
USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.ini")
ADVANCED_SETTINGS_FILE = os.path.join(CONFIG_DIR, "advanced_settings.json")

CONFIG_VERSION = 1


# ============================================================
# INTERNAL HELPERS
# ============================================================
def _ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _engine_name_map():
    """
    Build:
      name -> value
      value -> name

    from const.PLACE_DATABASE_ENGINE class attributes.
    """
    cls = const.PLACE_DATABASE_ENGINE
    name_to_value = {}
    value_to_name = {}

    for attr in dir(cls):
        if attr.startswith("_"):
            continue
        value = getattr(cls, attr)
        if isinstance(value, int):
            name_to_value[attr] = value
            value_to_name[value] = attr

    return name_to_value, value_to_name


def _engine_name_to_value(name, default=None):
    if name is None:
        return default
    name = str(name).strip().upper()
    name_to_value, _ = _engine_name_map()
    return name_to_value.get(name, default)


def _engine_value_to_name(value, default="NONE"):
    _, value_to_name = _engine_name_map()
    return value_to_name.get(value, default)


def _language_display_to_code(value, default=None):
    """
    Accept either:
      - display name like 'English'
      - code like 'en'

    Return code like 'en'.
    """
    if value is None:
        return default

    value = str(value).strip()

    # exact display name
    if value in const.available_languages:
        return const.available_languages[value]

    # already a language code?
    reverse = {v: k for k, v in const.available_languages.items()}
    if value in reverse:
        return value

    return default


def _language_code_to_display(code, default="English"):
    reverse = {v: k for k, v in const.available_languages.items()}
    return reverse.get(code, default)


def _to_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if value is None:
        return default

    value = str(value).strip().lower()
    if value in ("1", "true", "yes", "on", "y", "t"):
        return True
    if value in ("0", "false", "no", "off", "n", "f"):
        return False
    return default


def _to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def _to_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _deep_update(base: dict, override: dict):
    """
    Recursive dict merge.
    """
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value
    return base


def _enum_name_from_value(enum_class, value, exclude=None, default=None):
    """
    Convert enum/int/plain constant value to symbolic name.

    Works for:
      - Enum / IntEnum
      - plain classes with int constants

    If value is already a string and not resolvable, returns it.
    """
    exclude = set(exclude or [])

    if value is None:
        return default

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

    if isinstance(value, str):
        return value

    return default


def _enum_value_from_name(enum_class, name, exclude=None, default=None):
    """
    Convert symbolic name back to enum/plain constant value.

    Works for:
      - Enum / IntEnum
      - plain classes with int constants

    If input is already non-string (e.g. enum/int), returns it unchanged.
    """
    exclude = set(exclude or [])

    if name is None:
        return default

    if not isinstance(name, str):
        return name

    name = str(name).strip()

    if hasattr(enum_class, "__members__"):
        member = enum_class.__members__.get(name)
        if member is not None and name not in exclude:
            return member
    else:
        if hasattr(enum_class, name) and name not in exclude:
            return getattr(enum_class, name)

    return default


def _safe_const_attr(name, default=None):
    return getattr(const, name, default)


# ============================================================
# DEFAULT SETTINGS
# ============================================================
def get_default_user_settings():
    return {
        "meta": {
            "config_version": CONFIG_VERSION
        },
        "general": {
            "language": _language_code_to_display(
                getattr(const, "_DEFAULT_LANGUAGE", "en"),
                "English"
            ),
            "include_uranus_to_pluto": bool(
                getattr(const, "_INCLUDE_URANUS_TO_PLUTO", False)
            ),
            "use_24hour_format_in_to_dms": bool(
                getattr(const, "use_24hour_format_in_to_dms", True)
            ),
        },
        "location": {
            "database_engine": _engine_value_to_name(
                getattr(
                    const,
                    "database_engine",
                    getattr(const.PLACE_DATABASE_ENGINE, "NONE", 0)
                )
            ),
            "check_database_for_world_cities": bool(
                getattr(const, "check_database_for_world_cities", True)
            ),
            # kept for compatibility even if not exposed in dialog
            "get_place_elevation_from_internet": bool(
                getattr(const, "get_place_elevation_from_internet", False)
            ),
        },
        "calculation": {
            "default_ayanamsa_mode": str(
                getattr(const, "_DEFAULT_AYANAMSA_MODE", "TRUE_PUSHYA")
            ),
            "dhasa_year_duration_default": _enum_name_from_value(
                const.DHASA_YEAR_DURATION,
                getattr(
                    const,
                    "dhasa_year_duration_default",
                    getattr(const.DHASA_YEAR_DURATION, "TRUE_SIDEREAL_YEAR", None)
                ),
                exclude={"JHORA_DEFAULT", "DEFAULT"},
                default="TRUE_SIDEREAL_YEAR",
            ) if hasattr(const, "DHASA_YEAR_DURATION") else "TRUE_SIDEREAL_YEAR",
            "savana_year_method_default": _enum_name_from_value(
                const.SAVANA_YEAR_METHOD,
                getattr(
                    const,
                    "savana_year_method_default",
                    getattr(const.SAVANA_YEAR_METHOD, "PROSPECTIVE_0_to_360_JHORA", None)
                ),
                default="PROSPECTIVE_0_to_360_JHORA",
            ) if hasattr(const, "SAVANA_YEAR_METHOD") else "PROSPECTIVE_0_to_360_JHORA",
            "true_lunar_year_method_default": _enum_name_from_value(
                const.TRUE_LUNAR_YEAR_METHOD,
                getattr(
                    const,
                    "true_lunar_year_method_default",
                    getattr(const.TRUE_LUNAR_YEAR_METHOD, "TITHI_AT_DOB", None)
                ),
                default="TITHI_AT_DOB",
            ) if hasattr(const, "TRUE_LUNAR_YEAR_METHOD") else "TITHI_AT_DOB",
            "bhaava_madhya_method": getattr(const, "bhaava_madhya_method", 1),
            "tamil_month_method": int(
                getattr(const, "tamil_month_method", 3)
            ),
            "use_planet_speed_for_panchangam_end_timings": bool(
                getattr(const, "use_planet_speed_for_panchangam_end_timings", True)
            ),
        },
        "charts": {
            "include_special_and_arudha_lagna_in_charts": bool(
                getattr(const, "include_special_and_arudha_lagna_in_charts", True)
            ),
            "include_maandhi_in_charts": bool(
                getattr(const, "include_maandhi_in_charts", True)
            ),
            "include_charts_only_for_western_type": bool(
                getattr(const, "include_charts_only_for_western_type", False)
            ),
        }
    }


def get_default_advanced_settings():
    return {
        "config_version": CONFIG_VERSION,
        "nodes": {
            "use_true_nodes_for_rahu_ketu": bool(
                getattr(const, "_use_true_nodes_for_rahu_ketu", True)
            )
        },
        "calculation_variants": {
            "use_saravali_formula_for_uccha_bala": bool(
                getattr(const, "use_saravali_formula_for_uccha_bala", True)
            ),
            "hora_chart_by_pvr_method": bool(
                getattr(const, "hora_chart_by_pvr_method", True)
            ),
            "ashtottari_bhukthi_starts_from_dhasa_lord": bool(
                getattr(const, "ashtottari_bhukthi_starts_from_dhasa_lord", True)
            ),
            "planet_retrogression_calculation_method": int(
                getattr(const, "planet_retrogression_calculation_method", 1)
            ),
        },
        "tradition_overrides": {
            "force_kali_start_year_for_years_before_kali_year_4009": bool(
                getattr(const, "force_kali_start_year_for_years_before_kali_year_4009", True)
            ),
            "kali_start_year": int(
                getattr(const, "kali_start_year", 13)
            ),
            "ritu_per_solar_tamil_month": bool(
                getattr(const, "ritu_per_solar_tamil_month", True)
            ),
            "use_aharghana_for_vaara_calcuation": bool(
                getattr(const, "use_aharghana_for_vaara_calcuation", False)
            ),
            "scorpio_owner_for_dhasa_calculations": getattr(
                const, "scorpio_owner_for_dhasa_calculations", None
            ),
            "aquarius_owner_for_dhasa_calculations": getattr(
                const, "aquarius_owner_for_dhasa_calculations", None
            ),
            "use_kp_dictionary_for_lords_calculation": bool(
                getattr(const, "use_kp_dictionary_for_lords_calculation", False)
            ),
        },
        "compatibility": {
            "skip_using_girls_varna_for_minimum_tamil_porutham": bool(
                getattr(const, "skip_using_girls_varna_for_minimum_tamil_porutham", True)
            ),
            "mandatory_compatibility_south_list": list(
                getattr(const, "mandatory_compatibility_south_list", [1, 2, 3, 5])
            ),
            "compatibility_minimum_score_north": float(
                getattr(const, "compatibility_minimum_score_north", 18.0)
            ),
            "compatibility_minimum_score_south": float(
                getattr(const, "compatibility_minimum_score_south", 6.0)
            ),
            "compatibility_maximum_score_north": float(
                getattr(const, "compatibility_maximum_score_north", 36.0)
            ),
            "compatibility_maximum_score_south": float(
                getattr(const, "compatibility_maximum_score_south", 10.0)
            ),
        }
    }


# ============================================================
# APPLY SETTINGS INTO const
# ============================================================
def apply_user_settings(settings: dict):
    if not isinstance(settings, dict):
        return

    general = settings.get("general", {})
    location = settings.get("location", {})
    calculation = settings.get("calculation", {})
    charts = settings.get("charts", {})

    # -------------------------
    # general
    # -------------------------
    lang_code = _language_display_to_code(
        general.get("language"),
        getattr(const, "_DEFAULT_LANGUAGE", "en")
    )
    if lang_code:
        const._DEFAULT_LANGUAGE = lang_code

    const._INCLUDE_URANUS_TO_PLUTO = _to_bool(
        general.get("include_uranus_to_pluto"),
        getattr(const, "_INCLUDE_URANUS_TO_PLUTO", False)
    )

    const.use_24hour_format_in_to_dms = _to_bool(
        general.get("use_24hour_format_in_to_dms"),
        getattr(const, "use_24hour_format_in_to_dms", True)
    )

    # -------------------------
    # location
    # -------------------------
    engine_value = _engine_name_to_value(
        location.get("database_engine"),
        getattr(
            const,
            "database_engine",
            getattr(const.PLACE_DATABASE_ENGINE, "NONE", 0)
        )
    )
    if engine_value is not None and hasattr(const, "set_place_database_engine"):
        const.set_place_database_engine(engine_value)
    elif engine_value is not None:
        const.database_engine = engine_value

    if hasattr(const, "check_database_for_world_cities"):
        const.check_database_for_world_cities = _to_bool(
            location.get("check_database_for_world_cities"),
            getattr(const, "check_database_for_world_cities", True)
        )

    if hasattr(const, "get_place_elevation_from_internet"):
        const.get_place_elevation_from_internet = _to_bool(
            location.get("get_place_elevation_from_internet"),
            getattr(const, "get_place_elevation_from_internet", False)
        )

    # -------------------------
    # calculation
    # -------------------------
    ay = str(
        calculation.get(
            "default_ayanamsa_mode",
            getattr(const, "_DEFAULT_AYANAMSA_MODE", "TRUE_PUSHYA")
        )
    ).strip()
    if ay in getattr(const, "available_ayanamsa_modes", {}):
        const._DEFAULT_AYANAMSA_MODE = ay

    if hasattr(const, "DHASA_YEAR_DURATION"):
        const.dhasa_year_duration_default = _enum_value_from_name(
            const.DHASA_YEAR_DURATION,
            calculation.get("dhasa_year_duration_default"),
            exclude={"JHORA_DEFAULT", "DEFAULT"},
            default=getattr(
                const,
                "dhasa_year_duration_default",
                getattr(const.DHASA_YEAR_DURATION, "TRUE_SIDEREAL_YEAR", None)
            ),
        )

    if hasattr(const, "SAVANA_YEAR_METHOD"):
        const.savana_year_method_default = _enum_value_from_name(
            const.SAVANA_YEAR_METHOD,
            calculation.get("savana_year_method_default"),
            default=getattr(
                const,
                "savana_year_method_default",
                getattr(const.SAVANA_YEAR_METHOD, "PROSPECTIVE_0_to_360_JHORA", None)
            ),
        )

    if hasattr(const, "TRUE_LUNAR_YEAR_METHOD"):
        const.true_lunar_year_method_default = _enum_value_from_name(
            const.TRUE_LUNAR_YEAR_METHOD,
            calculation.get("true_lunar_year_method_default"),
            default=getattr(
                const,
                "true_lunar_year_method_default",
                getattr(const.TRUE_LUNAR_YEAR_METHOD, "TITHI_AT_DOB", None)
            ),
        )

    bh = calculation.get(
        "bhaava_madhya_method",
        getattr(const, "bhaava_madhya_method", 1)
    )
    try:
        bh = int(bh)
    except Exception:
        bh = str(bh).strip()
    const.bhaava_madhya_method = bh

    const.tamil_month_method = _to_int(
        calculation.get("tamil_month_method"),
        getattr(const, "tamil_month_method", 3)
    )

    const.use_planet_speed_for_panchangam_end_timings = _to_bool(
        calculation.get("use_planet_speed_for_panchangam_end_timings"),
        getattr(const, "use_planet_speed_for_panchangam_end_timings", True)
    )

    # -------------------------
    # charts
    # -------------------------
    const.include_special_and_arudha_lagna_in_charts = _to_bool(
        charts.get("include_special_and_arudha_lagna_in_charts"),
        getattr(const, "include_special_and_arudha_lagna_in_charts", True)
    )

    const.include_maandhi_in_charts = _to_bool(
        charts.get("include_maandhi_in_charts"),
        getattr(const, "include_maandhi_in_charts", True)
    )

    const.include_charts_only_for_western_type = _to_bool(
        charts.get("include_charts_only_for_western_type"),
        getattr(const, "include_charts_only_for_western_type", False)
    )


def apply_advanced_settings(settings: dict):
    if not isinstance(settings, dict):
        return

    nodes = settings.get("nodes", {})
    calc = settings.get("calculation_variants", {})
    tradition = settings.get("tradition_overrides", {})
    compatibility = settings.get("compatibility", {})

    # -------------------------
    # nodes
    # -------------------------
    true_nodes = _to_bool(
        nodes.get("use_true_nodes_for_rahu_ketu"),
        getattr(const, "_use_true_nodes_for_rahu_ketu", True)
    )

    if hasattr(const, "set_node_mode"):
        const.set_node_mode(true_nodes)
    else:
        const._use_true_nodes_for_rahu_ketu = true_nodes

    # -------------------------
    # calculation variants
    # -------------------------
    const.use_saravali_formula_for_uccha_bala = _to_bool(
        calc.get("use_saravali_formula_for_uccha_bala"),
        getattr(const, "use_saravali_formula_for_uccha_bala", True)
    )

    const.hora_chart_by_pvr_method = _to_bool(
        calc.get("hora_chart_by_pvr_method"),
        getattr(const, "hora_chart_by_pvr_method", True)
    )

    const.ashtottari_bhukthi_starts_from_dhasa_lord = _to_bool(
        calc.get("ashtottari_bhukthi_starts_from_dhasa_lord"),
        getattr(const, "ashtottari_bhukthi_starts_from_dhasa_lord", True)
    )

    const.planet_retrogression_calculation_method = _to_int(
        calc.get("planet_retrogression_calculation_method"),
        getattr(const, "planet_retrogression_calculation_method", 1)
    )

    # -------------------------
    # tradition overrides
    # -------------------------
    const.force_kali_start_year_for_years_before_kali_year_4009 = _to_bool(
        tradition.get("force_kali_start_year_for_years_before_kali_year_4009"),
        getattr(const, "force_kali_start_year_for_years_before_kali_year_4009", True)
    )

    const.kali_start_year = _to_int(
        tradition.get("kali_start_year"),
        getattr(const, "kali_start_year", 13)
    )

    const.ritu_per_solar_tamil_month = _to_bool(
        tradition.get("ritu_per_solar_tamil_month"),
        getattr(const, "ritu_per_solar_tamil_month", True)
    )

    const.use_aharghana_for_vaara_calcuation = _to_bool(
        tradition.get("use_aharghana_for_vaara_calcuation"),
        getattr(const, "use_aharghana_for_vaara_calcuation", False)
    )

    const.scorpio_owner_for_dhasa_calculations = tradition.get(
        "scorpio_owner_for_dhasa_calculations",
        getattr(const, "scorpio_owner_for_dhasa_calculations", None)
    )

    const.aquarius_owner_for_dhasa_calculations = tradition.get(
        "aquarius_owner_for_dhasa_calculations",
        getattr(const, "aquarius_owner_for_dhasa_calculations", None)
    )

    const.use_kp_dictionary_for_lords_calculation = _to_bool(
        tradition.get("use_kp_dictionary_for_lords_calculation"),
        getattr(const, "use_kp_dictionary_for_lords_calculation", False)
    )

    # -------------------------
    # compatibility
    # -------------------------
    const.skip_using_girls_varna_for_minimum_tamil_porutham = _to_bool(
        compatibility.get("skip_using_girls_varna_for_minimum_tamil_porutham"),
        getattr(const, "skip_using_girls_varna_for_minimum_tamil_porutham", True)
    )

    mand_list = compatibility.get(
        "mandatory_compatibility_south_list",
        getattr(const, "mandatory_compatibility_south_list", [1, 2, 3, 5])
    )
    if isinstance(mand_list, (list, tuple)):
        const.mandatory_compatibility_south_list = [int(x) for x in mand_list]
    else:
        const.mandatory_compatibility_south_list = [1, 2, 3, 5]

    const.compatibility_minimum_score_north = _to_float(
        compatibility.get("compatibility_minimum_score_north"),
        getattr(const, "compatibility_minimum_score_north", 18.0)
    )

    const.compatibility_minimum_score_south = _to_float(
        compatibility.get("compatibility_minimum_score_south"),
        getattr(const, "compatibility_minimum_score_south", 6.0)
    )

    const.compatibility_maximum_score_north = _to_float(
        compatibility.get("compatibility_maximum_score_north"),
        getattr(const, "compatibility_maximum_score_north", 36.0)
    )

    const.compatibility_maximum_score_south = _to_float(
        compatibility.get("compatibility_maximum_score_south"),
        getattr(const, "compatibility_maximum_score_south", 10.0)
    )


# ============================================================
# CURRENT RUNTIME -> SETTINGS DICTS
# ============================================================
def get_current_user_settings():
    """
    Return a settings dict derived from current runtime values in const.
    """
    return get_default_user_settings()


def get_current_advanced_settings():
    """
    Return a settings dict derived from current runtime values in const.
    """
    return get_default_advanced_settings()


# ============================================================
# LOAD / SAVE USER SETTINGS (INI)
# ============================================================
def save_user_settings(settings=None, file_path=USER_SETTINGS_FILE):
    """
    Save simple user settings to INI.
    If settings is None, save current runtime values from const.
    """
    _ensure_config_dir()

    if settings is None:
        settings = get_current_user_settings()

    parser = configparser.ConfigParser()

    for section, values in settings.items():
        if not isinstance(values, dict):
            continue

        parser[section] = {}
        for key, value in values.items():
            if isinstance(value, bool):
                parser[section][key] = "true" if value else "false"
            else:
                parser[section][key] = str(value)

    with open(file_path, "w", encoding="utf-8") as f:
        parser.write(f)


def load_user_settings(file_path=USER_SETTINGS_FILE, create_if_missing=True, apply=True):
    """
    Load simple user settings from INI.
    Missing file -> defaults (and optionally create it).
    """
    defaults = get_default_user_settings()
    settings = copy.deepcopy(defaults)

    if not os.path.exists(file_path):
        if create_if_missing:
            save_user_settings(settings, file_path=file_path)
        if apply:
            apply_user_settings(settings)
        return settings

    parser = configparser.ConfigParser()
    parser.read(file_path, encoding="utf-8")

    # meta
    if parser.has_section("meta"):
        settings["meta"]["config_version"] = _to_int(
            parser.get("meta", "config_version", fallback=str(CONFIG_VERSION)),
            CONFIG_VERSION
        )

    # general
    if parser.has_section("general"):
        sec = parser["general"]
        settings["general"]["language"] = sec.get(
            "language",
            settings["general"]["language"]
        )
        settings["general"]["include_uranus_to_pluto"] = _to_bool(
            sec.get("include_uranus_to_pluto"),
            settings["general"]["include_uranus_to_pluto"]
        )
        settings["general"]["use_24hour_format_in_to_dms"] = _to_bool(
            sec.get("use_24hour_format_in_to_dms"),
            settings["general"]["use_24hour_format_in_to_dms"]
        )

    # location
    if parser.has_section("location"):
        sec = parser["location"]
        settings["location"]["database_engine"] = sec.get(
            "database_engine",
            settings["location"]["database_engine"]
        )
        settings["location"]["check_database_for_world_cities"] = _to_bool(
            sec.get("check_database_for_world_cities"),
            settings["location"]["check_database_for_world_cities"]
        )
        settings["location"]["get_place_elevation_from_internet"] = _to_bool(
            sec.get("get_place_elevation_from_internet"),
            settings["location"]["get_place_elevation_from_internet"]
        )

    # calculation
    if parser.has_section("calculation"):
        sec = parser["calculation"]
        settings["calculation"]["default_ayanamsa_mode"] = sec.get(
            "default_ayanamsa_mode",
            settings["calculation"]["default_ayanamsa_mode"]
        )
        settings["calculation"]["dhasa_year_duration_default"] = sec.get(
            "dhasa_year_duration_default",
            settings["calculation"]["dhasa_year_duration_default"]
        )
        settings["calculation"]["savana_year_method_default"] = sec.get(
            "savana_year_method_default",
            settings["calculation"]["savana_year_method_default"]
        )
        settings["calculation"]["true_lunar_year_method_default"] = sec.get(
            "true_lunar_year_method_default",
            settings["calculation"]["true_lunar_year_method_default"]
        )
        settings["calculation"]["bhaava_madhya_method"] = sec.get(
            "bhaava_madhya_method",
            str(settings["calculation"]["bhaava_madhya_method"])
        )
        settings["calculation"]["tamil_month_method"] = _to_int(
            sec.get("tamil_month_method"),
            settings["calculation"]["tamil_month_method"]
        )
        settings["calculation"]["use_planet_speed_for_panchangam_end_timings"] = _to_bool(
            sec.get("use_planet_speed_for_panchangam_end_timings"),
            settings["calculation"]["use_planet_speed_for_panchangam_end_timings"]
        )

    # charts
    if parser.has_section("charts"):
        sec = parser["charts"]
        settings["charts"]["include_special_and_arudha_lagna_in_charts"] = _to_bool(
            sec.get("include_special_and_arudha_lagna_in_charts"),
            settings["charts"]["include_special_and_arudha_lagna_in_charts"]
        )
        settings["charts"]["include_maandhi_in_charts"] = _to_bool(
            sec.get("include_maandhi_in_charts"),
            settings["charts"]["include_maandhi_in_charts"]
        )
        settings["charts"]["include_charts_only_for_western_type"] = _to_bool(
            sec.get("include_charts_only_for_western_type"),
            settings["charts"]["include_charts_only_for_western_type"]
        )

    if apply:
        apply_user_settings(settings)

    return settings


# ============================================================
# LOAD / SAVE ADVANCED SETTINGS (JSON)
# ============================================================
def save_advanced_settings(settings=None, file_path=ADVANCED_SETTINGS_FILE):
    """
    Save advanced settings to JSON.
    If settings is None, save current runtime values from const.
    """
    _ensure_config_dir()

    if settings is None:
        settings = get_current_advanced_settings()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def load_advanced_settings(file_path=ADVANCED_SETTINGS_FILE, create_if_missing=True, apply=True):
    """
    Load advanced settings from JSON.
    Missing file -> defaults (and optionally create it).
    """
    defaults = get_default_advanced_settings()
    settings = copy.deepcopy(defaults)

    if not os.path.exists(file_path):
        if create_if_missing:
            save_advanced_settings(settings, file_path=file_path)
        if apply:
            apply_advanced_settings(settings)
        return settings

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            _deep_update(settings, loaded)
    except Exception:
        # If JSON is broken, silently fall back to defaults.
        settings = copy.deepcopy(defaults)

    if apply:
        apply_advanced_settings(settings)

    return settings


# ============================================================
# COMBINED LOAD / SAVE
# ============================================================
def load_all_settings(create_if_missing=True, apply=True):
    """
    Load both:
      - user_settings.ini
      - advanced_settings.json

    and apply them into const.

    Returns:
        {
            "user": ...,
            "advanced": ...
        }
    """
    user_settings = load_user_settings(
        file_path=USER_SETTINGS_FILE,
        create_if_missing=create_if_missing,
        apply=apply
    )

    advanced_settings = load_advanced_settings(
        file_path=ADVANCED_SETTINGS_FILE,
        create_if_missing=create_if_missing,
        apply=apply
    )

    return {
        "user": user_settings,
        "advanced": advanced_settings
    }


def save_all_settings(user_settings=None, advanced_settings=None):
    """
    Save both user + advanced settings.
    If either is None, current runtime values from const are saved.
    """
    save_user_settings(user_settings, file_path=USER_SETTINGS_FILE)
    save_advanced_settings(advanced_settings, file_path=ADVANCED_SETTINGS_FILE)


def reset_to_defaults(apply=True, save=False):
    """
    Reset runtime values to built-in defaults from const-backed default builders.
    Optionally save them immediately to disk.
    """
    user_defaults = get_default_user_settings()
    advanced_defaults = get_default_advanced_settings()

    if apply:
        apply_user_settings(user_defaults)
        apply_advanced_settings(advanced_defaults)

    if save:
        save_user_settings(user_defaults, file_path=USER_SETTINGS_FILE)
        save_advanced_settings(advanced_defaults, file_path=ADVANCED_SETTINGS_FILE)

    return {
        "user": user_defaults,
        "advanced": advanced_defaults
    }


_SETTINGS_LOADED = False


def initialize_runtime(force_reload=False, create_if_missing=True, silent=True):
    """
    Load and apply config-backed settings once per process.

    Why this exists:
      - built-in UIs should not need to call load_all_settings() manually
      - external users importing jhora modules should also get settings automatically
      - repeated imports should not reload settings unnecessarily

    Parameters
    ----------
    force_reload : bool
        If True, reload settings even if already loaded once.
    create_if_missing : bool
        If True, create default INI/JSON files if they do not exist.
    silent : bool
        If True, suppress exceptions and keep const defaults on error.

    Returns
    -------
    dict | None
        The loaded settings dict from load_all_settings(), or None if silent failure occurred.
    """
    global _SETTINGS_LOADED

    if _SETTINGS_LOADED and not force_reload:
        return None

    try:
        data = load_all_settings(create_if_missing=create_if_missing, apply=True)
        _SETTINGS_LOADED = True
        return data
    except Exception:
        if silent:
            # Keep built-in const defaults if config load fails
            return None
        raise


# ============================================================
# GENERIC GET / SET API
# ============================================================
_USER_SECTIONS = {"general", "location", "calculation", "charts"}
_ADVANCED_SECTIONS = {"nodes", "calculation_variants", "tradition_overrides", "compatibility"}


def _detect_scope_for_section(section: str) -> str:
    """
    Return:
        "user"      if section belongs to user settings
        "advanced"  if section belongs to advanced settings

    Raises:
        KeyError if section is unknown.
    """
    section = str(section).strip()

    if section in _USER_SECTIONS:
        return "user"
    if section in _ADVANCED_SECTIONS:
        return "advanced"

    raise KeyError(f"Unknown config section: {section}")


def get_user_settings_dict():
    """
    Return current user settings as a dict derived from runtime values in const.
    """
    return get_current_user_settings()


def get_advanced_settings_dict():
    """
    Return current advanced settings as a dict derived from runtime values in const.
    """
    return get_current_advanced_settings()


def get_setting(section: str, key: str, scope: str = "auto", fallback=None):
    """
    Generic getter for any config-backed item.

    Parameters
    ----------
    section : str
        Example: "general", "location", "calculation", "charts",
                 "nodes", "calculation_variants", "tradition_overrides", "compatibility"
    key : str
        Example: "language", "database_engine", "default_ayanamsa_mode"
    scope : str
        "auto" | "user" | "advanced"
    fallback :
        Returned if key is not found.

    Returns
    -------
    value
    """
    if scope == "auto":
        scope = _detect_scope_for_section(section)

    if scope == "user":
        data = get_current_user_settings()
    elif scope == "advanced":
        data = get_current_advanced_settings()
    else:
        raise ValueError(f"Invalid scope: {scope}")

    return data.get(section, {}).get(key, fallback)


def get_user_setting(section: str, key: str, fallback=None):
    return get_setting(section, key, scope="user", fallback=fallback)


def get_advanced_setting(section: str, key: str, fallback=None):
    return get_setting(section, key, scope="advanced", fallback=fallback)


def _set_nested_value(data: dict, section: str, key: str, value):
    if section not in data:
        data[section] = {}
    data[section][key] = value
    return data


def set_setting(section: str, key: str, value, scope: str = "auto", apply: bool = True, save: bool = False):
    """
    Generic setter for any config-backed item.

    Parameters
    ----------
    section : str
        Settings section name.
    key : str
        Key inside the section.
    value :
        New value.
    scope : str
        "auto" | "user" | "advanced"
    apply : bool
        If True, apply the updated setting immediately into const/runtime.
    save : bool
        If True, save to disk immediately after updating.

    Returns
    -------
    dict
        The updated settings dict for the chosen scope.
    """
    if scope == "auto":
        scope = _detect_scope_for_section(section)

    if scope == "user":
        data = get_current_user_settings()
        data = _set_nested_value(data, section, key, value)

        if apply:
            apply_user_settings(data)
        if save:
            save_user_settings(data)

        return data

    elif scope == "advanced":
        data = get_current_advanced_settings()
        data = _set_nested_value(data, section, key, value)

        if apply:
            apply_advanced_settings(data)
        if save:
            save_advanced_settings(data)

        return data

    else:
        raise ValueError(f"Invalid scope: {scope}")


def set_user_setting(section: str, key: str, value, apply: bool = True, save: bool = False):
    return set_setting(section, key, value, scope="user", apply=apply, save=save)


def set_advanced_setting(section: str, key: str, value, apply: bool = True, save: bool = False):
    return set_setting(section, key, value, scope="advanced", apply=apply, save=save)


def set_many_settings(updates: dict, scope: str = "auto", apply: bool = True, save: bool = False):
    """
    Bulk setter.

    Example:
        set_many_settings({
            "general": {"language": "Tamil"},
            "location": {"database_engine": "SQLITE"}
        }, scope="user", apply=True, save=False)

    If scope="auto", all sections must belong to the same scope family
    OR you should call this separately for user/advanced.
    """
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dict")

    if scope == "auto":
        detected_scopes = {_detect_scope_for_section(section) for section in updates.keys()}
        if len(detected_scopes) != 1:
            raise ValueError(
                "set_many_settings(scope='auto') requires all sections to belong to the same scope. "
                "Call separately for user and advanced settings."
            )
        scope = detected_scopes.pop()

    if scope == "user":
        data = get_current_user_settings()
        for section, values in updates.items():
            if not isinstance(values, dict):
                continue
            for key, value in values.items():
                _set_nested_value(data, section, key, value)

        if apply:
            apply_user_settings(data)
        if save:
            save_user_settings(data)

        return data

    elif scope == "advanced":
        data = get_current_advanced_settings()
        for section, values in updates.items():
            if not isinstance(values, dict):
                continue
            for key, value in values.items():
                _set_nested_value(data, section, key, value)

        if apply:
            apply_advanced_settings(data)
        if save:
            save_advanced_settings(data)

        return data

    else:
        raise ValueError(f"Invalid scope: {scope}")


def has_setting(section: str, key: str, scope: str = "auto") -> bool:
    """
    Return True if a config-backed key exists in the current settings structure.
    """
    sentinel = object()
    return get_setting(section, key, scope=scope, fallback=sentinel) is not sentinel


# ============================================================
# MAIN (optional quick test)
# ============================================================
if __name__ == "__main__":
    print("Loading settings...")
    data = load_all_settings(create_if_missing=True, apply=True)
    print("Loaded successfully.")
    print("User settings:")
    print(json.dumps(data["user"], indent=2, ensure_ascii=False))
    print("Advanced settings:")
    print(json.dumps(data["advanced"], indent=2, ensure_ascii=False))