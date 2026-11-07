#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""fix_resources.py - CHECK and FIX the resource files of one language (the 3rd of the 3 scripts).

    transliterate_resources.py             list_values / amsa_rulers / msg_strings from the Hindi files
    indic_translate_using_huggingface.py   the sentence files (dosha, prediction, yoga, raja_yoga) with NLLB / IndicTrans2
    fix_resources.py                       this file: check the result against the English files, fix what is wrong

Files handled for LANG (name = <base>_<lang>.txt or .json, whichever exists; the English file <base>_en.* is the reference):
    msg_strings, list_values (text, KEY=value)      amsa_rulers, dosha_msgs, raja_yoga_msgs, yoga_msgs, prediction_msgs (json)

MODE = "check"   reports problems, writes fix_resources_report_<lang>.csv (nothing is changed)
MODE = "fix"     applies the corrections below
MODE = "both"    fix, then check

CHECKS (text files): keys missing / extra, duplicate keys with different values, list lines with a different number of
    items, values identical to the English, Latin letters left (dxx_optiony_str / dn_*_str and codes are allowed),
    <br> / -> / numbers that differ from the English
CHECKS (json files): the structure against the English (same root keys, same lists lengths), and for every string
    UNTRANSLATED, TRUNCATED? (much shorter), SENTENCES? (fewer sentence endings), NUMBERS (a number is missing),
    MARKUP (<br> / &lt; / {placeholders} / <...> differ - also catches garbage such as "<ID 1>" the model invents)
    json keys are compared by POSITION, because inner keys without '_' are translated.
NUMBERS ignores ORDINALS (1st 2nd 3rd 4th ... 12th): many languages write them as words (Bodo: se-thi, nwi-thi, tham-thi),
    which would flag every house number. A real number (a year, 150, a yoga number such as 213) is still checked.
    Set IGNORE_ORDINALS = False to check them too.
list lines in msg_strings that also exist in list_values_<lang>.txt are NOT checked: the app reads them from list_values.

FIXES - three tables, each keyed by language; the file is never changed in structure:
    KEY_FIXES   {lang: {base: {key: "whole new value"}}}      text files; every line with that key is replaced
    WORD_FIXES  {lang: [(old, new), ...]}                     every string value of every file (keys are never touched):
                                                              the right tool for a wrong word the model used many times
    PATH_FIXES  {lang: {base: {"path/in/json": "new text"}}}  one json string, path = keys and list positions joined by '/'
Safety: a list line must keep the English item count; a fix may not add Latin letters; a fix that breaks a rule is
reported and not written. Keys, '#' lines, key order, line endings and BOM are kept. A backup <file>.bak is made ONCE
(never replaced, so the original is not lost). Running again changes nothing.

HOW TO RUN (VSCode: set LANG and MODE, press Run). The lang folder is taken from jhora, else this script's folder.
"""
import collections
import csv
import json
import os
import re
import shutil
import sys
import unicodedata

# ===================================================================================================
# CONFIGURATION
# ===================================================================================================
MODE = "both"                        # "check", "fix" or "both"
LANG = "doi"
BASES = ["msg_strings", "list_values", "amsa_rulers", "dosha_msgs", "raja_yoga_msgs", "yoga_msgs", "prediction_msgs"]
DRY_RUN = False
IGNORE_ORDINALS = True

KEY_FIXES = {
    # "mai": {"msg_strings": {"day_str": "..."}, "list_values": {"DAYS_LIST": "..."}},
}
WORD_FIXES = {
    "brx": [
        # three yoga numbers the model changed (the English says 213, 231, 294)
        ("233-5थि", "213-5थि"), ("211-जुदि 5थि", "231-जुदि 5थि"), ("295-अखाफोर आरो बुधआ", "294-अखाफोर आरो बुधआ"),
        # "pomegranates" became the garbage token <आइ. डि. 1>; अनार is the HINDI word - ask a Bodo reader for the Bodo one
        ("<आइ. डि. 1>", "अनार"),
        # planet and sign names the model spelt in English sounds: the same Sanskrit names the lists use
        ("मार्स", "मंगल"), ("सेटारन", "शनि"), ("जुपिटार", "बृहस्पति"),
        ("केटु", "केतु"), ("केथु", "केतु"), ("राहुल", "राहु"), ("राहुवा", "राहु"),
        ("एक्वेरियस", "कुंभ"), ("लिब्रा", "तुला"), ("स्कर्पिय'", "वृश्चिक"),
        # a stray space before the Bodo apostrophe: "न '" -> "न'"
        ("न '", "न'"), ("ल '", "ल'"),
        # optional - the model wrote 'lord' as इसोर 176 times and as लर्ड 31 times; remove the # to make it one word
        # ("लर्ड", "इसोर"),
    ],
}
PATH_FIXES = {
    # "ta": {"prediction_msgs": {"lord_of_a_house_joining_lord_of_another_house/1/0": "..."}},
}

# thresholds of the json checks
MIN_LEN_FOR_RATIO, LENGTH_RATIO_MIN = 80, 0.60
SENTENCE_RATIO_MIN, MIN_SENTENCES, LATIN_RATIO_MAX = 0.60, 3, 0.50
# ===================================================================================================

KEEP_ENGLISH = re.compile(r"^(?:d\d+_option\d+_str|dn_\w+_str)$")       # these values stay English by design
SHORT_KEY = re.compile(r"^\w+_short_str$")                              # abbreviations: Latin letters are fine
LIST_KEY = re.compile(r"^(?:[A-Z][A-Z0-9_]*|\w+_list)$")
LATIN_OK = re.compile(r"\(D\d+\)|\bD\d+\b|https?://\S+|\S+@\S+|\+/-\s*xx\.xxx|YYYY,MM,DD|HH:MM:SS|\bGMT\b|\bBC\b|\bAD\b|"
                      r"\bNone\b|\bN\b|\bDm\b|\bDn\b|\bcsv\b|\bPDF\b|\bID\b|\bDeepam\b|How to judge Horoscope|<br>|&lt;br&gt;|"
                      r"\bA\d+\b|\bAL\b|\bUL\b")
SENT_END = re.compile(r"[.!?\u0964\u0965\u06d4\u1c3e\uabeb](?=\s|$)")
MARKUP = re.compile(r"<[^>]+>|&[a-z]+;|\{[^}]*\}")
ORDINAL = re.compile(r"\d+\s?(?:st|nd|rd|th)\b", re.I)
ROOT_KEEP = {"source"}               # inner json keys that are never translated


def _folder():
    try:
        from jhora import const
        return const._LANGUAGE_PATH
    except Exception:
        return os.path.dirname(os.path.abspath(__file__)) + os.sep


def _find(folder, base, lang):
    for ext in (".txt", ".json"):
        p = os.path.join(folder, f"{base}_{lang}{ext}")
        if os.path.exists(p):
            return p
    return None


def _has_latin(s):
    return bool(re.search(r"[A-Za-z]", LATIN_OK.sub("", s)))


def _digits(s):
    return sorted(re.findall(r"\d+", "".join(str(unicodedata.digit(c)) if c.isdigit() else c for c in s)))


def _missing_numbers(en, tr):
    """Numbers of the English that are not in the translation (ordinals ignored when IGNORE_ORDINALS)."""
    e = ORDINAL.sub(" ", en) if IGNORE_ORDINALS else en
    e = re.sub(r"\(D\d+\)", " ", e)
    miss = _digits(e)
    for n in _digits(tr):
        if n in miss:
            miss.remove(n)
    return miss


def _read(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return (raw[3:] if bom else raw).decode("utf-8"), bom


def _write(path, text, bom):
    if DRY_RUN:
        return
    if os.path.exists(path) and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "wb") as f:
        f.write((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))


def _kv(line):
    body = line.rstrip("\r\n")
    if "=" in body and not body.lstrip().startswith("#"):
        k, v = body.split("=", 1)
        return k.strip(), v
    return None


def _text_rows(path):
    text, _ = _read(path)
    return [r for r in (_kv(l) for l in text.splitlines()) if r is not None]


# ---------------------------------------------------------------------------------------------------
# FIX
# ---------------------------------------------------------------------------------------------------
def fix_text(path, base, lang, en):
    keyfix = KEY_FIXES.get(lang, {}).get(base, {})
    words = WORD_FIXES.get(lang, [])
    text, bom = _read(path)
    lines = text.splitlines(keepends=True)
    changed, refused, seen = [], [], set()
    for i, raw in enumerate(lines):
        r = _kv(raw)
        if r is None or KEEP_ENGLISH.match(r[0]):
            continue
        k, value = r
        body = raw.rstrip("\r\n")
        eol = raw[len(body):]
        lead = value[:len(value) - len(value.lstrip())]
        new = None
        if k in keyfix:
            new = lead + keyfix[k]
            seen.add(k)
        elif words:
            cur = value
            for a, b in words:
                cur = cur.replace(a, b)
            new = cur if cur != value else None
        if new is None or new == value:
            continue
        if LIST_KEY.match(k) and k in en and new.count(",") != en[k].count(","):
            refused.append(f"{k}: {new.count(',') + 1} items, English has {en[k].count(',') + 1}")
            continue
        if _has_latin(new) and not _has_latin(value):
            refused.append(f"{k}: the fix would add Latin letters")
            continue
        lines[i] = f"{body.split('=', 1)[0]}={new}{eol}"
        changed.append(k)
    notes = [(f"{k}: kept in English by design (dxx_optiony_str / dn_*_str) - fix ignored" if KEEP_ENGLISH.match(k)
              else f"key not in the file (ignored): {k}") for k in keyfix if k not in seen]
    if changed:
        _write(path, "".join(lines), bom)
    return changed, refused + notes


def fix_json(path, base, lang):
    pathfix = PATH_FIXES.get(lang, {}).get(base, {})
    words = WORD_FIXES.get(lang, [])
    text, bom = _read(path)
    data = json.loads(text)
    changed, refused, used = [], [], set()

    def walk(node, p):
        if isinstance(node, dict):
            return {k: walk(v, p + [k]) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v, p + [str(i)]) for i, v in enumerate(node)]
        if isinstance(node, str):
            where = "/".join(p)
            new = node
            if where in pathfix:
                new = pathfix[where]
                used.add(where)
            else:
                for a, b in words:
                    new = new.replace(a, b)
            if new != node:
                if _has_latin(new) and not _has_latin(node):
                    refused.append(f"{where}: the fix would add Latin letters")
                    return node
                changed.append(where)
            return new
        return node

    out = walk(data, [])
    notes = [f"path not in the file (ignored): {w}" for w in pathfix if w not in used]
    if changed:
        _write(path, json.dumps(out, ensure_ascii=False, indent=4) + "\n", bom)
    return changed, refused + notes


# ---------------------------------------------------------------------------------------------------
# CHECK
# ---------------------------------------------------------------------------------------------------
def check_text(path, en_path, rows, dead_keys=frozenset()):
    f = os.path.basename(path)
    tr, en = _text_rows(path), (_text_rows(en_path) if en_path else [])
    tr_d, en_d = {}, {}
    for k, v in tr:
        tr_d.setdefault(k, v)
    for k, v in en:
        en_d.setdefault(k, v)
    if en_path:
        for k in en_d:
            if k not in tr_d:
                rows.append([f, k, "KEY MISSING", "in the English file, not here", "", ""])
        for k in tr_d:
            if k not in en_d:
                rows.append([f, k, "KEY EXTRA", "not in the English file (a misspelt key is never found by the app)", "", tr_d[k]])
    by = collections.defaultdict(list)
    for k, v in tr:
        by[k].append(v.strip())
    for k, v in by.items():
        if len(v) > 1 and len(set(v)) > 1:
            rows.append([f, k, "DUPLICATE KEY", "appears %d times with different values" % len(v), "", " | ".join(v)])
    for k, v in tr_d.items():
        e = en_d.get(k)
        if KEEP_ENGLISH.match(k) or e is None or k in dead_keys:
            continue
        if LIST_KEY.match(k) and e.count(",") != v.count(","):
            rows.append([f, k, "LIST ITEMS", f"{v.count(',') + 1} items, English has {e.count(',') + 1}", e, v])
        if not SHORT_KEY.match(k) and _has_latin(v):
            rows.append([f, k, "LATIN LEFT", "Latin letters still in the value", e, v])
        if v.strip() == e.strip() and re.search(r"[A-Za-z]{3}", e) and not SHORT_KEY.match(k):
            rows.append([f, k, "UNTRANSLATED", "identical to the English", e, v])
        if (e.count("<br>"), e.count("->")) != (v.count("<br>"), v.count("->")):
            rows.append([f, k, "MARKUP", "<br> or -> count differs", e, v])
        miss = _missing_numbers(e, v)
        if miss and not LIST_KEY.match(k):
            rows.append([f, k, "NUMBERS", "missing: " + ", ".join(miss), e, v])


def _pair_issues(e, t):
    out = []
    if not re.search(r"[^\W\d_]", e):
        return out
    if t.strip() == e.strip() and re.search(r"[A-Za-z]{3}", e):
        return [("UNTRANSLATED", "identical to the English")]
    letters = [c for c in t if c.isalpha()]
    if letters and sum("LATIN" in unicodedata.name(c, "") for c in letters) / len(letters) > LATIN_RATIO_MAX:
        out.append(("UNTRANSLATED", "mostly Latin letters"))
    if len(e) >= MIN_LEN_FOR_RATIO and len(t) < LENGTH_RATIO_MIN * len(e):
        out.append(("TRUNCATED?", f"length {len(t)} vs English {len(e)} ({len(t) / len(e):.0%})"))
    es, ts = len(SENT_END.findall(e)), len(SENT_END.findall(t))
    if es >= MIN_SENTENCES and ts < SENTENCE_RATIO_MIN * es:
        out.append(("SENTENCES?", f"{ts} sentence endings vs English {es}"))
    miss = _missing_numbers(e, t)
    if miss:
        out.append(("NUMBERS", "missing: " + ", ".join(miss)))
    if sorted(MARKUP.findall(e)) != sorted(MARKUP.findall(t)):
        out.append(("MARKUP", f"markup differs: English {MARKUP.findall(e)[:3]} vs {MARKUP.findall(t)[:3]}"))
    return out


def _walk(en, tr, path, depth, f, rows):
    where = "/".join(path)
    if isinstance(en, dict) and isinstance(tr, dict):
        ei, ti = list(en.items()), list(tr.items())
        if len(ei) != len(ti):
            rows.append([f, where, "STRUCTURE", f"{len(ei)} vs {len(ti)} keys", "", ""])
        for (ek, ev), (tk, tv) in zip(ei, ti):
            fixed = depth == 0 or "_" in ek or ek.isdigit() or ek.lower() in ROOT_KEEP
            if fixed and ek != tk:
                rows.append([f, where + "/" + ek, "STRUCTURE", f"key {ek!r} is {tk!r} here", ek, tk])
            _walk(ev, tv, path + [ek], depth + 1, f, rows)
    elif isinstance(en, list) and isinstance(tr, list):
        if len(en) != len(tr):
            rows.append([f, where, "STRUCTURE", f"{len(en)} vs {len(tr)} items", "", ""])
        for i, (ev, tv) in enumerate(zip(en, tr)):
            _walk(ev, tv, path + [str(i)], depth + 1, f, rows)
    elif isinstance(en, str) and isinstance(tr, str):
        if path and path[-1].lower() in ROOT_KEEP and depth > 1:
            return
        for issue, detail in _pair_issues(en, tr):
            rows.append([f, where, issue, detail, en, tr])
    elif type(en) is not type(tr):
        rows.append([f, where, "STRUCTURE", f"{type(en).__name__} vs {type(tr).__name__}", "", ""])


def check_json(path, en_path, rows):
    f = os.path.basename(path)
    if not en_path:
        rows.append([f, "", "NO ENGLISH", "no English reference file", "", ""])
        return
    _walk(json.loads(_read(en_path)[0]), json.loads(_read(path)[0]), [], 0, f, rows)


# ---------------------------------------------------------------------------------------------------
def main():
    kind = MODE.strip().lower()
    if kind not in ("check", "fix", "both"):
        sys.exit(f"MODE must be 'check', 'fix' or 'both', not {MODE!r}")
    folder = _folder()
    found = {b: _find(folder, b, LANG) for b in BASES}
    print(f"language {LANG!r}  MODE={kind}" + ("   [DRY RUN - nothing is written]" if DRY_RUN else ""))
    for b, p in found.items():
        if p is None:
            print(f"   {b}_{LANG}: not found - skipped")
    if kind in ("fix", "both"):
        print("\nFIX")
        for b, p in found.items():
            if p is None:
                continue
            en_p = _find(folder, b, "en")
            if p.endswith(".txt"):
                en = dict(_text_rows(en_p)) if en_p else {}
                changed, notes = fix_text(p, b, LANG, en)
            else:
                changed, notes = fix_json(p, b, LANG)
            print(f"   {os.path.basename(p)}: {len(changed)} corrected" + ("   [dry run]" if DRY_RUN and changed else ""))
            for n in notes:
                print("      ⚠️", n)
    if kind in ("check", "both"):
        rows = []
        lv = found.get("list_values")
        dead = {k for k, _ in _text_rows(lv)} if lv else set()      # these lists live in list_values, not in msg_strings
        for b, p in found.items():
            if p is None:
                continue
            en_p = _find(folder, b, "en")
            if p.endswith(".txt"):
                check_text(p, en_p, rows, dead if b == "msg_strings" else frozenset())
            else:
                check_json(p, en_p, rows)
        print("\nCHECK")
        per = collections.defaultdict(collections.Counter)
        for r in rows:
            per[r[0]][r[2]] += 1
        for b, p in found.items():
            if p is None:
                continue
            c = per[os.path.basename(p)]
            print(f"   {os.path.basename(p):32} " + ("no problems found" if not c else
                  "  ".join(f"{k} {n}" for k, n in sorted(c.items()))))
        out = os.path.join(folder, f"fix_resources_report_{LANG}.csv")
        with open(out, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows([["file", "key / path", "issue", "detail", "english", "translation"]] + rows)
        print(f"\nreport: {out}   (open in Excel; filter the issue column)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
