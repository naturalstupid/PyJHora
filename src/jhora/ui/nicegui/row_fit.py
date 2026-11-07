#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Fits a row of controls into one line without a scrollbar.

The control rows of the calculation pages used to be `flex-nowrap overflow-x-auto`: one line, but with a horizontal
scrollbar when the controls do not fit. fit_row() keeps the one line and removes the scrollbar instead by letting
the controls shrink:

  * every input and select that is a direct child of the row may become narrower than its own width (its width class
    stays the preferred width, so on a wide window nothing changes), down to nothing but its padding;
  * buttons and check boxes keep their width (a squeezed button would overflow its label), so the fields give way
    to them;
  * the text of the controls gets a smaller font, so more of a value is readable when a field is squeezed; a select
    shows the start of its value followed by an ellipsis when its value no longer fits;
  * on a narrow window (below FIT_BREAKPOINT_PX) the controls are not squeezed - the row wraps instead, because
    fields squeezed to nothing would be unusable on a phone.

Where it is applied: components.render_control_bar() applies it to BOTH of its rows (the birth-details row and
widgets['row2'], the row for the page's own controls), and components.navigation_header() adds the stylesheet to every
page once. So a page that uses render_control_bar() needs no code at all. A page that builds an extra row of its own
inputs can opt in with one line:

    from row_fit import fit_row
    fit_row(ui.row())            # (the stylesheet is already on the page)

The styling is plain CSS scoped to the `fit-row` class (fit_css()).
"""
from nicegui import ui

FIT_ROW_CLASS = 'fit-row'
DEFAULT_FONT_PX = 11
FIT_BREAKPOINT_PX = 768

_CSS_TEMPLATE = """
.fit-row { flex-wrap: nowrap !important; overflow: visible !important; }
.fit-row > * { flex: 0 1 auto !important; min-width: 0 !important; }
.fit-row > .q-btn, .fit-row > .q-checkbox, .fit-row > .q-toggle, .fit-row > .q-spinner { flex-shrink: 0 !important; }
.fit-row .q-field__native,
.fit-row .q-field__input,
.fit-row .q-field__prefix,
.fit-row .q-field__suffix,
.fit-row .q-field__label,
.fit-row .q-btn,
.fit-row .q-checkbox__label { font-size: {FONT}px !important; }
.fit-row .q-field__control { padding-left: 6px !important; padding-right: 4px !important; }
.fit-row .q-field__append { padding-left: 2px !important; }
.fit-row .q-field__native { overflow: hidden !important; }
.fit-row .q-field__native > span { overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 100%; }
.fit-row .q-btn { padding-left: 8px !important; padding-right: 8px !important; }
@media (max-width: {BREAKPOINT}px) {
  .fit-row { flex-wrap: wrap !important; }
  .fit-row > * { flex: 0 0 auto !important; }
}
"""


def fit_css(font_px=DEFAULT_FONT_PX):
    """Returns the stylesheet of the fit-row class (navigation_header() adds it to every page).

    Args:
        font_px: font size, in pixels, of the controls in a fitted row (default 11).
    """
    return (_CSS_TEMPLATE.replace('{FONT}', str(int(font_px)))
            .replace('{BREAKPOINT}', str(int(FIT_BREAKPOINT_PX))))


def fit_row(row, font_px=DEFAULT_FONT_PX, add_css=True):
    """Makes `row` one line that never needs a horizontal scrollbar (see the module docstring).

    Args:
        row: the row element.
        font_px: font size, in pixels, of the controls in the row (default 11); used only when add_css is True.
        add_css: also add the stylesheet to the page. components.render_control_bar() passes False, because
            navigation_header() has already added it; a page that calls fit_row() on its own leaves it True
            (adding the stylesheet twice is harmless).

    Returns:
        the row, so the call can be chained.
    """
    if add_css:
        ui.add_css(fit_css(font_px))
    row.classes(add=f'flex-nowrap {FIT_ROW_CLASS}', remove='flex-wrap overflow-x-auto')
    return row
