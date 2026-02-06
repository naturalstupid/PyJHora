# PyJHora Web Parity Report

**Generated: 2026-02-07**
**Methodology: Automated team of 5 research agents comparing Python (source of truth) vs TypeScript (pyjhora-web)**

---

## Executive Summary

| Area | Parity Level | Critical Issues | Missing Functionality |
|------|-------------|-----------------|----------------------|
| Constants | ~30% | 3 value mismatches | 100+ constants missing |
| Utils | ~40% | Missing interpolation functions | 60% of functions missing |
| Panchanga/Drik | ~8-10% | Sunrise algorithm wrong, Hora Lagna wrong | 130+ functions missing |
| Graha Dhasas | ~80% module coverage | 4 critical data/logic bugs | 2 modules missing entirely |
| Raasi Dhasas | 100% module coverage | 10 critical bugs | Systemic Lagna proxy issue |
| Horoscope/Charts | ~5% | N/A | 55+ functions missing |
| House | ~55% | Argala incomplete, Stronger Rasi simplified | Graha drishti, longevity missing |
| Strength | ~85% | Minor | Few internal helpers missing |
| Yoga | ~24% | N/A | 80+ yogas missing |
| Arudhas | ~90% | N/A | Minor |
| Ashtakavarga | ~90% | N/A | Minor |
| Test Coverage | 27 modules untested | N/A | 52% graha + 41% raasi untested |

---

## 1. CRITICAL BUGS (Will produce incorrect results)

### 1.1 Constants Value Mismatches

| # | Constant | Python Value | TypeScript Value | File | Impact |
|---|----------|-------------|-----------------|------|--------|
| C1 | `sidereal_year` | 365.256364 | 365.256363 | constants.ts:227 | Compounds across dasha calculations |
| C2 | `argala_houses` | [2,4,5,11] | [2,4,11] | constants.ts | Missing 5th house argala |
| C3 | `virodhargala_houses` | [12,10,9,3] | [12,10,3] | constants.ts | Missing 9th house virodhargala |
| C4 | ARYABHATA ayanamsa | swe.SIDM_ARYABHATA (~17) | 7 (=Yukteshwar) | constants.ts | Wrong ayanamsa mode |

### 1.2 Panchanga/Drik Critical Bugs

| # | Bug | Python (correct) | TypeScript (incorrect) | File:Line |
|---|-----|-----------------|----------------------|-----------|
| D1 | Sunrise sync uses crude approximation | `swe.rise_trans()` with Hindu rising flags | Latitude+seasonal formula (~30min off) | swe-adapter.ts |
| D2 | Hora Lagna formula wrong | `sun_long_at_sunrise + (time_since_sunrise * 0.5)` | `ascendant + (sunLong * 0.5)` | drik.ts:getHoraLagna |
| D3 | Tithi end time uses average motion | Inverse Lagrange interpolation (4-point) | Average daily motion constants | drik.ts:calculateTithi |
| D4 | Nakshatra end time approximate | 5-point inverse Lagrange with angle unwrap | Average lunar motion | drik.ts:calculateNakshatra |
| D5 | Sync sidereal longitude off by degrees | `swe.calc_ut()` with full flags | Linear extrapolation from J2000 | swe-adapter.ts:siderealLongitude |
| D6 | Async missing FLG_TRUEPOS flag | `FLG_SWIEPH\|FLG_SIDEREAL\|FLG_TRUEPOS\|FLG_SPEED` | `FLG_MOSEPH\|FLG_SPEED` only | swe-adapter.ts |
| D7 | Vara calculation offset | `ceil(jd+1)%7` | `floor(jd+1.5)%7` | drik.ts:calculateVara |

### 1.3 Graha Dhasa Critical Bugs

| # | Module | Bug Description | Python (correct) | TypeScript (incorrect) | File:Line |
|---|--------|----------------|-----------------|----------------------|-----------|
| G1 | ashtottari | Bhukti duration uses wrong lord | Uses current bhukti lord's years | Uses maha dasha lord's years | ashtottari.ts:302-309 |
| G2 | shastihayani | Nakshatra mod value wrong | `(nak+1)%28` (28 nakshatras) | `((nak)%27)+1` (27 nakshatras) | shastihayani.ts |
| G3 | naisargika | Antardasha logic completely different | House-based planet filtering with bhukthi_house_list | Equal division among 7 planets | naisargika.ts:108-127 |
| G4 | kaala | Missing solar date adjustment | `drik.next_solar_date(jd, place, ...)` | Uses `jd` directly | kaala.ts:183 |

### 1.4 Raasi Dhasa Critical Bugs

| # | Module | Bug Description | File |
|---|--------|----------------|------|
| R1 | brahma | Duration calc: Python sets 0 when lord in own sign; TS may not | brahma.ts:117-133 |
| R2 | drig, kendradhi, moola, trikona, yogardha | Duration missing `-1` subtraction AND exalted/debilitated adjustments | Multiple files |
| R3 | drig | `aspected_kendras_of_raasi()` simplified to fixed offsets | drig.ts:103-117 |
| R4 | chakra | Seed calculation missing dawn/day/dusk/night logic | chakra.ts:84-88 |
| R5 | chara | Missing PVN Rao progression method (Python's default) | chara.ts |
| R6 | kalachakra | Antardhasa completely different from Python | kalachakra.ts:291-310 |
| R7 | tara-lagna | Bhukti direction signs wrong: Virgo(5) replaced with Leo(4) | tara-lagna.ts:50 |
| R8 | yogardha | Both chara duration AND antardhasa logic differ | yogardha.ts:87-107, 178-185 |
| R9 | padhanadhamsa | Missing Narayana progression (Saturn/Ketu exceptions) | padhanadhamsa.ts:186 |

### 1.5 Systemic Issue: No Lagna/Ascendant in TypeScript

**Affects 17 of 22 raasi dhasa modules.**

- Python: `planet_positions[0]` = Ascendant/Lagna
- TypeScript: Planet arrays contain only Sun(0)..Ketu(8). Uses Sun as proxy for Lagna.
- Impact: ALL modules referencing ascendant get Sun's position instead.
- Affected: narayana, chara, chakra, drig, kendradhi, lagnamsaka, mandooka, moola, nirayana, paryaaya, shoola, sthira, sudasa, tara_lagna, trikona, varnada, yogardha

---

## 2. MISSING MODULES (No TypeScript equivalent exists)

### 2.1 Python Source Modules Missing Entirely in TypeScript

| Python Module | Lines | Functions | Priority |
|--------------|-------|-----------|----------|
| `horoscope/chart/dosha.py` | 335 | 20 | P1 - 8 doshas |
| `horoscope/chart/sphuta.py` | 274 | 26 | P2 - 14 sphutas |
| `horoscope/chart/raja_yoga.py` | 508 | 14 | P2 - Raja yogas |
| `horoscope/dhasa/graha/aayu.py` | ~100 | 3 | P3 - Longevity dasha |
| `horoscope/dhasa/graha/applicability.py` | ~150 | 8 | P3 - Dasha applicability checks |
| `horoscope/dhasa/annual/mudda.py` | ~200 | 5 | P3 - Annual dasha |
| `horoscope/dhasa/annual/patyayini.py` | ~200 | 5 | P3 - Annual dasha |
| `horoscope/dhasa/sudharsana_chakra.py` | ~150 | 3 | P3 - Sudharsana dasha |
| `horoscope/match/compatibility.py` | ~800 | 16 | P3 - Matching |
| `horoscope/transit/tajaka.py` | ~400 | 10 | P4 - Tajaka |
| `horoscope/transit/tajaka_yoga.py` | ~300 | 20 | P4 - Tajaka yogas |
| `horoscope/transit/saham.py` | ~200 | 36 | P4 - Arabic parts |
| `panchanga/vratha.py` | ~500 | 15 | P4 - Festival calendar |

### 2.2 Major Missing Function Groups

**Panchanga/Drik (~130 functions missing):**
- All muhurta calculations (Raahu Kaalam, Yamaganda, etc.)
- Lunar month/date/samvatsara
- Eclipse predictions
- Upagraha calculations
- Birth time rectification
- Tamil calendar functions
- All trikalam calculations

**Horoscope/Charts (~55 functions missing):**
- Bhava house systems (17 methods)
- 23 individual chart functions with chart_method support
- Mixed charts, custom divisional charts
- Vimsopaka/Vaiseshikamsa calculations
- Planet combustion detection
- Pushkara navamsa/bhaga detection

**Yoga (~80 yogas missing):**
- Dhana yogas (15+)
- Health yogas (10+)
- Speech yogas (5+)
- Raja yogas (14 in raja_yoga.py)
- Various named yogas (Chamara, Sankha, Bheri, etc.)

---

## 3. TEST COVERAGE GAPS

### 3.1 Source Files With No Tests

| Source File | Category |
|------------|----------|
| `src/core/constants.ts` | Core |
| `src/core/types.ts` | Core |
| `src/core/utils/format.ts` | Utils |
| `src/core/utils/geo.ts` | Utils |
| `src/core/ephemeris/swe-adapter.ts` | Ephemeris |
| `src/core/horoscope/varga-utils.ts` | Charts |
| `src/core/horoscope/yoga.ts` | Yoga |

### 3.2 Graha Dhasa Modules Missing Tests (11 of 21 = 52%)

chaturaseethi, dwadasottari, dwisatpathi, naisargika, panchottari, saptharishi, sataabdika, shastihayani, shattrimsa, shodasottari, tara

### 3.3 Raasi Dhasa Modules Missing Tests (9 of 22 = 41%)

brahma, kalachakra, padhanadhamsa, paryaaya, sandhya, sthira, sudasa, tara-lagna, varnada

### 3.4 Test Count Summary

| Area | Current Tests | Python Tests (Target) | Gap |
|------|--------------|----------------------|-----|
| Panchanga | ~18 | ~150 | ~132 |
| Charts | ~47 | ~800 | ~753 |
| Graha Dhasas | ~200 | ~600 | ~400 |
| Raasi Dhasas | ~100 | ~600 | ~500 |
| Strength | ~32 | ~400 | ~368 |
| House | ~8 | ~100 | ~92 |
| Yoga | 0 | ~600 | ~600 |
| **Total** | **~506** | **~6,500** | **~5,994** |

---

## 4. CONSTANTS MISSING FROM TYPESCRIPT

### High Priority (needed for existing features)
- Planet relationship tables (9x9 matrices)
- Planet exaltation/debilitation longitudes
- Moola trikona data
- House strength tables
- Kalachakra dhasa constants (entire set)
- Missing ayanamsa modes (USHASHASHI, SS_CITRA, TRUE_LAHIRI, KP-SENTHIL, etc.)
- Combustion ranges
- Retrograde limits

### Medium Priority (needed for planned features)
- Surya Siddhanta constants (entire set)
- Vimsopaka/Vaiseshikamsa tables
- KP 249 sublord dictionary
- Saham list
- Compatibility scoring constants
- Hadda lords table

### Low Priority
- Tamil name aliases
- Planet/zodiac Unicode symbols
- Pancha Pakshi tables
- Gauri Choghadiya tables

---

## 5. UTILITY FUNCTION GAPS

### Critical Missing Functions
- `inverse_lagrange()` - Needed for accurate panchanga timing
- `newton_polynomial()` - Numerical interpolation
- Chart/house mapping functions (4 functions)
- Proper timezone resolution (TimezoneFinder equivalent)

### Important Missing Functions
- DMS string parsing (3 functions)
- Date arithmetic (6 functions)
- Language/resource system (6 functions)
- `normalize_angle()` with `start` parameter

---

## 6. ARCHITECTURAL DIFFERENCES

### 6.1 Sync/Async Duality (TypeScript-specific)
TypeScript has dual sync/async paths. Sync uses crude approximations; async uses WASM Swiss Ephemeris. But core drik.ts functions call **sync** versions, making them inherently inaccurate.

### 6.2 Planet Position Format
- Python: `[[planet_id, (rasi, longitude)], ...]` with Lagna at index 0
- TypeScript: `{ planet, rasi, longitude, isRetrograde, nakshatra, nakshatraPada }` objects, no Lagna entry

### 6.3 Time Representation
- Python: Julian Day numbers throughout
- TypeScript: Mix of Julian Day and JS Date objects

### 6.4 Graha Drishti Indexing
- Python: 1-based house numbers (7th house = 7)
- TypeScript: 0-based offsets (7th house = offset 6)

---

## 7. MODULES WITH GOOD PARITY (No action needed)

These TypeScript modules closely match their Python counterparts:

**Raasi Dhasas:** navamsa, nirayana, paryaaya, sandhya, shoola, sthira
**Horoscope:** arudhas (~90%), ashtakavarga (~90%), strength (~85%)
**Graha Dhasas:** vimsottari (data matches), yogini (data matches), all lord/year arrays verified for 12 modules

---

## 8. RECOMMENDED FIX PRIORITY

### Phase 1: Fix Critical Bugs (Immediate)
1. Fix SIDEREAL_YEAR constant (C1)
2. Fix argala/virodhargala houses (C2, C3)
3. Fix ARYABHATA ayanamsa value (C4)
4. Fix tara-lagna bhukti signs (R7)
5. Fix ashtottari bhukti calculation (G1)
6. Fix shastihayani nakshatra mod (G2)
7. Fix naisargika antardasha logic (G3)
8. Fix Hora Lagna formula (D2)
9. Fix Vara calculation offset (D7)
10. Fix narayana duration in drig/kendradhi/moola/trikona/yogardha (R2)

### Phase 2: Fix Systemic Issues
1. Add Lagna/Ascendant to TypeScript planet positions
2. Fix duration calculation to include exalted/debilitated adjustments
3. Fix chakra seed calculation
4. Fix chara PVN Rao progression
5. Fix kalachakra antardhasa

### Phase 3: Add Missing Tests
1. Tests for 11 untested graha dhasa modules
2. Tests for 9 untested raasi dhasa modules
3. Tests for yoga.ts
4. Tests for core modules (constants, types, format, geo)

### Phase 4: Add Missing Features
1. Dosha calculations (P1)
2. Muhurta calculations (P1)
3. Missing yogas (P2)
4. Sphuta calculations (P2)
5. Raja yogas (P2)
6. Remaining features per PARITY_EPIC.md
