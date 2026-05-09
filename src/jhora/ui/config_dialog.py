from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QDialogButtonBox,
    QTabWidget,
    QMessageBox,
    QSizePolicy,
)

from jhora import const, config


# ============================================================
# HELPERS
# ============================================================

def _bool_to_text(value: bool) -> str:
    return "True" if bool(value) else "False"


def _text_to_bool(text: str) -> bool:
    return str(text).strip().lower() == "true"


def _safe_set_combo_value(combo: QComboBox, value):
    """
    Select combo item by stored userData first, then by visible text.
    """
    value_text = str(value)

    idx = combo.findData(value_text)
    if idx >= 0:
        combo.setCurrentIndex(idx)
        return

    idx = combo.findText(value_text)
    if idx >= 0:
        combo.setCurrentIndex(idx)
        return

    if combo.count() > 0:
        combo.setCurrentIndex(0)


def _populate_combo(combo: QComboBox, choices):
    """
    Populate a QComboBox from either:
      - ["A", "B", "C"]
      - [("key", "Label"), ...]

    For plain strings:
      visible text = stored value

    For (key, label):
      visible text = label
      stored value = key
    """
    combo.clear()

    for item in choices:
        if isinstance(item, (tuple, list)) and len(item) == 2:
            key, label = item
            combo.addItem(str(label), str(key))
        else:
            combo.addItem(str(item), str(item))


def _enum_names(enum_class, preferred=None, exclude=None):
    """
    Return constant/enum names from either:
      - real Enum / IntEnum classes
      - plain classes containing int constants

    Examples:
      const.DHASA_YEAR_DURATION       -> IntEnum
      const.PLACE_DATABASE_ENGINE     -> possibly plain int-constant class
    """
    preferred = preferred or []
    exclude = set(exclude or [])

    if hasattr(enum_class, "__members__"):
        names = [
            name
            for name in enum_class.__members__.keys()
            if name not in exclude
        ]
    else:
        names = []
        for attr, value in vars(enum_class).items():
            if attr.startswith("_"):
                continue

            if type(value) is int and attr not in exclude:
                names.append(attr)

    ordered = (
        [x for x in preferred if x in names]
        + [x for x in names if x not in preferred]
    )

    return ordered


def _enum_value_from_name(enum_class, name):
    """
    Convert enum/plain-class name to value.

    Examples:
      _enum_value_from_name(const.DHASA_YEAR_DURATION, "LUNAR_YEAR")
      _enum_value_from_name(const.PLACE_DATABASE_ENGINE, "SQLITE")
    """
    if hasattr(enum_class, "__members__"):
        return enum_class.__members__[name]

    return getattr(enum_class, name)


def _enum_name_from_value(enum_class, value, exclude=None):
    """
    Convert enum/plain-class value to first matching name.
    Works for Enum/IntEnum and plain int-constant classes.
    """
    exclude = set(exclude or [])

    if hasattr(enum_class, "__members__"):
        for name, member in enum_class.__members__.items():
            if name not in exclude and member == value:
                return name
    else:
        for attr, attr_value in vars(enum_class).items():
            if attr.startswith("_") or attr in exclude:
                continue

            if attr_value == value:
                return attr

    return None


def _enum_name_from_name_or_value(enum_class, value, exclude=None, fallback=None):
    """
    Return display name from either:
      - string name
      - Enum/IntEnum value
      - integer value

    Useful while loading current settings into combo boxes.
    """
    exclude = set(exclude or [])

    if value is None:
        return fallback

    if isinstance(value, str):
        if hasattr(enum_class, "__members__"):
            if value in enum_class.__members__ and value not in exclude:
                return value
        else:
            if hasattr(enum_class, value) and value not in exclude:
                return value

        return fallback or value

    name = _enum_name_from_value(enum_class, value, exclude=exclude)
    return name or fallback


def _engine_names():
    return _enum_names(
        const.PLACE_DATABASE_ENGINE,
        preferred=["NONE", "CSV_5K", "CSV_5K_IN", "PICKLE", "SQLITE"],
    )


def _language_names():
    return list(const.available_languages.keys())


def _ayanamsa_names():
    return list(const.available_ayanamsa_modes.keys())


def _dhasa_year_duration_names():
    return _enum_names(
        const.DHASA_YEAR_DURATION,
        preferred=[
            "TRUE_SIDEREAL_YEAR",
            "MEAN_SIDEREAL_YEAR",
            "MEAN_TROPICAL_YEAR",
            "TRUE_TROPICAL_YEAR",
            "SAVANA_YEAR",
            "LUNAR_YEAR",
        ],
        exclude=["JHORA_DEFAULT", "DEFAULT"],
    )


def _true_lunar_year_names():
    return _enum_names(
        const.TRUE_LUNAR_YEAR_METHOD,
        preferred=["TITHI_AT_DOB"],
    )


def _savana_year_method_names():
    return _enum_names(
        const.SAVANA_YEAR_METHOD,
        preferred=[
            "PROSPECTIVE_0_to_360_JHORA",
            "DEFAULT",
        ],
    )


def _house_method_choices(preferred_keys=None, exclude_keys=None):
    """
    Return house-system choices as ordered (key, label) pairs.

    UI should display the label, but config should store the key.
    """
    preferred_keys = [str(x) for x in (preferred_keys or [])]
    exclude_keys = {str(x) for x in (exclude_keys or [])}

    try:
        hs = const.available_house_systems()
    except Exception:
        hs = {}

    if isinstance(hs, dict) and hs:
        items = [
            (str(k), str(v))
            for k, v in hs.items()
            if str(k) not in exclude_keys
        ]

        preferred_items = [item for item in items if item[0] in preferred_keys]
        remaining_items = [item for item in items if item[0] not in preferred_keys]

        preferred_items.sort(key=lambda item: preferred_keys.index(item[0]))

        return preferred_items + remaining_items

    fallback = str(getattr(const, "bhaava_madhya_method", 1))
    return [(fallback, fallback)]


def _yes_no_choices():
    return ["True", "False"]


def _tamil_month_method_choices():
    return ["0", "1", "2", "3"]


def _retrogression_method_choices():
    return ["1", "2"]


def _setting_to_display_text(key, value):
    """
    Converts runtime/config value into combo-box stored key/text.

    For enum-like fields, convert enum/int values back to their symbolic names.
    For house method, keep raw key string (combo userData uses key).
    """
    if key == "dhasa_year_duration_default":
        return _enum_name_from_name_or_value(
            const.DHASA_YEAR_DURATION,
            value,
            exclude=["JHORA_DEFAULT", "DEFAULT"],
            fallback="TRUE_SIDEREAL_YEAR",
        )

    if key == "savana_year_method_default" and hasattr(const, "SAVANA_YEAR_METHOD"):
        return _enum_name_from_name_or_value(
            const.SAVANA_YEAR_METHOD,
            value,
            fallback="PROSPECTIVE_0_to_360_JHORA",
        )

    if key == "true_lunar_year_method_default" and hasattr(const, "TRUE_LUNAR_YEAR_METHOD"):
        return _enum_name_from_name_or_value(
            const.TRUE_LUNAR_YEAR_METHOD,
            value,
            fallback="TITHI_AT_DOB",
        )

    return str(value)


# ============================================================
# FIELD SCHEMAS
# ============================================================

USER_FIELDS = [
    # general
    {
        "section": "general",
        "key": "language",
        "label": "Language",
        "choices": _language_names,
    },
    {
        "section": "general",
        "key": "include_uranus_to_pluto",
        "label": "Include Uranus / Neptune / Pluto",
        "choices": _yes_no_choices,
    },
    {
        "section": "general",
        "key": "use_24hour_format_in_to_dms",
        "label": "Use 24-hour format",
        "choices": _yes_no_choices,
    },

    # location
    {
        "section": "location",
        "key": "database_engine",
        "label": "Place Database Engine",
        "choices": _engine_names,
    },
    {
        "section": "location",
        "key": "check_database_for_world_cities",
        "label": "Check database for world cities",
        "choices": _yes_no_choices,
    },

    # calculation
    {
        "section": "calculation",
        "key": "default_ayanamsa_mode",
        "label": "Default Ayanamsa Mode",
        "choices": _ayanamsa_names,
    },
    {
        "section": "calculation",
        "key": "dhasa_year_duration_default",
        "label": "Dhasa Year Duration",
        "choices": _dhasa_year_duration_names,
    },
    {
        "section": "calculation",
        "key": "savana_year_method_default",
        "label": "Savana Year Method",
        "choices": _savana_year_method_names,
    },
    {
        "section": "calculation",
        "key": "true_lunar_year_method_default",
        "label": "True Lunar Year Method",
        "choices": _true_lunar_year_names,
    },
    {
        "section": "calculation",
        "key": "bhaava_madhya_method",
        "label": "Bhava Madhya Method",
        "choices": _house_method_choices,
    },
    {
        "section": "calculation",
        "key": "tamil_month_method",
        "label": "Tamil Month Method",
        "choices": _tamil_month_method_choices,
    },
    {
        "section": "calculation",
        "key": "use_planet_speed_for_panchangam_end_timings",
        "label": "Use planet speed for Panchangam end timings",
        "choices": _yes_no_choices,
    },

    # charts
    {
        "section": "charts",
        "key": "include_special_and_arudha_lagna_in_charts",
        "label": "Include special & arudha lagna in charts",
        "choices": _yes_no_choices,
    },
    {
        "section": "charts",
        "key": "include_maandhi_in_charts",
        "label": "Include Maandhi in charts",
        "choices": _yes_no_choices,
    },
    {
        "section": "charts",
        "key": "include_charts_only_for_western_type",
        "label": "Include charts only for western type",
        "choices": _yes_no_choices,
    },
]


ADVANCED_FIELDS = [
    # nodes
    {
        "section": "nodes",
        "key": "use_true_nodes_for_rahu_ketu",
        "label": "Use true nodes for Rahu / Ketu",
        "choices": _yes_no_choices,
    },

    # calculation_variants
    {
        "section": "calculation_variants",
        "key": "use_saravali_formula_for_uccha_bala",
        "label": "Use Saravali formula for Uccha Bala",
        "choices": _yes_no_choices,
    },
    {
        "section": "calculation_variants",
        "key": "hora_chart_by_pvr_method",
        "label": "Hora chart by PVR method",
        "choices": _yes_no_choices,
    },
    {
        "section": "calculation_variants",
        "key": "ashtottari_bhukthi_starts_from_dhasa_lord",
        "label": "Ashtottari Bhukthi starts from Dhasa lord",
        "choices": _yes_no_choices,
    },
    {
        "section": "calculation_variants",
        "key": "planet_retrogression_calculation_method",
        "label": "Planet retrogression calculation method",
        "choices": _retrogression_method_choices,
    },

    # tradition_overrides
    {
        "section": "tradition_overrides",
        "key": "force_kali_start_year_for_years_before_kali_year_4009",
        "label": "Force Kali start year before Kali year 4009",
        "choices": _yes_no_choices,
    },
    {
        "section": "tradition_overrides",
        "key": "kali_start_year",
        "label": "Kali start year",
        "choices": lambda: ["1", "13"],
    },
    {
        "section": "tradition_overrides",
        "key": "ritu_per_solar_tamil_month",
        "label": "Ritu per solar Tamil month",
        "choices": _yes_no_choices,
    },
    {
        "section": "tradition_overrides",
        "key": "use_aharghana_for_vaara_calcuation",
        "label": "Use aharghana for vaara calculation",
        "choices": _yes_no_choices,
    },
    {
        "section": "tradition_overrides",
        "key": "use_kp_dictionary_for_lords_calculation",
        "label": "Use KP dictionary for lords calculation",
        "choices": _yes_no_choices,
    },

    # compatibility
    {
        "section": "compatibility",
        "key": "skip_using_girls_varna_for_minimum_tamil_porutham",
        "label": "Skip girl's varna for minimum Tamil porutham",
        "choices": _yes_no_choices,
    },
]


# Keys that should be interpreted as bool when saving
BOOL_KEYS = {
    "include_uranus_to_pluto",
    "use_24hour_format_in_to_dms",
    "check_database_for_world_cities",
    "use_internet_for_location_check",
    "get_place_elevation_from_internet",
    "use_planet_speed_for_panchangam_end_timings",
    "include_special_and_arudha_lagna_in_charts",
    "include_maandhi_in_charts",
    "include_charts_only_for_western_type",
    "use_true_nodes_for_rahu_ketu",
    "use_saravali_formula_for_uccha_bala",
    "hora_chart_by_pvr_method",
    "ashtottari_bhukthi_starts_from_dhasa_lord",
    "force_kali_start_year_for_years_before_kali_year_4009",
    "ritu_per_solar_tamil_month",
    "use_aharghana_for_vaara_calcuation",
    "use_kp_dictionary_for_lords_calculation",
    "skip_using_girls_varna_for_minimum_tamil_porutham",
}


# Keys that should be interpreted as int when saving
INT_KEYS = {
    "tamil_month_method",
    "planet_retrogression_calculation_method",
    "kali_start_year",
}


# Keys that should remain strings in settings file
STRING_KEYS = {
    "language",
    "database_engine",
    "default_ayanamsa_mode",
    "bhaava_madhya_method",
    "dhasa_year_duration_default",
    "savana_year_method_default",
    "true_lunar_year_method_default",
}


# ============================================================
# CONFIG TAB
# ============================================================

class ConfigTab(QWidget):
    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode
        self._field_widgets = {}

        self._build_ui()
        self._load_current_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        fields = USER_FIELDS if self.mode == "user" else ADVANCED_FIELDS

        for field in fields:
            label = QLabel(field["label"])
            combo = QComboBox()
            combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            field_choices = field["choices"]
            choices = field_choices() if callable(field_choices) else field_choices

            _populate_combo(combo, choices)

            form.addRow(label, combo)
            self._field_widgets[(field["section"], field["key"])] = combo

        layout.addLayout(form)
        layout.addStretch(1)

    def _load_current_values(self):
        if self.mode == "user":
            settings = config.get_current_user_settings()
            fields = USER_FIELDS
        else:
            settings = config.get_current_advanced_settings()
            fields = ADVANCED_FIELDS

        for field in fields:
            section = field["section"]
            key = field["key"]
            combo = self._field_widgets[(section, key)]

            value = settings.get(section, {}).get(key)

            if key in BOOL_KEYS:
                value_to_select = _bool_to_text(bool(value))
            else:
                value_to_select = _setting_to_display_text(key, value)

            _safe_set_combo_value(combo, value_to_select)

    def get_settings_dict(self):
        """
        Returns a settings dict in the same shape expected by config.py.

        For normal choices:
            visible text == stored value

        For mapped choices like house methods:
            visible text = label
            stored value = key
        """
        if self.mode == "user":
            base = config.get_current_user_settings()
            fields = USER_FIELDS
        else:
            base = config.get_current_advanced_settings()
            fields = ADVANCED_FIELDS

        for field in fields:
            section = field["section"]
            key = field["key"]
            combo = self._field_widgets[(section, key)]

            raw_value = combo.currentData()
            if raw_value is None:
                raw_value = combo.currentText()

            raw_text = str(raw_value)

            if key in BOOL_KEYS:
                value = _text_to_bool(raw_text)
            elif key in INT_KEYS:
                try:
                    value = int(raw_text)
                except Exception:
                    value = raw_text
            else:
                value = raw_text

            if section not in base:
                base[section] = {}

            base[section][key] = value

        return base


# ============================================================
# MAIN DIALOG
# ============================================================

class ConfigDialog(QDialog):
    """
    mode:
        "user"      -> only User tab
        "advanced"  -> only Advanced tab
        "both"      -> both tabs
    """
    def __init__(self, mode="both", parent=None):
        super().__init__(parent)

        mode = str(mode).strip().lower()
        if mode not in ("user", "advanced", "both"):
            mode = "both"

        self.mode = mode
        self._user_tab = None
        self._advanced_tab = None

        self.setWindowTitle("Configuration")

        self._build_ui()
        self.adjustSize()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        if self.mode in ("user", "both"):
            self._user_tab = ConfigTab("user", self)
            self._tabs.addTab(self._user_tab, "User")

        if self.mode in ("advanced", "both"):
            self._advanced_tab = ConfigTab("advanced", self)
            self._tabs.addTab(self._advanced_tab, "Advanced")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def _on_save(self):
        try:
            if self._user_tab is not None:
                user_settings = self._user_tab.get_settings_dict()
                config.apply_user_settings(user_settings)
                config.save_user_settings(user_settings)

            if self._advanced_tab is not None:
                advanced_settings = self._advanced_tab.get_settings_dict()
                config.apply_advanced_settings(advanced_settings)
                config.save_advanced_settings(advanced_settings)

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration.\n\n{e}",
            )


# ============================================================
# OPTIONAL TEST
# ============================================================

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    try:
        config.load_all_settings()
    except Exception:
        pass

    dlg = ConfigDialog(mode="both")
    dlg.exec()

    sys.exit(0)
