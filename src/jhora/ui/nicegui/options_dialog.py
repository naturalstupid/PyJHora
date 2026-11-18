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
from nicegui import ui, run
import contextvars
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


# ==== page-title quick settings (added by fix_options_dialog.py) ====
HEADER_KEYS = ("astrology_engine", "default_ayanamsa_mode", "language")   # shown next to the page title, in order

# setting key -> (NLS key of the label, fallback label text, combo width)
_HEADER_META = {
    "astrology_engine":      ("calculation_type_str", "Calculation Type:", "w-48"),
    "default_ayanamsa_mode": ("ayanamsam_str",        "Ayanamsam:",        "w-40"),
    "language":              ("language_tooltip_str",         "Language:",         "w-36"),
}

# astrology_engine stored value -> NLS key of its display name
_CALC_METHOD_NLS = {
    1: "drik_panchang_str", 2: "ss_panchang_str", 3: "kk_panchang_str", 4: "gl_panchang_str",
    5: "ts_panchang_str",   6: "vp_panchang_str", 7: "ms_panchang_str", 8: "vs_panchang_str",
    9: "st_panchang_str",
}


def _res(key, fallback):
    """Returns the language resource string for `key`, or `fallback` if it is not available."""
    try:
        from jhora import utils as _jutils
        return _jutils.resource_strings.get(key, fallback)
    except Exception:
        return fallback


# The Options dialog no longer shows the three settings that are edited next to the page title.
_visible_sections_all = _visible_sections


def _visible_sections(tab_name, include_header=False):
    """Same as the original _visible_sections(), but leaves out HEADER_KEYS unless include_header is True."""
    result = _visible_sections_all(tab_name)
    if include_header:
        return result
    out = {}
    for section_name, items in result.items():
        kept = [it for it in items if it.get('key') not in HEADER_KEYS]
        if kept:
            out[section_name] = kept
    return out


def _header_items():
    """Returns the schema items of HEADER_KEYS (with this visitor's values), in HEADER_KEYS order."""
    found = {}
    for tab_name in config.get_ui_tabs():
        for items in _visible_sections(tab_name, include_header=True).values():
            for item in items:
                if item.get('key') in HEADER_KEYS:
                    found[item['key']] = item
    missing = [k for k in HEADER_KEYS if k not in found]
    if missing:
        print(f"[options] page-title settings not found in the schema: {missing}")
    return [found[k] for k in HEADER_KEYS if k in found]


def _commit(values):
    """Stores `values` ({key: value}) the same way the Options dialog's Save does (no reload)."""
    if _per_user():
        web_settings.set_user_values(values)          # this browser only
    else:
        with calc_lock():
            config.set_values(values, apply=True, save=False)
            web_settings.rebuild_engine_flags()
            config.save_all_settings()
        apply_current_language()


def _same_value(a, b):
    try:
        return web_settings._same(a, b)
    except Exception:
        return a == b


# ---- "Please wait" overlay + Calculate highlight for the page-title combos ----
_CALC_MARKERS = {}      # NiceGUI client id -> mark_dirty() of this page's Calculate button (calc_highlight)
_HEADER_WIDGETS = {}    # NiceGUI client id -> the page-title combos of that page

# Shown by the BROWSER as soon as an entry of a page-title combo is clicked, before the server answers
# (on a slow server the answer can take seconds). The server removes it again (_WAIT_HIDE_JS), or the page
# reload does.
_WAIT_HEAD_HTML = """
<script>
(function () {
  if (window.__sjWaitInstalled) { return; }
  window.__sjWaitInstalled = true;
  window.sjShowWait = function (msg) {
    if (document.getElementById('sj-wait')) { return; }
    var d = document.createElement('div');
    d.id = 'sj-wait';
    d.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(255,255,255,.55);' +
                      'display:flex;align-items:center;justify-content:center;cursor:wait';
    var b = document.createElement('div');
    b.style.cssText = 'background:#fff;border:2px solid #2e7d32;border-radius:8px;padding:14px 24px;' +
                      'font:bold 15px sans-serif;color:#2e7d32;box-shadow:0 2px 12px rgba(0,0,0,.25)';
    b.textContent = msg || 'Please wait...';
    d.appendChild(b);
    document.body.appendChild(d);
  };
  window.sjHideWait = function () { var e = document.getElementById('sj-wait'); if (e) { e.remove(); } };
  document.addEventListener('click', function (ev) {
    var item = ev.target.closest && ev.target.closest('.sj-hdr-pop .q-item');
    if (item && !item.classList.contains('q-item--active') && item.getAttribute('aria-selected') !== 'true') {
      window.sjShowWait(window.__sjWaitText);
    }
  }, true);
})();
</script>
"""
_WAIT_HIDE_JS = 'window.sjHideWait && window.sjHideWait()'


def _client_id():
    try:
        return ui.context.client.id
    except Exception:
        return None


def register_calculate_marker(mark_dirty):
    """Called by components.render_control_bar() with calc_highlight's mark_dirty() of the page's Calculate
    button. A change of Calculation Type / Ayanamsam then highlights Calculate (as an edited birth detail
    does) instead of reloading the page."""
    cid = _client_id()
    if cid is None or mark_dirty is None:
        return
    _CALC_MARKERS[cid] = mark_dirty
    try:
        ui.context.client.on_disconnect(lambda: (_CALC_MARKERS.pop(cid, None), _HEADER_WIDGETS.pop(cid, None)))
    except Exception:
        pass


def _set_header_enabled(cid, enabled):
    for w in _HEADER_WIDGETS.get(cid, []):
        try:
            w.enable() if enabled else w.disable()
        except Exception:
            pass


def _store_global(values):
    """Server-wide part of _commit() (admin mode). Runs in a worker thread: calc_lock() can wait for a
    running calculation, and blocking the event loop that long makes the browser show "Connection lost"."""
    with calc_lock():
        config.set_values(values, apply=True, save=False)
        web_settings.rebuild_engine_flags()
        config.save_all_settings()


def _wire_header_widget(widget, key, type_):
    """Stores the setting when the visitor changes a page-title combo.
    Calculation Type / Ayanamsam: no reload - the Calculate button is highlighted (results on screen are
    out of date). Language, or a page without a Calculate button: the page is reloaded.
    A "Please wait..." overlay covers the page meanwhile (drawn at once by the browser)."""
    holder = {'shown': _read_setting_widget(widget, type_)}
    cid = _client_id()
    if cid is not None:
        _HEADER_WIDGETS.setdefault(cid, []).append(widget)

    async def _changed(_e=None):
        try:
            new_value = _read_setting_widget(widget, type_)
            if _same_value(new_value, holder['shown']):
                ui.run_javascript(_WAIT_HIDE_JS)
                return
            ui.run_javascript(f'window.sjShowWait && window.sjShowWait(window.__sjWaitText)')
            _set_header_enabled(cid, False)
            try:
                if _per_user():
                    web_settings.set_user_values({key: new_value})      # this browser only (fast)
                else:
                    ctx = contextvars.copy_context()
                    await run.io_bound(ctx.run, _store_global, {key: new_value})
                    apply_current_language()
                holder['shown'] = new_value
            except Exception as e:
                print(f"[options] page-title setting save failed for {key}: {e!r}")
                ui.run_javascript(_WAIT_HIDE_JS)
                _set_header_enabled(cid, True)
                safe_notify(f'Failed to save setting: {e}', type='negative')
                return
            mark_dirty = _CALC_MARKERS.get(cid)
            if key == 'language' or mark_dirty is None:
                ui.run_javascript('location.reload()')       # overlay stays until the new page is shown
                return
            mark_dirty()
            ui.run_javascript(_WAIT_HIDE_JS)
            _set_header_enabled(cid, True)
        except RuntimeError:        # the browser went away meanwhile (disconnected client)
            pass

    widget.on_value_change(_changed)


def render_header_settings():
    """Draws Calculation Type / Ayanamsam / Language (a label and a combo each) in one row. Called by
    components.render_page_title(), so the three controls sit next to the page title on every page.
    Returns the row, or None if none of the three settings exists.
    """
    items = _header_items()
    if not items:
        return None
    ui.add_head_html(_WAIT_HEAD_HTML)
    _wait = str(_res('please_wait_str', 'Please wait...')).replace('\\', '').replace("'", "\\'")
    ui.add_head_html(f"<script>window.__sjWaitText = '{_wait}';</script>")
    ui.add_css(
        '.hdr-sel .q-field__control, .hdr-sel .q-field__marginal { height: 30px; min-height: 30px; }'
        '.hdr-sel .q-field__native { min-height: 30px; padding-top: 0; padding-bottom: 0; font-size: 13px; }'
    )
    with ui.row().classes('items-center gap-x-4 gap-y-1 flex-wrap no-print') as row:
        for item in items:
            key = item['key']
            nls_key, fallback, width = _HEADER_META[key]
            label_text = str(_res(nls_key, fallback)).strip()
            if not label_text.endswith(':'):
                label_text += ':'
            with ui.row().classes('items-center gap-1 flex-nowrap'):
                ui.label(label_text).classes('text-sm text-gray-700 whitespace-nowrap')
                widget, type_ = _create_setting_widget(item)
                widget.props('options-dense popup-content-class=sj-hdr-pop')
                widget.classes(remove='w-64', add=f'hdr-sel {width}')
                if key == "language": # each language in its own script (const.available_languages_native)
                    try:
                        from jhora import const as _jconst
                        widget.set_options({
                            i: _jconst.language_native_name(stored)
                            for i, (stored, _label) in enumerate(widget._normalized_choices)
                        })
                    except Exception as e:
                        print(f"[options] native language names not applied: {e!r}")
                if key == "astrology_engine":      # NLS names: Drik, Vakya Panchanga, ...
                    try:
                        widget.set_options({
                            i: str(_res(_CALC_METHOD_NLS.get(stored), label)).strip()
                            for i, (stored, label) in enumerate(widget._normalized_choices)
                        })
                    except Exception as e:
                        print(f"[options] calculation type names not applied: {e!r}")
                _wire_header_widget(widget, key, type_)
    return row
