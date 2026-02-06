# PyJHora Web Parity Epic

Bring pyjhora-web to full feature and test parity with Python PyJHora library.

---

## Epic: PyJHora Web Feature & Test Parity

- type: epic
- priority: 1
- labels: parity, web, python

### Description

Complete end-to-end parity between Python PyJHora library and pyjhora-web TypeScript implementation.

**Current Status:**
- Features: ~60% implemented
- Tests: ~8% coverage (506 of ~6,500 tests)

**Goals:**
1. Implement all missing features from Python version
2. Port all tests from Python to TypeScript/Vitest
3. Ensure calculation accuracy matches Python implementation

---

## Task: Implement Dosha Calculations

- type: feature
- priority: 1
- labels: parity, critical, doshas
- estimate: 480

### Description

Implement all 8 dosha calculations that are completely missing from the web version.

**Doshas to implement:**
1. Kala Sarpa Dosha
2. Manglik Dosha
3. Pitru Dosha
4. Guru Chandala Dosha
5. Ganda Moola Dosha
6. Kalathra Dosha
7. Ghata Dosha
8. Shrapit Dosha

### Acceptance Criteria

- [ ] Create `/src/core/horoscope/dosha.ts`
- [ ] Port logic from Python `dosha.py` (436 lines)
- [ ] All 8 doshas correctly detected
- [ ] Add comprehensive tests in `/tests/core/horoscope/dosha.test.ts`

---

## Task: Implement Special Time Periods (Muhurta)

- type: feature
- priority: 1
- labels: parity, critical, panchanga
- estimate: 360

### Description

Implement special time period calculations for muhurta (auspicious timing).

**Time periods to implement:**
1. Raahu Kaalam (inauspicious time)
2. Yamaganda (death time)
3. Gulika Kaalam
4. Trikalam (three dangerous periods)
5. Durmuhurtam (unlucky moments)
6. Abhijit Muhurta (auspicious time)
7. Brahma Muhurtha (dawn)
8. Godhuli Muhurtha (twilight)
9. Sandhya periods
10. Vijaya Muhurtha
11. Nishitha Kaala
12. Shubha Hora
13. Amrita Gadiya
14. Varjya

### Acceptance Criteria

- [ ] Add functions to `/src/core/panchanga/drik.ts`
- [ ] Calculations match Python drik.py implementation
- [ ] Add tests in `/tests/core/drik.test.ts`

---

## Task: Implement Upagraha Calculations

- type: feature
- priority: 2
- labels: parity, panchanga, upagrahas
- estimate: 240

### Description

Implement all upagraha (sub-planet) position calculations.

**Upagrahas to implement:**
1. Gulika (Mandi)
2. Dhuma
3. Vyatipaata
4. Parivesha
5. Indrachapa
6. Upakethu
7. Kaala
8. Mrithyu
9. Artha Praharaka
10. Yama Ghantaka

### Acceptance Criteria

- [ ] Create `/src/core/panchanga/upagraha.ts`
- [ ] Port logic from Python drik.py upagraha functions
- [ ] Add tests for all upagrahas

---

## Task: Implement Missing Special Lagnas

- type: feature
- priority: 2
- labels: parity, lagnas
- estimate: 180

### Description

Implement special lagna calculations missing from web version.

**Special Lagnas to implement:**
1. Ghati Lagna
2. Vighati Lagna
3. Pranapada Lagna
4. Indu Lagna
5. Kunda Lagna
6. Bhrigu Bindhu Lagna

### Acceptance Criteria

- [ ] Add functions to `/src/core/panchanga/drik.ts`
- [ ] Match Python implementation accuracy
- [ ] Add tests for each special lagna

---

## Task: Implement Missing Divisional Charts

- type: feature
- priority: 2
- labels: parity, charts, divisional
- estimate: 300

### Description

Implement missing divisional chart calculations.

**Charts to implement:**
1. D-5 (Panchamsa)
2. D-6 (Shashthamsa)
3. D-8 (Ashtamsa)
4. D-11 (Rudramsa)
5. D-13 (Kalamsa)
6. D-81 (Nava Navamsa)
7. D-108 (Ashtotharamsa)
8. D-144 (Dwadas Dwadasamsa)
9. D-150 (Nadiamsa)

### Acceptance Criteria

- [ ] Add varga calculations to `/src/core/horoscope/charts.ts`
- [ ] Update varga-utils.ts with new chart types
- [ ] Add tests for each new chart in charts.test.ts

---

## Task: Implement Sphuta Calculations

- type: feature
- priority: 3
- labels: parity, sphuta
- estimate: 240

### Description

Implement all sphuta (sensitive point) calculations.

**Sphutas to implement:**
1. Tri Sphuta
2. Chatur Sphuta
3. Pancha Sphuta
4. Prana Sphuta
5. Deha Sphuta
6. Mrityu Sphuta
7. Sookshma Tri Sphuta
8. Beeja Sphuta
9. Kshetra Sphuta
10. Tithi Sphuta
11. Yoga Sphuta
12. Yogi Sphuta
13. Avayogi Sphuta
14. Rahu Tithi Sphuta

### Acceptance Criteria

- [ ] Create `/src/core/horoscope/sphuta.ts`
- [ ] Port logic from Python sphuta.py (316 lines)
- [ ] Add comprehensive tests

---

## Task: Implement Graha Drishti (Planetary Aspects)

- type: feature
- priority: 2
- labels: parity, aspects
- estimate: 180

### Description

Implement full graha drishti (planetary aspects) with all 8 aspect types.

**Required aspects:**
1. Sun aspects (7th house)
2. Moon aspects (7th house)
3. Mars aspects (4th, 7th, 8th houses)
4. Mercury aspects (7th house)
5. Jupiter aspects (5th, 7th, 9th houses)
6. Venus aspects (7th house)
7. Saturn aspects (3rd, 7th, 10th houses)
8. Rahu/Ketu aspects

### Acceptance Criteria

- [ ] Add graha drishti functions to `/src/core/horoscope/house.ts`
- [ ] Port logic from Python house.py
- [ ] Add tests for all aspect combinations

---

## Task: Implement Karakas (Significators)

- type: feature
- priority: 2
- labels: parity, karakas
- estimate: 120

### Description

Implement all karaka (significator) calculations.

**Karakas to implement:**
1. Naisargika Karakas (7 natural significators)
2. Sthira Karakas (fixed significators)
3. Complete Chara Karaka calculations

### Acceptance Criteria

- [ ] Add karaka functions to `/src/core/horoscope/house.ts`
- [ ] Ensure Chara Karaka implementation is complete
- [ ] Add tests for all karaka types

---

## Task: Implement Longevity Calculations

- type: feature
- priority: 3
- labels: parity, longevity
- estimate: 180

### Description

Implement longevity and death-related calculations.

**Features to implement:**
1. Alpayu (short life) calculation
2. Madhyayu (medium life) calculation
3. Poornayu (full life) calculation
4. Maraka planet identification
5. Rudra, Brahma, Maheshwara
6. Trishoola Rasis
7. Marana Karaka Sthana

### Acceptance Criteria

- [ ] Add longevity module `/src/core/horoscope/longevity.ts`
- [ ] Port logic from Python house.py longevity functions
- [ ] Add comprehensive tests

---

## Task: Implement Tajaka/Transit System

- type: feature
- priority: 3
- labels: parity, tajaka, transit
- estimate: 480

### Description

Implement complete Tajaka (annual horoscope) system.

**Features to implement:**
1. Varsha Pravesh (annual chart)
2. Maasa Pravesh (monthly chart)
3. Sixty Hour Chart
4. Muntha calculations
5. Lord of the year/month
6. Tajaka Yogas (Ishkavala, Induvara, Ithasala, etc.)
7. All 36 Sahams (Arabic Parts)

### Acceptance Criteria

- [ ] Create `/src/core/tajaka/` directory
- [ ] Implement tajaka.ts, tajaka-yoga.ts, saham.ts
- [ ] Port logic from Python tajaka.py, tajaka_yoga.py, saham.py
- [ ] Add comprehensive tests

---

## Task: Implement Compatibility/Matching

- type: feature
- priority: 3
- labels: parity, compatibility, matching
- estimate: 360

### Description

Implement complete Ashtakoota compatibility matching system.

**Features to implement:**
1. Varna Porutham (1 point)
2. Vasiya Porutham (2 points)
3. Dina Porutham (3 points)
4. Tara Porutham (3 points)
5. Nakshathra Porutham (4 points)
6. Gana Porutham (6 points)
7. Yoni Porutham (4 points)
8. Maitri Porutham (5 points)
9. Raasi Adhipathi (2 points)
10. Additional: Bhuta, Raasi, Naadi, Mahendra, Vedha, Rajju, Sthree Dheerga

### Acceptance Criteria

- [ ] Create `/src/core/compatibility/` directory
- [ ] Implement matching.ts with all 16 matching criteria
- [ ] Support North and South Indian methods
- [ ] Add comprehensive tests

---

## Task: Implement Festival/Vratha Calendar

- type: feature
- priority: 4
- labels: parity, festivals
- estimate: 240

### Description

Implement festival and vratha (observance) calendar system.

**Features to implement:**
1. Pradosham, Sankranti, Amavasya, Pournami
2. Ekadashi, Shashthi, Chathurthi
3. Shivaratri, Chandra Dharshan
4. Mahalaya Paksha
5. Festival search and filtering
6. Multi-language festival names

### Acceptance Criteria

- [ ] Create `/src/core/calendar/` directory
- [ ] Port festival data from Python CSV files
- [ ] Implement vratha calculations
- [ ] Add search functionality

---

## Task: Implement Annual Dasha Systems

- type: feature
- priority: 3
- labels: parity, dasha
- estimate: 180

### Description

Implement missing annual dasha systems.

**Systems to implement:**
1. Mudda Dasha
2. Patyayini Dasha
3. Varsha Vimsottari Dasha
4. Varsha Narayana Dasha
5. Sudharsana Chakra Dasha
6. Aayu Dasha

### Acceptance Criteria

- [ ] Add annual dasha modules to `/src/core/dhasa/annual/`
- [ ] Port logic from Python dhasa modules
- [ ] Add tests for each system

---

## Task: Create Yoga Detection Tests

- type: task
- priority: 1
- labels: tests, critical, yoga
- estimate: 480

### Description

Create comprehensive tests for all 84+ implemented yogas. Currently NO tests exist for yoga detection.

**Test categories needed:**
1. Parivartana Yogas (Vesi, Vosi, Ubhayachara, Nipuna)
2. Mahapurusha Yogas (Ruchaka, Bhadra, Sasa, Maalavya, Hamsa)
3. Naabhasa/Shape Yogas (58 yogas)
4. Dala Yogas (16 yogas)
5. Aakriti Yogas (50+ yogas)
6. Raja Yogas
7. Malika Yogas (12 yogas)

### Acceptance Criteria

- [ ] Create `/tests/core/horoscope/yoga.test.ts`
- [ ] Add at least 600 test cases
- [ ] Cover all 84+ implemented yogas
- [ ] Use test data from Python pvr_tests.py

---

## Task: Expand Panchanga Tests

- type: task
- priority: 1
- labels: tests, panchanga
- estimate: 240

### Description

Expand panchanga tests from current 18 to ~150 (matching Python coverage).

**Tests to add:**
1. Tithi edge cases and sequences
2. Nakshatra pada validation
3. Yoga accuracy tests
4. Karana sequences
5. Special time period tests
6. Calendar system tests

### Acceptance Criteria

- [ ] Expand `/tests/core/drik.test.ts`
- [ ] Add 130+ new test cases
- [ ] Cover edge cases (month boundaries, leap years)
- [ ] Validate against Python expected values

---

## Task: Expand Divisional Chart Tests

- type: task
- priority: 2
- labels: tests, charts
- estimate: 360

### Description

Expand divisional chart tests from 47 to ~800 (matching Python coverage).

**Tests to add:**
1. All planet positions in each D-chart
2. Boundary cases (sign transitions)
3. D-5, D-6, D-8, D-11, D-13 (when implemented)
4. D-81, D-108, D-144, D-150, D-300 (when implemented)
5. Mixed chart calculations

### Acceptance Criteria

- [ ] Expand `/tests/core/horoscope/charts.test.ts`
- [ ] Add 700+ new test cases
- [ ] Cover all implemented varga charts
- [ ] Validate planet positions against Python

---

## Task: Expand Dasha System Tests

- type: task
- priority: 2
- labels: tests, dasha
- estimate: 480

### Description

Expand dasha tests from 305 to ~1,200 (matching Python coverage).

**Tests to add per dasha:**
1. Balance at birth precision
2. Mahadasha start/end dates
3. Bhukti calculations (50+ per system)
4. Antardasha calculations
5. Edge cases (birth at dasha boundary)

### Acceptance Criteria

- [ ] Each of 43 dasha systems needs 25-30 additional tests
- [ ] Total ~895 new test cases
- [ ] Validate dates against Python implementation

---

## Task: Expand Strength Calculation Tests

- type: task
- priority: 2
- labels: tests, strength
- estimate: 360

### Description

Expand strength tests from 32 to ~400 (matching Python coverage).

**Tests to add:**
1. Each Shadbala component individually
2. Bhava Bala tests
3. Vimsopaka Bala tests
4. Ishta Phala, Subha Rashmi tests
5. Cheshta Bala, Naisargika Bala

### Acceptance Criteria

- [ ] Expand `/tests/core/horoscope/strength.test.ts`
- [ ] Add 368 new test cases
- [ ] Use VP Jain and BV Raman book test data

---

## Task: Create House Analysis Tests

- type: task
- priority: 2
- labels: tests, house
- estimate: 180

### Description

Expand house analysis tests from 8 to ~100 (matching Python coverage).

**Tests to add:**
1. Graha Drishti (all aspect combinations)
2. All karaka types
3. Longevity calculations
4. Maraka identification
5. Badhaka planets

### Acceptance Criteria

- [ ] Expand `/tests/core/horoscope/house.test.ts`
- [ ] Add 92 new test cases
- [ ] Cover all aspect rules

---

## Task: Add Multi-language Support

- type: feature
- priority: 4
- labels: parity, i18n
- estimate: 240

### Description

Add multi-language support matching Python's 6 languages.

**Languages to support:**
1. English (en) - already implemented
2. Hindi (hi)
3. Kannada (ka)
4. Malayalam (ml)
5. Tamil (ta)
6. Telugu (te)

### Acceptance Criteria

- [ ] Create `/src/i18n/` directory
- [ ] Port language JSON files from Python
- [ ] Implement language switching
- [ ] Update all display components

---

## Task: Implement 17 House Systems

- type: feature
- priority: 4
- labels: parity, houses
- estimate: 360

### Description

Currently only Placidus house system is implemented. Add remaining 16 systems.

**House systems to implement:**
1. Equal Housing
2. KP System (Krishnamurti)
3. Sripathi
4. Koch
5. Porphyrius
6. Regiomontanus
7. Campanus
8. Vehlow Equal
9. Axial Rotation
10. Azimuthal/Horizontal
11. Topocentric (Polich/Page)
12. Alcabitus
13. Morinus
14. Whole Sign
15. And more...

### Acceptance Criteria

- [ ] Add house calculation methods to ephemeris adapter
- [ ] Implement house system selection in UI
- [ ] Add tests for each house system
