"""Divisional-chart options dialog: method of a standard varga, or factor, cycle, base rasi and counting of a custom one.

Web counterpart of the desktop VargaChartOptionsDialog.
"""
from collections import namedtuple

from nicegui import ui

from components import res_str
from jhora import const, utils

BASE_RASI_LABELS = {0: 'Aries Always', 1: 'The rasi itself'}
CUSTOM_CHART_KEY = 'custom_varga_kundali_str'

VargaChoice = namedtuple('VargaChoice', 'method varga_factor base_rasi count_from_end text')
VargaChoice.__doc__ = """Result of the dialog.

Fields:
    method: method index; 1-based for a standard varga, 0-based for a custom non-cyclic one, 0 for a custom cyclic one.
    varga_factor: chosen factor for a custom varga, None for a standard one.
    base_rasi: 0 (Aries always) or 1 (the rasi itself) for a custom non-cyclic varga, otherwise None.
    count_from_end: True/False for a custom non-cyclic varga, otherwise None.
    text: description to show beside the chart.
"""


def custom_factors():
    """Returns the factors offered for a custom varga."""
    start_factors = range(2, const.MAX_DHASAVARGA_FACTOR + 1)
    if getattr(const, 'TREAT_STANDARD_CHART_AS_CUSTOM', False):
        return list(start_factors)
    return [f for f in start_factors if f not in const.division_chart_factors]


def is_standard(chart_index, varga_factor):
    """Returns True when the options are those of a standard varga.

    Args:
        chart_index: index into const.division_chart_factors, or None for a custom chart.
        varga_factor: factor of a custom chart, or None for a standard one.
    """
    if varga_factor is None:
        return chart_index is not None and chart_index < len(const.division_chart_factors)
    return varga_factor in const.division_chart_factors


def method_captions(factor, standard):
    """Returns {method index: caption} for a varga.

    Args:
        factor: divisional chart factor.
        standard: True for a standard varga (methods are numbered from 1), False for a custom one (from 0).
    """
    count = utils.get_varga_option_dict()[factor][0]
    if standard:
        return {n: res_str(f'd{factor}_option{n}_str', f'D{factor} method {n}') for n in range(1, count + 1)}
    return {n: res_str(f'dn_custom_option{n}_str', f'Method {n}') for n in range(count)}


def describe(standard, factor, method, captions, base_rasi, count_from_end, cyclic):
    """Returns the text describing a choice.

    Args:
        standard: True for a standard varga.
        factor: divisional chart factor.
        method: chosen method index.
        captions: result of method_captions().
        base_rasi: chosen base rasi option, or None.
        count_from_end: chosen counting, or None.
        cyclic: True when a custom varga is cyclic.
    """
    if standard:
        return captions.get(method, '')
    if cyclic:
        return f"D{factor}: {res_str('dn_custom_cyclic_str', 'Cyclic')}"
    parts = [f"D{factor}: {res_str('dn_custom_non_cyclic_str', 'Non-cyclic')}", captions.get(method, ''),
             BASE_RASI_LABELS.get(base_rasi, '')]
    if count_from_end:
        parts.append(res_str('dn_custom_count_from_end_of_sign_str', 'Count from end of sign'))
    return ' / '.join(p for p in parts if p)


class VargaOptionsDialog:
    """The dialog; create it once per page and call open() each time it is needed."""

    def __init__(self):
        self.on_accept = None
        self.on_cancel = None
        self.accepted = False
        self.standard = True
        self.factor = 1
        with ui.dialog() as self.dialog, ui.card().classes('gap-2 min-w-[360px] max-w-[96vw]'):
            ui.label(res_str('choose_varga_chart_method_str', 'Choose chart method')).classes('text-lg font-bold text-green-700')
            self.body = ui.column().classes('gap-2 w-full')
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button(res_str('cancel_str', 'Cancel'), on_click=lambda: self.dialog.close()).props('outlined dense')
                ui.button(res_str('accept_str', 'Accept'), on_click=lambda: self.accept()).classes('bg-green-600 text-white')
        self.dialog.on('hide', lambda e=None: self.on_hide())

    def open(self, chart_index=None, method=0, varga_factor=None, base_rasi=None, count_from_end=None,
             on_accept=None, on_cancel=None):
        """Opens the dialog.

        Args:
            chart_index: index into const.division_chart_factors; None for a custom chart.
            method: current method index.
            varga_factor: factor of a custom chart; None for a standard one.
            base_rasi: current base rasi option of a custom non-cyclic chart.
            count_from_end: current counting of a custom non-cyclic chart.
            on_accept: callable(VargaChoice) called on Accept.
            on_cancel: callable() called when the dialog closes without Accept.
        """
        self.on_accept, self.on_cancel, self.accepted = on_accept, on_cancel, False
        self.standard = is_standard(chart_index, varga_factor)
        if self.standard:
            self.factor = varga_factor if varga_factor is not None else const.division_chart_factors[chart_index]
        else:
            self.factor = varga_factor if varga_factor in custom_factors() else const.DEFAULT_CUSTOM_VARGA_FACTOR
        self.build(method, base_rasi, count_from_end)
        self.dialog.open()

    def build(self, method, base_rasi, count_from_end):
        """Builds all the controls for the current factor."""
        self.body.clear()
        with self.body:
            if not self.standard:
                self.factor_select = ui.select(
                    custom_factors(), value=self.factor, label=res_str('dn_custom_varga_number_str', 'Custom varga number'),
                    on_change=lambda e: self.on_factor_change(e.value)).props('outlined dense').classes('w-full')
                self.cyclic = ui.radio(
                    {True: res_str('dn_custom_cyclic_str', 'Cyclic'), False: res_str('dn_custom_non_cyclic_str', 'Non-cyclic')},
                    value=(method == 0 and base_rasi is None), on_change=lambda e: self.show_non_cyclic()).props('inline')
            self.methods_box = ui.column().classes('gap-2 w-full')
        self.build_methods(method, base_rasi, count_from_end)
        if not self.standard:
            self.show_non_cyclic()

    def build_methods(self, method, base_rasi, count_from_end):
        """Builds the controls that depend on the factor: base rasi, methods and counting."""
        self.methods_box.clear()
        with self.methods_box:
            if not self.standard:
                self.base = ui.select(BASE_RASI_LABELS, value=base_rasi if base_rasi in BASE_RASI_LABELS else 0,
                                      label='Base Rasi').props('outlined dense').classes('w-full')
            name_key = const._chart_names[const.division_chart_factors.index(self.factor)] if self.standard else CUSTOM_CHART_KEY
            ui.label(f"{res_str('varga_option_str', 'Varga option')} {res_str(name_key, name_key)}")
            self.captions = method_captions(self.factor, self.standard)
            self.method = ui.radio(self.captions, value=method if method in self.captions else next(iter(self.captions)))
            if not self.standard:
                self.count_from_end = ui.checkbox(res_str('dn_custom_count_from_end_of_sign_str', 'Count from end of sign'),
                                                  value=bool(count_from_end))

    def show_non_cyclic(self):
        """Shows the base rasi, method and counting controls only for a non-cyclic custom varga."""
        self.methods_box.set_visibility(not self.cyclic.value)

    def on_factor_change(self, factor):
        """Rebuilds the method choices for the newly chosen custom factor, keeping the base and counting choices."""
        base, count = self.base.value, bool(self.count_from_end.value)
        self.factor = factor
        self.build_methods(0, base, count)

    def accept(self):
        """Reports the choice and closes."""
        if self.standard:
            method, factor, base, count, cyclic = self.method.value, None, None, None, False
        else:
            factor, cyclic = int(self.factor_select.value), bool(self.cyclic.value)
            if cyclic:
                method, base, count = 0, None, None
            else:
                method, base, count = self.method.value, self.base.value, bool(self.count_from_end.value)
        text = describe(self.standard, self.factor if self.standard else factor, method, self.captions, base, count, cyclic)
        self.accepted = True
        callback = self.on_accept
        self.dialog.close()
        if callback is not None:
            callback(VargaChoice(method, factor, base, count, text))

    def on_hide(self):
        """Reports a cancel when the dialog closed without Accept."""
        if not self.accepted and self.on_cancel is not None:
            callback, self.on_cancel = self.on_cancel, None
            callback()
