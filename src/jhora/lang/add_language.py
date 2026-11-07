#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Registers a new UI language in PyJHora (run AFTER transliterate_resources.py has created msg_strings_<code>.txt).

Does the three manual steps:
  1. const.py              : adds  'Name':'code'  to available_languages = {...}
  2. factory_settings.json : adds  ["code", "Name"]  to "language" -> "choices"
  3. every msg_strings_<lang>.txt : adds (or updates) the last line  <name>_str=<name of the new language in that language>

Where the name in each language comes from (in this order):
  a. LOCAL_NAMES[lang]            a name you typed - always wins
  b. "en"                         NEW_NAME
  c. a language in SCRIPT_OF      NEW_NAME_DEVANAGARI transliterated into that language's script with aksharamukha
                                  (a Devanagari language gets it unchanged). A DRAFT: spelling conventions such as a short
                                  or long final vowel (ಕೊಂಕಣಿ / ಕೋಂಕಣೀ) are for a native reader to settle - correct it in LOCAL_NAMES
  d. anything else                NEW_NAME in English, with a warning
Why the Devanagari name and not the English one: aksharamukha converts between Indic scripts letter by letter. English
spelling does not say which letters were meant (Konkani -> கொன்கனி is wrong), and a translation model gets proper
names wrong. The names actually used are printed as a LOCAL_NAMES dict at the end - correct any, paste it into
LOCAL_NAMES and run again (a changed name replaces the line, nothing is added twice).

Safe to run again. A backup <file>.bak is made ONCE per file (never replaced). DRY_RUN = True prints what would change.
Needs:  python -m pip install aksharamukha      (only when a name has to be transliterated)
"""
import ast
import glob
import json
import os
import re
import shutil
import warnings

# ===================================================================================================
# CONFIGURATION - edit for each new language
# ===================================================================================================
NEW_CODE = "kaa"
NEW_NAME = "Kashmiri_Urdu"                       # English display name used by the UI
NEW_NAME_DEVANAGARI = "कश्मीरी_उर्दू"              # the language's name written in Devanagari (the source of the transliterations)
LOCAL_NAMES = {                             # optional: names you checked, per language code; they always win
    # "ta": "மைதிலி",
}
RESOURCE_KEY = "kashmiri_urdu_str" # NEW_NAME.lower() + "_str"    # e.g. maithili_str

# aksharamukha script of every language that has (or will have) a msg_strings file. "Devanagari" = the name is used unchanged.
# Sindhi: Devanagari here; use "Arab-Pa" if you write Sindhi in Perso-Arabic.
SCRIPT_OF = {
    "as": "Assamese", "bn": "Bengali", "gu": "Gujarati", "ka": "Kannada", "ml": "Malayalam", "or": "Oriya",
    "pa": "Gurmukhi", "ta": "Tamil", "te": "Telugu", "ur": "Urdu", "sat": "Santali", "kas": "Arab-Pa", "mni": "MeeteiMayek",
    "hi": "Devanagari", "mr": "Devanagari", "ne": "Devanagari", "sa": "Devanagari", "kok": "Devanagari",
    "mai": "Devanagari", "doi": "Devanagari", "brx": "Devanagari", "snd": "Devanagari", "doi": "Devanagari",
    "mni":"MeeteiMayek", "kaa":"Urdu",
}
STRIP_ARABIC_MARKS = True                   # Urdu / Perso-Arabic: drop the short-vowel signs (everyday writing leaves them out)
FACTORY_SETTINGS_FILE = None                # None = search for factory_settings.json under the jhora package
DRY_RUN = False
# ===================================================================================================

from jhora import const

_ARABIC_MARKS = re.compile("[\u064b-\u065f\u0670]")
_RESOURCE_FILES = ("msg_strings_{}.txt", "list_values_{}.txt", "amsa_rulers_{}.json", "dosha_msgs_{}.json",
                   "raja_yoga_msgs_{}.json", "yoga_msgs_{}.json", "prediction_msgs_{}.json")


def _backup_and_write(path, text):
    if DRY_RUN:
        print(f"   (dry run - {path} not written)")
        return
    if os.path.exists(path) and not os.path.exists(path + ".bak"):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _read(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        text = f.read()
    return text, ("\r\n" if "\r\n" in text else "\n")


def _matching_close(text, open_idx):
    """Index of the bracket closing text[open_idx] ('{' or '['), skipping quoted strings."""
    pairs = {"{": "}", "[": "]"}
    stack, i, quote = [], open_idx, None
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c in pairs:
            stack.append(pairs[c])
        elif stack and c == stack[-1]:
            stack.pop()
            if not stack:
                return i
        i += 1
    raise ValueError("unbalanced brackets")


def _insert_before_close(text, close_idx, item):
    """Inserts `item` as the last element before the closing bracket at close_idx."""
    head = text[:close_idx].rstrip()
    tail_ws = text[len(head):close_idx]
    sep = "" if head.endswith((",", "{", "[")) else ","
    return head + sep + item + tail_ws + text[close_idx:]


# ---------------------------------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------------------------------
def transliterate_name(script):
    """NEW_NAME_DEVANAGARI written in `script`. Raises if aksharamukha does not know the script."""
    if script == "Devanagari":
        return NEW_NAME_DEVANAGARI
    from aksharamukha import transliterate
    text = NEW_NAME_DEVANAGARI
    if script == "Gurmukhi":                       # same clean-up as transliterate_resources.py
        text = text.replace("ष", "श").replace("ृ", "्रि").replace("ऋ", "रि")
    kwargs = {"post_options": ["TamilRemoveNumbers"]} if script == "Tamil" else {}
    with warnings.catch_warnings():
        warnings.simplefilter("error")             # an unknown script name must stop, not silently return Devanagari
        out = transliterate.process("Devanagari", script, text, **kwargs)
    if STRIP_ARABIC_MARKS and script in ("Urdu", "Arab-Pa"):
        out = _ARABIC_MARKS.sub("", out)
    return out.strip()


def resolve_names(codes):
    """Returns ({code: name}, {code: how}) for every msg_strings language code."""
    names, how = {}, {}
    for code in codes:
        if code in LOCAL_NAMES:
            names[code], how[code] = LOCAL_NAMES[code], "manual"
        elif code == "en":
            names[code], how[code] = NEW_NAME, "English"
        elif code in SCRIPT_OF:
            try:
                names[code], how[code] = transliterate_name(SCRIPT_OF[code]), "transliterated (draft)"
            except ImportError:
                names[code], how[code] = NEW_NAME, "FALLBACK"
                print(f"   ⚠️ {code}: aksharamukha is not installed (python -m pip install aksharamukha) - using '{NEW_NAME}'")
            except Exception as e:
                names[code], how[code] = NEW_NAME, "FALLBACK"
                print(f"   ⚠️ {code}: script {SCRIPT_OF[code]!r} failed ({type(e).__name__}) - using '{NEW_NAME}'")
        else:
            names[code], how[code] = NEW_NAME, "FALLBACK"
            print(f"   ⚠️ {code}: not in SCRIPT_OF and not in LOCAL_NAMES - using '{NEW_NAME}'")
    return names, how


# ---------------------------------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------------------------------
def step1_const():
    path = const.__file__
    print(f"1. {path}")
    text, _ = _read(path)
    m = re.search(r"^available_languages\s*=\s*\{", text, re.M)
    if not m:
        print("   ⚠️ 'available_languages = {' not found - add it by hand.")
        return
    open_idx = m.end() - 1
    close_idx = _matching_close(text, open_idx)
    langs = ast.literal_eval(text[open_idx:close_idx + 1])
    if NEW_CODE in langs.values() or NEW_NAME in langs:
        print(f"   already present: {langs}")
        return
    new_text = _insert_before_close(text, close_idx, f" '{NEW_NAME}':'{NEW_CODE}'")
    new_close = _matching_close(new_text, open_idx)
    assert ast.literal_eval(new_text[open_idx:new_close + 1])[NEW_NAME] == NEW_CODE
    print(f"   added '{NEW_NAME}':'{NEW_CODE}'")
    _backup_and_write(path, new_text)


def _find_factory_settings():
    if FACTORY_SETTINGS_FILE:
        return FACTORY_SETTINGS_FILE
    root = os.path.dirname(os.path.dirname(os.path.abspath(const.__file__)))
    hits = glob.glob(os.path.join(root, "**", "factory_settings.json"), recursive=True)
    if len(hits) != 1:
        raise FileNotFoundError(f"factory_settings.json: found {hits or 'none'} - set FACTORY_SETTINGS_FILE.")
    return hits[0]


def step2_factory_settings():
    path = _find_factory_settings()
    print(f"2. {path}")
    text, nl = _read(path)
    choices = json.loads(text)["language"]["choices"]
    if any(c[0] == NEW_CODE for c in choices):
        print(f"   already present: {[c for c in choices if c[0] == NEW_CODE][0]}")
        return
    # Edit the text (not json.dump) so the rest of the file keeps its exact formatting.
    lang = re.search(r'"language"\s*:\s*\{', text)
    ch = re.compile(r'"choices"\s*:\s*\[').search(text, lang.end())
    open_idx = ch.end() - 1
    close_idx = _matching_close(text, open_idx)
    last_line = text[:close_idx].rstrip().rsplit("\n", 1)[-1]
    indent = last_line[:len(last_line) - len(last_line.lstrip())]
    new_text = _insert_before_close(text, close_idx,
                                    f"{nl}{indent}{json.dumps([NEW_CODE, NEW_NAME], ensure_ascii=False)}")
    assert [NEW_CODE, NEW_NAME] in json.loads(new_text)["language"]["choices"]   # still valid JSON
    print(f'   added ["{NEW_CODE}", "{NEW_NAME}"]')
    _backup_and_write(path, new_text)


def step3_msg_strings():
    # Only real language files (msg_strings_ta.txt), not leftovers such as msg_strings_pa_IT.txt.
    files = {}
    for path in sorted(glob.glob(os.path.join(const._LANGUAGE_PATH, "msg_strings_*.txt"))):
        m = re.fullmatch(r"msg_strings_([A-Za-z]+)\.txt", os.path.basename(path))
        if m:
            files[m.group(1)] = path
    print(f"3. {len(files)} msg_strings files in {const._LANGUAGE_PATH}: {list(files)}")
    names, how = resolve_names(list(files))
    key_re = re.compile(rf"^[ \t]*{re.escape(RESOURCE_KEY)}[ \t]*=[^\r\n]*", re.M)
    for code, path in files.items():
        text, nl = _read(path)
        line = f"{RESOURCE_KEY}={names[code]}"
        found = key_re.search(text)
        if found:
            if found.group(0).strip() == line:
                print(f"   {code}: already has {line}")
                continue
            new_text = text[:found.start()] + line + text[found.end():]
            print(f"   {code}: updated -> {line}   ({how[code]})")
        else:
            new_text = text + ("" if not text or text.endswith(("\n", "\r")) else nl) + line + nl
            print(f"   {code}: added   {line}   ({how[code]})")
        _backup_and_write(path, new_text)
    # Ready-to-paste dict: correct any wrong name, paste into LOCAL_NAMES above and run again.
    print("\n   Names used (paste into LOCAL_NAMES to correct and re-run):")
    print("   LOCAL_NAMES = {")
    for code in files:
        print(f'       "{code}": "{names[code]}",   # {how[code]}')
    print("   }")


def check_nls_files():
    missing = [f.format(NEW_CODE) for f in _RESOURCE_FILES
               if not os.path.exists(os.path.join(const._LANGUAGE_PATH, f.format(NEW_CODE)))]
    if missing:
        print(f"⚠️ resource files not found for '{NEW_CODE}': {missing}")


if __name__ == "__main__":
    print(f"Adding language {NEW_NAME} ({NEW_CODE}), resource key {RESOURCE_KEY}" + ("   [DRY RUN]" if DRY_RUN else ""))
    check_nls_files()
    for step in (step1_const, step2_factory_settings, step3_msg_strings):
        try:
            step()
        except Exception as e:
            print(f"   ❌ {type(e).__name__}: {e}")
    print("Done. Restart the app to see the new language.")
