"""Highlights a page's Compute button while its inputs differ from the results on screen.

components.render_control_bar() calls install(); pages need no code of their own.
"""
import time

from nicegui import ui

DIRTY_CLASS = 'calc-dirty'
GRACE_S = 0.6
DEFAULT_HINT = 'Inputs changed - click to update the results'
CONTROL_BAR_INPUTS = ('dob_input', 'tob_input', 'place_select', 'lat_input', 'lon_input', 'tz_input', 'gender_select')
OPAQUE_TYPES = ('Dialog', 'Menu', 'ContextMenu', 'Tooltip')

# Inline, because an inline !important declaration outranks Quasar's layered !important colour rules.
DIRTY_STYLE = ('background: #f59e0b !important; color: #111827 !important; font-weight: 800 !important; '
               'outline: 2px solid #b45309 !important; outline-offset: 1px')

CSS = """
.q-btn.calc-dirty { animation: calc-dirty-pulse 1.4s ease-in-out infinite; }
@keyframes calc-dirty-pulse {
  0%   { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.75); }
  70%  { box-shadow: 0 0 0 9px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}
@media (prefers-reduced-motion: reduce) {
  .q-btn.calc-dirty { animation: none; }
}
"""


def _walk(element):
    """Yields every descendant of `element`, without descending into dialogs and menus."""
    for child in list(element.default_slot.children):
        yield child
        if type(child).__name__ not in OPAQUE_TYPES:
            yield from _walk(child)


def _is_input(element):
    """Returns True for an element that holds a value the user edits."""
    return hasattr(element, 'on_value_change') and hasattr(element, 'value')


class CalcHighlighter:
    """Marks and clears the highlight of one Compute button.

    Args:
        button: the Compute button element.
        hint: tooltip shown while highlighted.
        grace: seconds after a calculation ends during which input changes are ignored.
    """

    def __init__(self, button, hint=None, grace=GRACE_S):
        self.button = button
        self.hint = (hint or DEFAULT_HINT).replace('"', "'")
        self.grace = grace
        self.dirty = False
        self.quiet_until = 0.0
        original_disable, original_enable = button.disable, button.enable

        def disable(*args, **kwargs):
            self.mark_clean()  # a calculation is starting
            return original_disable(*args, **kwargs)

        def enable(*args, **kwargs):
            self.quiet_until = time.monotonic() + self.grace
            return original_enable(*args, **kwargs)

        button.disable = disable
        button.enable = enable

    def mark_dirty(self, *_event):
        """Highlights the button; ignored during the quiet period after a calculation."""
        if self.dirty or time.monotonic() < self.quiet_until:
            return
        self.dirty = True
        self.button.classes(add=DIRTY_CLASS)
        self.button.style(add=DIRTY_STYLE)
        self.button.props(f'title="{self.hint}"')

    def mark_clean(self):
        """Removes the highlight."""
        if not self.dirty:
            return
        self.dirty = False
        self.button.classes(remove=DIRTY_CLASS)
        self.button.style(remove=DIRTY_STYLE)
        self.button.props(remove='title')

    def watch(self, element):
        """Highlights the button when `element`'s value changes; skips elements flagged `_calc_no_dirty`."""
        if getattr(element, '_calc_no_dirty', False) or getattr(element, '_calc_watched', False):
            return
        element._calc_watched = True
        element.on_value_change(self.mark_dirty)

    def watch_tree(self, root):
        """Watches every input below `root`."""
        for element in _walk(root):
            if _is_input(element):
                self.watch(element)


def install(widgets, hint=None, grace=GRACE_S):
    """Wires the Compute-button highlight of one control bar.

    Args:
        widgets: dict returned by components.render_control_bar(); needs 'calculate_button'. Gains 'mark_dirty'
            and 'mark_clean'.
        hint: tooltip of the highlighted button.
        grace: seconds after a calculation ends during which input changes are ignored.

    Returns:
        The CalcHighlighter, or None when there is no Compute button.
    """
    button = widgets.get('calculate_button')
    if button is None:
        return None
    ui.add_css(CSS)
    highlighter = CalcHighlighter(button, hint=hint, grace=grace)
    for key in CONTROL_BAR_INPUTS:
        element = widgets.get(key)
        if element is not None:
            highlighter.watch(element)
    row2 = widgets.get('row2')
    if row2 is not None:
        ui.timer(0.3, lambda: highlighter.watch_tree(row2), once=True)  # the page fills row 2 after this returns
    widgets['mark_dirty'] = highlighter.mark_dirty
    widgets['mark_clean'] = highlighter.mark_clean
    return highlighter
