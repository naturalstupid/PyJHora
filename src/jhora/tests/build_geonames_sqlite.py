import csv
import os
import re
import sqlite3
import time
import unicodedata

# ============================================================
# CONFIG
# ============================================================
DATA_DIR = r"C:\LaptopBackup\Local\Personal\GitHub\JHora_World_Data"

CSV_FILE = os.path.join(DATA_DIR, "geonames_places_5k.csv")
DB_FILE = os.path.join(DATA_DIR, "geonames_places_5k.db")

ALT_NAME_SEPARATOR = "|"

# If True, rebuild the DB from scratch
RECREATE_DB = True

# Print progress every N rows
PROGRESS_EVERY = 10000


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """Normalize text for exact/prefix searching."""
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_alt_names(value, sep=ALT_NAME_SEPARATOR):
    """Split alternate_names safely."""
    if value is None:
        return []
    value = str(value).strip()
    if not value:
        return []
    return [x.strip() for x in value.split(sep) if x.strip()]


def build_display_label(place_name: str, state: str, country: str) -> str:
    """Build canonical label like 'Pune, Maharashtra, India'."""
    parts = []
    if place_name:
        parts.append(place_name.strip())
    if state:
        parts.append(state.strip())
    if country:
        parts.append(country.strip())
    return ", ".join(parts)


def build_aliases(place_name: str, ascii_name: str, alternate_names: str):
    """
    Return deduplicated aliases preserving order.
    Output: list of tuples -> [(alias, alias_norm), ...]
    """
    aliases = []
    seen = set()

    def add_alias(a):
        if not a:
            return
        a = str(a).strip()
        if not a:
            return
        norm = normalize_text(a)
        if not norm:
            return
        if norm in seen:
            return
        seen.add(norm)
        aliases.append((a, norm))

    add_alias(place_name)
    add_alias(ascii_name)

    for alt in split_alt_names(alternate_names):
        add_alias(alt)

    return aliases


# ============================================================
# SQLITE SCHEMA
# ============================================================

def create_tables(conn):
    cur = conn.cursor()

    if RECREATE_DB:
        cur.execute("DROP TABLE IF EXISTS aliases;")
        cur.execute("DROP TABLE IF EXISTS places;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT NOT NULL,
            ascii_name TEXT,
            state TEXT,
            country TEXT,
            display_label TEXT NOT NULL,
            display_label_norm TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timezone_hours REAL NOT NULL,
            elevation REAL NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            alias_norm TEXT NOT NULL,
            is_primary INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(place_id) REFERENCES places(id) ON DELETE CASCADE
        );
    """)

    conn.commit()


def create_indexes(conn):
    cur = conn.cursor()

    # Indexes for fast lookup
    cur.execute("CREATE INDEX IF NOT EXISTS idx_places_display_label_norm ON places(display_label_norm);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aliases_alias_norm ON aliases(alias_norm);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_aliases_place_id ON aliases(place_id);")

    # Prevent duplicate aliases for the same place
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_aliases_place_alias
        ON aliases(place_id, alias_norm);
    """)

    conn.commit()


def optimize_for_build(conn):
    """
    Build-time pragmas for faster inserts.
    Safe for one-time DB generation.
    """
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA journal_mode = MEMORY;")
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA temp_store = MEMORY;")
    cur.execute("PRAGMA cache_size = -200000;")  # ~200 MB if available
    conn.commit()


def finalize_db(conn):
    cur = conn.cursor()
    cur.execute("ANALYZE;")
    conn.commit()


# ============================================================
# BUILD DATABASE
# ============================================================

def build_sqlite_from_csv(csv_file, db_file):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    start = time.time()

    conn = sqlite3.connect(db_file)
    try:
        optimize_for_build(conn)
        create_tables(conn)

        cur = conn.cursor()

        place_insert_sql = """
            INSERT INTO places (
                place_name,
                ascii_name,
                state,
                country,
                display_label,
                display_label_norm,
                latitude,
                longitude,
                timezone_hours,
                elevation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        alias_insert_sql = """
            INSERT OR IGNORE INTO aliases (
                place_id,
                alias,
                alias_norm,
                is_primary
            )
            VALUES (?, ?, ?, ?)
        """

        row_count = 0
        alias_count = 0

        with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                row_count += 1

                place_name = (row.get("place_name") or "").strip()
                ascii_name = (row.get("ascii_name") or "").strip()
                alternate_names = (row.get("alternate_names") or "").strip()
                state = (row.get("state") or "").strip()
                country = (row.get("country") or "").strip()

                try:
                    latitude = float(row.get("latitude", 0.0))
                except Exception:
                    latitude = 0.0

                try:
                    longitude = float(row.get("longitude", 0.0))
                except Exception:
                    longitude = 0.0

                try:
                    timezone_hours = float(row.get("timezone_hours", 0.0))
                except Exception:
                    timezone_hours = 0.0

                try:
                    elevation = float(row.get("altitude/elevation", 0.0))
                except Exception:
                    elevation = 0.0

                display_label = build_display_label(place_name, state, country)
                display_label_norm = normalize_text(display_label)

                cur.execute(
                    place_insert_sql,
                    (
                        place_name,
                        ascii_name,
                        state,
                        country,
                        display_label,
                        display_label_norm,
                        latitude,
                        longitude,
                        timezone_hours,
                        elevation,
                    )
                )
                place_id = cur.lastrowid

                aliases = build_aliases(place_name, ascii_name, alternate_names)

                primary_norms = {
                    normalize_text(place_name),
                    normalize_text(ascii_name),
                }

                for alias, alias_norm in aliases:
                    is_primary = 1 if alias_norm in primary_norms else 0
                    cur.execute(alias_insert_sql, (place_id, alias, alias_norm, is_primary))
                    alias_count += 1

                if row_count % PROGRESS_EVERY == 0:
                    conn.commit()
                    elapsed = time.time() - start
                    print(
                        f"Processed {row_count:,} rows | "
                        f"aliases inserted: ~{alias_count:,} | "
                        f"elapsed: {elapsed:.2f}s",
                        flush=True
                    )

        conn.commit()

        print("Creating indexes...", flush=True)
        create_indexes(conn)
        finalize_db(conn)

        elapsed = time.time() - start
        print("\nDone!", flush=True)
        print(f"SQLite DB created: {db_file}", flush=True)
        print(f"Rows inserted into places: {row_count:,}", flush=True)
        print(f"Alias rows inserted: ~{alias_count:,}", flush=True)
        print(f"Elapsed time: {elapsed:.2f} seconds", flush=True)

    finally:
        conn.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    build_sqlite_from_csv(CSV_FILE, DB_FILE)