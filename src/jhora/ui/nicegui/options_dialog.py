#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Options (settings) dialog shared by all pages.

Built from the schema in factory_settings.json (through jhora.config): one tab per configuration
tab, one expansion section per group and one widget per setting (switch, number, select or text).

Public mode (JHORA_PUBLIC=1): the values shown and saved are this browser's own overrides
(web_settings), server-wide settings are hidden and user_settings.json is not written.
Admin mode (default): every setting is shown and Save writes the server baseline.
After Save or Restore Defaults the page is reloaded.
"""
from nicegui import ui
from jhora import config
import web_settings
from engine_sync import calc_lock, apply_current_language, safe_notify, ignore_disconnected_client


def _per_user():
    """Returns True when settings are kept per browser (public mode)."""
    return web_settings.MULTI_USER and not web_settings.ADMIN


def _list_to_text(value):
    """Returns a list as comma-separated text ("" for None)."""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(x) for x in value)
    return "" if value is None else str(value)


def _text_to_list(text, subtype):
    """Converts comma-separated text to a list; items that do not convert are dropped.

    Args:
        text: comma-separated text.
        subtype: 'int_list', 'float_list' or any other value for a list of strings.
    """
    raw_items = [x.strip() for x in str(text).split(",") if x.strip() != ""]
    if subtype == "int_list":
        out = []
        for item in raw_items:
            try: out.append(int(item))
            except Exception: pass
        return out
    if subtype == "float_list":
        out = []
        for item in raw_items:
            try: out.append(float(item))
            except Exception: pass
        return out
    return raw_items


def _create_setting_widget(meta):
    """Creates the widget for one setting.

    Args:
        meta: setting description (type, value/default, choices, description).

    Returns:
        (widget, type_). Choice widgets keep their (stored value, label) pairs in `_normalized_choices`.
    """
    type_ = str(meta.get("type", "string")).strip().lower()
    value = meta.get("value", meta.get("default"))
    description = meta.get("description", "")
    if type_ == "bool":
        widget = ui.switch(value=bool(value))
    elif type_ == "int":
        try: num_value = int(value)
        except Exception: num_value = int(meta.get("default", 0) or 0)
        widget = ui.number(value=num_value, format='%d').props('dense outlined').classes('w-40')
    elif type_ == "float":
        try: num_value = float(value)
        except Exception: num_value = float(meta.get("default", 0.0) or 0.0)
        widget = ui.number(value=num_value, step=0.01).props('dense outlined').classes('w-40')
    elif type_ == "choice":
        choices = meta.get("choices", [])
        normalized = []
        for item in choices:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                normalized.append((item[0], str(item[1])))
            else:
                normalized.append((item, str(item)))
        options = {i: label for i, (_stored, label) in enumerate(normalized)}
        current_idx = 0
        for i, (stored, _label) in enumerate(normalized):
            # Compare the type as well as the value: True == 1 and False == 0 in Python, so bool-valued choices
            # (e.g. Geocentric / Topocentric) would otherwise match the wrong entry.
            if (type(stored) is type(value) and stored == value) or str(stored) == str(value):
                current_idx = i; break
        widget = ui.select(options=options, value=current_idx).props('dense outlined').classes('w-64')
        widget._normalized_choices = normalized
    elif type_ in ("int_list", "float_list", "string_list"):
        widget = ui.input(value=_list_to_text(value), placeholder="Comma-separated values").props('dense outlined').classes('w-64')
    else:
        widget = ui.input(value="" if value is None else str(value)).props('dense outlined').classes('w-64')
    if description:
        widget.tooltip(description)
    return widget, type_


def _read_setting_widget(widget, type_):
    """Returns the setting value held by `widget`, converted according to `type_` (for choices, the
    stored value of the selected entry).
    """
    if type_ == "bool": return bool(widget.value)
    if type_ == "int":
        try: return int(widget.value)
        except Exception: return 0
    if type_ == "float":
        try: return float(widget.value)
        except Exception: return 0.0
    if type_ == "choice":
        idx = widget.value
        normalized = getattr(widget, "_normalized_choices", [])
        if isinstance(idx, int) and 0 <= idx < len(normalized):
            return normalized[idx][0]
        return None
    if type_ in ("int_list", "float_list", "string_list"):
        return _text_to_list(widget.value, type_)
    return widget.value


def _visible_sections(tab_name):
    """Returns the settings of one tab as {section name: [setting, ...]}. In public mode only settings
    a visitor may change are included, with this visitor's value.

    Args:
        tab_name: configuration tab name.
    """
    result = {}
    for section_name, items in config.get_ui_sections(tab=tab_name, visible_only=True).items():
        kept = []
        for item in items:
            key = item['key']
            if _per_user():
                if not web_settings.is_user_setting(key):
                    continue
                item = dict(item)
                item['value'] = web_settings.effective_value(key)
            kept.append(item)
        if kept:
            result[section_name] = kept
    return result


def open_options_dialog(on_saved=None):
    """Opens the Options dialog.

    Args:
        on_saved: accepted for compatibility; not used (the page is reloaded after saving).

    Returns:
        The dialog, or None if there is no schema or no configurable option.
    """
    tabs_all = config.get_ui_tabs()
    if not tabs_all:
        safe_notify('No configuration schema found (factory_settings.json).', type='negative')
        return None
    tab_sections = {t: _visible_sections(t) for t in tabs_all}
    tabs_list = [t for t in tabs_all if tab_sections[t]]
    if not tabs_list:
        safe_notify('No user-configurable options are available.', type='warning')
        return None
    widgets = {}
    shown = {}      # value each widget showed when the dialog opened
    dialog = ui.dialog().props('persistent')
    with dialog, ui.card().classes('w-full max-w-4xl'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('Options').classes('text-xl font-bold')
            ui.button(icon='close', on_click=dialog.close).props('flat round dense')
        if _per_user():
            ui.label('These settings apply to this browser only.').classes('text-xs text-gray-500')
        with ui.tabs().classes('w-full') as qtabs:
            for t in tabs_list:
                ui.tab(t)
        with ui.tab_panels(qtabs, value=tabs_list[0]).classes('w-full'):
            for tab_name in tabs_list:
                with ui.tab_panel(tab_name):
                    with ui.scroll_area().classes('h-[55vh] w-full pr-2'):
                        for section_name, items in tab_sections[tab_name].items():
                            section_title = str(section_name).replace("_", " ").title()
                            with ui.expansion(section_title, value=True).classes('w-full border rounded mb-2'):
                                for item in items:
                                    key = item['key']
                                    with ui.row().classes('w-full items-center justify-between gap-4 py-1'):
                                        lbl = ui.label(item.get('label', key)).classes('flex-1')
                                        if item.get('description'):
                                            lbl.tooltip(item['description'])
                                        widget, type_ = _create_setting_widget(item)
                                    widgets[key] = (widget, type_)
                                    shown[key] = _read_setting_widget(widget, type_)

        @ignore_disconnected_client
        def do_save():
            values = {key: _read_setting_widget(w, t) for key, (w, t) in widgets.items()}
            if _per_user():
                # Store only what the visitor actually changed; everything else keeps following
                # the release's value (see web_settings.py).
                values = {k: v for k, v in values.items() if not web_settings._same(v, shown.get(k))}
            probe = 'planet_position_reference_frame'
            try:
                if _per_user():
                    web_settings.set_user_values(values)      # this browser only
                else:
                    with calc_lock():
                        config.set_values(values, apply=True, save=False)
                        web_settings.rebuild_engine_flags()
                        config.save_all_settings()
                    apply_current_language()
                dialog.close()
                safe_notify('Settings saved. Reloading to apply...', type='positive')
                ui.run_javascript('location.reload()')
            except Exception as e:
                print(f"[options] SAVE FAILED: {e!r}")
                safe_notify(f'Failed to save configuration: {e}', type='negative')

        @ignore_disconnected_client
        def do_restore_defaults():
            if _per_user():
                web_settings.reset_user_values()
            else:
                with calc_lock():
                    config.reset_all(apply=True, save=True)
                    web_settings.rebuild_engine_flags()
                apply_current_language()
            dialog.close()
            safe_notify('Settings restored to defaults. Reloading...', type='info')
            ui.run_javascript('location.reload()')

        with ui.row().classes('w-full justify-end gap-2 mt-2'):
            ui.button('Restore Defaults', on_click=do_restore_defaults).props('flat')
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Save', on_click=do_save).classes('bg-green-600 text-white font-bold')
    dialog.open()
    return dialog
