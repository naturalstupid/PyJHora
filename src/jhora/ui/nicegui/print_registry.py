#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Central "Save as PDF" feature: THE ONLY WAY to print anything in this app. Every page's own,
separate print button has been REMOVED (see each page's own file for the specific buttons/dialogs
that used to live there) - this module's single global button + dialog is the ONLY print entry
point, app-wide, per the user's own explicit final requirement (confirmed after an earlier version
of this feature mistakenly left every page's own button in place alongside this one - that was a
real gap against the agreed plan, corrected here).

WHY THIS NEEDS A "HEADLESS" BUILD FUNCTION PER PAGE (not just "call that page's own print_button()")
------------------------------------------------------------------------------------------------
Every page in this app is a separate NiceGUI @ui.page() route. A visitor sitting on, say, the
Kundali page has NO live UI state from Dhasa, Panchangam, etc. - those pages' own widgets and
in-memory closures simply do not exist until that page is actually visited. So this one global
dialog - which lets a visitor check off several DIFFERENT pages and print them all together in one
PDF - cannot work by "triggering each page's own print button" one after another; it needs each
registered page to supply a plain, HEADLESS build function instead: given the visitor's birth
details (and, optionally, this page's own sub-option values, e.g. which varga to use), it draws its
own print content directly into a container THIS module provides - reusing the exact same
`_..._locked()` calculation function that page already has for its own on-page "please wait"
worker-thread pattern. No live widget of that page is ever read.

HOW A PAGE REGISTERS ITSELF
----------------------------
Call `register(key, label, category, build, sub_option_ui=None)` ONCE, at MODULE level (i.e.
directly inside the page's .py file, OUTSIDE its own `@ui.page(...)` function).
  key: short, unique string (e.g. 'yoga', 'dosha', 'dhasa', 'kundali').
  label: plain, human-readable string shown as this entry's checkbox label in the dialog.
  category: a plain grouping string shown as a sub-heading above this entry in the dialog (e.g.
      'Charts', 'Calculations', 'Strength', 'Dhasa', 'Yoga / Dosha / Prediction', 'Compatibility') -
      purely cosmetic, has no effect on behavior.
  build: an async callable with this exact signature:
      async def build(container, dob, tob, place, lat, lon, tz, sub_option_values):
          ...draws this page's own print content directly into `container` (a NiceGUI element the
          dialog provides) using `with container: ...`.
      Args passed to build():
          container: the NiceGUI element to draw into (already placed inside the hidden
              combined-report container this module manages).
          dob: (year, month, day) tuple. tob: (hour, minute, second) tuple.
          place, lat, lon, tz: place name (string) and float latitude/longitude/timezone-offset.
          sub_option_values: a PLAIN DICT of whatever this entry's OWN sub_option_ui collected (see
              below) - {} if this entry has no sub_option_ui at all. A page with a custom UI reads
              whatever keys ITS OWN sub_option_ui function chose to put in this dict (the dict's
              shape is entirely up to that page - this module does not interpret it).
      If `build` needs to do its own slow calculation, it should reuse that page's existing
      `_..._locked()` function, run via `nicegui.run.io_bound()` (the SAME pattern
      components.DelayedBusyIndicator already uses).
  sub_option_ui: optional callable with this exact signature:
      def sub_option_ui() -> dict_of_nicegui_widgets:
          ...draws this entry's OWN custom widgets (checkboxes, radios, selects - whatever this
          page needs) directly into whatever NiceGUI container is CURRENTLY OPEN (i.e. just use
          plain `ui.xxx(...)` calls - the dialog already has a `with` block open around the right
          spot when it calls this). Returns a dict of {name: widget} for whatever widgets were
          drawn, so the dialog can later read each widget's own `.value` when building the combined
          report (see _collect_sub_option_values() below - this module does the generic ".value"
          reading FOR every page, so no page needs to hand-write that part itself).
      Called ONLY once this entry's own checkbox is CHECKED (and redrawn fresh every time it is
      checked again) - exactly matching the Dhasa "Print Multiple Dhasas" dialog's own old behavior,
      where ITS sub-options only appeared once its own checkbox/radio state was set. Pass None (the
      default) for a page with nothing to configure (a plain checkbox, no extra UI at all) - most
      of the 18 "simple" pages (Calculate/Strength/Yoga/Dosha/Prediction/Compatibility/Panchangam)
      use this, since they have no sub_option_ui need (see each of those files' own registration
      call for confirmation) - only Dhasa and Kundali currently define a real sub_option_ui (see
      those two files' own registration calls).

HOW THE DIALOG ITSELF WORKS
-----------------------------
render_global_print_button() draws ONE button plus a normally-hidden container
(`.all-charts-report`, reusing the EXACT SAME CSS class/convention kundali_chart.py's/
panchangam_tab.py's/dhasa_tab.py's own (now-removed) multi-page reports already used). Call this
function ONCE per page - see components.py's navigation_header() for where this is wired in (the
ONE central edit that gives every page the button "for free", instead of each page file needing its
own call).

Clicking the button opens open_global_print_dialog(): a plain list of every registered entry, each
with a checkbox. If that entry has a sub_option_ui, checking its checkbox reveals that entry's own
custom widgets directly below it (built fresh each time via sub_option_ui() - see
_CustomUIHolder._rebuild() below), exactly as Dhasa's own old "Print Multiple Dhasas" dialog did.
Birth details are read from the SAME shared, per-browser state every page already reads via
components.ensure_default_state() (app.storage.user-backed, survives reconnects) - the dialog does
NOT ask the visitor to re-enter them.

On "Generate & Print": for every CHECKED entry, in registration order, this module first collects
that entry's OWN sub_option_values (by reading `.value` off every widget its own sub_option_ui()
returned - see _collect_sub_option_values()), then awaits its own build() in turn (sequentially, not
in parallel, to keep worker-thread usage predictable and errors easy to attribute to a specific
entry), each wrapped in its own `.print-report-page` + (for every entry after the first) a
`.print-report-page-break` - so each selected PAGE starts on its own fresh page, while whatever
INTERNAL pagination that page's own build() wants is left completely alone.

A build() that raises is reported via safe_notify() and SKIPPED (not fatal to the whole combined
report).
"""
import asyncio
from nicegui import ui, run
from components import ensure_default_state, res_str, safe_notify, trigger_print_js, _footer_inner_html
_REGISTRY = {}
# Explicit display order for the dialog - matches the app's own nav-bar tab order top to bottom,
# left to right (Panchangam -> Charts dropdown -> Dhasa -> Calculations dropdown -> Strength
# dropdown -> Yoga/Dosha/Prediction dropdown -> Compatibility), per the user's own explicit
# requirement. A category/key NOT listed here still appears (at the END of its category, or as a
# trailing category after all of these, in plain registration order) rather than being silently
# hidden - this is a deliberate safety net for a page registered in the future whose key is not yet
# added to either list below; see _ordered_categories()/_ordered_keys_in_category() for exactly how
# that fallback works.
_CATEGORY_ORDER = [
    'Panchangam', 'Charts', 'Dhasa', 'Calculations', 'Strength',
    'Yoga / Dosha / Prediction', 'Compatibility',
]
_KEY_ORDER_WITHIN_CATEGORY = {
    # Matches the "Charts" dropdown's own on-screen order (Kundali, Bhava, Chakra, Transit) - only
    # 'kundali' is actually registered as of this writing; 'bhava'/'chakra'/'transit' are listed
    # here PRE-EMPTIVELY so they slot into the correct position automatically, the moment any of
    # them is registered later, with NO further edit needed here.
    'Charts': ['kundali', 'bhava', 'chakra', 'transit'],
    # Matches the "Calculations" dropdown's own on-screen order, EXCLUDING Vratha (explicitly out
    # of scope for printing, per the user's own earlier decision) - 'drishti' is listed here
    # PRE-EMPTIVELY (see the note above for 'bhava') since it is NOT YET actually registered as of
    # this writing - see this module's own session notes for this gap.
    'Calculations': [
        'amsa_ruler', 'sphuta', 'saham', 'drishti', 'arudha', 'ashtakavarga', 'argala',
        'shodhaya_pinda', 'kpinfo',
    ],
    # Matches the "Strength" dropdown's own on-screen order (Vimsopaka Bala down to Bhava Bala).
    'Strength': ['vimsopaka_bala', 'vaiseshikamsa_bala', 'other_bala', 'shad_bala', 'bhava_bala'],
    # Matches the "Yoga / Dosha / Prediction" dropdown's own on-screen order.
    'Yoga / Dosha / Prediction': ['yoga', 'dosha', 'prediction'],
}
def _ordered_categories(categories_present):
    """Returns the categories actually present in the registry, in _CATEGORY_ORDER's own order,
    followed by any category NOT listed there (in whatever order Python's dict first saw it in) -
    see the module-level comment above _CATEGORY_ORDER for why an unlisted category is still shown
    rather than silently dropped.
    """
    ordered = [c for c in _CATEGORY_ORDER if c in categories_present]
    ordered += [c for c in categories_present if c not in _CATEGORY_ORDER]
    return ordered
def _ordered_keys_in_category(category, keys_present):
    """Returns the keys of one category, in _KEY_ORDER_WITHIN_CATEGORY's own order for that
    category (if any is defined), followed by any key NOT listed there - same "never silently
    drop" fallback as _ordered_categories().
    """
    explicit = _KEY_ORDER_WITHIN_CATEGORY.get(category, [])
    ordered = [k for k in explicit if k in keys_present]
    ordered += [k for k in keys_present if k not in explicit]
    return ordered
def register(key, label, category, build, sub_option_ui=None):
    """Registers one printable page's entry for the central "Save as PDF" dialog. Call this ONCE, at
    MODULE level in that page's own .py file (see this module's own docstring for the full
    contract). Calling it again with the same `key` simply overwrites the previous entry.
    """
    _REGISTRY[key] = {
        'label': label, 'category': category, 'build': build, 'sub_option_ui': sub_option_ui,
    }
def _parse_tob(tob_str, fallback=(12, 0, 0)):
    """Parses a time string 'H:M' or 'H:M:S' into an (hour, minute, second) tuple; `fallback` (default
    noon) if the text cannot be parsed. Kept as a small, self-contained copy here (every page file
    already has its own near-identical helper) rather than importing one from any single page, since
    this module must not depend on any ONE page's own file.
    """
    try:
        parts = [int(x) for x in str(tob_str).strip().split(':')]
        if len(parts) == 2:
            parts.append(0)
        if len(parts) != 3:
            raise ValueError
        return tuple(parts)
    except Exception:
        return fallback
def render_global_print_button():
    """Draws ONLY the one global "Save as PDF" button (not the combined-report container - see
    ensure_combined_report_container() for that, which MUST be called outside of any 'no-print'
    ancestor). Call this ONCE per page - see components.py's render_control_bar() (row1's last
    button, alongside Settings/Calculate) for where this is wired in. (Originally lived in
    navigation_header(), in its own full-width row above the green nav bar - moved per the user's
    own explicit request, since that dedicated row wasted page height; it now sits on the light
    page background instead of the green header, hence the restyle below away from white-on-white.)
    """
    ui.button(res_str('save_pdf_str', 'Save as PDF'),
              on_click=lambda: open_global_print_dialog()) \
        .props('outlined dense').classes('text-green-700 border-green-700 px-3 shrink-0 no-print')
def ensure_combined_report_container():
    """Creates the (normally hidden) combined-report container that open_global_print_dialog()'s
    build logic fills in. Call this ONCE per page, OUTSIDE of row1's own 'no-print' column (see
    components.py's render_control_bar(), right after that column closes) - NOT nested inside any
    'no-print' ancestor. This matters because '.no-print { display: none !important; }' removes
    that ancestor (and therefore this whole container, wherever it is nested inside it) from
    rendering entirely; a descendant's own 'body.printing-all .all-charts-report { display: block
    !important; }' rule (see components.py's _PRINT_CSS) cannot undo an ancestor's display:none -
    there is no CSS mechanism for a child to override that. Nesting this container inside row1's
    'no-print' wrapper (alongside the button above) would silently break every combined PDF on this
    page: the dialog would still open and "build" the report into this container, but the container
    itself would never actually appear in the printed output.
    """
    global _combined_report_container
    _combined_report_container = ui.column().classes('all-charts-report w-full gap-0')
_combined_report_container = None
class _CustomUIHolder:
    """Holds ONE registered entry's own custom sub_option_ui() widgets, rebuilding them fresh each
    time that entry's checkbox is checked/unchecked - mirrors Dhasa's own old "Print Multiple
    Dhasas" dialog, whose sub-options only existed while relevant and were rebuilt on every open.
    """
    def __init__(self, container, sub_option_ui_fn):
        self._container = container
        self._sub_option_ui_fn = sub_option_ui_fn
        self.widgets = {}
    def rebuild_if_checked(self, checked):
        self._container.clear()
        self.widgets = {}
        if checked and self._sub_option_ui_fn is not None:
            with self._container:
                self.widgets = self._sub_option_ui_fn() or {}
def _collect_sub_option_values(widgets):
    """Returns {name: widget.value} for every widget in `widgets` (a _CustomUIHolder's own
    .widgets dict) - the generic ".value" reading every registered page's build() receives as its
    own sub_option_values dict, so no page needs to hand-write this part itself.
    """
    return {name: getattr(widget, 'value', None) for name, widget in widgets.items()}
def open_global_print_dialog():
    """Opens the central "Save as PDF" dialog: one checkbox per registered page (grouped by
    category). If that entry has its own sub_option_ui, checking its checkbox reveals that entry's
    own custom widgets directly below it. "Generate & Print" builds the combined hidden report and
    prints it - see this module's own docstring for the full behavior.
    """
    state = ensure_default_state()
    categories = {}
    for key, entry in _REGISTRY.items():
        categories.setdefault(entry['category'], []).append(key)
    # Both the category list itself AND each category's own list of keys are reordered to match
    # the app's nav-bar tab order - see _CATEGORY_ORDER / _KEY_ORDER_WITHIN_CATEGORY above for the
    # full reasoning (including the "never silently drop an unlisted entry" safety net).
    categories = {c: _ordered_keys_in_category(c, categories[c]) for c in _ordered_categories(categories.keys())}
    checkboxes = {}
    custom_ui_holders = {}
    # 'no-print' on the dialog's own card: a hard safety net - see the comment just above
    # `dialog.close()` further below for the actual root cause/fix (a timing issue, not a missing
    # CSS class) this is paired with. Even if the timing fix below is ever bypassed or insufficient
    # on some browser, this still guarantees the dialog can never end up baked into a printed PDF.
    # 'transition-show="none" transition-hide="none"' (ADDED): Quasar's DEFAULT dialog
    # show/hide uses an animated fade (~300ms) for both the dialog card AND its backdrop (the
    # semi-transparent grey overlay covering the rest of the page). Disabling that transition
    # means dialog.close() removes the dialog AND its backdrop from the DOM essentially
    # instantly, rather than leaving the backdrop to fade out over the next ~300ms - removing
    # the ENTIRE category of "something is still fading when we print" risk at its source,
    # rather than only papering over it with a guessed delay afterwards (see the next comment).
    with ui.dialog() as dialog, ui.card().classes('gap-3 max-w-2xl w-full no-print'):
        dialog.props('transition-show="none" transition-hide="none"')
        ui.label(res_str('save_pdf_str', 'Save as PDF')).classes('text-lg font-bold text-green-700')
        ui.label('Select which pages to include, then click "Generate & Print".').classes('text-sm text-gray-600')
        with ui.column().classes('gap-1 max-h-[55vh] overflow-y-auto w-full'):
            for category in categories:
                ui.label(category).classes('font-bold text-brown-700 mt-2')
                for key in categories[category]:
                    entry = _REGISTRY[key]
                    with ui.column().classes('gap-0.5 w-full pl-2'):
                        cb = ui.checkbox(entry['label'], value=False)
                        checkboxes[key] = cb
                        if entry['sub_option_ui'] is not None:
                            custom_container = ui.column().classes('gap-1 pl-8')
                            holder = _CustomUIHolder(custom_container, entry['sub_option_ui'])
                            custom_ui_holders[key] = holder
                            cb.on_value_change(lambda e, h=holder: h.rebuild_if_checked(e.value))
        status_row = ui.row().classes('items-center gap-2')
        with status_row:
            spinner = ui.spinner(size='sm')
            status_label = ui.label('')
        spinner.set_visibility(False)
        status_label.set_visibility(False)
        async def on_generate():
            selected_keys = [k for k, cb in checkboxes.items() if cb.value]
            if not selected_keys:
                safe_notify('Select at least one page to include.', type='warning')
                return
            try:
                dob_val = state['date_dob']; tob_val = state['time_tob']
                place_val = state['place_name']
                lat_val = float(state['latitude']); lon_val = float(state['longitude']); tz_val = float(state['timezone'])
                year, month, day = (int(x) for x in dob_val.split(','))
                dob = (year, month, day)
                tob = _parse_tob(tob_val)
            except Exception as e:
                safe_notify(f'Error reading birth details: {e}', type='negative')
                return
            spinner.set_visibility(True)
            status_label.set_visibility(True)
            status_label.set_text(f'Building {len(selected_keys)} section(s)... this can take a while, please wait.')
            if _combined_report_container is None:
                safe_notify('Internal error: the combined-report container was not initialized '
                           '(render_global_print_button() must be called once on this page before '
                           'opening this dialog).', type='negative')
                spinner.set_visibility(False); status_label.set_visibility(False)
                return
            _combined_report_container.clear()
            any_succeeded = False
            for i, key in enumerate(selected_keys):
                entry = _REGISTRY[key]
                sub_option_values = {}
                if key in custom_ui_holders:
                    sub_option_values = _collect_sub_option_values(custom_ui_holders[key].widgets)
                page_break_class = ' print-report-page-break' if i > 0 else ''
                try:
                    with _combined_report_container:
                        section = ui.column().classes('w-full print-report-page' + page_break_class)
                    await entry['build'](section, dob, tob, place_val, lat_val, lon_val, tz_val, sub_option_values)
                    with section:
                        ui.separator().classes('mt-2')
                        ui.html(_footer_inner_html()).classes('text-xs text-gray-600 text-center w-full mt-1')
                    any_succeeded = True
                except Exception as e:
                    print(f"[print_registry] build() failed for key={key!r}: {type(e).__name__}: {e}")
                    safe_notify(f"Could not build \"{entry['label']}\" - skipped (see server console).", type='warning')
            spinner.set_visibility(False)
            status_label.set_visibility(False)
            if not any_succeeded:
                safe_notify('Could not build any of the selected sections - see the server console.', type='negative')
                return
            dialog.close()
            # ROOT CAUSE of an actual confirmed bug ("every PDF page looks like the print dialog is
            # in front of it" / "grey background on every page"): `dialog.close()` only STARTS
            # (or, previously, triggered) this Quasar dialog's own closing animation, including its
            # semi-transparent backdrop fading out - it does NOT make that happen instantly or
            # guarantee it has finished before the next line runs.
            #
            # An EARLIER version of this fix disabled the browser-side fade via a flat
            # `await asyncio.sleep(0.35)` (a SERVER-side guess at how long the fade takes) before
            # calling window.print(). That guess is unrelated to how busy the BROWSER actually is:
            # confirmed from an actual report (selecting only 2 small sections printed with a
            # clean white background; selecting ALL sections - ~90 pages' worth of freshly built,
            # dense HTML tables just pushed to the browser by the loop just above - printed with a
            # visible grey background on every page). With a large selection, the browser's main
            # thread is still busy laying out/painting that huge just-inserted DOM when the
            # server's fixed 0.35s elapses, so the dialog's own close/backdrop-fade had not even
            # STARTED yet - window.print() then fired while the backdrop was still fully opaque.
            # A fixed sleep can never account for this: the "safe" delay needed scales with
            # exactly how much content was just selected, which this function has no way to
            # predict in advance.
            #
            # Fix (two parts, defense in depth):
            #   1) `transition-show="none" transition-hide="none"` on the dialog (above) removes
            #      the fade/animation entirely, so dialog.close() removes the dialog AND its
            #      backdrop from the DOM essentially synchronously, regardless of how busy the
            #      browser's main thread is with OTHER, unrelated work.
            #   2) The JS below, run via trigger_print_js(), actively POLLS the DOM (instead of
            #      guessing a duration) for the actual absence of any '.q-dialog__backdrop'
            #      element before calling window.print() - capped at a generous 3-second safety
            #      timeout so a visitor is never stuck waiting indefinitely if something
            #      unexpected keeps a backdrop element around. This scales correctly with
            #      how much work the browser still has queued, because it is checking the
            #      browser's OWN actual state rather than assuming a fixed amount of time is
            #      always enough.
            # trigger_print_js() (components.py) must be AWAITED here, directly in this handler - see
            # that function's own docstring for why (NiceGUI's client/websocket context must still be
            # live when the script reaches the browser).
            await trigger_print_js("""
                (function () {
                    return new Promise((resolve) => {
                        const deadline = Date.now() + 3000;
                        const checkBackdropGone = () => {
                            const backdrop = document.querySelector('.q-dialog__backdrop');
                            const stillVisible = backdrop &&
                                getComputedStyle(backdrop).display !== 'none' &&
                                parseFloat(getComputedStyle(backdrop).opacity || '0') > 0.01;
                            if (!stillVisible || Date.now() > deadline) {
                                resolve();
                            } else {
                                requestAnimationFrame(checkBackdropGone);
                            }
                        };
                        checkBackdropGone();
                    });
                })().then(() => {
                    document.body.classList.add('printing-all');
                    if (!window.__jhora_afterprint_installed) {
                        window.__jhora_afterprint_installed = true;
                        window.addEventListener('afterprint', () => document.body.classList.remove('printing-all'));
                    }
                    window.print();
                });
            """)
        with ui.row().classes('gap-2 justify-end w-full'):
            ui.button(res_str('cancel_str', 'Cancel'), on_click=dialog.close).props('outlined dense')
            ui.button('Generate & Print', on_click=on_generate).classes('bg-green-600 text-white')
    dialog.open()
