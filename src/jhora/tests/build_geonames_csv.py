import os
import pandas as pd

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = r"C:\LaptopBackup\Local\Personal\GitHub\JHora_World_Data"

ALLCOUNTRIES_FILE = os.path.join(BASE_DIR, "allCountries.txt")
ADMIN1_FILE = os.path.join(BASE_DIR, "admin1CodesASCII.txt")
COUNTRYINFO_FILE = os.path.join(BASE_DIR, "countryInfo.txt")
TIMEZONES_FILE = os.path.join(BASE_DIR, "timeZones.txt")
OUTPUT_FILE = os.path.join(BASE_DIR, "geonames_places_500_IN.csv")
# True  = only cities / towns / villages (feature_class == "P")
# False = keep all GeoNames feature types
ONLY_POPULATED_PLACES = True
# None   = no population filtering
# 500    = keep rows with population >= 500
# 1000   = keep rows with population >= 1000
# 10000  = keep rows with population >= 10000
POPULATION_MIN = 500
# Keep population=0 rows for these countries even when POPULATION_MIN is set
# Example: India, USA
ALLOW_ZERO_POP_COUNTRIES = {"IN"}
# Search/helpful text columns
INCLUDE_ASCII_NAME = True
INCLUDE_ALTERNATE_NAMES = True
# If True:
#   - output place_name will use ascii_name when available
#   - ascii_name column will NOT be written separately
# If False:
#   - output place_name uses GeoNames name
#   - ascii_name column behavior is controlled by INCLUDE_ASCII_NAME
USE_ASCII_NAME_AS_PLACE_NAME = True

# True = only keep ASCII-only alternate names
# False = keep all alternate names
INCLUDE_ONLY_ASCII_ALTERNATE_NAMES = True

# How alternate names will be stored inside ONE CSV column
ALT_NAME_SEPARATOR = "|"

# NEW SWITCH:
# False = keep original behavior (state/country text in CSV)
# True  = write compact IDs instead:
#         state_id   = admin1_code
#         country_id = country_code
USE_IDS_FOR_STATE_COUNTRY = False

# Process large file in chunks
CHUNK_SIZE = 200000


# ============================================================
# HELPERS
# ============================================================
def choose_output_place_name(name, asciiname, use_ascii_as_place_name=False):
    """
    Return the place name to write into output.

    If use_ascii_as_place_name=True and asciiname is present,
    use asciiname; otherwise use name.
    """
    name = "" if name is None else str(name).strip()
    asciiname = "" if asciiname is None else str(asciiname).strip()

    if use_ascii_as_place_name and asciiname:
        return asciiname

    return name


def is_ascii_text(text: str) -> bool:
    """
    Return True only if text contains ASCII characters only.
    """
    if not text:
        return False
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def normalize_alternate_names(value, sep="|", ascii_only=False):
    """
    GeoNames alternatenames are comma-separated in the source data.
    Convert them into a single string using the preferred separator,
    remove blanks, remove duplicates case-insensitively while preserving
    the first encountered original spelling, and optionally keep only
    ASCII alternate names.
    """
    seen_keys = set()
    items = []

    for name in str(value).split(","):
        clean = name.strip()
        if not clean:
            continue

        if ascii_only and not is_ascii_text(clean):
            continue

        # Case-insensitive dedupe key
        key = clean.casefold()

        if key not in seen_keys:
            seen_keys.add(key)
            items.append(clean)

    return sep.join(items)


# ============================================================
# LOAD LOOKUP TABLES
# ============================================================
def load_admin1_lookup(admin1_file):
    """
    admin1CodesASCII.txt columns:
    code, name, asciiname, geonameid

    Example code format:
    US.IL
    IN.25
    """
    admin1 = pd.read_csv(
        admin1_file,
        sep="\t",
        header=None,
        names=["admin1_key", "state_name", "state_ascii", "admin1_geonameid"],
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    admin1["state"] = admin1["state_name"].where(
        admin1["state_name"] != "",
        admin1["state_ascii"]
    )

    return dict(zip(admin1["admin1_key"], admin1["state"]))


def load_country_lookup(countryinfo_file):
    """
    countryInfo.txt has comment lines starting with '#'
    We only need:
      ISO     -> country code
      Country -> country name
    """
    country_cols = [
        "ISO", "ISO3", "ISONumeric", "fips", "Country", "Capital",
        "AreaSqKm", "Population", "Continent", "tld", "CurrencyCode",
        "CurrencyName", "Phone", "PostalCodeFormat", "PostalCodeRegex",
        "Languages", "geonameid", "neighbours", "EquivalentFipsCode"
    ]

    country = pd.read_csv(
        countryinfo_file,
        sep="\t",
        comment="#",
        header=None,
        names=country_cols,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    return dict(zip(country["ISO"], country["Country"]))


def load_timezone_lookup(timezones_file):
    """
    timeZones.txt columns:
      countryCode, timezoneId, gmtOffsetJan, dstOffsetJul, rawOffset

    We use rawOffset as timezone_hours because it is the base offset
    without DST.
    """
    tz = pd.read_csv(
        timezones_file,
        sep="\t",
        comment="#",
        header=None,
        names=["countryCode", "timezoneId", "gmtOffsetJan", "dstOffsetJul", "rawOffset"],
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    tz["timezone_hours"] = pd.to_numeric(tz["rawOffset"], errors="coerce").fillna(0.0)

    return dict(zip(tz["timezoneId"], tz["timezone_hours"]))


# ============================================================
# MAIN PROCESSOR
# ============================================================
def build_output_csv(
    allcountries_file,
    admin1_lookup,
    country_lookup,
    timezone_lookup,
    output_file,
    only_populated_places=False,
    population_min=None,
    include_ascii_name=True,
    include_alternate_names=True,
    use_ascii_name_as_place_name=False,
    use_ids_for_state_country=False,
    alt_name_separator="|",
    chunk_size=200000
):
    """
    Reads allCountries.txt in chunks and creates output CSV.

    Base output columns:
      place_name, state, country, latitude, longitude, timezone_hours, altitude/elevation

    Optional extra columns:
      ascii_name
      alternate_names

    If use_ids_for_state_country=True:
      output state_id / country_id instead of full state / country names
    """

    geonames_cols = [
        "geonameid", "name", "asciiname", "alternatenames",
        "latitude", "longitude",
        "feature_class", "feature_code",
        "country_code", "cc2",
        "admin1_code", "admin2_code", "admin3_code", "admin4_code",
        "population", "elevation", "dem", "timezone", "modification_date"
    ]

    if os.path.exists(output_file):
        os.remove(output_file)

    chunk_iter = pd.read_csv(
        allcountries_file,
        sep="\t",
        header=None,
        names=geonames_cols,
        dtype=str,
        encoding="utf-8-sig",
        keep_default_na=False,
        chunksize=chunk_size,
        on_bad_lines="skip"
    )

    first_chunk = True
    total_written = 0

    for i, chunk in enumerate(chunk_iter, start=1):
        # Optional filter: only populated places
        if only_populated_places:
            chunk = chunk[chunk["feature_class"] == "P"].copy()

        # Convert population to numeric
        chunk["population_num"] = pd.to_numeric(
            chunk["population"].replace("", pd.NA),
            errors="coerce"
        ).fillna(0)

        # Optional filter: population threshold
        if population_min is not None:
            zero_pop_country_mask = (
                (chunk["population_num"] == 0) &
                (chunk["country_code"].isin(ALLOW_ZERO_POP_COUNTRIES))
            )

            normal_pop_mask = chunk["population_num"] >= population_min

            chunk = chunk[normal_pop_mask | zero_pop_country_mask].copy()

        # Build lookup key for state/province
        chunk["admin1_key"] = chunk["country_code"].fillna("") + "." + chunk["admin1_code"].fillna("")

        # Only resolve full names if we are NOT using compact IDs
        if not use_ids_for_state_country:
            chunk["state"] = chunk["admin1_key"].map(admin1_lookup).fillna("")
            chunk["country"] = chunk["country_code"].map(country_lookup).fillna("")

        chunk["timezone_hours"] = chunk["timezone"].map(timezone_lookup).fillna(0.0)

        # altitude/elevation logic:
        # 1) use elevation if present
        # 2) otherwise use dem
        # 3) if both missing, use 0.0
        elev = pd.to_numeric(chunk["elevation"].replace("", pd.NA), errors="coerce")
        dem = pd.to_numeric(chunk["dem"].replace("", pd.NA), errors="coerce")
        chunk["altitude/elevation"] = elev.fillna(dem).fillna(0.0)

        # Clean / normalize optional search fields
        chunk["asciiname"] = chunk["asciiname"].fillna("").astype(str)

        if include_alternate_names:
            chunk["alternatenames"] = chunk["alternatenames"].fillna("").astype(str)
            chunk["alternatenames"] = chunk["alternatenames"].apply(
                lambda x: normalize_alternate_names(
                    x,
                    alt_name_separator,
                    ascii_only=INCLUDE_ONLY_ASCII_ALTERNATE_NAMES
                )
            )

        # Decide what goes into output place_name
        chunk["output_place_name"] = chunk.apply(
            lambda r: choose_output_place_name(
                r.get("name", ""),
                r.get("asciiname", ""),
                use_ascii_as_place_name=use_ascii_name_as_place_name
            ),
            axis=1
        )

        # Select final columns
        selected_cols = ["output_place_name"]

        # Only include ascii_name separately if we are NOT already using it as place_name
        if include_ascii_name and not use_ascii_name_as_place_name:
            selected_cols.append("asciiname")

        if include_alternate_names:
            selected_cols.append("alternatenames")

        # State/Country choice
        if use_ids_for_state_country:
            selected_cols.extend(["admin1_code", "country_code"])
        else:
            selected_cols.extend(["state", "country"])

        # Numeric columns
        selected_cols.extend([
            "latitude",
            "longitude",
            "timezone_hours",
            "altitude/elevation"
        ])

        out = chunk[selected_cols].copy()

        # Rename output columns
        rename_map = {
            "output_place_name": "place_name",
            "asciiname": "ascii_name",
            "alternatenames": "alternate_names",
            "admin1_code": "state_id",
            "country_code": "country_id"
        }
        out.rename(columns=rename_map, inplace=True)

        # Clean numeric columns
        out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce")
        out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce")
        out["timezone_hours"] = pd.to_numeric(out["timezone_hours"], errors="coerce").fillna(0.0)
        out["altitude/elevation"] = pd.to_numeric(out["altitude/elevation"], errors="coerce").fillna(0.0)

        # Drop rows with missing coordinates
        out = out.dropna(subset=["latitude", "longitude"])

        # Write output
        out.to_csv(
            output_file,
            mode="w" if first_chunk else "a",
            index=False,
            header=first_chunk,
            encoding="utf-8-sig"
        )

        rows_written = len(out)
        total_written += rows_written
        print(f"Chunk {i}: wrote {rows_written:,} rows (total so far: {total_written:,})")

        first_chunk = False

    print("\nDone!")
    print(f"Output file created: {output_file}")
    print(f"Total rows written: {total_written:,}")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    print("Loading lookup files...")

    # Only load name lookups if we need full text state/country output
    if USE_IDS_FOR_STATE_COUNTRY:
        admin1_lookup = {}
        country_lookup = {}
    else:
        admin1_lookup = load_admin1_lookup(ADMIN1_FILE)
        country_lookup = load_country_lookup(COUNTRYINFO_FILE)

    timezone_lookup = load_timezone_lookup(TIMEZONES_FILE)

    print("Building final CSV...")
    build_output_csv(
        allcountries_file=ALLCOUNTRIES_FILE,
        admin1_lookup=admin1_lookup,
        country_lookup=country_lookup,
        timezone_lookup=timezone_lookup,
        output_file=OUTPUT_FILE,
        only_populated_places=ONLY_POPULATED_PLACES,
        population_min=POPULATION_MIN,
        include_ascii_name=INCLUDE_ASCII_NAME,
        include_alternate_names=INCLUDE_ALTERNATE_NAMES,
        use_ascii_name_as_place_name=USE_ASCII_NAME_AS_PLACE_NAME,
        use_ids_for_state_country=USE_IDS_FOR_STATE_COUNTRY,
        alt_name_separator=ALT_NAME_SEPARATOR,
        chunk_size=CHUNK_SIZE
    )
