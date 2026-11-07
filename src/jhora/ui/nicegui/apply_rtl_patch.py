#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Right-to-left (RTL) support for Urdu (and other RTL languages) in JHoraWeb - version 2.

Safe to run on a fresh components.py AND on one that already has the version-1 patch: it upgrades it in place.
A backup <file>.bak is written before a file is changed; running it again changes nothing.

What it does
  components.py   - adds RTL_LANGUAGES, is_rtl_language() and _RTL_HEAD_HTML before navigation_header()
                  - makes navigation_header() add that HTML to the page head when the visitor's language is RTL
                  - NEW in version 2: _RTL_HEAD_HTML now also fixes signed numbers. In a right-to-left page the
                    browser shows "(+2)" as "(2+)" and "-87.6" as "87.6-". A small script puts an invisible
                    left-to-right mark around such numbers, in every piece of text the page shows (also text that
                    NiceGUI adds after the page has loaded), so no page file has to be edited.
  transit_tab.py  - marks the Transit chart box 'keep-ltr' so the chart is never mirrored (optional)

HOW TO RUN: copy this file next to components.py (src/jhora/ui/nicegui), open it in VSCode and press Run, or
            python apply_rtl_patch.py        Then restart the app (and hard-refresh the browser: Ctrl+F5).
UNDO:       copy components.py.bak / transit_tab.py.bak back over the originals.
"""
import os
import py_compile
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = HERE                      # folder that holds components.py - change it if you run this from elsewhere
MARKER = "rtl-signed-numbers v2"   # present in the version-2 block

HEAD_HTML = r'''_RTL_HEAD_HTML = r"""
<!-- __MARKER__ -->
<script>
(function () {
  document.documentElement.setAttribute('dir', 'rtl');
  var LRM = '\u200E';
  // a sign directly before a digit, at the start of a text or after a space or "(":  (+1)  (+2)  -87.6  -13000
  var SIGNED = /(^|[\s(])([+\-]\d+(?:\.\d+)?)/g;
  function mark(node) {
    var t = node.nodeValue;
    if (!t || (t.indexOf('+') === -1 && t.indexOf('-') === -1)) { return; }
    var u = t.replace(SIGNED, function (m, pre, num) { return pre + LRM + num + LRM; });
    if (u !== t) { node.nodeValue = u; }            // the new text no longer matches, so this cannot loop
  }
  function walk(root) {
    if (root.nodeType === 3) { mark(root); return; }
    if (root.nodeType !== 1) { return; }
    var tag = root.nodeName;
    if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'TEXTAREA') { return; }
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) { mark(n); }
  }
  new MutationObserver(function (list) {
    for (var i = 0; i < list.length; i++) {
      var m = list[i];
      if (m.type === 'characterData') { mark(m.target); }
      else { for (var j = 0; j < m.addedNodes.length; j++) { walk(m.addedNodes[j]); } }
    }
  }).observe(document.documentElement, {childList: true, subtree: true, characterData: true});
  document.addEventListener('DOMContentLoaded', function () { walk(document.body); });
})();
</script>
<style>
  /* charts and anything marked keep-ltr are never mirrored */
  .chart-surface, .keep-ltr { direction: ltr !important; }
  .q-field__native, .q-field__input { unicode-bidi: plaintext; }
</style>
"""
'''.replace("__MARKER__", MARKER)

HELPERS = '''\
# ---------------------------------------------------------------------------------------------------
# Right-to-left (RTL) languages. When the visitor's language is one of these, every page gets
# dir="rtl" on <html> (the browser then mirrors the layout: nav bar, headings, cards, text alignment).
# Charts (.chart-surface) and anything marked 'keep-ltr' stay left-to-right, because a mirrored chart
# would put the signs in the wrong cells.
# ---------------------------------------------------------------------------------------------------
RTL_LANGUAGES = {"ur", "ar", "fa", "he", "ps", "sd", "ks"}      # language codes (as in available_languages)
_RTL_LANGUAGE_NAMES = {"urdu", "arabic", "persian", "farsi", "hebrew", "pashto", "sindhi", "kashmiri"}
def _visitor_language():
  """Returns the current visitor's language code, lower-case: the visitor's own language in public mode,
  otherwise the server's language (const._DEFAULT_LANGUAGE)."""
  lang = None
  try:
      import web_language
      lang = web_language._active_language()      # None when the visitor uses the server's language
  except Exception:
      pass
  return str(lang or getattr(const, '_DEFAULT_LANGUAGE', 'en') or 'en').strip().lower()
def is_rtl_language(lang=None):
  """True if `lang` (default: the visitor's language) is written right to left."""
  lang = (str(lang).strip().lower() if lang else _visitor_language())
  return lang in RTL_LANGUAGES or lang in _RTL_LANGUAGE_NAMES
'''

CALL = ("ui.add_head_html(_PAGE_THEME_CSS)\n"
        "{i}if is_rtl_language():\n"
        "{i}    ui.add_head_html(_RTL_HEAD_HTML)\n")

HEAD_RX = re.compile(r'^_RTL_HEAD_HTML = r?"""(.*?)"""[ \t]*\r?\n', re.S | re.M)


def _read(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return f.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _finish(path, new_text, what):
    shutil.copy2(path, path + ".bak")
    _write(path, new_text)
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(path + ".bak", path)
        print(f"{os.path.basename(path)}: the changed file did not compile, original restored: {e}")
        return False
    print(f"{os.path.basename(path)}: {what} (backup: {os.path.basename(path)}.bak).")
    return True


def patch_components(path):
    text = _read(path)
    nl = "\r\n" if "\r\n" in text else "\n"
    head = HEAD_HTML.replace("\n", nl)
    if "def is_rtl_language" in text:                          # version 1 (or 2) is already there
        m = HEAD_RX.search(text)
        if not m:
            print("components.py: is_rtl_language() is there, but the _RTL_HEAD_HTML block was not found. "
                  "Nothing changed - send me components.py.")
            return False
        if MARKER in m.group(1):
            print("components.py: already up to date (version 2) - nothing to do.")
            return True
        return _finish(path, text[:m.start()] + head + text[m.end():],
                       "upgraded to version 2 (signed numbers such as (+1) now show correctly)")
    # fresh file: insert helpers + head html after '_PAGE_THEME_CSS += _PRINT_CSS', add the call
    m1 = re.search(r"^_PAGE_THEME_CSS \+= _PRINT_CSS[ \t]*\r?\n", text, re.M)
    m2 = re.search(r"^([ \t]*)ui\.add_head_html\(_PAGE_THEME_CSS\)[ \t]*\r?\n", text, re.M)
    if not m1 or not m2 or len(re.findall(r"ui\.add_head_html\(_PAGE_THEME_CSS\)", text)) != 1:
        print("components.py: could not find the two places to change (is this the expected version?). "
              "Nothing changed.")
        return False
    indent = m2.group(1)
    new_text = (text[:m1.end()] + HELPERS.replace("\n", nl) + head + text[m1.end():m2.start()]
                + (indent + CALL.format(i=indent)).replace("\n", nl) + text[m2.end():])
    return _finish(path, new_text, "patched (version 2)")


def patch_transit(path):
    if not os.path.exists(path):
        print("transit_tab.py: not found next to components.py - skipped (optional).")
        return True
    text = _read(path)
    old = "chart_container = ui.column().classes('items-center mt-4')"
    new = "chart_container = ui.column().classes('items-center mt-4 keep-ltr')"
    if new in text:
        print("transit_tab.py: already patched.")
        return True
    if text.count(old) != 1:
        print("transit_tab.py: the chart box line was not found exactly once - skipped. "
              "Add the class 'keep-ltr' to the Transit chart container by hand.")
        return True
    return _finish(path, text.replace(old, new), "patched")


if __name__ == "__main__":
    comp = os.path.join(FOLDER, "components.py")
    if not os.path.exists(comp):
        print(f"components.py not found in {FOLDER} - copy this script next to it (or edit FOLDER).")
        sys.exit(1)
    ok = patch_components(comp) and patch_transit(os.path.join(FOLDER, "transit_tab.py"))
    print("\nDone. Restart the app, press Ctrl+F5 in the browser and select Urdu." if ok
          else "\nSomething was not changed - see the messages above.")
    sys.exit(0 if ok else 1)
