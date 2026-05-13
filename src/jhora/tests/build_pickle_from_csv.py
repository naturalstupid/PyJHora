import csv
import os
import pickle
import re
import time
import unicodedata
from jhora import const
# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = r"C:\LaptopBackup\Local\Personal\GitHub\JHora_World_Data"

CSV_FILE = os.path.join(BASE_DIR,"geonames_places_all.csv")   # <-- change if needed
PICKLE_FILE = os.path.join(BASE_DIR, "geonames_places_all.pkl")

# ============================================================
# CONFIG
# ============================================================
ALT_NAME_SEPARATOR = "|"
DEBUG = True
PROGRESS_EVERY = 5000

# If True, also include alternate_names in alias index
USE_ALT_NAMES_IN_UI_INDEX = True


def debug_print(*args):
    if DEBUG:
        print(*args, flush=True)


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
# HELPERS
# ============================================================
def _split_alt_names(value, sep=ALT_NAME_SEPARATOR):
    """Split alternate_names column safely."""
    if value is None:
        return []
    value = str(value).strip()
    if not value:
        return []
    return [x.strip() for x in value.split(sep) if x.strip()]


def _build_aliases_for_row(row, include_alt_names=False):
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


def _make_location_record_from_csv_row(row):
    """
    Parse one CSV row into the compact record structure
    used by the pickle engine.
    """
    city = (row.get("place_name") or "").strip()
    state = (row.get("state") or "").strip()
    country = (row.get("country") or "").strip()

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
        "name": display_label,      # canonical display label for UI
        "city_name": city,          # raw city only
        "state": state,
        "country": country,
        "display_label": display_label,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone_hours,
        "elevation": elevation,
        "source": "pickle",
    }


# ============================================================
# MAIN BUILD
# ============================================================
def build_pickle_from_csv(csv_file, pickle_file, include_alt_names=True):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    start = time.time()

    world_cities_dict = {}         # normalized alias -> list[int]
    world_cities_label_dict = {}   # normalized display label -> int
    world_city_records = []        # record_id -> compact record
    world_cities_list = []         # visible display labels
    world_cities_search = []       # (normalized_alias, display_label, record_id)

    seen_display_labels = set()
    seen_search_pairs = set()

    debug_print("Opening CSV:", csv_file)

    with open(csv_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        row_count = 0
        alias_link_count = 0

        for row in reader:
            row_count += 1

            record = _make_location_record_from_csv_row(row)
            record_id = len(world_city_records)
            world_city_records.append(record)

            display_label = record["display_label"]
            norm_label = normalize_text(display_label)

            # exact label lookup
            if norm_label not in world_cities_label_dict:
                world_cities_label_dict[norm_label] = record_id

            # visible list for completer
            if display_label not in seen_display_labels:
                world_cities_list.append(display_label)
                seen_display_labels.add(display_label)

            aliases = _build_aliases_for_row(row, include_alt_names=include_alt_names)

            for alias in aliases:
                norm_alias = normalize_text(alias)
                if not norm_alias:
                    continue

                world_cities_dict.setdefault(norm_alias, [])

                if record_id not in world_cities_dict[norm_alias]:
                    world_cities_dict[norm_alias].append(record_id)
                    alias_link_count += 1

                pair = (norm_alias, display_label, record_id)
                if pair not in seen_search_pairs:
                    world_cities_search.append(pair)
                    seen_search_pairs.add(pair)

            if row_count % PROGRESS_EVERY == 0:
                elapsed = time.time() - start
                debug_print(
                    f"Processed {row_count:,} rows "
                    f"(records: {len(world_city_records):,}, "
                    f"alias links: {alias_link_count:,}, "
                    f"display labels: {len(world_cities_list):,}, "
                    f"search entries: {len(world_cities_search):,}) "
                    f"in {elapsed:.2f}s"
                )

    data = {
        "world_cities_dict": world_cities_dict,
        "world_cities_label_dict": world_cities_label_dict,
        "world_city_records": world_city_records,
        "world_cities_list": world_cities_list,
        "world_cities_search": world_cities_search,
    }

    debug_print("Saving pickle:", pickle_file)
    with open(pickle_file, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    elapsed = time.time() - start
    debug_print("\nDone!")
    debug_print(f"Pickle created: {pickle_file}")
    debug_print(f"Rows processed: {row_count:,}")
    debug_print(f"Alias links: {alias_link_count:,}")
    debug_print(f"Elapsed time: {elapsed:.2f}s")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    build_pickle_from_csv(
        csv_file=CSV_FILE,
        pickle_file=PICKLE_FILE,
        include_alt_names=USE_ALT_NAMES_IN_UI_INDEX
    )