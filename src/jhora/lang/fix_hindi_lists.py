#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Corrects known errors in list_values_hi.txt (the source every transliterated language is generated from).

Three kinds of correction, all safe to run on an already-corrected file:
  LINES           a whole KEY=value line is replaced (item count checked)
  ITEM_FIXES      single items are replaced inside a line ("wrong item" -> "right item"); the item count never changes.
                  Items are compared after Unicode normalisation: ढ़ stored as one character (U+095D) and as ढ + nukta
                  (U+0922 U+093C) look identical but are different strings, and an exact comparison silently missed them.
  PREFIXED_NAMES  a list whose items start with a symbol (the rasi signs): the names are replaced, each item keeps its symbol
Everything else - other lines, '#' lines, line endings, a BOM - is kept. A backup <file>.bak is written once.
At the end every one of the 29 lists is checked (present once, right item count, no full list pasted over by its short list).

HOW TO RUN (VSCode: press Run). The file is looked up in the jhora lang folder, else next to this script.
"""
import os
import shutil
import sys
import unicodedata

FILE = "list_values_hi.txt"
DRY_RUN = False

NO = "कोई अंश नहीं"
_DEIT = "कामेश्वरी,भगमालिनी,नित्यक्लिन्ना,भेरुण्डा,वह्निवासिनी,महावज्रेश्वरी,शिवदूती,त्वरिता,कुलसुन्दरी,नित्या,नीलपताका,विजया,सर्वमङ्गला,ज्वालामालिनी".split(",")
_TS = "प्रति,द्विती,तृती,चतु,पञ्च,षष्ठी,सप्त,अष्ट,नव,दश,एका,द्वाद,त्रयो,चतुर्द".split(",")

LINES = {
    # the 27 yogas in their fixed order (Shukla was missing in older copies)
    "YOGAM_LIST": "विष्कम्भ,प्रीति,आयुष्मान,सौभाग्य,शोभन,अतिगण्ड,सुकर्मा,धृति,शूल,गण्ड,वृद्धि,ध्रुव,व्याघात,हर्षण,वज्र,सिद्धि,"
                  "व्यतीपात,वरीयान्,परिघ,शिव,सिद्ध,साध्य,शुभ,शुक्ल,ब्रह्म,इन्द्र,वैधृति",
    # karanas: Tamil-style spellings replaced by the Sanskrit names
    "KARANA_LIST": ",".join(["किंस्तुघ्न"] + ["बव", "बालव", "कौलव", "तैतिल", "गर", "वणिज", "विष्टि (भद्रा)"] * 8
                            + ["शकुनि", "चतुष्पद", "नाग"]),
    "RAASI_SHORT_LIST": "मे,वृष,मि,कर्क,सिं,कन्या,तु,वृश्चि,ध,मक,कुं,मी",
    "TITHI_SHORT_LIST": ",".join(_TS + ["पूर्णि"] + _TS + ["अमा"]),
    "TITHI_DEITIES": ",".join(_DEIT + ["षोडशी"] + _DEIT + ["चित्रा"]),
    # the -amsa names ended in -मांस ("flesh"), -मास ("month") or -मस
    "SHADVARGAMSA_NAMES": ",".join([NO, NO, "किंशुकांश", "व्यंजनांश", "चामरांश", "छत्रांश", "कुण्डलांश"]),
    "SAPTAVARGAMSA_NAMES": ",".join([NO, NO, "किंशुकांश", "व्यंजनांश", "चामरांश", "छत्रांश", "कुण्डलांश", "मुकुटांश"]),
    "DHASAVARGAMSA_NAMES": ",".join([NO, NO, "पारिजातांश", "उत्तमांश", "गोपुरांश", "सिंहासनांश", "पारावतांश", "देवलोकांश",
                                     "ब्रह्मलोकांश", "ऐरावतांश", "श्रीधामांश"]),
    "SHODASAVARGAMSA_NAMES": ",".join([NO, NO, "भेदकांश", "कुसुमांश", "नागपुरुषांश", "कन्दुकांश", "केरलांश", "कल्पवृक्षांश",
                                       "चन्दनवनांश", "पूर्णचन्द्रांश", "उच्चैःश्रवांश", "धन्वन्तर्यांश", "सूर्यकान्तांश",
                                       "विद्रुमांश", "इन्द्रासनांश", "गोलोकांश", "श्रीवल्लभांश"]),
}

ITEM_FIXES = {
    "NANAKSHAHI_MONTH_LIST": {"षाढ़": "आषाढ़"},
    "BHUKTHI_LIST": {"चंद्र भक्ति": "चंद्र भुक्ति", "रागु भुक्ति": "राहु भुक्ति"},
    "DHASA_LIST": {"रागु दशा": "राहु दशा"},
    "NAKSHATRA_LIST": {"म्रृगशीर्षा": "मृगशीर्षा", "अश्लेषा": "आश्लेषा"},
    "NAKSHATRA_SHORT_LIST": {"म्रृग": "मृग", "अश्ले": "आश्ले"},
    "YEAR_LIST": {"प्रभाव": "प्रभव", "प्रमोदूत": "प्रमोद", "वृषप्रजा": "वृष", "रक्तक्षी": "रक्ताक्षी",
                  "हेविळम्बि": "हेमलम्बि", "विळम्बि": "विलम्बि"},
    "ISLAMIC_MONTH_LIST": {"धू अल-क़ादा": "ज़ुल-क़ादा", "धू अल-हिज्जा": "ज़ुल-हिज्जा"},
}

# Lists whose items start with a symbol that must be kept while the name after it is replaced.
PREFIXED_NAMES = {
    "RAASI_LIST": ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
}

EXPECT_COUNT = {"YOGAM_LIST": 27, "KARANA_LIST": 60, "RAASI_SHORT_LIST": 12, "TITHI_SHORT_LIST": 30, "TITHI_DEITIES": 30,
                "SHADVARGAMSA_NAMES": 7, "SAPTAVARGAMSA_NAMES": 8, "DHASAVARGAMSA_NAMES": 11, "SHODASAVARGAMSA_NAMES": 17}

ALL_COUNTS = {"PLANET_NAMES": 12, "RAASI_LIST": 12, "NAKSHATRA_LIST": 28, "NAKSHATRA_SHORT_LIST": 28, "TITHI_LIST": 30,
              "KARANA_LIST": 60, "DAYS_LIST": 7, "PAKSHA_LIST": 2, "YOGAM_LIST": 27, "MONTH_LIST": 12, "YEAR_LIST": 60,
              "DHASA_LIST": 12, "BHUKTHI_LIST": 12, "PLANET_SHORT_NAMES": 12, "RAASI_SHORT_LIST": 12,
              "SHADVARGAMSA_NAMES": 7, "SAPTAVARGAMSA_NAMES": 8, "DHASAVARGAMSA_NAMES": 11, "SHODASAVARGAMSA_NAMES": 17,
              "SEASON_NAMES": 6, "TITHI_DEITIES": 30, "DAYS_SHORT_NAMES": 7, "TITHI_SHORT_LIST": 30, "MONTH_LIST_EN": 12,
              "MONTH_SHORT_LIST_EN": 12, "ISLAMIC_MONTH_LIST": 12, "NANAKSHAHI_MONTH_LIST": 12,
              "BANGLADESH_MONTH_LIST": 12, "NEPAL_BS_MONTH_LIST": 12}
# a full-name list must not equal its short-name list (a line pasted over the wrong key)
SHORT_PAIRS = [("RAASI_LIST", "RAASI_SHORT_LIST"), ("NAKSHATRA_LIST", "NAKSHATRA_SHORT_LIST"),
               ("PLANET_NAMES", "PLANET_SHORT_NAMES"), ("DAYS_LIST", "DAYS_SHORT_NAMES"), ("TITHI_LIST", "TITHI_SHORT_LIST")]

# letters with a nukta: the one-character form (U+0958..U+095F) is what the Hindi file uses
_PRECOMPOSED = {"\u0915\u093c": "\u0958", "\u0916\u093c": "\u0959", "\u0917\u093c": "\u095a", "\u091c\u093c": "\u095b",
                "\u0921\u093c": "\u095c", "\u0922\u093c": "\u095d", "\u092b\u093c": "\u095e", "\u092f\u093c": "\u095f"}


def _norm(s):
    """Comparison form: both spellings of a nukta letter become the same string."""
    return unicodedata.normalize("NFD", s)


def _one_char_nukta(s):
    """Writes nukta letters in their one-character form, like the rest of the file."""
    s = unicodedata.normalize("NFD", s)
    for k, v in _PRECOMPOSED.items():
        s = s.replace(k, v)
    return s


def _prefix(item):
    """The leading symbol characters of an item (everything before the first Devanagari letter)."""
    for i, ch in enumerate(item):
        if "\u0900" <= ch <= "\u097f":
            return item[:i]
    return item


def _folder():
    try:
        from jhora import const
        return const._LANGUAGE_PATH
    except Exception:
        return os.path.dirname(os.path.abspath(__file__)) + os.sep


def _check(lines):
    """Every one of the 29 lists present once with the right item count, and no full list overwritten by its short list."""
    d = {}
    for l in lines:
        b = l.rstrip("\r\n")
        if "=" in b and not b.lstrip().startswith("#"):
            k, v = b.split("=", 1)
            d.setdefault(k.strip(), []).append(v)
    out = []
    for k, n in ALL_COUNTS.items():
        if k not in d:
            out.append(f"{k}: line missing")
        elif len(d[k]) > 1:
            out.append(f"{k}: appears {len(d[k])} times")
        elif len(d[k][0].split(",")) != n:
            out.append(f"{k}: {len(d[k][0].split(','))} items, expected {n}")
    for full, short in SHORT_PAIRS:
        if full in d and short in d:
            strip = lambda x: "".join(c for c in x if "\u0900" <= c <= "\u097f" or c in " ./()-")
            fa = [strip(x) for x in d[full][0].split(",")]
            sa = [strip(x) for x in d[short][0].split(",")]
            same = sum(a == b and a != "" for a, b in zip(fa, sa))
            if same > len(fa) // 2:
                out.append(f"{full}: {same} of {len(fa)} items are the same as {short} - one may have been pasted over the other")
    return out


def main():
    path = os.path.join(_folder(), FILE)
    if not os.path.exists(path):
        print(f"❌ {path} not found.")
        return 1
    for k, v in LINES.items():
        if len(v.split(",")) != EXPECT_COUNT[k]:
            print(f"❌ internal error: {k} has {len(v.split(','))} items, expected {EXPECT_COUNT[k]} - nothing written.")
            return 1
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    lines = (raw[3:] if bom else raw).decode("utf-8").splitlines(keepends=True)
    fixes_n = {k: {_norm(a): b for a, b in v.items()} for k, v in ITEM_FIXES.items()}
    changed, notes, seen = [], [], set()
    for i, raw_line in enumerate(lines):
        body = raw_line.rstrip("\r\n")
        eol = raw_line[len(body):]
        if not body.strip() or body.lstrip().startswith("#") or "=" not in body:
            continue
        key, value = body.split("=", 1)
        k = key.strip()
        seen.add(k)
        new = value
        if k in LINES:
            new = LINES[k]
        if k in PREFIXED_NAMES:
            items, names = new.split(","), PREFIXED_NAMES[k]
            if len(items) == len(names):
                new = ",".join(_prefix(x) + n for x, n in zip(items, names))
        if k in fixes_n:
            new = ",".join(_one_char_nukta(fixes_n[k][_norm(x)]) if _norm(x) in fixes_n[k] else x for x in new.split(","))
        if new != value:
            if len(new.split(",")) != len(value.split(",")) and k not in EXPECT_COUNT:
                notes.append(f"{k}: item count changed - skipped")
                continue
            if k in EXPECT_COUNT and len(value.split(",")) != EXPECT_COUNT[k]:
                notes.append(f"{k}: had {len(value.split(','))} items, now {EXPECT_COUNT[k]}")
            lines[i] = f"{key}={new}{eol}"
            changed.append(k)
    print(f"{FILE}: {len(changed)} line(s) corrected")
    for k in changed:
        print("   ", k)
    for n in notes:
        print("   note:", n)
    for k in sorted(set(list(LINES) + list(ITEM_FIXES) + list(PREFIXED_NAMES)) - seen):
        print("   key not in the file (skipped):", k)
    problems = _check(lines)
    print("   final check:", "all lists OK" if not problems else "")
    for p in problems:
        print("   ⚠️", p)
    if changed and not DRY_RUN:
        if not os.path.exists(path + ".bak"):
            shutil.copy2(path, path + ".bak")
        with open(path, "wb") as f:
            f.write((b"\xef\xbb\xbf" if bom else b"") + "".join(lines).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
