#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Adds the Nepal Bikram Sambat calendar to the two places that build the date text of a calendar day:

    vedic_calendar.py   (PyQt6)    VedicCalendar._get_days_panchanga_info()
    calendar_tab.py     (NiceGUI)  _build_day_header()

Without this change both functions send the Nepal calendar type through their lunar "else" branch:
  * vedic_calendar.py  crashes with IndexError (utils.YEAR_LIST has 60 items, the BS year is 2083), which
                       computeCalendar() swallows - the grid stays empty;
  * calendar_tab.py    shows a lunar month and "(Amantha)" instead of the Nepali month  (e.g. "Ashvina 1" for Kartik 1).

What is added, in each file (nothing is removed or changed):
  1. after the _BANGLADESH_MONTH_LIST line: _NEPAL_BS_MONTH_LIST (English transliteration, used for every language),
     _NEPAL_BS_MONTH_LIST_NE (everyday Nepali names, used when the UI language is Nepali) and _nepal_bs_month_name()
  2. in the calendar-type if/elif chain: one  elif  branch for NEPAL_BIKRAM_SAMBAT that writes
        "<month name> <day> (<calendar name>)"   and the year as "(2083)"
     the calendar name comes from the resource string  nepal_bikram_sambat_str  (English fallback in the code)
Paksha and tithi are still appended to the header, as for the solar and lunar calendars.

SAFETY: the file is changed only if both places are found exactly once; the new text must compile; a line diff must show
ONLY added lines. A backup <file>.nepal_ui.bak is written first. Running it again changes nothing.

HOW TO RUN (VSCode: press Run).  It looks for the two files under the jhora package folder above this script.
If you keep them somewhere else, put the full paths into PATHS below.
"""
import ast
import difflib
import os
import py_compile
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PATHS = {"vedic_calendar.py": None, "calendar_tab.py": None}        # e.g. {"vedic_calendar.py": r"C:\...\vedic_calendar.py"}

CONSTANTS_BLOCK = '''\
# Month names of the Nepal Bikram Sambat calendar. vedic_date() returns the month 1-based (1 = Baisakh).
# English transliterations are used for every language; everyday Nepali (Devanagari) names when the UI language is Nepali.
_NEPAL_BS_MONTH_LIST = ['Baisakh','Jestha','Ashadh','Shrawan','Bhadra','Ashwin','Kartik','Mangsir','Poush','Magh','Falgun','Chaitra']
_NEPAL_BS_MONTH_LIST_NE = ['वैशाख','जेठ','असार','साउन','भदौ','असोज','कात्तिक','मङ्सिर','पुस','माघ','फागुन','चैत']
def _nepal_bs_month_name(month, language_code):
    """Name of month `month` (1 = Baisakh ... 12 = Chaitra) of the Nepal Bikram Sambat calendar.
    @param month: 1-based month as returned by drik.vedic_date().
    @param language_code: UI language code, e.g. 'ne' (Nepali names); any other code gives the English names.
    @return: month name.
    """
    _names = _NEPAL_BS_MONTH_LIST_NE if str(language_code).strip().lower() == 'ne' else _NEPAL_BS_MONTH_LIST
    return _names[(month-1) % 12]
'''

BRANCH_VEDIC = '''\
        elif _cal_type == const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT:
            day_str = str(td)
            spl_month_text = (_nepal_bs_month_name(tm, _lang) + ' ' + day_str + ' (' +
                              self.res.get('nepal_bikram_sambat_str', 'Nepal Bikram Sambat') + ')')
            year_str = '('+str(ty)+')'
'''
BRANCH_TAB = '''\
    elif cal_type == _NEPALI:
        nepal_label = res_str('nepal_bikram_sambat_str', 'Nepal Bikram Sambat')
        spl_month_text = f"{_nepal_bs_month_name(tm, const._DEFAULT_LANGUAGE)} {td} ({nepal_label})"
        year_str = f"({ty})"
'''

# where the new text goes (regular expressions on the LF-normalised text; each must match exactly once)
CONST_ANCHOR = r"^_BANGLADESH_MONTH_LIST = \[[^\n]*\]\n"
SPECS = {
    "vedic_calendar.py": {
        "branch": BRANCH_VEDIC,
        "branch_anchor": r"^        else:\n            day_str = str\(td\)\n            tm -= 1\n",
        "done_marker": "_cal_type == const.CALENDAR_TYPE.NEPAL_BIKRAM_SAMBAT",
    },
    "calendar_tab.py": {
        "branch": BRANCH_TAB,
        "branch_anchor": r"^    else:\n        adhik = utils\.resource_strings\.get\('adhika_maasa_str', ''\) if am else ''\n",
        "done_marker": "cal_type == _NEPALI",
    },
}


def find_file(name):
    """Full path of `name`: PATHS override, else searched under the 'jhora' package folder above this script."""
    if PATHS.get(name):
        return PATHS[name]
    root, p = None, HERE
    while True:
        if os.path.basename(p).lower() == "jhora":
            root = p
            break
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    if root is None:
        root = HERE
    hits = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git", "node_modules")]
        if name in files:
            hits.append(os.path.join(d, name))
    if len(hits) == 1:
        return hits[0]
    print(f"   {name}: {'not found' if not hits else 'found more than once'} under {root}"
          + ("" if not hits else ": " + "; ".join(hits)) + " - put the full path into PATHS at the top of this script.")
    return None


def patch(path, spec):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    work = text.replace("\r\n", "\n")
    done_const = "def _nepal_bs_month_name(" in work
    done_branch = spec["done_marker"] in work
    if done_const and done_branch:
        print(f"   {os.path.basename(path)}: already patched - nothing to do.")
        return True
    if done_const != done_branch:
        print(f"   {os.path.basename(path)}: only half of the change is present (constants: {done_const}, branch: {done_branch}). "
              "Nothing changed - send me the file.")
        return False
    m_const = list(re.finditer(CONST_ANCHOR, work, re.M))
    m_branch = list(re.finditer(spec["branch_anchor"], work, re.M))
    if len(m_const) != 1 or len(m_branch) != 1:
        print(f"   {os.path.basename(path)}: anchors found {len(m_const)} / {len(m_branch)} times (need 1 / 1) - the file differs from the "
              "version this script was written for. Nothing changed.")
        return False
    # build the new text (insert the later position first so the earlier offset stays valid)
    b = m_branch[0].start()
    new = work[:b] + spec["branch"] + work[b:]
    c = m_const[0].end()
    new = new[:c] + CONSTANTS_BLOCK + new[c:]
    # checks: compiles, only added lines, anchors still there
    try:
        ast.parse(new)
    except SyntaxError as e:
        print(f"   {os.path.basename(path)}: the new text would not compile ({e}). Nothing changed.")
        return False
    diff = list(difflib.unified_diff(work.split("\n"), new.split("\n"), lineterm="", n=0))
    removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
    added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
    if removed:
        print(f"   {os.path.basename(path)}: the change would remove {len(removed)} line(s) - not expected. Nothing changed.")
        return False
    out = new.replace("\n", nl).encode("utf-8")
    if bom:
        out = b"\xef\xbb\xbf" + out
    backup = path + ".nepal_ui.bak"
    shutil.copy2(path, backup)
    with open(path, "wb") as f:
        f.write(out)
    try:
        py_compile.compile(path, cfile=os.path.join(tempfile.gettempdir(), "nepal_ui_check.pyc"), doraise=True)
    except py_compile.PyCompileError as e:
        shutil.copy2(backup, path)
        print(f"   {os.path.basename(path)}: the changed file did not compile, original restored: {e}")
        return False
    print(f"   {os.path.basename(path)}: patched - {len(added)} lines added, 0 removed (backup: {os.path.basename(backup)}).")
    return True


def main():
    print("Nepal Bikram Sambat - calendar day text")
    ok = True
    for name, spec in SPECS.items():
        path = find_file(name)
        if path is None:
            ok = False
            continue
        print(f" {path}")
        ok = patch(path, spec) and ok
    print("\nDone. Restart the app." if ok else "\nSomething was not changed - see the messages above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
