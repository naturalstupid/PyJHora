import os
# Undo the startup SSL injection on this machine (pip._vendor.truststore replaces ssl.SSLContext
# globally, which makes ssl.py recurse forever on any HTTPS call). Must run before torch/transformers.
try:
    from pip._vendor.truststore import extract_from_ssl
    extract_from_ssl()
except Exception:
    pass
# Models are loaded from local folders, so never contact the Hub (no HTTPS needed at all).
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
import glob
import json
import re
import sys
import time
import types
from jhora import const
# ===================================================================================================
# CONFIGURATION
# ===================================================================================================
# Translation model: "nllb" (Meta NLLB-200) or "indictrans2" (AI4Bharat IndicTrans2, en -> Indic).
# Both use the same language codes (eng_Latn, ory_Orya, asm_Beng, pan_Guru ...).
MODEL_TYPE = "nllb"
# Local model folders (downloaded once by hand - see the notes at the end of this file).
MODEL_PATHS = {
    "nllb": r"C:\models\nllb-200-distilled-600M",                 # facebook/nllb-200-distilled-600M
    "indictrans2": r"C:\models\indictrans2-en-indic-dist-200M",   # ai4bharat/indictrans2-en-indic-dist-200M
}
# English source files (in const._LANGUAGE_PATH). Supported types:
#   .json  - every string value is translated.
#            Keys: ROOT-level keys are never translated. Inner keys are translated unless they contain
#            '_', are a number string ("1", "12") or are in JSON_KEY_EXCEPTIONS.
#   .txt   - "key=value" lines: only the value (text after the first '=') is translated; the key,
#            spaces, delimiters and symbols are kept. Lines starting with '#' are kept as they are.
# The output file name replaces "_en." with "_<LANG_SUFFIX>." (msg_strings_en.txt -> msg_strings_or.txt).
FILES = [
    "msg_strings_en.txt",
    #"list_values_en.txt",
    "amsa_rulers_en.json",
    "raja_yoga_msgs_en.json",
    "dosha_msgs_en.json",
    "yoga_msgs_en.json",
    "prediction_msgs_en.json",
]
# Language codes (same for NLLB and IndicTrans2) - see indian_22_languages.txt for the full list:
# Hindi: hin_Deva | Telugu: tel_Telu | Tamil: tam_Taml | Bengali: ben_Beng | Odia: ory_Orya
# Marathi: mar_Deva | Gujarati: guj_Gujr | Kannada: kan_Knda | Malayalam: mal_Mlym
# Assamese: asm_Beng | Punjabi: pan_Guru | Nepali: npi_Deva | Sanskrit: san_Deva
TARGET_LANG_CODE = "kas_Arab"
LANG_SUFFIX = "kaa"            # used in the output file names
SRC_LANG_CODE = "eng_Latn"
# To compare the two models on the same files without overwriting, set this to True: output files then
# get the model name too (msg_strings_or.indictrans2.txt). Rename the one you keep afterwards.
OUTPUT_WITH_MODEL_NAME = False
# One sentence -> translation cache per target language AND model, shared by all files. Saved after
# every batch, so a stopped run (Ctrl+C) resumes where it left off. Delete it to re-translate.
CACHE_FILE = const._LANGUAGE_PATH + f"sentence_cache_{LANG_SUFFIX}_{MODEL_TYPE}.json"
BATCH_SIZE = 8                # sentences per model call
NUM_BEAMS = 4                 # 1 = fastest, 4-5 = better quality (slower on CPU)
MAX_SENTENCE_TOKENS = 120     # a "sentence" longer than this (in source tokens) is split further at : ,
MAX_NEW_TOKENS_CAP = 400      # hard upper limit on the output length of one sentence
# --- .json rules ------------------------------------------------------------------------------------
# Inner keys that are never translated (in addition to keys with '_' and number strings). Their values
# are kept as they are too (e.g. "source": "ChinmayaAstrolger.com").
JSON_KEY_EXCEPTIONS = {"source"}
# --- .txt rules -------------------------------------------------------------------------------------
# A key is a comma-separated LIST (each item translated on its own, item count kept exactly) when it
# is all upper case (PLANET_NAMES, RAASI_LIST ...) or ends with "_list" (planet_separation_angle_list).
def is_list_key(key):
    return key.isupper() or key.lower().endswith("_list")
# Optional: regex of .txt keys whose values should be copied unchanged, e.g.
#   SKIP_KEY_RE = re.compile(r"_short")   # keep abbreviations like PLANET_SHORT_NAMES in English
# None = translate every value.
SKIP_KEY_RE = None
# Never translated, kept verbatim inside any value (.txt and .json): HTML tags / entities, URLs,
# e-mails, divisional chart codes (D9), option numbers "1->", number lists, format masks and
# astrology / zodiac symbols (☉ ♈︎ ℒ ...).
PROTECT_RE = re.compile(
    r"(&lt;[^&]*?&gt;|<[^>]+>|&[a-zA-Z]+;|https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+|\(D\d+\)|\bD\d+\b"
    r"|\d+\s*-(?:&gt;|>)|-(?:&gt;|>)|\d+(?:,\d+)+|YYYY,MM,DD|HH:MM:SS|\+/-\s*xx\.xxx"
    r"|[\u2100-\u214F\u2190-\u21FF\u2600-\u27BF\uFE0E\uFE0F]+)")
# --- Glossary: astrology terms never sent to the model ------------------------------------------
# English -> target terms are read from list_values_en.txt + list_values_<LANG_SUFFIX>.txt (same index),
# for the lists below. A text of at most GLOSSARY_MAX_WORDS words gets these terms replaced directly;
# longer sentences are translated whole (cutting them apart would break the grammar).
GLOSSARY_LISTS = ["PLANET_NAMES", "RAASI_LIST", "NAKSHATRA_LIST", "DAYS_LIST", "DHASA_LIST", "BHUKTHI_LIST"]
GLOSSARY_MAX_WORDS = 6
# Extra terms per language (not in list_values). Add a block for each language you translate.
MANUAL_GLOSSARY = {
    "ne": {"Dhasa": "दशा", "Dasa": "दशा", "Bhukthi": "भुक्ति", "Bhukti": "भुक्ति",
           "Lagna": "लग्न", "Antara": "अन्तर"},
}
# Abbreviations whose trailing '.' must NOT end a sentence.
_ABBREVIATIONS = ["B.V.", "e.g.", "i.e.", "viz.", "etc.", "Dr.", "Mr.", "Mrs.", "Ms.", "No.", "vs.", "cf.",
                  "St.", "Sri.", "Smt.", "approx.", "deg."]
# ===================================================================================================
# Model (loaded only when something needs translating)
# ===================================================================================================
_tokenizer = _model = _device = _BOS_ID = _indic_proc = None
def _model_path():
    if MODEL_TYPE not in MODEL_PATHS:
        raise ValueError(f"MODEL_TYPE must be one of {list(MODEL_PATHS)}, not '{MODEL_TYPE}'.")
    path = MODEL_PATHS[MODEL_TYPE]
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Model folder not found: {path} - download the model first "
                                f"(see the notes at the end of this script).")
    return path
def _patch_transformers_for_indictrans_toolkit():
    """IndicTransToolkit 1.1.1 was written for transformers 4.x and does
        from transformers.tokenization_utils import PreTrainedTokenizerBase
    which no longer works in transformers 5.x (the class lives elsewhere now). This makes that old
    import path work again, without changing the installed packages. Does nothing on transformers 4.x."""
    try:
        from transformers.tokenization_utils import PreTrainedTokenizerBase  # noqa: F401
        return
    except Exception:
        pass
    try:
        from transformers import PreTrainedTokenizerBase as base_cls
    except ImportError:
        from transformers.tokenization_utils_base import PreTrainedTokenizerBase as base_cls
    mod = sys.modules.get("transformers.tokenization_utils")
    if mod is None:
        try:
            import importlib
            mod = importlib.import_module("transformers.tokenization_utils")
        except Exception:
            mod = types.ModuleType("transformers.tokenization_utils")
            sys.modules["transformers.tokenization_utils"] = mod
    setattr(mod, "PreTrainedTokenizerBase", base_cls)
    print("   (applied transformers 5.x compatibility shim for IndicTransToolkit)")
def _import_indic_processor():
    try:
        import IndicTransToolkit  # noqa: F401
    except ModuleNotFoundError:
        raise ImportError("IndicTrans2 needs AI4Bharat's toolkit: python -m pip install IndicTransToolkit")
    except ImportError:
        # Installed, but failed to import - normally the transformers 5.x incompatibility.
        for name in [n for n in sys.modules if n.startswith("IndicTransToolkit")]:
            del sys.modules[name]
        _patch_transformers_for_indictrans_toolkit()
    try:
        from IndicTransToolkit.processor import IndicProcessor
    except ImportError:
        from IndicTransToolkit import IndicProcessor   # older toolkit layout
    return IndicProcessor
def _load_model():
    global _tokenizer, _model, _device, _BOS_ID, _indic_proc
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    path = _model_path()
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"⚙️ Loading {MODEL_TYPE} model from {path} onto {_device}...")
    if MODEL_TYPE == "nllb":
        _tokenizer = AutoTokenizer.from_pretrained(path, src_lang=SRC_LANG_CODE)
        _model = AutoModelForSeq2SeqLM.from_pretrained(path).to(_device)
        token_id = _tokenizer.convert_tokens_to_ids(TARGET_LANG_CODE)
        if token_id is None or token_id == getattr(_tokenizer, "unk_token_id", None):
            token_id = getattr(_tokenizer, "lang_code_to_id", {}).get(TARGET_LANG_CODE)
        if token_id is None:
            raise ValueError(f"Unknown NLLB language code '{TARGET_LANG_CODE}'.")
        _BOS_ID = token_id
    else:   # indictrans2
        IndicProcessor = _import_indic_processor()
        _indic_proc = IndicProcessor(inference=True)
        # trust_remote_code: IndicTrans2 ships its own model code inside the model folder.
        _tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        _model = AutoModelForSeq2SeqLM.from_pretrained(path, trust_remote_code=True).to(_device)
    _model.eval()
    try:
        _model.generation_config.max_length = None   # stops the max_length / max_new_tokens warning
    except Exception:
        pass
def _token_len(text):
    if _tokenizer is not None:
        try:
            return len(_tokenizer(text, add_special_tokens=False)["input_ids"])
        except Exception:
            pass
    return int(len(text.split()) * 1.4)          # rough word-based estimate
def _generate(inputs, max_new):
    """Runs generation. IndicTrans2's own model code does not work with the decoding cache in
    recent transformers 4.x ('NoneType' object has no attribute 'shape'), so it runs without it."""
    import torch
    kwargs = dict(max_new_tokens=max_new, num_beams=NUM_BEAMS, num_return_sequences=1)
    if MODEL_TYPE == "nllb":
        kwargs.update(forced_bos_token_id=_BOS_ID, no_repeat_ngram_size=4)
        use_cache = True
    else:
        use_cache = False
    with torch.no_grad():
        return _model.generate(**inputs, use_cache=use_cache, **kwargs)
def translate_batch(sentences):
    """Translates a batch of sentences locally (blocking; no network)."""
    if MODEL_TYPE == "nllb":
        inputs = _tokenizer(sentences, return_tensors="pt", padding=True, truncation=True,
                            max_length=512).to(_device)
    else:
        prepared = _indic_proc.preprocess_batch(sentences, src_lang=SRC_LANG_CODE, tgt_lang=TARGET_LANG_CODE)
        inputs = _tokenizer(prepared, truncation=True, padding="longest", max_length=512,
                            return_tensors="pt", return_attention_mask=True).to(_device)
    longest = int(inputs["attention_mask"].sum(dim=1).max())
    max_new = min(MAX_NEW_TOKENS_CAP, int(longest * 3) + 20)   # Indic output needs more tokens
    generated = _generate(inputs, max_new)
    decoded = _tokenizer.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    if MODEL_TYPE == "indictrans2":
        decoded = _indic_proc.postprocess_batch(decoded, lang=TARGET_LANG_CODE)
    return decoded
# ===================================================================================================
# Sentence splitting
# ===================================================================================================
_PROTECT = "\uE000"   # private-use placeholder for a '.' that must not end a sentence
def _split_sentences(text):
    t = text
    for abbr in _ABBREVIATIONS:
        t = t.replace(abbr, abbr.replace(".", _PROTECT))
    t = re.sub(r"(?<=\d)\.(?=\d)", _PROTECT, t)                 # 2.5
    t = re.sub(r"(?<=\b[A-Z])\.(?=\s*[A-Z]\.)", _PROTECT, t)    # initials: B. V.
    parts = re.split(r"(?<=[.?!;])\s+", t)
    return [p.replace(_PROTECT, ".").strip() for p in parts if p.strip()]
def _split_long(sentence):
    if _token_len(sentence) <= MAX_SENTENCE_TOKENS:
        return [sentence]
    pieces = re.split(r"(?<=[:,])\s+", sentence)
    chunks, cur = [], ""
    for p in pieces:
        cand = f"{cur} {p}".strip() if cur else p
        if cur and _token_len(cand) > MAX_SENTENCE_TOKENS:
            chunks.append(cur)
            cur = p
        else:
            cur = cand
    if cur:
        chunks.append(cur)
    return chunks
def segment(text):
    units = []
    for s in _split_sentences(text):
        units.extend(_split_long(s))
    return units or [text]
_LATIN = re.compile(r"[A-Za-z]")
# ===================================================================================================
# Glossary
# ===================================================================================================
GLOSSARY = {}
_ACTIVE_PROTECT_RE = PROTECT_RE
_SYM = re.compile(r"[\u2100-\u214F\u2190-\u21FF\u2600-\u27BF\uFE0E\uFE0F]")
def _read_lists(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8-sig") as f:
        for l in f:
            if "=" in l and not l.lstrip().startswith("#"):
                k, v = l.rstrip("\r\n").split("=", 1)
                out[k.strip()] = [_SYM.sub("", x).strip() for x in v.split(",")]
    return out
def _derive_suffix_terms(en_items, tr_items):
    """'Sun Dhasa' / 'सूर्य दशा' -> {'Dhasa': 'दशा'}; only if every pair agrees on the same last word."""
    found = {}
    for a, b in zip(en_items, tr_items):
        aw, bw = a.split(), b.split()
        if len(aw) < 2 or len(bw) < 2:
            return {}
        found.setdefault(aw[-1], set()).add(bw[-1])
    return {k: next(iter(v)) for k, v in found.items() if len(v) == 1}
def load_glossary():
    """Builds GLOSSARY (English term -> target term) and the protect regex that includes the terms."""
    global GLOSSARY, _ACTIVE_PROTECT_RE
    en = _read_lists(const._LANGUAGE_PATH + "list_values_en.txt")
    tr = _read_lists(const._LANGUAGE_PATH + f"list_values_{LANG_SUFFIX}.txt")
    g, skipped = {}, []
    for key in GLOSSARY_LISTS:
        e, t = en.get(key), tr.get(key)
        if not e or not t or len(e) != len(t):
            skipped.append(key)
            continue
        for a, b in zip(e, t):
            if a and b and _LATIN.search(a) and not _LATIN.search(b):   # only properly translated items
                g.setdefault(a, b)
    for key in ("DHASA_LIST", "BHUKTHI_LIST"):
        e, t = en.get(key), tr.get(key)
        if e and t and len(e) == len(t):
            for a, b in _derive_suffix_terms(e, t).items():
                g.setdefault(a, b)
    g.update(MANUAL_GLOSSARY.get(LANG_SUFFIX, {}))
    GLOSSARY = g
    if g:
        alt = "|".join(re.escape(k) for k in sorted(g, key=len, reverse=True))
        _ACTIVE_PROTECT_RE = re.compile(PROTECT_RE.pattern[:-1] + r"|\b(?:" + alt + r")\b)")
    print(f"📘 Glossary: {len(g)} terms" + (f" (lists skipped - missing or item count differs: {skipped})" if skipped else ""))

# ===================================================================================================
# Plans: what to translate in a piece of text, and how to put it back together
#   plan = list of ("keep", text) | ("tr", leading_ws, [units], trailing_ws)
# ===================================================================================================
def plan_text(text, units_out):
    """Splits `text` around protected tokens; every remaining piece containing Latin letters becomes
    sentences to translate (added to units_out). Whitespace around each piece is preserved.
    Short texts (labels, list items) also have their glossary terms replaced directly."""
    plan = []
    rx = _ACTIVE_PROTECT_RE if len(text.split()) <= GLOSSARY_MAX_WORDS else PROTECT_RE
    for i, piece in enumerate(rx.split(text)):
        if not piece:
            continue
        if i % 2 == 1 and piece in GLOSSARY:
            plan.append(("keep", GLOSSARY[piece]))
            continue
        if i % 2 == 1 or not _LATIN.search(piece):
            plan.append(("keep", piece))
            continue
        core = piece.strip()
        lead = piece[:len(piece) - len(piece.lstrip())]
        trail = piece[len(piece.rstrip()):]
        units = segment(core)
        for u in units:
            units_out.setdefault(u, None)
        plan.append(("tr", lead, units, trail))
    return plan
def render(plan, cache, list_item=False):
    out = []
    for step in plan:
        if step[0] == "keep":
            out.append(step[1])
            continue
        _, lead, units, trail = step
        text = " ".join(cache.get(u) or u for u in units).replace("\n", " ").strip()
        if list_item:
            text = re.sub(r"\s*,\s*", " ", text)   # a comma would change the item count of the list
        out.append(lead + text + trail)
    return "".join(out)
# ===================================================================================================
# .txt files ("key=value" lines)
# ===================================================================================================
def plan_txt(content, units_out):
    """Returns (lines, stats). Each line is ("keep", raw_line) or ("kv", key, kind, plan, eol)."""
    lines, stats = [], {"translated": 0, "skipped": 0, "comments_or_other": 0}
    for raw in content.splitlines(keepends=True):
        body = raw.rstrip("\r\n")
        eol = raw[len(body):]
        if not body.strip() or body.lstrip().startswith("#") or "=" not in body:
            lines.append(("keep", raw))
            stats["comments_or_other"] += 1
            continue
        key, value = body.split("=", 1)
        k = key.strip()
        if not _LATIN.search(value) or (SKIP_KEY_RE is not None and SKIP_KEY_RE.search(k)):
            lines.append(("keep", raw))
            stats["skipped"] += 1
            continue
        if is_list_key(k):
            lines.append(("kv", key, "list", [plan_text(it, units_out) for it in value.split(",")], eol))
        else:
            lines.append(("kv", key, "text", plan_text(value, units_out), eol))
        stats["translated"] += 1
    return lines, stats
def render_txt(lines, cache):
    out = []
    for ln in lines:
        if ln[0] == "keep":
            out.append(ln[1])
            continue
        _, key, kind, plan, eol = ln
        if kind == "list":
            value = ",".join(render(p, cache, list_item=True) for p in plan)
        else:
            value = render(plan, cache)
        out.append(f"{key}={value}{eol}")
    return "".join(out)
def _txt_pairs(content):
    return [l.split("=", 1) for l in content.splitlines()
            if l.strip() and not l.lstrip().startswith("#") and "=" in l]
# ===================================================================================================
# .json files
# ===================================================================================================
def _is_exception(key):
    return isinstance(key, str) and key.strip().lower() in {k.lower() for k in JSON_KEY_EXCEPTIONS}
def should_translate_key(key, depth):
    """Root-level keys (depth 0) are never translated. Inner keys are translated unless they contain
    '_', are a number string ("1", "12") or are in JSON_KEY_EXCEPTIONS."""
    if depth == 0:
        return False
    return isinstance(key, str) and not (key.strip().isdigit() or "_" in key or _is_exception(key))
def collect_strings(data, plans, units, depth=0):
    if isinstance(data, dict):
        for k, v in data.items():
            if should_translate_key(k, depth) and k not in plans:
                plans[k] = plan_text(k, units)
            if depth > 0 and _is_exception(k):
                continue                                  # exception key: value kept as it is
            collect_strings(v, plans, units, depth + 1)
    elif isinstance(data, list):
        for item in data:
            collect_strings(item, plans, units, depth + 1)
    elif isinstance(data, str) and data.strip() and data not in plans:
        plans[data] = plan_text(data, units)
def rebuild_json_tree(data, translated, depth=0):
    if isinstance(data, dict):
        return {(translated.get(k, k) if should_translate_key(k, depth) else k):
                (v if depth > 0 and _is_exception(k) else rebuild_json_tree(v, translated, depth + 1))
                for k, v in data.items()}
    if isinstance(data, list):
        return [rebuild_json_tree(item, translated, depth + 1) for item in data]
    if isinstance(data, str):
        return translated.get(data, data)
    return data
# ===================================================================================================
# Cache
# ===================================================================================================
def load_cache():
    cache = {}
    if MODEL_TYPE == "nllb":
        # Re-use sentences translated by earlier NLLB runs (before the cache name included the model).
        old = glob.glob(const._LANGUAGE_PATH + f"*_{LANG_SUFFIX}.json.sentence_cache.json")
        old.append(const._LANGUAGE_PATH + f"sentence_cache_{LANG_SUFFIX}.json")
        for path in old:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cache.update(json.load(f))
                except Exception:
                    pass
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache.update(json.load(f))
    return cache
def save_cache(cache):
    tmp = CACHE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE_FILE)
# ===================================================================================================
# Pipeline
# ===================================================================================================
def output_name(name):
    if "_en." not in name:
        raise ValueError(f"{name}: expected '_en.' in the file name")
    out = name.replace("_en.", f"_{LANG_SUFFIX}.")
    if OUTPUT_WITH_MODEL_NAME:
        stem, ext = os.path.splitext(out)
        out = f"{stem}.{MODEL_TYPE}{ext}"
    return out
def prepare(files):
    """Reads every input file and returns (jobs, all_units)."""
    jobs, units = [], {}
    for name in files:
        with open(const._LANGUAGE_PATH + name, "r", encoding="utf-8-sig", newline="") as f:
            content = f.read()
        if name.lower().endswith(".json"):
            data = json.loads(content)
            plans = {}
            collect_strings(data, plans, units)
            jobs.append(("json", name, data, plans))
            print(f"📖 {name}: {len(plans)} strings / keys to translate (root-level keys kept in English)")
        else:
            lines, stats = plan_txt(content, units)
            jobs.append(("txt", name, content, lines))
            print(f"📖 {name}: {stats['translated']} values to translate, {stats['skipped']} kept as is, "
                  f"{stats['comments_or_other']} comment / blank lines")
    return jobs, list(units)
def write_outputs(jobs, cache):
    for kind, name, src, plan in jobs:
        out_path = const._LANGUAGE_PATH + output_name(name)
        if kind == "json":
            translated = {s: render(p, cache) for s, p in plan.items()}
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(rebuild_json_tree(src, translated), f, ensure_ascii=False, indent=4)
        else:
            text = render_txt(plan, cache)
            with open(out_path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            # Safety check: same keys in the same order, same item count for every list.
            en, tr = _txt_pairs(src), _txt_pairs(text)
            if [k.strip() for k, _ in en] != [k.strip() for k, _ in tr]:
                print(f"⚠️ {out_path}: key order/count differs from the English file!")
            bad = [ek.strip() for (ek, ev), (_, tv) in zip(en, tr)
                   if is_list_key(ek.strip()) and ev.count(",") != tv.count(",")]
            if bad:
                print(f"⚠️ {out_path}: list item count differs for {bad}")
        print(f"🎉 Written: {out_path}")
def main():
    print(f"Model: {MODEL_TYPE}  |  {SRC_LANG_CODE} -> {TARGET_LANG_CODE}  |  cache: {CACHE_FILE}")
    load_glossary()
    jobs, all_units = prepare(FILES)
    cache = load_cache()
    todo = sorted((u for u in all_units if u not in cache), key=len)
    print(f"🎯 {len(all_units)} unique sentences ({len(all_units) - len(todo)} already in cache, "
          f"{len(todo)} to translate).")
    if todo:
        _load_model()
    total = (len(todo) + BATCH_SIZE - 1) // BATCH_SIZE
    start, failed = time.time(), 0
    for b, i in enumerate(range(0, len(todo), BATCH_SIZE), start=1):
        chunk = todo[i:i + BATCH_SIZE]
        try:
            for src, dst in zip(chunk, translate_batch(chunk)):
                cache[src] = dst
        except Exception as e:
            failed += len(chunk)
            print(f"❌ Batch {b} failed ({type(e).__name__}: {e}) - these sentences stay in English.")
        save_cache(cache)
        elapsed = time.time() - start
        print(f"🚀 Batch {b}/{total} done  |  elapsed {elapsed/60:.1f} min  |  "
              f"~{elapsed / b * (total - b) / 60:.1f} min left")
    write_outputs(jobs, cache)
    print(f"⏱️ Took {(time.time() - start)/60:.1f} min. Failed sentences: {failed}.")
if __name__ == "__main__":
    main()
# ===================================================================================================
# DOWNLOADING A MODEL (once, by hand - this script never downloads)
# ===================================================================================================
# The extract_from_ssl() part is needed on this machine because of the SSL recursion problem.
#
# NLLB (public):
#   python -c "from pip._vendor.truststore import extract_from_ssl; extract_from_ssl(); from huggingface_hub import snapshot_download; snapshot_download('facebook/nllb-200-distilled-600M', local_dir=r'C:\models\nllb-200-distilled-600M')"
#
# IndicTrans2 (gated - accept the terms on the model page first; first: python -m pip install IndicTransToolkit).
# In the same command window:   set HF_TOKEN=hf_...   (a Read token; delete it on huggingface.co afterwards)
#   python -c "from pip._vendor.truststore import extract_from_ssl; extract_from_ssl(); from huggingface_hub import snapshot_download; snapshot_download('ai4bharat/indictrans2-en-indic-dist-200M', local_dir=r'C:\models\indictrans2-en-indic-dist-200M')"
# Larger / better (slower on CPU): ai4bharat/indictrans2-en-indic-1B -> C:\models\indictrans2-en-indic-1B
