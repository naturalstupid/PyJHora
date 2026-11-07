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
"""Panchangam page (/): the panchangam for the entered date, time and place, in three columns.
HEADER_FORMAT and KEY_VALUE_FORMAT are the HTML templates for a section heading and a key / value line;
the Vedic Calendar page uses them too.
PRINTING: this page has NO print button of its own anymore - see print_registry.py's own module
docstring for the project-wide reason (ONE global "Save as PDF" button + dialog, app-wide, is now
the ONLY print entry point). This page is registered there (see _build_print_section() below) as a
plain checkbox, Panchangam text ONLY, with NO sub-options.
"Include Charts" (an earlier version of this page's own, now-REMOVED "Include Charts & Save as
PDF" button, which appended a hidden "every varga" chart report to the Panchangam print) is DROPPED
ENTIRELY as a Panchangam-specific concept, per the user's own explicit decision - NOT moved into
this page's own registry entry as a sub-option. If a visitor wants both the Panchangam text and
every varga's chart in one combined PDF, they separately check BOTH this page's own checkbox AND
Kundali's own checkbox (which has its own varga/"all vargas" sub-option) in the SAME dialog - the
dialog's own job of combining whatever is checked into one PDF already achieves the same combined
result without this page needing any chart-related code or sub-option UI of its own at all.
The panchangam columns print by staying side by side (components.py's '.print-cols3') rather than
stacking vertically, matching the on-screen 3-column layout - see components.py's module docstring
for why this differs from the earlier, failed "auto-balance one flow into N columns" print attempts,
and what is still not confirmed about it for very long panchangam content spanning many pages.
Reuses _panchangam_locked() and _split_panchangam_into_columns(), the SAME functions this page's own
compute_and_display() calls, for its print_registry.py registration.
"""
from nicegui import ui, run
from jhora import const, utils
from jhora.panchanga import info
drik = utils.hora_engine_proxy
from components import (
    navigation_header, render_control_bar, ensure_default_state, calc_lock,
    res_str, safe_notify, ignore_disconnected_client, DelayedBusyIndicator, render_footer,
    run_io_bound_ctx,
)
# chart_render / chart_details / print_button / trigger_print_js imports REMOVED - this page no
# longer builds its own "every varga" chart report or has its own print button at all (see the
# "Include Charts" removal note inside panchangam_page() below for the full reasoning).
import print_registry
_KEY_COLOR = 'brown'; _VALUE_COLOR = 'blue'; _HEADER_COLOR = 'green'
HEADER_FORMAT = '<b><span style="color:' + _HEADER_COLOR + ';">{}</span></b><br>'
KEY_VALUE_FORMAT = '<span style="color:' + _KEY_COLOR + ';">{}  </span><span style="color:' + _VALUE_COLOR + ';">{}</span><br>'
def _panchangam_locked(dob, tob, place_val, lat_val, lon_val, tz_val):
    """Computes the panchangam resources for one date/time/place under calc_lock().
    This is the slow part of the Panchangam page's compute_and_display(); pulled out to a plain,
    blocking function so it can run in a worker thread via components.DelayedBusyIndicator.run() while
    a non-intrusive "please wait" message is shown only if it takes more than a moment.
    """
    with calc_lock():
        jd = utils.julian_day_number(dob, tob)
        place_obj = drik.Place(place_val, lat_val, lon_val, tz_val, 0.0)
        return info.get_panchangam_resources(jd, place_obj, ayanamsa_mode=const._DEFAULT_AYANAMSA_MODE)
def _split_panchangam_into_columns(results_dict, column_count=3):
    """Splits a panchangam results dict into `column_count` roughly-equal HTML chunks, using the
    SAME HEADER_FORMAT/KEY_VALUE_FORMAT templates the page's own compute_and_display() uses -
    extracted to module level so BOTH that function and print_registry.py's headless
    _build_print_section() below use the SAME split logic.
    """
    sep_str = '<br>'
    info_str = ''.join([
        HEADER_FORMAT.format(k) if v.strip() == '' else KEY_VALUE_FORMAT.format(k, v)
        for k, v in results_dict.items()
    ])
    info_list = [ele for ele in info_str.split(sep_str) if ele.strip() != '']
    info_len = int(len(info_list) / column_count)
    columns = []
    for c in range(column_count):
        start = c * info_len
        end = None if c == column_count - 1 else (c + 1) * info_len
        columns.append(sep_str.join(info_list[start:end]))
    return columns
@ui.page('/')
def panchangam_page():
    """Panchangam page (/): the panchangam for the entered date, time and place, in three columns."""
    navigation_header()
    state = ensure_default_state()
    _panch_str = res_str('panchangam_str',"Panchangam")
    with ui.column().classes('w-full p-2 gap-1'):
        with ui.row().classes('w-full items-center justify-between no-print'):
            ui.label(_panch_str).classes('text-xl font-bold text-green-700')
            # Both print_button() AND the former "Include Charts & Save as PDF" button are REMOVED -
            # printing is now exclusively via the ONE global "Save as PDF" button (print_registry.py).
            # Per the user's own explicit decision, "Include Charts" is DROPPED ENTIRELY as a
            # Panchangam-specific concept (not just moved) - if a visitor wants charts too, they
            # separately check Kundali's own checkbox in the global dialog (with ITS own varga/"all
            # vargas" sub-option); the global dialog's own job of combining whatever is checked into
            # one PDF already achieves the same combined result without Panchangam needing to know
            # about charts at all. This page is still registered with print_registry.py (see
            # _build_print_section() below) for its own Panchangam text - see that function's own
            # docstring for confirmation this registration is text-only, with no chart report.
        @ignore_disconnected_client
        async def compute_and_display():
            """Reads the control bar, computes the panchangam in a worker thread (showing a non-intrusive
            "please wait" message via DelayedBusyIndicator only if it takes more than a moment) and
            fills the three columns."""
            try:
                dob_val = w['dob_input'].value.strip()
                tob_val = w['tob_input'].value.strip()
                place_val = w['place_select'].value.strip() if w['place_select'].value else 'Chennai'
                lat_val = float(w['lat_input'].value.strip())
                lon_val = float(w['lon_input'].value.strip())
                tz_val = float(w['tz_input'].value.strip())
                year, month, day = dob_val.split(",")
                dob = (int(year), int(month), int(day))
                tob = tuple([int(x) for x in tob_val.split(':')])
            except Exception as e:
                safe_notify(f'Error computing Panchangam: {str(e)}', type='negative')
                return
            try:
                results_dict = await busy.run(_panchangam_locked, dob, tob, place_val, lat_val, lon_val, tz_val,
                                              wait_text=res_str('computing_str', 'Computing... please wait.'))
            except Exception as e:
                safe_notify(f'Error computing Panchangam: {str(e)}', type='negative')
                return
            if results_dict is DelayedBusyIndicator.STOPPED:
                return  # Stop (or a newer call) superseded this one; discard the stale result quietly
            try:
                c1, c2, c3 = _split_panchangam_into_columns(results_dict, 3)
                info_html_1.set_content(c1)
                info_html_2.set_content(c2)
                info_html_3.set_content(c3)
            except Exception as e:
                safe_notify(f'Error computing Panchangam: {str(e)}', type='negative')
        w = render_control_bar(show_dob_tob=True, on_options_saved=lambda: compute_and_display(),
                                on_calculate=compute_and_display)
        ui.separator()
        busy = DelayedBusyIndicator(buttons=[w.get('calculate_button')], stop_label=res_str('stop_str', 'Stop'))
        # print-cols3 (see components.py's _PRINT_CSS and its module docstring): on screen this stays
        # the original 3-column side-by-side row; for print it becomes a CSS Grid with the same 3
        # equal columns, each card allowed to break across as many pages as it needs
        # (break-inside: auto, overriding the general '.q-card { break-inside: avoid }' rule). Unlike
        # the two earlier, failed multi-column print attempts (which asked the browser to
        # auto-balance ONE flow into columns), these 3 columns are already separate content (split by
        # Python just above, not by CSS) - see the module docstring for what is and is not yet
        # confirmed about this across multiple pages.
        # 'single-chart-print-block' (added here): this page's own normal on-screen content must be
        # HIDDEN during the global "Save as PDF" combined print (body.printing-all - see
        # components.py's _PRINT_CSS) - otherwise it prints ALONGSIDE the Panchangam section
        # print_registry.py's own _build_print_section() builds fresh into the hidden
        # '.all-charts-report' container below, producing a duplicate Panchangam (once from this
        # live, on-page content - first page, since it sits earlier in the DOM - and once from the
        # registry's own built copy - last page, since it is appended later). This mirrors
        # kundali_chart.py's / dhasa_tab.py's own identical fix for the same combined-print
        # duplication risk. (An EARLIER, now-removed version of this page had its own separate
        # "Include Charts & Save as PDF" button and deliberately left this class OFF so its own
        # on-page content would print together with ITS OWN combined report - that feature is gone
        # now that Panchangam prints exclusively via the global dialog, so that reasoning no longer
        # applies and left this class missing by oversight.)
        with ui.row().classes('w-full justify-between items-start gap-4 flex-nowrap overflow-x-auto print-cols3 single-chart-print-block'):
            with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow print-expand print-compact-text'):
                info_html_1 = ui.html('')
            with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow print-expand print-compact-text'):
                info_html_2 = ui.html('')
            with ui.card().classes('flex-1 min-h-[300px] p-4 bg-gray-50 shadow print-expand print-compact-text'):
                info_html_3 = ui.html('')
        # The former hidden "every varga" chart report + _build_combined_report() are REMOVED
        # entirely - see this page's own "Include Charts" removal note above for why (that concept
        # is dropped, not moved - charts now come from Kundali's own checkbox in the global dialog).
        ui.timer(0.1, compute_and_display, once=True)
    render_footer()
async def _build_print_section(container, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_values):
    """HEADLESS build function for print_registry.py's central "Save as PDF" dialog - see that
    module's own docstring for the full contract. Prints the Panchangam text ONLY - no sub-options
    at all (sub_option_values is always {} here - this entry was registered with no sub_option_ui).
    "Include Charts" is NOT part of this registration at all - see the module docstring for why
    that is dropped entirely rather than reimplemented here (a visitor wanting both checks Kundali's
    OWN checkbox separately in the same dialog). Reuses _panchangam_locked() and
    _split_panchangam_into_columns(), the SAME functions this page's own compute_and_display() calls.
    """
    try:
        #results_dict = await run.io_bound(_panchangam_locked, dob, tob, place_val, lat_val, lon_val, tz_val)
        results_dict = await run_io_bound_ctx(_panchangam_locked, dob, tob, place_val, lat_val, lon_val, tz_val)
    except Exception as e:
        with container:
            ui.html(f"<i>Error computing Panchangam: {e}</i>")
        return
    c1, c2, c3 = _split_panchangam_into_columns(results_dict, 3)
    with container:
        ui.label(res_str('panchangam_str', 'Panchangam')).classes('text-base font-bold text-green-700 print-attach-next')
        with ui.row().classes('w-full justify-between items-start gap-4 flex-nowrap print-cols3'):
            with ui.card().classes('flex-1 p-2 bg-gray-50 shadow print-expand print-compact-text'):
                ui.html(c1)
            with ui.card().classes('flex-1 p-2 bg-gray-50 shadow print-expand print-compact-text'):
                ui.html(c2)
            with ui.card().classes('flex-1 p-2 bg-gray-50 shadow print-expand print-compact-text'):
                ui.html(c3)
print_registry.register('panchangam', res_str('panchangam_str', 'Panchangam'), 'Panchangam', _build_print_section)
