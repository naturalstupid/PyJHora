#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Creates resource files for SEVERAL languages by TRANSLITERATING the Hindi (Devanagari) files.

    INPUT_TYPE = "text"  ->  list_values_hi.txt   ->  list_values_<lang>.txt
    INPUT_TYPE = "json"  ->  amsa_rulers_hi.json  ->  amsa_rulers_<lang>.json
    INPUT_TYPE = "msg"   ->  msg_strings_hi.txt   ->  msg_strings_<lang>.txt        (NEW)
    INPUT_TYPE = "both"  ->  text + json (as before)
    INPUT_TYPE = "all"   ->  text + json + msg, in one run

Why transliterate and not translate: both files hold proper names (planets, rasis, nakshatras, tithis, years,
civil-calendar months, deities, sages, nadiamsas). A translation model turns them into ordinary words
("Mercury" -> metal, "Pisces" -> fish). The Hindi files have the correct names; converting them letter by letter
keeps them correct. English spelling is never used as a source (it is ambiguous: "Harh", "Chet" ...).

Rules
  text: '#' lines, blank lines and lines without '=' are copied unchanged; in "KEY=value" only the value is converted.
        ONLY_KEYS = None             -> the whole file is regenerated
        ONLY_KEYS = ["KEY", ...]     -> only those keys are updated / appended; every other line of an existing
                                        list_values_<lang>.txt stays exactly as it is (hand corrections are kept)
        LANGUAGE_OVERRIDES[lang][KEY] replaces a whole value (same number of items).
  json: keys ("2" ... "150") and the number of names in every list are kept.
  both: symbols (♈ ☉ ...), digits, Latin text and commas are kept, so item counts never change; a value whose item
        count would change keeps the Hindi text and is reported.
  A target whose script is "Devanagari" (mr, ne, sa ...) gets the Hindi text unchanged.
  A wrong script name stops that language (aksharamukha would otherwise return the Hindi text silently).
  An existing output file is backed up as <file>.bak before it is overwritten (the backup is made ONCE: a second run
  never replaces the first backup, so the original is not lost).
  msg:  msg_strings holds mixed text (Devanagari words + digits, <br>, ->, (D9), YYYY,MM,DD, URLs, symbols), so ONLY the
        Devanagari words of every value are converted; everything else is left exactly as it is (converting a whole
        line would turn 9 into ٩ for Perso-Arabic and every ',' into '،' for Urdu). The danda becomes the script's own
        full stop. MSG_OVERRIDES[lang][key] replaces one value (words that differ in that language). Keys, '#' lines,
        order, line endings and BOM are copied from the Hindi file; every output is checked (same keys in the same
        order, same number of ',' / <br> / ->, no Devanagari left) and is NOT written if a check fails.
        An existing msg_strings_<lang>.txt is NOT touched unless MSG_OVERWRITE_EXISTING = True (hand-corrected files!).

HOW TO RUN (VSCode: set INPUT_TYPE and TARGETS, press Run).  Needs:  python -m pip install aksharamukha
"""
import json
import os
import re
import shutil
import sys
import warnings

# ===================================================================================================
# CONFIGURATION
# ===================================================================================================
INPUT_TYPE = "all"                     # "text", "json", "msg", "both" (= text + json) or "all"

TEXT_SOURCE = "list_values_hi.txt"
JSON_SOURCE = "amsa_rulers_hi.json"
MSG_SOURCE = "msg_strings_hi.txt"

# aksharamukha script names. Ol Chiki = "Santali" (NOT "OlChiki"); Odia = "Oriya"; Punjabi = "Gurmukhi".
TARGETS = [
    #{"lang": "as",  "script": "Assamese"},
    #{"lang": "bn",  "script": "Bengali"},
    #{"lang": "gu",  "script": "Gujarati"},
    #{"lang": "ka",  "script": "Kannada"},
    #{"lang": "ml",  "script": "Malayalam"},
    #{"lang": "mr",  "script": "Devanagari"},
    #{"lang": "ne",  "script": "Devanagari"},
    #{"lang": "or",  "script": "Oriya"},
    #{"lang": "pa",  "script": "Gurmukhi"},
    #{"lang": "ta",  "script": "Tamil"},
    #{"lang": "te",  "script": "Telugu"},
    #{"lang": "ur",  "script": "Urdu"},
    #{"lang": "sat", "script": "Santali"},
    #{"lang": "kok", "script": "Devanagari"},
    #{"lang": "mai", "script": "Tirhuta"},
    #{"lang": "brx", "script": "Devanagari"},
    #{"lang": "doi", "script": "Dogra"},
    {"lang": "mni", "script": "MeeteiMayek"},
]

# text only: None = regenerate every key; a list = update/append only these keys
ONLY_KEYS = None # ["DAYS_LIST", "DAYS_SHORT_NAMES"]
# text only: whole values that differ in a language (same number of comma-separated items as the Hindi line)
LANGUAGE_OVERRIDES = {
    "doi": {
        "MONTH_LIST":            "चैत,बसाख,जेठ,आड़,सोन,पाद्रो,असु,कत्याल,मगेर,पोह,माघ,फगन",
        "NANAKSHAHI_MONTH_LIST": "चैत,बसाख,जेठ,आड़,सोन,पाद्रो,असु,कत्याल,मगेर,पोह,माघ,फगन",},
    "pa": {"DAYS_LIST":        "ਐਤਵਾਰ,ਸੋਮਵਾਰ,ਮੰਗਲਵਾਰ,ਬੁੱਧਵਾਰ,ਵੀਰਵਾਰ,ਸ਼ੁੱਕਰਵਾਰ,ਸ਼ਨੀਵਾਰ",
           "DAYS_SHORT_NAMES": "ਐਤ,ਸੋਮ,ਮੰਗਲ,ਬੁੱਧ,ਵੀਰ,ਸ਼ੁੱਕਰ,ਸ਼ਨੀ"},
    "ne": {"DAYS_LIST":        "आइतबार,सोमबार,मङ्गलबार,बुधबार,बिहीबार,शुक्रबार,शनिबार",
           "DAYS_SHORT_NAMES": "आइत,सोम,मङ्गल,बुध,बिही,शुक्र,शनि"},
    "mr": {"DAYS_LIST":        "रविवार,सोमवार,मंगळवार,बुधवार,गुरुवार,शुक्रवार,शनिवार",
           "DAYS_SHORT_NAMES": "रवि,सोम,मंगळ,बुध,गुरु,शुक्र,शनि"},
    "ta": {"DAYS_LIST":        "ஞாயிற்றுக்கிழமை,திங்கட்கிழமை,செவ்வாய்க்கிழமை,புதன்கிழமை,வியாழக்கிழமை,வெள்ளிக்கிழமை,சனிக்கிழமை",
           "DAYS_SHORT_NAMES": "ஞாயிறு,திங்கள்,செவ்வாய்,புதன்,வியாழன்,வெள்ளி,சனி"},
    "ml": {"DAYS_LIST":        "ഞായറാഴ്ച,തിങ്കളാഴ്ച,ചൊവ്വാഴ്ച,ബുധനാഴ്ച,വ്യാഴാഴ്ച,വെള്ളിയാഴ്ച,ശനിയാഴ്ച",
           "DAYS_SHORT_NAMES": "ഞായർ,തിങ്കൾ,ചൊവ്വ,ബുധൻ,വ്യാഴം,വെള്ളി,ശനി"},
    "te": {"DAYS_LIST":        "ఆదివారం,సోమవారం,మంగళవారం,బుధవారం,గురువారం,శుక్రవారం,శనివారం",
           "DAYS_SHORT_NAMES": "ఆది,సోమ,మంగళ,బుధ,గురు,శుక్ర,శని"},
    "ka": {"DAYS_LIST":        "ಭಾನುವಾರ,ಸೋಮವಾರ,ಮಂಗಳವಾರ,ಬುಧವಾರ,ಗುರುವಾರ,ಶುಕ್ರವಾರ,ಶನಿವಾರ",
           "DAYS_SHORT_NAMES": "ಭಾನು,ಸೋಮ,ಮಂಗಳ,ಬುಧ,ಗುರು,ಶುಕ್ರ,ಶನಿ"},
    "gu": {"DAYS_LIST":        "રવિવાર,સોમવાર,મંગળવાર,બુધવાર,ગુરુવાર,શુક્રવાર,શનિવાર",
           "DAYS_SHORT_NAMES": "રવિ,સોમ,મંગળ,બુધ,ગુરુ,શુક્ર,શનિ"},
    "or": {"DAYS_LIST":        "ରବିବାର,ସୋମବାର,ମଙ୍ଗଳବାର,ବୁଧବାର,ଗୁରୁବାର,ଶୁକ୍ରବାର,ଶନିବାର",
           "DAYS_SHORT_NAMES": "ରବି,ସୋମ,ମଙ୍ଗଳ,ବୁଧ,ଗୁରୁ,ଶୁକ୍ର,ଶନି"},
    "bn": {"DAYS_LIST":        "রবিবার,সোমবার,মঙ্গলবার,বুধবার,বৃহস্পতিবার,শুক্রবার,শনিবার",
           "DAYS_SHORT_NAMES": "রবি,সোম,মঙ্গল,বুধ,বৃহস্পতি,শুক্র,শনি"},
    "as": {"DAYS_LIST":        "দেওবাৰ,সোমবাৰ,মঙলবাৰ,বুধবাৰ,বৃহস্পতিবাৰ,শুক্ৰবাৰ,শনিবাৰ",
           "DAYS_SHORT_NAMES": "দেও,সোম,মঙল,বুধ,বৃহস্পতি,শুক্ৰ,শনি"},
    "ur": {"DAYS_LIST":        "اتوار,پیر,منگل,بدھ,جمعرات,جمعہ,ہفتہ",
           "DAYS_SHORT_NAMES": "اتوار,پیر,منگل,بدھ,جمعرات,جمعہ,ہفتہ"},
    "sat": {"DAYS_LIST":        "ᱥᱤᱸᱜᱤ ᱢᱟᱦᱟ,ᱚᱛᱮ ᱢᱟᱦᱟ,ᱵᱟᱞᱮ ᱢᱟᱦᱟ,ᱥᱟᱹᱜᱩᱱ ᱢᱟᱦᱟ,ᱥᱟᱹᱨᱫᱤ ᱢᱟᱦᱟ,ᱡᱟᱹᱨᱩᱢ ᱢᱟᱦᱟ,ᱧᱩᱦᱩᱢ ᱢᱟᱦᱟ",
            "DAYS_SHORT_NAMES": "ᱥᱤᱸᱜᱤ,ᱚᱛᱮ,ᱵᱟᱞᱮ,ᱥᱟᱹᱜᱩᱱ,ᱥᱟᱹᱨᱫᱤ,ᱡᱟᱹᱨᱩᱢ,ᱧᱩᱦᱩᱢ"},
}
# msg only: words that differ in a language, written in that language's own script: {lang: {key: value}}.
# A leading space of the Hindi value is kept. A key that is not in the file is reported, never added.
# Example (remove the # to use):   "kas": {"day_str": "<Kashmiri word for Day>"},
MSG_OVERRIDES = {
}
# msg only: False = a msg_strings_<lang>.txt that already exists is left alone (it may be hand-corrected).
MSG_OVERWRITE_EXISTING = True
DRY_RUN = False
# ===================================================================================================

_COMMA_GUARD = "\x01"                  # shields ',' (Urdu's transliterator rewrites it as '،')


def _lang_path():
    try:
        from jhora import const
        return const._LANGUAGE_PATH
    except Exception:
        return os.path.dirname(os.path.abspath(__file__)) + os.sep


def _convert(transliterate, text, script):
    """Converts Devanagari `text` to `script`; commas are kept; an unknown script raises."""
    if script == "Devanagari":
        return text
    if script == "Gurmukhi":           # Punjabi writes ष as ਸ਼ and ऋ / ृ as ਰਿ / ੍ਰਿ
        text = text.replace("ष", "श").replace("ृ", "्रि").replace("ऋ", "रि")
    # Tamil: drop the superscript numbers aksharamukha adds to tell ka/kha/ga/gha apart (Tamil does not write them)
    kwargs = {"post_options": ["TamilRemoveNumbers"]} if script == "Tamil" else {}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = transliterate.process("Devanagari", script, text.replace(",", _COMMA_GUARD), **kwargs)
    return out.replace(_COMMA_GUARD, ",")


def _backup_and_write(path, text):
    if DRY_RUN:
        return
    if os.path.exists(path) and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


# ---------------------------------------------------------------------------------------------------
# text: list_values
# ---------------------------------------------------------------------------------------------------
def _text_one(transliterate, folder, content, lang, script):
    overrides = LANGUAGE_OVERRIDES.get(lang, {})
    warn, out_lines, new_by_key, comment_of, last_comment = [], [], {}, {}, None
    for raw in content.splitlines(keepends=True):
        body = raw.rstrip("\r\n")
        eol = raw[len(body):]
        if not body.strip() or body.lstrip().startswith("#") or "=" not in body:
            out_lines.append(raw)
            if body.lstrip().startswith("#"):
                last_comment = body
            continue
        key, value = body.split("=", 1)
        k = key.strip()
        if ONLY_KEYS is not None and k not in ONLY_KEYS:
            out_lines.append(raw)
            last_comment = None
            continue
        new = _convert(transliterate, value, script)
        if k in overrides:
            if overrides[k].count(",") == value.count(","):
                new = overrides[k]
                if lang in ("doi","mai") and script != "Devanagari":
                    new = _convert(transliterate, new, script)
            else:
                warn.append(f"{k}: override has a different item count - skipped")
        if new.count(",") != value.count(","):
            warn.append(f"{k}: item count changed - Hindi value kept, please fix by hand")
            new = value
        out_lines.append(f"{key}={new}{eol}")
        new_by_key[k] = f"{key}={new}"
        if last_comment is not None:
            comment_of[k] = last_comment
        last_comment = None
    path = os.path.join(folder, f"list_values_{lang}.txt")
    if ONLY_KEYS is None:
        _backup_and_write(path, "".join(out_lines))
        return path, f"{len(new_by_key)} keys (whole file)", warn
    # merge only ONLY_KEYS into an existing file
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            existing = f.read()
        nl = "\r\n" if "\r\n" in existing else "\n"
        lines = existing.splitlines(keepends=True)
    else:
        nl, lines = "\n", []
    pending, replaced, added = dict(new_by_key), [], []
    for i, raw in enumerate(lines):
        body = raw.rstrip("\r\n")
        if "=" in body and not body.lstrip().startswith("#"):
            k = body.split("=", 1)[0].strip()
            if k in pending:
                lines[i] = pending.pop(k) + (raw[len(body):] or nl)
                replaced.append(k)
    if pending:
        if lines and not lines[-1].endswith(("\n", "\r")):
            lines[-1] += nl
        for k, line in pending.items():
            lines.append(comment_of.get(k, "### " + k) + nl)
            lines.append(line + nl)
            added.append(k)
    _backup_and_write(path, "".join(lines))
    return path, f"{len(added)} added, {len(replaced)} updated, other lines untouched", warn


# ---------------------------------------------------------------------------------------------------
# json: amsa_rulers
# ---------------------------------------------------------------------------------------------------
def _json_one(transliterate, folder, src, lang, script):
    out = {k: [_convert(transliterate, n, script) for n in v] for k, v in src.items()}
    bad = [k for k in src if len(out[k]) != len(src[k])]
    if bad:
        raise ValueError(f"list lengths changed for keys {bad}")
    path = os.path.join(folder, f"amsa_rulers_{lang}.json")
    _backup_and_write(path, json.dumps(out, ensure_ascii=False, indent=4) + "\n")
    return path, f"{len(out)} keys, {sum(len(v) for v in out.values())} names", []


# ---------------------------------------------------------------------------------------------------
# msg: msg_strings (mixed text - only the Devanagari words are converted)
# ---------------------------------------------------------------------------------------------------
_DEV_RUN = re.compile("[\u0900-\u0963\u0966-\u097f\u200c\u200d]+")
_DANDA = re.compile("[\u0964\u0965]")
_FULL_STOP = {"Arab-Pa": "\u06d4", "Urdu": "\u06d4"}      # aksharamukha returns an ASCII '.' for Perso-Arabic


def _word(transliterate, text, script, cache):
    if text not in cache:
        t = text
        if script == "Gurmukhi":
            t = t.replace("\u0937", "\u0936").replace("\u0943", "\u094d\u0930\u093f").replace("\u090b", "\u0930\u093f")
        kwargs = {"post_options": ["TamilRemoveNumbers"]} if script == "Tamil" else {}
        with warnings.catch_warnings():
            warnings.simplefilter("error")                # an unknown script name must stop, not silently return Hindi
            cache[text] = transliterate.process("Devanagari", script, t, **kwargs)
    return cache[text]


def _msg_value(transliterate, value, script, cache):
    """Converts only the Devanagari words of `value`; digits, Latin text, punctuation, markup, symbols stay as they are."""
    if script == "Devanagari":
        return value
    out = _DEV_RUN.sub(lambda m: _word(transliterate, m.group(0), script, cache), value)
    stop = _FULL_STOP.get(script)
    if stop is not None:
        return _DANDA.sub(stop, out)
    return _DANDA.sub(lambda m: _word(transliterate, m.group(0), script, cache), out)


def _kv_key(body):
    return body.split("=", 1)[0].strip() if ("=" in body and not body.lstrip().startswith("#")) else None


def _msg_one(transliterate, folder, src, lang, script):
    path = os.path.join(folder, f"msg_strings_{lang}.txt")
    if os.path.exists(path) and not MSG_OVERWRITE_EXISTING:
        return path, "skipped - file exists (MSG_OVERWRITE_EXISTING = True replaces it, with a .bak)", []
    overrides = MSG_OVERRIDES.get(lang, {})
    bom = src.startswith(b"\xef\xbb\xbf")
    text = (src[3:] if bom else src).decode("utf-8")
    cache, seen, problems, out, keys_in = {}, set(), [], [], []
    n_conv = 0
    for raw in text.splitlines(keepends=True):
        body = raw.rstrip("\r\n")
        eol = raw[len(body):]
        k = _kv_key(body)
        if k is None:
            out.append(raw)
            continue
        key, value = body.split("=", 1)
        lead = value[:len(value) - len(value.lstrip())]
        if k in overrides:
            new = lead + overrides[k]
            seen.add(k)
        else:
            new = _msg_value(transliterate, value, script, cache)
            n_conv += new != value
            for tok in (",", "<br>", "->"):
                if value.count(tok) != new.count(tok):
                    problems.append(f"{k}: the number of '{tok}' changed")
        if script != "Devanagari" and re.search("[\u0900-\u0963\u0966-\u097f]", new):      # the danda U+0964 is shared by Gurmukhi / Bengali / Odia
            problems.append(f"{k}: Devanagari left in the value")
        keys_in.append(k)
        out.append(f"{key}={new}{eol}")
    missing = [k for k in overrides if k not in seen]
    data = "".join(out).encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    notes = [f"override key not in the file (ignored): {k}" for k in missing]
    if problems:
        return path, f"NOT written - {len(problems)} problem(s)", problems[:15] + notes
    if not DRY_RUN:
        if os.path.exists(path) and not os.path.exists(path + ".bak"):
            shutil.copy2(path, path + ".bak")
        with open(path, "wb") as f:
            f.write(data)
    return path, f"{len(keys_in)} keys, {n_conv} converted, {len(seen)} override(s)", notes


# ---------------------------------------------------------------------------------------------------
def main():
    try:
        from aksharamukha import transliterate
    except ImportError:
        sys.exit("Needs aksharamukha:  python -m pip install aksharamukha")
    kind = INPUT_TYPE.strip().lower()
    if kind not in ("text", "json", "msg", "both", "all"):
        sys.exit(f"INPUT_TYPE must be 'text', 'json', 'msg', 'both' or 'all', not {INPUT_TYPE!r}")
    folder = _lang_path()
    needed = {"text": TEXT_SOURCE, "json": JSON_SOURCE, "msg": MSG_SOURCE}
    wanted = {"text": ("text", "both", "all"), "json": ("json", "both", "all"), "msg": ("msg", "all")}
    for part, name in needed.items():
        if kind in wanted[part] and not os.path.exists(os.path.join(folder, name)):
            sys.exit(f"{name} not found in {folder} - INPUT_TYPE={kind!r} needs it.")
    jobs = []
    if kind in ("text", "both", "all"):
        with open(os.path.join(folder, TEXT_SOURCE), encoding="utf-8-sig", newline="") as f:
            jobs.append(("text", TEXT_SOURCE, f.read(), _text_one))
    if kind in ("json", "both", "all"):
        with open(os.path.join(folder, JSON_SOURCE), encoding="utf-8-sig") as f:
            jobs.append(("json", JSON_SOURCE, json.load(f), _json_one))
    if kind in ("msg", "all"):
        with open(os.path.join(folder, MSG_SOURCE), "rb") as f:
            jobs.append(("msg", MSG_SOURCE, f.read(), _msg_one))
    print(f"INPUT_TYPE={kind}  ->  {len(TARGETS)} language(s)" + ("   [DRY RUN - nothing written]" if DRY_RUN else ""))
    total_warn = 0
    for _, source, data, fn in jobs:
        print(f"\n{source}")
        for t in TARGETS:
            lang, script = t["lang"], t["script"]
            try:
                path, detail, warn = fn(transliterate, folder, data, lang, script)
            except Exception as e:
                print(f"   {lang:4} ({script}): SKIPPED - {type(e).__name__}: {e}  (check the script name)")
                total_warn += 1
                continue
            print(f"   {lang:4} ({script:10}) -> {os.path.basename(path)}  {detail}")
            for w in warn:
                print(f"        ⚠️ {w}")
            total_warn += len(warn)
    print(f"\nDone, {total_warn} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
