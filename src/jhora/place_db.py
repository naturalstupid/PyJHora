#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) Open Astro Technologies, USA.
# Modified by Sundar Sundaresan, USA. carnaticmusicguru2015@comcast.net
# Downloaded from https://github.com/naturalstupid/PyJHora

# This file is part of the "PyJHora" Python library
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
    Release History:
    V4.8.6 - Added CSV/Pickle/SQLite config for 1K, 1K_IN, 10K, 10K_IN.
"""
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
"""
    Release History:
    V4.8.6 - Moved hardcoded settings from this file to factory/user settings
"""
# Pre-compiled regexes to shift string processing loops from Python into C
_sub_combining = re.compile(r'[\u0300-\u036f\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]').sub
_sub_non_alphanum = re.compile(r"[^a-z0-9]+").sub
_normalize = unicodedata.normalize

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # NFKD decomposes accents; the regex strips the combining marks instantly in C
    return _sub_non_alphanum(" ", _sub_combining("", _normalize("NFKD", text)).lower()).strip()


def _build_world_city_index_from_csv():
    alias_map = {}
    label_map = {}
    records = []
    display_list = []
    search_list = []
    seen_display_labels = set()

    print("Opening CSV:", const._place_database_file)
    t0 = time.time()

    # Cache method lookups locally to eliminate dot-notation overhead inside the loop
    state_map_get = _backend.state_map.get
    country_map_get = _backend.country_map.get

    with open(const._place_database_file, "r", encoding="utf-8-sig", newline="") as file:
        # csv.reader is significantly faster than DictReader
        reader = csv.reader(file)
        try:
            header = next(reader)
        except StopIteration:
            return alias_map, label_map, records, display_list, search_list

        # Map header columns to positional integer indices once
        idx_place_name = header.index("place_name") if "place_name" in header else -1
        idx_state = header.index("state") if "state" in header else -1
        idx_country = header.index("country") if "country" in header else -1
        idx_latitude = header.index("latitude") if "latitude" in header else -1
        idx_longitude = header.index("longitude") if "longitude" in header else -1
        idx_tz = header.index("timezone_hours") if "timezone_hours" in header else -1
        
        idx_elevation = -1
        for k in ("elevation", "altitude/elevation"):
            if k in header:
                idx_elevation = header.index(k)
                break

        idx_ascii_name = header.index("ascii_name") if "ascii_name" in header else -1
        idx_alternate_names = header.index("alternate_names") if "alternate_names" in header else -1
        idx_state_id = header.index("state_id") if "state_id" in header else -1
        idx_country_id = header.index("country_id") if "country_id" in header else -1

        row_count = 0
        alias_link_count = 0

        for row in reader:
            if not row:
                continue
            row_count += 1

            # 1) Extract fields quickly using positional indices
            city = row[idx_place_name].strip() if idx_place_name != -1 else ""
            
            # Resolve State
            state = row[idx_state].strip() if idx_state != -1 else ""
            if not state and idx_state_id != -1:
                sid = row[idx_state_id].strip()
                if sid:
                    state = state_map_get(sid, sid)

            # Resolve Country
            country = row[idx_country].strip() if idx_country != -1 else ""
            if not country and idx_country_id != -1:
                cid = row[idx_country_id].strip()
                if cid:
                    country = country_map_get(cid, cid)

            # Fast inline numeric parsing
            try:
                latitude = round(float(row[idx_latitude]), 4) if idx_latitude != -1 else 0.0
            except Exception:
                latitude = 0.0

            try:
                longitude = round(float(row[idx_longitude]), 4) if idx_longitude != -1 else 0.0
            except Exception:
                longitude = 0.0

            try:
                timezone_hours = round(float(row[idx_tz]), 2) if idx_tz != -1 else 0.0
            except Exception:
                timezone_hours = 0.0

            elevation = 0.0
            if idx_elevation != -1:
                ev = row[idx_elevation]
                if ev and ev != "None":
                    try:
                        elevation = float(ev)
                    except Exception:
                        pass

            # Construct display label efficiently via string joining
            label_parts = []
            if city: label_parts.append(city)
            if state: label_parts.append(state)
            if country: label_parts.append(country)
            display_label = ", ".join(label_parts) if label_parts else city

            record_id = len(records)
            records.append({
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
            })

            # 2) Build label map lookup index
            norm_label = normalize_text(display_label)
            if norm_label not in label_map:
                label_map[norm_label] = record_id

            if display_label not in seen_display_labels:
                display_list.append(display_label)
                seen_display_labels.add(display_label)

            # 3) Build aliases and search lists in a single, unified pass
            aliases_set = set()
            
            if city:
                norm_city = normalize_text(city)
                if norm_city:
                    aliases_set.add(norm_city)
                    if norm_city in alias_map:
                        alias_map[norm_city].append(record_id)
                    else:
                        alias_map[norm_city] = [record_id]
                    search_list.append((norm_city, display_label, record_id))
                    alias_link_count += 1

            if idx_ascii_name != -1:
                ascii_name = row[idx_ascii_name].strip()
                if ascii_name:
                    norm_ascii = normalize_text(ascii_name)
                    if norm_ascii and norm_ascii not in aliases_set:
                        aliases_set.add(norm_ascii)
                        if norm_ascii in alias_map:
                            alias_map[norm_ascii].append(record_id)
                        else:
                            alias_map[norm_ascii] = [record_id]
                        search_list.append((norm_ascii, display_label, record_id))
                        alias_link_count += 1

            if idx_alternate_names != -1:
                alt_names_str = row[idx_alternate_names]
                if alt_names_str:
                    # Inlined loop handles split + strip + normalize directly
                    for alt in alt_names_str.split("|"):
                        alt = alt.strip()
                        if alt:
                            norm_alt = normalize_text(alt)
                            if norm_alt and norm_alt not in aliases_set:
                                aliases_set.add(norm_alt)
                                if norm_alt in alias_map:
                                    alias_map[norm_alt].append(record_id)
                                else:
                                    alias_map[norm_alt] = [record_id]
                                search_list.append((norm_alt, display_label, record_id))
                                alias_link_count += 1

    elapsed = time.time() - t0
    print(f"Finished building world city index from CSV: {row_count:,} rows in {elapsed:.2f}s")
    return alias_map, label_map, records, display_list, search_list

class CompactRecord:
    __slots__ = ("name", "city_name", "state", "country", "display_label", "latitude", "longitude", "timezone", "elevation")
    
    def __init__(self, city, state, country, display_label, latitude, longitude, timezone, elevation):
        self.name = display_label
        self.city_name = city
        self.state = state
        self.country = country
        self.display_label = display_label
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.elevation = elevation

    def __getitem__(self, key):
        if key == "source":
            return "csv"
        return getattr(self, key)

    def get(self, key, default=None):
        if key == "source":
            return "csv"
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def keys(self):
        return ("name", "city_name", "state", "country", "display_label", "latitude", "longitude", "timezone", "elevation", "source")
    
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
    const.PLACE_DATABASE_ENGINE.CSV_1K,
    const.PLACE_DATABASE_ENGINE.PICKLE_1K,
    const.PLACE_DATABASE_ENGINE.SQLITE_1K,
    const.PLACE_DATABASE_ENGINE.CSV_1K_IN,
    const.PLACE_DATABASE_ENGINE.PICKLE_1K_IN,
    const.PLACE_DATABASE_ENGINE.SQLITE_1K_IN,
    const.PLACE_DATABASE_ENGINE.CSV_10K,
    const.PLACE_DATABASE_ENGINE.PICKLE_10K,
    const.PLACE_DATABASE_ENGINE.SQLITE_10K,
    const.PLACE_DATABASE_ENGINE.CSV_10K_IN,
    const.PLACE_DATABASE_ENGINE.PICKLE_10K_IN,
    const.PLACE_DATABASE_ENGINE.SQLITE_10K_IN,
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
        const.PLACE_DATABASE_ENGINE.CSV_1K,
        const.PLACE_DATABASE_ENGINE.CSV_1K_IN,
        const.PLACE_DATABASE_ENGINE.CSV_10K,
        const.PLACE_DATABASE_ENGINE.CSV_10K_IN,
    )


def _pickle_enabled() -> bool:
    return _current_engine() in (
        const.PLACE_DATABASE_ENGINE.PICKLE_5K,
        const.PLACE_DATABASE_ENGINE.PICKLE_5K_IN,
        const.PLACE_DATABASE_ENGINE.PICKLE_500,
        const.PLACE_DATABASE_ENGINE.PICKLE_500_IN,
        const.PLACE_DATABASE_ENGINE.PICKLE_1K,
        const.PLACE_DATABASE_ENGINE.PICKLE_1K_IN,
        const.PLACE_DATABASE_ENGINE.PICKLE_10K,
        const.PLACE_DATABASE_ENGINE.PICKLE_10K_IN,
    )

def _sqlite_enabled() -> bool:
    return _current_engine() in (
        const.PLACE_DATABASE_ENGINE.SQLITE_5K,
        const.PLACE_DATABASE_ENGINE.SQLITE_5K_IN,
        const.PLACE_DATABASE_ENGINE.SQLITE_500,
        const.PLACE_DATABASE_ENGINE.SQLITE_500_IN,
        const.PLACE_DATABASE_ENGINE.SQLITE_1K,
        const.PLACE_DATABASE_ENGINE.SQLITE_1K_IN,
        const.PLACE_DATABASE_ENGINE.SQLITE_10K,
        const.PLACE_DATABASE_ENGINE.SQLITE_10K_IN,
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
    if city: label_parts.append(city)
    if state: label_parts.append(state)
    if country: label_parts.append(country)

    display_label = ", ".join(label_parts) if label_parts else city

    return CompactRecord(city, state, country, display_label, latitude, longitude, timezone_hours, elevation)


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


# ============================================================
# GOOGLE-MAPS SCRAPE FALLBACK -- OFF BY DEFAULT
# ============================================================
# _fallback_google_lookup() scrapes an UNDOCUMENTED embedded JS state
# blob out of a Google Maps HTML page. It has no way to verify the
# parsed coordinates actually correspond to the requested place -- if
# Google can't resolve the (possibly malformed/unencoded) query string,
# it has been observed to silently fall back to the REQUESTER'S OWN
# IP-GEOLOCATED map view instead of failing, and the scraper then
# returns those coordinates as if they were a valid geocode result for
# the query. Nominatim (below) is a real, documented geocoding API and
# does not have this failure mode, so it is now tried FIRST; Google
# scraping is kept only as an optional last resort, disabled by default.
_ENABLE_GOOGLE_SCRAPE_FALLBACK = False
def set_enable_google_scrape_fallback(enabled: bool):
    """
    Enable/disable the Google-Maps scrape fallback (see warning above).
    Disabled by default -- Nominatim is tried first and is normally
    sufficient. Only enable this if you understand the risk that it can
    silently return your own current location instead of failing when
    a place cannot be resolved.
    """
    global _ENABLE_GOOGLE_SCRAPE_FALLBACK
    _ENABLE_GOOGLE_SCRAPE_FALLBACK = bool(enabled)
def get_enable_google_scrape_fallback() -> bool:
    return _ENABLE_GOOGLE_SCRAPE_FALLBACK


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

    # 3) Nominatim fallback -- tried FIRST, since it's a real, documented
    #    geocoding API (unlike the Google scrape below).
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

    # 4) Google fallback -- OFF by default; see _ENABLE_GOOGLE_SCRAPE_FALLBACK
    #    above for why this is no longer tried first.
    if _ENABLE_GOOGLE_SCRAPE_FALLBACK:
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

    return None


# ============================================================
# CSV / PICKLE IN-MEMORY LOADERS
# ============================================================

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

    # Nominatim fallback -- tried FIRST, since it's a real, documented
    # geocoding API (see _ENABLE_GOOGLE_SCRAPE_FALLBACK note above).
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

    # Google fallback -- OFF by default; see _ENABLE_GOOGLE_SCRAPE_FALLBACK.
    if _ENABLE_GOOGLE_SCRAPE_FALLBACK:
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