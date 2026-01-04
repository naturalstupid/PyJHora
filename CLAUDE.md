# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyJHora is a complete Vedic Astrology Python package based on "Vedic Astrology - An Integrated Approach" by PVR Narasimha Rao and Jagannatha Hora V8.0 software. It provides panchanga calculations, horoscope charts, 40+ dasha systems, 100+ yogas, and PyQt6-based GUIs.

## Build and Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run all tests (~6500 tests, assumes Lahiri ayanamsa)
# Tests use custom framework, not pytest
python -c "
import sys; sys.path.insert(0, 'src')
from jhora import utils
utils.set_language('en')
from jhora.tests import pvr_tests
pvr_tests.all_unit_tests()
"

# Run subset of tests (edit some_tests_only() in pvr_tests.py to select)
python -c "
import sys; sys.path.insert(0, 'src')
from jhora import utils
utils.set_language('en')
from jhora.tests import pvr_tests
pvr_tests.some_tests_only()
"
```

## Key Architecture

### Core Modules (`src/jhora/`)

- **`const.py`**: All constants - planet IDs (SUN=0 to KETU=8, URANUS=9, NEPTUNE=10, PLUTO=11), house numbers (HOUSE_1=0 to HOUSE_12=11), rasi names (ARIES=0 to PISCES=11), 20+ ayanamsa modes (Lahiri default)
- **`utils.py`**: Helper functions for geolocation, timezone, Julian day conversion, language support (`set_language()`)

### Panchanga (`jhora/panchanga/`)

- **`drik.py`** (183KB): Main panchanga functions - sunrise/set, tithi, nakshatra, yogam, karana, planet positions, special lagnas, upagrahas. This is the astronomical calculation engine.
- **`vratha.py`**: Special day calculations (amavasya, ekadashi, etc.)

### Horoscope (`jhora/horoscope/`)

- **`main.py`** (128KB): Main `Horoscope` class orchestrating all features
- **`chart/charts.py`** (142KB): Divisional charts (D-1 to D-300), bhava calculations, 17 house systems
- **`chart/yoga.py`** (364KB): 100+ yoga calculations
- **`chart/house.py`** (71KB): Aspects, drishti, karakas, stronger planet/rasi calculations
- **`dhasa/graha/`**: 22 graha dasha systems (vimsottari, ashtottari, yogini, etc.)
- **`dhasa/raasi/`**: 22 rasi dasha systems (narayana, chara, kalachakra, etc.)

### UI (`jhora/ui/`)

- **`horo_chart_tabs.py`**: Main multi-tab UI with 100+ pages of data
- **`panchangam.py`**: Simple panchanga UI widget
- **`chart_styles.py`**: South/North/East Indian chart widgets

## Data Structures

Planet positions: `[[planet_index, (rasi, longitude)], ...]`

Charts/houses: `['', '', '2', '7', '1/5', ...]` (planets in each house)

Key namedtuples in utils: `Date`, `Place`

## Language Support

6 languages via JSON files in `lang/`: 'en', 'hi', 'ka', 'ml', 'ta', 'te'

Switch with `utils.set_language('ta')`

## External Dependencies

- **pyswisseph**: Swiss Ephemeris for celestial calculations (required)
- **PyQt6**: GUI framework
- **geopy/timezonefinder**: Geolocation and timezone detection

## Important Notes

- Tests assume `const._DEFAULT_AYANAMSA_MODE='LAHIRI'`
- Ephemeris files in `data/ephe/` required for calculations (JPL compressed)
- Accuracy: 13000 BCE to 16800 CE (Swiss Ephemeris range)
- Some modules marked experimental: `prediction/`, `surya_sidhantha.py`, `khanda_khaadyaka.py`
