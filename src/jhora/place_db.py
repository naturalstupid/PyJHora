import csv
import os
import pickle
import sqlite3
import time
import unicodedata
import re
import shutil
import urllib.request
import urllib.error
from dataclasses import dataclass, field

from jhora import const
_ENGINE_DISPLAY_LABELS = {
    "NONE": "NONE",

    "CSV_5K" : "CSV (Population > 5000)",
    "SQLITE_5K" : "SQLITE (Population > 5000)",
    "PICKLE_5K" : "PICKLE (Population > 5000)",

    "CSV_5K_IN" : "CSV (Population > 5000, India >= 0)",
    "PICKLE_5K_IN" : "PICKLE (Population > 5000, India >= 0)",
    "SQLITE_5K_IN" : "SQLITE (Population > 5000, India >= 0)",

    "CSV_500" : "CSV (Population > 500)",
    "PICKLE_500" : "PICKLE (Population > 500)",
    "SQLITE_500" : "SQLITE (Population > 500)",

    "CSV_500_IN" : "CSV (Population > 500, India >= 0)",
    "PICKLE_500_IN" : "PICKLE (Population > 500, India >= 0)",
    "SQLITE_500_IN" : "SQLITE (Population > 500, India >= 0)",
}

# ============================================================
# CONFIG
# ============================================================
ALT_NAME_SEPARATOR = "|"
DEBUG_WORLD_CITY_LOAD = False
DEBUG_WORLD_CITY_PROGRESS_EVERY = 5000


def debug_print(*args):
    if DEBUG_WORLD_CITY_LOAD:
        print(*args, flush=True)


# ============================================================
# INTERNAL DOWNLOAD CONFIG (HIDDEN FROM NORMAL USERS)
# ============================================================

# Only these engines are downloadable automatically
_DOWNLOADABLE_ENGINES = {
    const.PLACE_DATABASE_ENGINE.CSV_5K,
    const.PLACE_DATABASE_ENGINE.PICKLE_5K,
    const.PLACE_DATABASE_ENGINE.SQLITE_5K,
    const.PLACE_DATABASE_ENGINE.CSV_5K_IN,
    const.PLACE_DATABASE_ENGINE.PICKLE_5K_IN,
    const.PLACE_DATABASE_ENGINE.SQLITE_5K_IN,
    const.PLACE_DATABASE_ENGINE.CSV_500,
    const.PLACE_DATABASE_ENGINE.PICKLE_500,
    const.PLACE_DATABASE_ENGINE.SQLITE_500,
    const.PLACE_DATABASE_ENGINE.CSV_500_IN,
    const.PLACE_DATABASE_ENGINE.PICKLE_500_IN,
    const.PLACE_DATABASE_ENGINE.SQLITE_500_IN,
}

# Auto-download behavior
_AUTO_DOWNLOAD_PLACE_DATABASE = True

# GitHub data repository details (published release, pre-release is fine)
_RELEASE_OWNER = "naturalstupid"
_RELEASE_REPO = "JHora_World_data"
_RELEASE_TAG = "world-places-data-v1"

# Network timeout
_DOWNLOAD_TIMEOUT_SEC = 180


def set_auto_download_place_database(enabled: bool):
    """
    Enable/disable automatic download of missing downloadable engines.
    Intended for advanced users / internal setup.
    """
    global _AUTO_DOWNLOAD_PLACE_DATABASE
    _AUTO_DOWNLOAD_PLACE_DATABASE = bool(enabled)


def get_auto_download_place_database() -> bool:
    return _AUTO_DOWNLOAD_PLACE_DATABASE


def configure_download_release(owner=None, repo=None, tag=None):
    """
    Optional helper to change the GitHub release source used for downloads.
    Example:
        configure_download_release(
            owner="naturalstupid",
            repo="JHora_World_data",
            tag="world-data-v1"
        )
    """
    global _RELEASE_OWNER, _RELEASE_REPO, _RELEASE_TAG

    if owner is not None:
        _RELEASE_OWNER = str(owner).strip()
    if repo is not None:
        _RELEASE_REPO = str(repo).strip()
    if tag is not None:
        _RELEASE_TAG = str(tag).strip()


# ============================================================
# BACKEND STATE
# ============================================================
@dataclass
class _PlaceDBState:
    engine: int | None = None
    loaded: bool = False
    loading: bool = False
    source_file: str | None = None
    conn: sqlite3.Connection | None = None

    # For CSV / PICKLE in-memory engines
    alias_map: dict = field(default_factory=dict)         # normalized alias -> list[int]
    label_map: dict = field(default_factory=dict)         # normalized display label -> int
    records: list = field(default_factory=list)           # list[dict]
    display_list: list = field(default_factory=list)      # list[str]
    search_list: list = field(default_factory=list)       # list[(norm_alias, display_label, record_id)]

    # Optional maps for future compact-id CSVs
    state_map: dict = field(default_factory=dict)         # state_id -> state_name
    country_map: dict = field(default_factory=dict)       # country_id -> country_name

    def reset(self):
        self.engine = None
        self.loaded = False
        self.loading = False
        self.source_file = None

        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
        self.conn = None

        self.alias_map = {}
        self.label_map = {}
        self.records = []
        self.display_list = []
        self.search_list = []

        # state_map / country_map are intentionally preserved


_backend = _PlaceDBState()


# ============================================================
# OPTIONAL FUTURE SUPPORT FOR ID-BASED CSVs
# ============================================================
def set_state_country_maps(state_map=None, country_map=None):
    """
    Optional helper for future compact CSVs that store:
      state_id / country_id
    instead of:
      state / country

    For your CURRENT CSV, you do NOT need this.
    """
    _backend.state_map = state_map or {}
    _backend.country_map = country_map or {}


# ============================================================
# TEXT NORMALIZATION
# ============================================================
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ============================================================
# INTERNAL HELPERS
# ============================================================
def _current_engine():
    return getattr(const, "database_engine", const.PLACE_DATABASE_ENGINE.NONE)


def _engine_name(engine: int) -> str:
    return _ENGINE_DISPLAY_LABELS.get(engine, f"UNKNOWN({engine})")


def _csv_enabled() -> bool:
    return _current_engine() in (
        const.PLACE_DATABASE_ENGINE.CSV_5K,
        const.PLACE_DATABASE_ENGINE.CSV_5K_IN,
        const.PLACE_DATABASE_ENGINE.CSV_500,
        const.PLACE_DATABASE_ENGINE.CSV_500_IN,
    )


def _pickle_enabled() -> bool:
    return _current_engine() in (
        const.PLACE_DATABASE_ENGINE.PICKLE_5K,
        const.PLACE_DATABASE_ENGINE.PICKLE_500,
        const.PLACE_DATABASE_ENGINE.PICKLE_500_IN
    )

def _sqlite_enabled() -> bool:
    return _current_engine() in (
        const.PLACE_DATABASE_ENGINE.SQLITE_5K,
        const.PLACE_DATABASE_ENGINE.SQLITE_500,
        const.PLACE_DATABASE_ENGINE.SQLITE_500_IN
    )

def _split_display_and_lookup_text(place_name):
    """
    If selected text is:
        'alias — canonical'
    then:
        display_text = full selected string
        lookup_text  = canonical part
    otherwise:
        display_text = place_name
        lookup_text  = place_name
    """
    display_text = str(place_name).strip()

    if " — " in display_text:
        _, canonical_text = display_text.split(" — ", 1)
        lookup_text = canonical_text.strip()
    else:
        lookup_text = display_text

    return display_text, lookup_text


def _split_alt_names(value, sep=ALT_NAME_SEPARATOR):
    """Split alternate_names column safely."""
    if value is None:
        return []
    value = str(value).strip()
    if not value:
        return []
    return [x.strip() for x in value.split(sep) if x.strip()]


def _build_aliases_for_row(row, include_alt_names=True):
    """
    Build all searchable aliases for a CSV row:
      - place_name
      - ascii_name
      - optional alternate_names
    """
    aliases = []

    place_name = (row.get("place_name") or "").strip()
    ascii_name = (row.get("ascii_name") or "").strip()

    if place_name:
        aliases.append(place_name)

    if ascii_name and normalize_text(ascii_name) != normalize_text(place_name):
        aliases.append(ascii_name)

    if include_alt_names:
        alternate_names = _split_alt_names(row.get("alternate_names"))
        seen = {normalize_text(a) for a in aliases}
        for alt in alternate_names:
            norm_alt = normalize_text(alt)
            if alt and norm_alt not in seen:
                aliases.append(alt)
                seen.add(norm_alt)

    return aliases


def _resolve_state_country_from_row(row):
    """
    Current CSV:
      uses 'state' and 'country'

    Future compact CSV:
      may use 'state_id' and 'country_id'

    If ids are present and maps are configured, resolve them.
    Otherwise fall back to raw ids as strings.
    """
    state = (row.get("state") or "").strip()
    country = (row.get("country") or "").strip()

    if not state:
        state_id = (row.get("state_id") or "").strip()
        if state_id:
            state = _backend.state_map.get(state_id, state_id)

    if not country:
        country_id = (row.get("country_id") or "").strip()
        if country_id:
            country = _backend.country_map.get(country_id, country_id)

    return state, country


def _make_location_record_from_csv_row(row):
    """
    Parse the CSV DictReader row once and keep only needed values.

    IMPORTANT:
    rec["name"] is a display label like:
      "Inverness, Highland, United Kingdom"
    """
    city = (row.get("place_name") or "").strip()
    state, country = _resolve_state_country_from_row(row)

    try:
        latitude = round(float(row.get("latitude", 0.0)), 4)
    except Exception:
        latitude = 0.0

    try:
        longitude = round(float(row.get("longitude", 0.0)), 4)
    except Exception:
        longitude = 0.0

    try:
        timezone_hours = round(float(row.get("timezone_hours", 0.0)), 2)
    except Exception:
        timezone_hours = 0.0

    elevation = 0.0
    elev_value = row.get("altitude/elevation", row.get("elevation", 0.0))
    if elev_value not in (None, "", "None"):
        try:
            elevation = float(elev_value)
        except Exception:
            elevation = 0.0

    label_parts = []
    if city:
        label_parts.append(city)
    if state:
        label_parts.append(state)
    if country:
        label_parts.append(country)

    display_label = ", ".join(label_parts) if label_parts else city

    return {
        "name": display_label,
        "city_name": city,
        "state": state,
        "country": country,
        "display_label": display_label,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_hours,
        "elevation": elevation,
        "source": "csv",
    }


# ============================================================
# LOCAL FILE / DOWNLOAD HELPERS
# ============================================================
def _default_local_file_for_engine(engine):
    filename = const._PLACE_DATABASE_FILES.get(engine)
    if filename is None:
        return None
    return os.path.join(const.ROOT_DIR, "data", filename)


def _ensure_engine_file_path_initialized(engine):
    """
    Ensure const._place_database_file has a value.

    If the user used const.set_place_database_engine(...), this will already be set.
    If not, and it is None, initialize it using the default local filename.
    """
    if getattr(const, "_place_database_file", None) is None:
        if hasattr(const, "set_place_database_engine"):
            const.set_place_database_engine(engine)
        else:
            # fallback if setter doesn't exist
            const._place_database_file = _default_local_file_for_engine(engine)


def _engine_is_downloadable(engine) -> bool:
    return engine in _DOWNLOADABLE_ENGINES


def _release_asset_filename_for_engine(engine):
    """
    Use the SAME filename for remote download as the configured local filename.

    This keeps const._PLACE_DATABASE_FILES / const._place_database_file
    as the single source of truth for filenames.
    """
    _ensure_engine_file_path_initialized(engine)

    local_file = getattr(const, "_place_database_file", None)
    if not local_file:
        return None

    return os.path.basename(local_file)


def _release_asset_url_for_engine(engine):
    filename = _release_asset_filename_for_engine(engine)
    if not filename:
        raise ValueError(f"No release asset filename configured for engine {_engine_name(engine)}")

    owner = _RELEASE_OWNER.strip()
    repo = _RELEASE_REPO.strip()
    tag = _RELEASE_TAG.strip()

    if not owner or not repo or not tag:
        raise ValueError("GitHub release download configuration is incomplete.")

    # Works for published releases and pre-releases
    return f"https://github.com/{owner}/{repo}/releases/download/{tag}/{filename}"


def _ensure_parent_dir(file_path):
    parent = os.path.dirname(file_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def _download_file(url, target_path):
    timeout = _DOWNLOAD_TIMEOUT_SEC
    temp_path = target_path + ".part"

    _ensure_parent_dir(target_path)

    print(f"Downloading place database asset from:\n{url}")
    print(f"Saving to:\n{target_path}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PyJHora-PlaceDB/1.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response, open(temp_path, "wb") as f:
            shutil.copyfileobj(response, f)

        os.replace(temp_path, target_path)

        size_bytes = os.path.getsize(target_path) if os.path.exists(target_path) else 0
        print(f"Download complete: {target_path} ({size_bytes:,} bytes)")

    except urllib.error.HTTPError as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise RuntimeError(
            f"HTTP error while downloading place database asset: {e.code} {e.reason}\nURL: {url}"
        ) from e

    except urllib.error.URLError as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise RuntimeError(
            f"Network error while downloading place database asset:\n{e}\nURL: {url}"
        ) from e

    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise RuntimeError(
            f"Unexpected error while downloading place database asset:\n{e}\nURL: {url}"
        ) from e


def _ensure_place_database_file_available(engine):
    """
    Ensure the selected engine file exists locally.

    Behavior:
      - if local file exists -> return it
      - if missing and auto-download is enabled and engine is downloadable -> download it
      - otherwise -> raise FileNotFoundError with a clear message
    """
    _ensure_engine_file_path_initialized(engine)
    local_path = getattr(const, "_place_database_file", None)

    if engine == const.PLACE_DATABASE_ENGINE.NONE:
        return None

    if not local_path:
        raise FileNotFoundError(
            "No local place database file is configured.\n"
            "Did you call const.set_place_database_engine(...)?"
        )

    if os.path.exists(local_path):
        return local_path

    # Missing locally
    if _engine_is_downloadable(engine):
        if _AUTO_DOWNLOAD_PLACE_DATABASE:
            print(
                f"Local place database file not found for engine {_engine_name(engine)}.\n"
                f"Auto-download is enabled. Downloading now..."
            )
            url = _release_asset_url_for_engine(engine)
            _download_file(url, local_path)

            if os.path.exists(local_path):
                return local_path

            raise FileNotFoundError(
                f"Download was attempted but the file is still missing:\n{local_path}"
            )

        raise FileNotFoundError(
            f"Local place database file not found:\n{local_path}\n\n"
            f"Engine: {_engine_name(engine)}\n\n"
            f"This engine supports optional download, but auto-download is currently OFF.\n"
            f"Either:\n"
            f"  1. enable auto-download by calling:\n"
            f"       from jhora import place_db\n"
            f"       place_db.set_auto_download_place_database(True)\n"
            f"  2. or download/copy the file manually into the local data folder.\n"
        )

    # Non-downloadable engine (bundled CSV expected locally)
    raise FileNotFoundError(
        f"Local place database file not found:\n{local_path}\n\n"
        f"Engine: {_engine_name(engine)}\n\n"
        f"This engine is expected to be bundled locally.\n"
        f"Please restore or copy the required file into the local data folder."
    )


# ============================================================
# SQLITE HELPERS
# ============================================================
def _sqlite_connect():
    """
    Open SQLite connection once and keep it in backend state.
    Read-only mode for runtime search.
    """
    if _backend.conn is not None:
        return _backend.conn

    db_file = const._place_database_file
    print("Checking world city SQLite file:", db_file)

    if not os.path.exists(db_file):
        raise FileNotFoundError(f"SQLite DB file not found: {db_file}")

    t0 = time.time()

    conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA query_only = ON;")
    cur.execute("PRAGMA temp_store = MEMORY;")
    cur.execute("PRAGMA cache_size = -50000;")
    cur.execute("PRAGMA mmap_size = 268435456;")

    _backend.conn = conn
    debug_print("Opened SQLite connection in", round(time.time() - t0, 3), "seconds")
    return _backend.conn


def _sqlite_row_to_record(row):
    if row is None:
        return None

    return {
        "name": row["display_label"],
        "city_name": row["place_name"],
        "state": row["state"] or "",
        "country": row["country"] or "",
        "display_label": row["display_label"],
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "timezone": float(row["timezone_hours"]),
        "elevation": float(row["elevation"]),
        "source": "sqlite",
    }


def _sqlite_prefix_hi(prefix: str) -> str:
    return prefix + "\uffff"


def _sqlite_load():
    """
    SQLite backend init.
    We do NOT preload the full dataset into RAM.
    """
    conn = _sqlite_connect()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM places;")
    place_count = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM aliases;")
    alias_count = cur.fetchone()["c"]

    debug_print(
        "SQLite world city DB ready:",
        f"places={place_count:,}, aliases={alias_count:,}"
    )


def _sqlite_get_exact_alias_labels(query, limit=15):
    q = normalize_text(query)
    if not q:
        return []

    conn = _sqlite_connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT p.display_label
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm = ?
        ORDER BY p.display_label
        LIMIT ?
    """, (q, int(limit)))

    return [row["display_label"] for row in cur.fetchall()]


def _sqlite_search_places_for_completer(query, limit=15):
    """
    Fast search for live completer:
      1. exact display-label match
      2. exact alias match
      3. prefix alias match only
    """
    q = normalize_text(query)
    if not q:
        return []

    conn = _sqlite_connect()
    cur = conn.cursor()

    results = []
    seen = set()

    def add_result(matched_alias, row):
        rec = _sqlite_row_to_record(row)
        label = rec["display_label"]
        city_name = rec.get("city_name", "")

        if normalize_text(matched_alias) == normalize_text(city_name):
            item = label
        else:
            item = f"{matched_alias} — {label}"

        if item not in seen:
            results.append(item)
            seen.add(item)

    # 1) exact display-label match
    cur.execute("""
        SELECT *
        FROM places
        WHERE display_label_norm = ?
        LIMIT 1
    """, (q,))
    row = cur.fetchone()
    if row is not None:
        rec = _sqlite_row_to_record(row)
        add_result(rec.get("city_name", rec["display_label"]), row)
        if len(results) >= limit:
            return results[:limit]

    # 2) exact alias match
    cur.execute("""
        SELECT a.alias, p.*
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm = ?
        ORDER BY a.is_primary DESC, p.display_label
        LIMIT ?
    """, (q, int(limit)))
    for row in cur.fetchall():
        add_result(query.strip(), row)
        if len(results) >= limit:
            return results[:limit]

    # 3) prefix alias match only
    lo = q
    hi = _sqlite_prefix_hi(q)

    cur.execute("""
        SELECT a.alias, p.*
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm >= ? AND a.alias_norm < ?
        ORDER BY a.is_primary DESC, a.alias_norm, p.display_label
        LIMIT ?
    """, (lo, hi, int(limit * 3)))

    for row in cur.fetchall():
        add_result(row["alias"], row)
        if len(results) >= limit:
            return results[:limit]

    return results[:limit]


def _sqlite_search_places_contains(query, limit=30):
    """
    Wider search (used by non-live/debug scenarios).
    Includes exact + prefix + contains fallback.
    """
    q = normalize_text(query)
    if not q:
        return []

    conn = _sqlite_connect()
    cur = conn.cursor()

    results = []
    seen = set()

    def add_result(matched_alias, row):
        rec = _sqlite_row_to_record(row)
        label = rec["display_label"]
        city_name = rec.get("city_name", "")

        if normalize_text(matched_alias) == normalize_text(city_name):
            item = label
        else:
            item = f"{matched_alias} — {label}"

        if item not in seen:
            results.append(item)
            seen.add(item)

    # 1) exact display-label match
    cur.execute("""
        SELECT *
        FROM places
        WHERE display_label_norm = ?
        LIMIT 1
    """, (q,))
    row = cur.fetchone()
    if row is not None:
        rec = _sqlite_row_to_record(row)
        add_result(rec.get("city_name", rec["display_label"]), row)
        if len(results) >= limit:
            return results[:limit]

    # 2) exact alias match
    cur.execute("""
        SELECT a.alias, p.*
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm = ?
        ORDER BY a.is_primary DESC, p.display_label
        LIMIT ?
    """, (q, int(limit)))
    for row in cur.fetchall():
        add_result(query.strip(), row)
        if len(results) >= limit:
            return results[:limit]

    # 3) prefix alias match
    lo = q
    hi = _sqlite_prefix_hi(q)

    cur.execute("""
        SELECT a.alias, p.*
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm >= ? AND a.alias_norm < ?
        ORDER BY a.is_primary DESC, a.alias_norm, p.display_label
        LIMIT ?
    """, (lo, hi, int(limit * 3)))

    for row in cur.fetchall():
        add_result(row["alias"], row)
        if len(results) >= limit:
            return results[:limit]

    # 4) contains fallback
    if len(results) < limit and len(q) >= 4:
        cur.execute("""
            SELECT a.alias, p.*
            FROM aliases a
            JOIN places p ON p.id = a.place_id
            WHERE a.alias_norm LIKE ?
            ORDER BY a.is_primary DESC, a.alias_norm, p.display_label
            LIMIT ?
        """, ("%" + q + "%", int(limit * 2)))

        for row in cur.fetchall():
            add_result(row["alias"], row)
            if len(results) >= limit:
                return results[:limit]

    return results[:limit]


# ============================================================
# FALLBACKS (lazy import to avoid circular import)
# ============================================================
def _fallback_get_place_from_user_ip_address():
    from jhora import utils as _utils
    return _utils.get_place_from_user_ip_address()


def _fallback_google_lookup(place_name):
    from jhora import utils as _utils
    return _utils._scrap_google_map_for_latlongtz_from_city_with_country(place_name)


def _fallback_nominatim_lookup(place_name):
    from jhora import utils as _utils
    return _utils.get_location_using_nominatim(place_name)


def _sqlite_get_location_record(place_name=None):
    """
    Exact resolution rules:
      1) exact display-label match
      2) exact alias match; if exactly one distinct place -> return it
         else ambiguous -> return None
    """
    if place_name is None or place_name.strip() == "":
        result = _fallback_get_place_from_user_ip_address()
        if result:
            city, lat, lon, tz = result
            return {
                "name": city,
                "canonical_name": city,
                "latitude": float(lat),
                "longitude": float(lon),
                "timezone": float(tz),
                "elevation": 0.0,
                "source": "ip",
            }
        return None

    display_text, lookup_text = _split_display_and_lookup_text(place_name)

    q = normalize_text(lookup_text)
    conn = _sqlite_connect()
    cur = conn.cursor()

    # 1) exact display label
    cur.execute("""
        SELECT *
        FROM places
        WHERE display_label_norm = ?
        LIMIT 1
    """, (q,))
    row = cur.fetchone()
    if row is not None:
        rec = _sqlite_row_to_record(row)
        canonical_name = rec["name"]
        rec["canonical_name"] = canonical_name
        rec["name"] = display_text if display_text else canonical_name
        return rec

    # 2) exact alias match
    cur.execute("""
        SELECT p.*, MAX(a.is_primary) AS primary_rank
        FROM aliases a
        JOIN places p ON p.id = a.place_id
        WHERE a.alias_norm = ?
        GROUP BY p.id
        ORDER BY primary_rank DESC, p.display_label
        LIMIT 2
    """, (q,))
    rows = cur.fetchall()
    if len(rows) == 1:
        rec = _sqlite_row_to_record(rows[0])
        canonical_name = rec["name"]
        rec["canonical_name"] = canonical_name
        rec["name"] = display_text if display_text else canonical_name
        return rec
    elif len(rows) > 1:
        return None

    # 3) Google fallback
    result = _fallback_google_lookup(lookup_text)
    if result and len(result) == 3:
        lat, lon, tz = result
        return {
            "name": display_text,
            "canonical_name": lookup_text,
            "latitude": float(lat),
            "longitude": float(lon),
            "timezone": float(tz),
            "elevation": 0.0,
            "source": "google",
        }

    # 4) Nominatim fallback
    result = _fallback_nominatim_lookup(lookup_text)
    if result:
        city, lat, lon, tz = result
        return {
            "name": display_text if display_text else city,
            "canonical_name": city,
            "latitude": float(lat),
            "longitude": float(lon),
            "timezone": float(tz),
            "elevation": 0.0,
            "source": "nominatim",
        }

    return None


# ============================================================
# CSV / PICKLE IN-MEMORY LOADERS
# ============================================================
def _build_world_city_index_from_csv():
    """
    Build compact structures directly from the CSV file:
      - alias_map       (normalized alias -> list of record ids)
      - label_map       (normalized display label -> record id)
      - records         (list of parsed records)
      - display_list    (display labels)
      - search_list     (normalized alias, display label, record_id)
    """
    alias_map = {}
    label_map = {}
    records = []
    display_list = []
    search_list = []

    seen_display_labels = set()
    seen_search_pairs = set()

    print("Opening CSV:", const._place_database_file)
    t0 = time.time()

    with open(const._place_database_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        row_count = 0
        alias_link_count = 0

        for row in reader:
            row_count += 1

            record = _make_location_record_from_csv_row(row)
            record_id = len(records)
            records.append(record)

            display_label = record["display_label"]
            norm_label = normalize_text(display_label)

            # exact label lookup
            if norm_label not in label_map:
                label_map[norm_label] = record_id

            # visible list for completer
            if display_label not in seen_display_labels:
                display_list.append(display_label)
                seen_display_labels.add(display_label)

            aliases = _build_aliases_for_row(row, include_alt_names=True)

            for alias in aliases:
                norm_alias = normalize_text(alias)
                if not norm_alias:
                    continue

                alias_map.setdefault(norm_alias, [])

                if record_id not in alias_map[norm_alias]:
                    alias_map[norm_alias].append(record_id)
                    alias_link_count += 1

                pair = (norm_alias, display_label, record_id)
                if pair not in seen_search_pairs:
                    search_list.append(pair)
                    seen_search_pairs.add(pair)

            if row_count % DEBUG_WORLD_CITY_PROGRESS_EVERY == 0:
                elapsed = time.time() - t0
                debug_print(
                    f"Processed {row_count:,} rows "
                    f"(records: {len(records):,}, "
                    f"alias links: {alias_link_count:,}, "
                    f"display labels: {len(display_list):,}, "
                    f"search entries: {len(search_list):,}) "
                    f"in {elapsed:.2f}s"
                )

    elapsed = time.time() - t0
    debug_print(
        f"Finished building world city index from CSV: "
        f"{row_count:,} rows, "
        f"{len(records):,} records, "
        f"{alias_link_count:,} alias links, "
        f"{len(label_map):,} label lookups, "
        f"{len(display_list):,} display labels, "
        f"{len(search_list):,} search entries "
        f"in {elapsed:.2f}s"
    )

    return alias_map, label_map, records, display_list, search_list


def _load_pickle_file():
    """
    Direct PICKLE engine:
    load the provided .pkl file directly.
    Expected keys:
      world_cities_dict
      world_cities_label_dict
      world_city_records
      world_cities_list
      world_cities_search
    """
    pickle_file = const._place_database_file
    print("Opening PICKLE:", pickle_file)

    if not os.path.exists(pickle_file):
        raise FileNotFoundError(f"Pickle file not found: {pickle_file}")

    t0 = time.time()
    with open(pickle_file, "rb") as f:
        data = pickle.load(f)

    if not isinstance(data, dict):
        raise ValueError("Pickle file does not contain a dict structure.")

    required_keys = [
        "world_cities_dict",
        "world_cities_label_dict",
        "world_city_records",
        "world_cities_list",
        "world_cities_search",
    ]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Pickle file missing required key: {key}")

    debug_print("Loaded pickle object in", round(time.time() - t0, 3), "seconds")

    return (
        data["world_cities_dict"],
        data["world_cities_label_dict"],
        data["world_city_records"],
        data["world_cities_list"],
        data["world_cities_search"],
    )


# ============================================================
# ENGINE LOADERS
# ============================================================
def _load_csv():
    (
        _backend.alias_map,
        _backend.label_map,
        _backend.records,
        _backend.display_list,
        _backend.search_list,
    ) = _build_world_city_index_from_csv()


def _load_pickle():
    (
        _backend.alias_map,
        _backend.label_map,
        _backend.records,
        _backend.display_list,
        _backend.search_list,
    ) = _load_pickle_file()


# ============================================================
# PUBLIC LOADER
# ============================================================
def use_database_for_world_cities(enable_database=False):
    """
    Unified public entry point.
    Dispatches by engine:
      NONE      -> disable
      CSV_5K    -> load in-memory structures from CSV
      CSV_5K_IN -> load in-memory structures from CSV
      PICKLE    -> load in-memory structures directly from pickle
      SQLITE    -> open sqlite DB

    If the local file is missing and auto-download is enabled for the engine,
    it will be downloaded first.
    """
    engine = _current_engine()

    if not enable_database or engine == const.PLACE_DATABASE_ENGINE.NONE:
        debug_print("World city database disabled.")
        _backend.reset()
        const.check_database_for_world_cities = False
        return

    source_file = _ensure_place_database_file_available(engine)

    if _backend.loaded and _backend.engine == engine and _backend.source_file == source_file:
        debug_print("World city database already loaded. Skipping reload.")
        return

    if _backend.loading:
        debug_print("World city database load already in progress. Skipping duplicate call.")
        return

    _backend.reset()
    _backend.loading = True
    _backend.engine = engine
    _backend.source_file = source_file

    try:
        start_time = time.time()
        debug_print(
            f"Starting use_database_for_world_cities() | "
            f"engine={_engine_name(engine)} | file={source_file}"
        )

        if _csv_enabled():
            _load_csv()

        elif _pickle_enabled():
            _load_pickle()

        elif _sqlite_enabled():
            _sqlite_load()

        else:
            raise ValueError(f"Unsupported database engine: {engine}")

        _backend.loaded = True
        const.check_database_for_world_cities = True

        debug_print(
            "Finished use_database_for_world_cities() in",
            round(time.time() - start_time, 3),
            "seconds"
        )

    finally:
        _backend.loading = False


# ============================================================
# IN-MEMORY SEARCH HELPERS (CSV / PICKLE)
# ============================================================
def _memory_search_places_contains(query, limit=30):
    q = normalize_text(query)
    if not q:
        return []

    results = []
    seen = set()

    def add_result(matched_alias, record_id):
        rec = _backend.records[record_id]
        label = rec["display_label"]
        city_name = rec.get("city_name", "")

        if normalize_text(matched_alias) == normalize_text(city_name):
            item = label
        else:
            item = f"{matched_alias} — {label}"

        if item not in seen:
            results.append(item)
            seen.add(item)

    # 1) Exact display-label match
    record_id = _backend.label_map.get(q)
    if record_id is not None:
        rec = _backend.records[record_id]
        add_result(rec.get("city_name", rec["display_label"]), record_id)

    # 2) Exact alias match
    record_ids = _backend.alias_map.get(q, [])
    for record_id in record_ids:
        add_result(query.strip(), record_id)
        if len(results) >= limit:
            return results[:limit]

    # 3) Startswith
    for norm_alias, display_label, record_id in _backend.search_list:
        if norm_alias.startswith(q):
            add_result(norm_alias, record_id)
        if len(results) >= limit:
            return results[:limit]

    # 4) Contains
    for norm_alias, display_label, record_id in _backend.search_list:
        if q in norm_alias:
            add_result(norm_alias, record_id)
        if len(results) >= limit:
            return results[:limit]

    return results[:limit]


def _memory_get_exact_alias_labels(query, limit=15):
    q = normalize_text(query)
    if not q:
        return []

    record_ids = _backend.alias_map.get(q, [])
    labels = []
    seen = set()

    for record_id in record_ids:
        label = _backend.records[record_id]["display_label"]
        if label not in seen:
            labels.append(label)
            seen.add(label)
        if len(labels) >= limit:
            break

    return labels


def _memory_get_location_record(place_name=None):
    """
    In-memory DB-only resolution.
    Does NOT do IP / Google / Nominatim fallback here.
    Unified public function handles fallback after this.
    """
    if place_name is None or place_name.strip() == "":
        return None

    display_text, lookup_text = _split_display_and_lookup_text(place_name)
    normalized_input = normalize_text(lookup_text)

    # 1) exact display-label match
    record_id = _backend.label_map.get(normalized_input)
    if record_id is not None:
        rec = dict(_backend.records[record_id])  # copy
        canonical_name = rec["name"]
        rec["canonical_name"] = canonical_name
        rec["name"] = display_text if display_text else canonical_name
        return rec

    # 2) alias match
    record_ids = _backend.alias_map.get(normalized_input)
    if record_ids:
        if len(record_ids) == 1:
            rec = dict(_backend.records[record_ids[0]])  # copy
            canonical_name = rec["name"]
            rec["canonical_name"] = canonical_name
            rec["name"] = display_text if display_text else canonical_name
            return rec

        # ambiguous exact alias match
        return None

    return None


# ============================================================
# PUBLIC SEARCH / LOOKUP API
# ============================================================
def search_places_for_completer(query, limit=15):
    if _sqlite_enabled():
        return _sqlite_search_places_for_completer(query, limit)

    return _memory_search_places_contains(query, limit)


def search_places_contains(query, limit=30):
    if _sqlite_enabled():
        return _sqlite_search_places_contains(query, limit)

    return _memory_search_places_contains(query, limit)


def get_exact_alias_labels(query, limit=15):
    if _sqlite_enabled():
        return _sqlite_get_exact_alias_labels(query, limit)

    return _memory_get_exact_alias_labels(query, limit)


def get_location_record(place_name=None):
    if _sqlite_enabled():
        return _sqlite_get_location_record(place_name)

    # CSV / PICKLE memory engines
    rec = _memory_get_location_record(place_name)
    if rec:
        return rec

    # Fallback logic
    if place_name is None or place_name.strip() == "":
        result = _fallback_get_place_from_user_ip_address()
        if result:
            city, lat, lon, tz = result
            return {
                "name": city,
                "canonical_name": city,
                "latitude": float(lat),
                "longitude": float(lon),
                "timezone": float(tz),
                "elevation": 0.0,
                "source": "ip",
            }
        return None

    display_text, lookup_text = _split_display_and_lookup_text(place_name)

    # Google fallback
    result = _fallback_google_lookup(lookup_text)
    if result and len(result) == 3:
        lat, lon, tz = result
        return {
            "name": display_text,
            "canonical_name": lookup_text,
            "latitude": float(lat),
            "longitude": float(lon),
            "timezone": float(tz),
            "elevation": 0.0,
            "source": "google",
        }

    # Nominatim fallback
    result = _fallback_nominatim_lookup(lookup_text)
    if result:
        city, lat, lon, tz = result
        return {
            "name": display_text if display_text else city,
            "canonical_name": city,
            "latitude": float(lat),
            "longitude": float(lon),
            "timezone": float(tz),
            "elevation": 0.0,
            "source": "nominatim",
        }

    return None


def get_place(place_name=None):
    """
    Canonical API:
    return drik.Place object from CSV / IP / Google / Nominatim / SQLite.
    """
    rec = get_location_record(place_name)
    if not rec:
        return None

    from jhora.panchanga.drik import Place

    return Place(
        rec["name"],
        rec["latitude"],
        rec["longitude"],
        rec["timezone"],
        elevation=rec.get("elevation", 0.0)
    )


def get_location(place_name=None):
    rec = get_location_record(place_name)
    if not rec:
        return []
    return [
        rec["name"],
        rec["latitude"],
        rec["longitude"],
        rec["timezone"],
        rec["elevation"]
    ]


def debug_trace_alias(query, limit=20):
    q = normalize_text(query)
    print("=" * 100)
    print("QUERY:", query)
    print("NORMALIZED:", q)

    if _sqlite_enabled():
        print("Backend: SQLITE")
        print("DB file:", const._place_database_file)

        conn = _sqlite_connect()
        cur = conn.cursor()

        print("\n1) Exact alias presence in aliases:")
        cur.execute("""
            SELECT a.alias, p.display_label, p.latitude, p.longitude
            FROM aliases a
            JOIN places p ON p.id = a.place_id
            WHERE a.alias_norm = ?
            ORDER BY a.is_primary DESC, p.display_label
            LIMIT ?
        """, (q, int(limit)))
        rows = cur.fetchall()
        print("Alias record count:", len(rows))
        for idx, row in enumerate(rows, start=1):
            print(f"[{idx}] {row['alias']} -> {row['display_label']} -> lat={row['latitude']}, lon={row['longitude']}")

        print("\n2) search_places_contains results:")
        suggestions = search_places_contains(query, limit=limit)
        for idx, s in enumerate(suggestions, start=1):
            print(f"[{idx}] {s}")

        print("\n3) Exact label lookup:")
        cur.execute("""
            SELECT *
            FROM places
            WHERE display_label_norm = ?
            LIMIT 1
        """, (q,))
        row = cur.fetchone()
        print("Exact label found:", row is not None)
        if row is not None:
            print(dict(row))
        return

    print("Backend:", "CSV" if _csv_enabled() else "PICKLE")
    print("Source file:", const._place_database_file)

    print("\n1) Exact alias presence in alias_map:")
    record_ids = _backend.alias_map.get(q, [])
    print("Alias record count:", len(record_ids))

    for idx, record_id in enumerate(record_ids[:limit], start=1):
        rec = _backend.records[record_id]
        print(f"[{idx}] {rec['display_label']} -> lat={rec['latitude']}, lon={rec['longitude']}")

    print("\n2) search_places_contains results:")
    suggestions = search_places_contains(query, limit=limit)
    for idx, s in enumerate(suggestions, start=1):
        print(f"[{idx}] {s}")

    print("\n3) Exact label lookup:")
    label_id = _backend.label_map.get(q)
    print("Exact label id:", label_id)
    if label_id is not None:
        rec = _backend.records[label_id]
        print("Exact label record:", rec)