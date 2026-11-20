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
    Vimsottari Dhasa / Bhukthi predictions (B.V. Raman, 'How to Judge a Horoscope').
    UI-independent: used by the PyQt app (horo_chart_tabs.py) and can be used by the web app (prediction_tab.py).

    * Maha Dasa lords, Bhukthi lords and all dates come from dhasa_selector (the same engine as the Dhasa tab,
      default Vimsottari options), so the Prediction and Dhasa tabs always agree.
    * Texts come from dasha_predictions_<lang>.json in const._LANGUAGE_PATH (English used if <lang> is missing):
        - key = Maha Dasa lord's planet number as text (Sun "0" .. Ketu "8");
        - ["predictions"][n] = Maha Dasa text, n = natal Rasi (0 Aries .. 11 Pisces) of the Maha lord;
        - ["bhuktis"][i]     = text of the i-th Bhukthi of that Maha Dasa, in dhasa_selector's order
          (i = 0 is the Maha lord's own Bhukthi, then the Vimsottari sequence).
"""
import html as _html
import json
import os
from jhora import const, utils
from jhora.horoscope.dhasa import dhasa_selector
from jhora.horoscope.chart import charts
drik = utils.hora_engine_proxy

_VIM_SEQ = [0, 1, 2, 7, 4, 6, 3, 8, 5]
_VIM_JSON_KEY = {planet: str(planet) for planet in range(9)}
_DASHA_JSON_PATTERN = 'dasha_predictions_{lang}.json'
_DASHA_JSON_CACHE = {}
_DASHA_JSON_SEARCHED = []
_DEFAULT_CAUTION = ("Please note that these predictions are excerpts from the book 'How to judge Horoscope' of "
                    "B.V. Raman. These are general in nature. The exact nature of the results should be "
                    "interpreted by taking into account, the various dignities and strengths of planets and houses.")
_ENGLISH_RAASI = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius',
                  'Capricorn', 'Aquarius', 'Pisces']

def _res(key, default):
    try:
        val = utils.resource_strings.get(key)
        return val if val else default
    except Exception:
        return default
def vimsottari_title():
    """ 'Vimsottari Dhasa Bhukthi' (localized) """
    return _res('vimsottari_str', 'Vimsottari') + ' ' + _res('dhasa_str', 'Dhasa') + ' ' + _res('bhukthi_str', 'Bhukthi')
def _dasha_json_dirs(extra_dirs=None):
    dirs = []
    lang_path = getattr(const, '_LANGUAGE_PATH', None)
    if isinstance(lang_path, str) and lang_path:
        dirs.append(lang_path)
    if extra_dirs:
        dirs += list(extra_dirs)
    here = os.path.dirname(os.path.abspath(__file__))
    dirs += [here, os.path.join(here, 'lang')]
    seen, out = set(), []
    for d in dirs:
        d = os.path.normpath(d)
        if d not in seen:
            seen.add(d); out.append(d)
    return out
def load_dasha_predictions(language=None, extra_dirs=None):
    """ Dasha prediction JSON (dict) for language (falls back to English), cached per file. {} if not found. """
    lang = str(language or getattr(const, '_DEFAULT_LANGUAGE', 'en') or 'en').strip().lower()
    _DASHA_JSON_SEARCHED.clear()
    for code in dict.fromkeys((lang, 'en')):
        for folder in _dasha_json_dirs(extra_dirs):
            path = os.path.join(folder, _DASHA_JSON_PATTERN.format(lang=code))
            if path in _DASHA_JSON_CACHE:
                return _DASHA_JSON_CACHE[path]
            _DASHA_JSON_SEARCHED.append(path)
            if os.path.isfile(path):
                try:
                    with open(path, encoding='utf-8-sig') as f:
                        _DASHA_JSON_CACHE[path] = json.load(f)
                    return _DASHA_JSON_CACHE[path]
                except Exception as ex:
                    print(f"[dasha_prediction] cannot read {path}: {type(ex).__name__}: {ex}")
    print("[dasha_prediction] dasha_predictions_<lang>.json NOT FOUND. Looked for:\n  " + "\n  ".join(_DASHA_JSON_SEARCHED))
    return {}
def missing_json_note(language=None):
    """ HTML warning when no prediction file could be loaded ('' otherwise). """
    if load_dasha_predictions(language):
        return ''
    tried = '<br>'.join(_html.escape(x) for x in _DASHA_JSON_SEARCHED[:6])
    return ("<div style='color:#b91c1c; margin:6px 0;'><b>Prediction texts not found:</b> "
            f"{_html.escape(_DASHA_JSON_PATTERN.format(lang='en'))} must be placed in the language folder "
            f"(const._LANGUAGE_PATH). Looked in:<br>{tried}</div>")
def _lord_ints(lords):
    if isinstance(lords, (list, tuple)):
        out = []
        for x in lords:
            try:
                if not isinstance(x, bool):
                    out.append(int(x))
            except (TypeError, ValueError):
                pass
        return out
    try:
        return [int(lords)]
    except (TypeError, ValueError):
        return []
def fmt_date(t):
    """ 'YYYY-MM-DD' for a (year, month, day, fractional_hours) tuple ('' if empty) """
    if not t:
        return ''
    return f"{int(t[0]):04d}-{int(t[1]):02d}-{int(t[2]):02d}"
def _sign_name(sign_index):
    try:
        return utils.RAASI_LIST[sign_index]
    except Exception:
        return _ENGLISH_RAASI[sign_index % 12]
def vimsottari_report(dob, tob, place):
    """
        Vimsottari Maha Dasa / Bhukthi periods and the natal Rasi of each Maha lord.
        @param dob: drik.Date ; @param tob: (h, m, s) ; @param place: drik.Place
        @return list (one dict per Maha Dasa, in time order):
            {'lord': planet, 'label': str, 'sign': natal rasi 0..11, 'start': t, 'end': t,
             'bhuktis': [{'label': str, 'start': t, 'end': t, 'index': i}, ...]}
        Raises ValueError when a Maha lord cannot be identified.
    """
    jd = utils.julian_day_number(dob, tob)
    rasi_of = {}
    for entry in charts.rasi_chart(jd, place):
        if isinstance(entry[0], int) and not isinstance(entry[0], bool):
            rasi_of[entry[0]] = int(entry[1][0])
    roots = dhasa_selector.get_dhasa_root_nodes(0, 'vimsottari', dob, tob, place, divisional_chart_factor=1)
    child_kwargs = {'jd_at_dob': jd, 'place': place, 'divisional_chart_factor': 1}
    report = []
    for lords, label, start, end in roots:
        ids = _lord_ints(lords)
        if not ids or ids[0] not in _VIM_JSON_KEY:
            raise ValueError(f"Cannot identify the Vimsottari Maha lord from {lords!r}")
        maha = ids[0]
        rows = dhasa_selector.get_dhasa_children('vimsottari', lords, start, parent_end=end, **child_kwargs) or []
        bhuktis = []
        for i, (b_lords, b_label, b_start, b_end) in enumerate(rows):
            idx = i
            if len(rows) != len(_VIM_SEQ):
                b_ids = _lord_ints(b_lords)
                if b_ids and b_ids[-1] in _VIM_SEQ:
                    idx = (_VIM_SEQ.index(b_ids[-1]) - _VIM_SEQ.index(maha)) % len(_VIM_SEQ)
            bhuktis.append({'label': b_label, 'start': b_start, 'end': b_end, 'index': idx})
        report.append({'lord': maha, 'label': label, 'sign': rasi_of.get(maha, 0), 'start': start,
                       'end': end, 'bhuktis': bhuktis})
    return report
def vimsottari_blocks(report, language=None):
    """ [(kind 'maha'|'bhukthi', heading_html, plain text), ...] for the report """
    data = load_dasha_predictions(language)
    blocks = []
    for maha in report:
        entry = data.get(_VIM_JSON_KEY[maha['lord']]) or {}
        preds, bhuks = entry.get('predictions') or [], entry.get('bhuktis') or []
        sign = maha['sign']
        maha_text = preds[sign] if 0 <= sign < len(preds) else ''
        blocks.append(('maha',
                       f"{_html.escape(str(maha['label']))} {_res('dhasa_str', 'Dhasa')} "
                       f"({fmt_date(maha['start'])} &ndash; {fmt_date(maha['end'])}) &mdash; "
                       f"{_html.escape(str(maha['label']))} / {_html.escape(str(_sign_name(sign)))}",
                       maha_text))
        for b in maha['bhuktis']:
            i = b['index']
            blocks.append(('bhukthi',
                           f"{_html.escape(str(b['label']))} ({fmt_date(b['start'])} &ndash; {fmt_date(b['end'])})",
                           bhuks[i] if 0 <= i < len(bhuks) else ''))
    return blocks
def vimsottari_html(report, language=None):
    """ Report as one HTML string (QTextEdit-friendly: no CSS background/border dependency) """
    if not report:
        return f"<i>{_html.escape(_res('no_results_str', 'No predictions found.'))}</i>"
    caution = _res('general_prediction_caution', _DEFAULT_CAUTION)
    parts = [f"<b><u>{_html.escape(vimsottari_title())}</u></b><br>",
             f"<i>{_html.escape(caution)}</i><br>", missing_json_note(language), "<br>"]
    for kind, heading, text in vimsottari_blocks(report, language):
        if kind == 'maha':
            parts.append(f"<p style='margin-top:12px; color:#15803d;'><b>{heading}</b></p>")
            parts.append(f"<p style='margin-top:2px;'>{_html.escape(text)}</p>")
        else:
            parts.append(f"<p style='margin-left:14px; margin-top:6px;'><b><u>{heading}</u></b></p>")
            parts.append(f"<p style='margin-left:14px; margin-top:2px;'>{_html.escape(text)}</p>")
    return ''.join(parts)
