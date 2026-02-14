# PyJHora vs PyJHora-Web: Complete Parity Analysis

**Date**: 2026-02-07
**Python source**: `/src/jhora/` | **TypeScript port**: `/pyjhora-web/src/core/`

---

## Executive Summary

| Category | Python | TypeScript | Parity |
|----------|--------|------------|--------|
| **drik.py functions** | ~200+ | ~14 | ~7% |
| **Graha Dhasa systems** | 22 + aayu + applicability | 21 (missing aayu, applicability) | 88% |
| **Raasi Dhasa systems** | 22 | 22 | 100% |
| **Yoga functions** | ~551 (yoga.py) | ~99 exports (yoga.ts) | ~18% |
| **House functions** | ~54 (house.py) | ~18 | ~33% |
| **Chart functions** | ~99 (charts.py) | ~3 | ~3% |
| **Strength functions** | ~53 (strength.py) | ~30+ | ~57% |
| **Dosha module** | 15+ functions | **MISSING** | 0% |
| **Sphuta module** | 27 functions | **MISSING** | 0% |
| **Raja Yoga module** | 18 functions | **MISSING** | 0% |
| **Transit module** | ~80 functions | **MISSING** | 0% |
| **Annual Dhasa** | 2 systems | **MISSING** | 0% |
| **Sudharsana Chakra** | 4 functions | **MISSING** | 0% |
| **Compatibility/Match** | 1 module | **MISSING** | 0% |
| **Prediction** | 3 modules | **MISSING** | 0% |
| **Test functions** | ~170+ | ~29 files | See below |

---

## 1. MISSING MODULES (Entire Python modules with no TS equivalent)

### 1.1 Dosha Module (`horoscope/chart/dosha.py`) - **NOT PORTED**
Functions: `kala_sarpa`, `manglik`, `pitru_dosha`, `guru_chandala_dosha`, `kalathra`, `ganda_moola`, `ghata`, `shrapit` + resource/result helpers (~15 functions total)

### 1.2 Sphuta Module (`horoscope/chart/sphuta.py`) - **NOT PORTED**
Functions: `tri_sphuta`, `chatur_sphuta`, `pancha_sphuta`, `prana_sphuta`, `deha_sphuta`, `mrityu_sphuta`, `sookshma_tri_sphuta`, `beeja_sphuta`, `kshetra_sphuta`, `tithi_sphuta`, `yoga_sphuta`, `yogi_sphuta`, `avayogi_sphuta`, `rahu_tithi_sphuta` + mixed_chart variants (27 functions total)

### 1.3 Raja Yoga Module (`horoscope/chart/raja_yoga.py`) - **NOT PORTED**
Functions: `get_raja_yoga_details`, `dharma_karmadhipati_raja_yoga`, `get_raja_yoga_pairs`, `vipareetha_raja_yoga`, `neecha_bhanga_raja_yoga`, `check_other_raja_yoga_1/2/3` (18 functions total)

### 1.4 Transit Module (`horoscope/transit/`) - **NOT PORTED**

#### 1.4.1 `tajaka.py` (~30 functions)
- Annual chart: `varsha_pravesh`, `annual_chart`, `annual_chart_approximate`
- Monthly chart: `maasa_pravesh`, `monthly_chart`
- 60-hour chart: `sixty_hour_chart`
- Lord calculations: `lord_of_the_year`, `lord_of_the_month`
- Tajaka aspects: `trinal_aspects_of_the_raasi/planet`, `sextile_aspects_of_the_raasi/planet`, `square_aspects_of_the_raasi/planet`, `benefic_aspects_of_the_raasi/planet`, `malefic_aspects_of_the_raasi/planet`, `opposition_aspects_of_the_raasi/planet`, `conjunction_aspects_of_the_raasi/planet`, `semi_sextile_aspects_of_the_raasi/planet`, `neutral_aspects_of_the_raasi/planet`
- Helpers: `both_planets_within_their_deeptamsa`, `both_planets_approaching`

#### 1.4.2 `tajaka_yoga.py` (~20 functions)
- `ishkavala_yoga`, `induvara_yoga`, `ithasala_yoga`, `eesarpha_yoga`, `nakta_yoga`, `check_yamaya_yoga`
- Pair/triple finders: `get_ithasala_yoga_planet_pairs`, `get_eesarpha_yoga_planet_pairs`, `get_nakta_yoga_planet_triples`, `get_yamaya_yoga_planet_triples`, `get_manahoo_yoga_planet_pairs`, `get_kamboola_yoga_planet_pairs`, `get_gairi_kamboola_yoga_planet_pairs`, `get_khallasara_yoga_planet_pairs`, `get_radda_yoga_planet_pairs`, `get_duhphali_kutta_yoga_planet_pairs`

#### 1.4.3 `saham.py` (~35 functions)
- `punya_saham`, `vidya_saham`, `yasas_saham`, `mitra_saham`, `mahatmaya_saham`, `asha_saham`, `samartha_saham`, `bhratri_saham`, `gaurava_saham`, `pithri_saham`, `rajya_saham`, `maathri_saham`, `puthra_saham`, `jeeva_saham`, `karma_saham`, `roga_saham`, `kali_saham`, `sastra_saham`, `bandhu_saham`, `mrithyu_saham`, `paradesa_saham`, `artha_saham`, `paradara_saham`, `vanika_saham`, `karyasiddhi_saham`, `vivaha_saham`, `santapa_saham`, `sraddha_saham`, `preethi_saham`, `jadya_saham`, `vyaapaara_saham`, `sathru_saham`, `jalapatna_saham`, `bandhana_saham`, `apamrithyu_saham`, `laabha_saham`

### 1.5 Annual Dhasa (`horoscope/dhasa/annual/`) - **NOT PORTED**
- `patyayini.py`: Patyayini dasa system
- `mudda.py`: Mudda varsha vimsottari dasa

### 1.6 Sudharsana Chakra (`horoscope/dhasa/sudharsana_chakra.py`) - **NOT PORTED**
Functions: `sudharshana_chakra_chart`, `sudharsana_chakra_dhasa_for_divisional_chart`, `sudharsana_pratyantardasas`

### 1.7 Aayu/Longevity Dhasa (`horoscope/dhasa/graha/aayu.py`) - **NOT PORTED**
Functions: `pindayu_dhasa_bhukthi`, `nisargayu_dhasa_bhukthi`, `amsayu_dhasa_bhukthi`, `longevity`, `get_dhasa_antardhasa` + many internal harana functions (25 functions total)

### 1.8 Applicability Module (`horoscope/dhasa/graha/applicability.py`) - **NOT PORTED**
Dhasa applicability check functions

### 1.9 Compatibility/Match (`horoscope/match/compatibility.py`) - **NOT PORTED**

### 1.10 Prediction Modules (`horoscope/prediction/`) - **NOT PORTED**
- `general.py`: General predictions
- `longevity.py`: Longevity predictions
- `naadi_marriage.py`: Naadi marriage predictions

### 1.11 Panchanga Extras - **NOT PORTED**
- `vratha.py`: Special day calculations (amavasya, ekadashi, etc.)
- `pancha_paksha.py`: Pancha paksha calculations
- `info.py`: Panchanga info

---

## 2. PARTIALLY PORTED MODULES (Module exists but missing many functions)

### 2.1 drik.py → drik.ts (~7% coverage)

**TS has (14 functions):**
- `nakshatraPada`, `calculateTithi`, `calculateNakshatra`, `calculateYoga`, `calculateKarana`, `calculateVara`
- `getPlanetLongitude`, `getAllPlanetPositions`
- `dayLength`, `nightLength`
- `sreeLagnaFromLongitudes`, `getSreeLagna`, `getHoraLagna`

**Missing from TS (~180+ functions):**

| Category | Missing Functions |
|----------|-----------------|
| **Muhurta** | `gauri_choghadiya`, `shubha_hora`, `trikalam`, `durmuhurtam`, `abhijit_muhurta`, `brahma_muhurtha`, `godhuli_muhurtha`, `vijaya_muhurtha`, `nishita_kaala`, `nishita_muhurtha`, `muhurthas`, `udhaya_lagna_muhurtha`, `amrit_kaalam` |
| **Bhava** | `bhaava_madhya`, `bhaava_madhya_swe`, `bhaava_madhya_kp`, `bhaava_madhya_sripathi`, `_assign_planets_to_houses`, `_bhaava_madhya_new` |
| **Additional Lagnas** | `special_ascendant` (ghati/bhava/vighati), `pranapada_lagna`, `indu_lagna`, `kunda_lagna`, `bhrigu_bindhu_lagna`, `ascendant` |
| **Varnada Lagna** | Part of special lagnas |
| **Upagrahas** | `solar_upagraha_longitudes`, `upagraha_longitude` |
| **Lunar Calendar** | `lunar_month`, `lunar_month_date`, `vedic_date`, `samvatsara`, `ritu`, `new_moon`, `full_moon`, `next_tithi`, `lunar_phase`, `elapsed_year`, `lunar_year_index` |
| **Tamil Calendar** | `tamil_solar_month_and_date` (5+ variants), `days_in_tamil_month`, `tamil_solar_month_and_date_from_jd` |
| **Sankranti** | `previous_sankranti_date`, `next_sankranti_date` |
| **Eclipses** | `is_solar_eclipse`, `next_solar_eclipse`, `next_lunar_eclipse` |
| **Conjunctions** | `next_conjunction_of_planet_pair`, `previous_conjunction_of_planet_pair` |
| **Planet Transit** | `next_planet_entry_date`, `previous_planet_entry_date`, `next_planet_retrograde_change_date`, `next_ascendant_entry_date` |
| **Divisional Charts** | `dasavarga_from_long`, `dhasavarga` |
| **Graha Yudh** | `planets_in_graha_yudh` |
| **Declination** | `declination_of_planets` |
| **Special Calcs** | `nisheka_time`, `graha_drekkana`, `sahasra_chandrodayam`, `amrita_gadiya`, `varjyam`, `anandhaadhi_yoga`, `triguna`, `vivaha_chakra_palan`, `tamil_yogam` |
| **Vedic Time** | `float_hours_to_vedic_time`, `float_hours_to_vedic_time_equal_day_night_ghati` |
| **Panchanga Extras** | `thaaraabalam`, `chandrabalam`, `panchaka_rahitha`, `chandrashtama`, `nava_thaara`, `special_thaara`, `karaka_tithi`, `karaka_yogam`, `fraction_moon_yet_to_traverse`, `shiva_vaasa`, `agni_vaasa`, `pushkara_yoga`, `aadal_yoga`, `vidaal_yoga`, `disha_shool`, `yogini_vaasa` |
| **Solar Dates** | `next_solar_date`, `next_annual_solar_date_approximate`, `next_solar_month`, `next_solar_year`, `previous_solar_month`, `previous_solar_year`, `next_lunar_month`, `previous_lunar_month`, `next_lunar_year`, `previous_lunar_year` |
| **Birth Rectification** | `_birthtime_rectification_nakshathra_suddhi`, `_birthtime_rectification_lagna_suddhi`, `_birthtime_rectification_janma_suddhi` |

### 2.2 yoga.py → yoga.ts (~18% coverage)

**Python**: 551 `def` statements (many internal)
**TypeScript**: ~99 exports

**TS has** (partial list):
- Ravi yogas: `vesiYoga`, `vosiYoga`, `ubhayacharaYoga`, `nipunaYoga`/`budhaAadityaYoga`
- Chandra yogas: `sunaphaaYoga`, `anaphaaYoga`, `duradharaYoga`/`dhurdhuraYoga`, `kemadrumaYoga`, `chandraMangalaYoga`, `adhiYoga`
- Pancha Mahapurusha: `ruchakaYoga`, `bhadraYoga`, `sasaYoga`, `maalavyaYoga`, `hamsaYoga`
- Naabhasa/Aakriti: `rajjuYoga`, `musalaYoga`, `nalaYoga`, `maalaaYoga`, `sarpaYoga`, `gadaaYoga`, `sakataYoga`, `vihangaYoga`, `sringaatakaYoga`, `halaYoga`, `vajraYoga`, `yavaYoga`, `kamalaYoga`, `vaapiYoga`, `yoopaYoga`, `saraYoga`, `saktiYoga`, `dandaYoga`, `naukaaYoga`, `kootaYoga`, `chatraYoga`, `chaapaYoga`, `ardhaChandraYoga`, `chakraYoga`, `samudraYoga`
- Others: `gajaKesariYoga`, `guruMangalaYoga`, `amalaYoga`, `parvataYoga`, `harshaYoga`, `saralaYoga`, `vimalaYoga`, `chatussagaraYoga`, `rajalakshanaYoga`

**Missing from TS** (major categories):
- Most raja yogas (~50+ functions in Python)
- Sankhya yogas (7 types)
- Dala yogas (many)
- Many "other" yogas from Python
- Planetary combination yogas
- All "check_yoga_for_chart" orchestration functions
- Yoga resource/description infrastructure

### 2.3 house.py → house.ts (~33% coverage)

**Python**: ~54 functions
**TS has**: `getArgala`, `getLordOfSign`, `getRaasiDrishtiFromChart`, `getCharaKarakas`, `getStrongerPlanetFromPositions`, `getStrongerRasi`, `getBrahma`, `getPlanetToHouseDict`, `getHouseToPlanetList`, `getHouseOwnerFromPlanetPositions` + helpers (~18)

**Missing**: Many graha drishti functions, aspect detail functions, planet friendship/relationship calculations, most helper/utility functions

### 2.4 charts.py → charts.ts (~3% coverage)

**Python**: ~99 functions (all divisional chart methods: Parashara, Jagannatha, Parivritti, Parivritti Cyclic, etc.)
**TS has**: `getLongitudeInVarga`, `getDivisionalChart`, `calculateDivisionalChart` (3 main functions)

**Missing**: Most individual chart method implementations, mixed chart calculations, detailed varga-specific functions

### 2.5 strength.py → strength.ts (~57% coverage)

**Python**: ~53 functions
**TS has**: `calculateUchchaBala`, `calculateSaptavargajaBala`, `calculateOjayugamaBala`, `calculateKendraBala`, `calculateDreshkonBala`, `calculateSthanaBala`, `calculateNathonnathBala`, `calculatePakshaBala`, `calculateTribhagaBala`, `calculateAbdadhipathiBala`, `calculateMasadhipathiBala`, `calculateVaaradhipathiBala`, `calculateHoraBala`, `calculateAyanaBala`, `calculateYuddhaBala`, `calculateKaalaBala`, `calculateDigBala`, `calculateCheshtaBala`, `calculateNaisargikaBala`, `calculateDrikBala`, `calculateShadBala`, `calculateBhavaAdhipathiBala`, `calculateBhavaDigBala`, `calculateBhavaBala`, `calculateHarshaBala`, `calculatePanchaVargeeyaBala`, `calculateDwadhasaVargeeyaBala`, `calculatePlanetAspectRelationshipTable` (~30)

**Missing**: Some subcomponent functions, ishta/kashta phala calculations

---

## 3. GRAHA DHASA PARITY

| # | Python Module | TS Module | Status |
|---|--------------|-----------|--------|
| 1 | vimsottari.py | vimsottari.ts | **Ported** |
| 2 | ashtottari.py | ashtottari.ts | **Ported** |
| 3 | yogini.py | yogini.ts | **Ported** |
| 4 | kaala.py | kaala.ts | **Ported** |
| 5 | naisargika.py | naisargika.ts | **Ported** |
| 6 | buddhi_gathi.py | buddhi-gathi.ts | **Ported** |
| 7 | karaka.py | karaka.ts | **Ported** |
| 8 | shastihayani.py | shastihayani.ts | **Ported** |
| 9 | chathuraaseethi_sama.py | chaturaseethi.ts | **Ported** |
| 10 | karana_chathuraaseethi_sama.py | karana-chathuraaseethi.ts | **Ported** |
| 11 | dwadasottari.py | dwadasottari.ts | **Ported** |
| 12 | dwisatpathi.py | dwisatpathi.ts | **Ported** |
| 13 | panchottari.py | panchottari.ts | **Ported** |
| 14 | saptharishi_nakshathra.py | saptharishi.ts | **Ported** |
| 15 | sataatbika.py | sataabdika.ts | **Ported** |
| 16 | shattrimsa_sama.py | shattrimsa.ts | **Ported** |
| 17 | shodasottari.py | shodasottari.ts | **Ported** |
| 18 | tara.py | tara.ts | **Ported** |
| 19 | tithi_ashtottari.py | tithi-ashtottari.ts | **Ported** |
| 20 | tithi_yogini.py | tithi-yogini.ts | **Ported** |
| 21 | yoga_vimsottari.py | yoga-vimsottari.ts | **Ported** |
| 22 | **aayu.py** | - | **MISSING** |
| - | **applicability.py** | - | **MISSING** |

### 21/22 graha dhasa systems ported (95%). Missing: aayu (longevity) dhasa.

---

## 4. RAASI DHASA PARITY

| # | Python Module | TS Module | Status |
|---|--------------|-----------|--------|
| 1 | narayana.py | narayana.ts | **Ported** |
| 2 | chara.py | chara.ts | **Ported** |
| 3 | kalachakra.py | kalachakra.ts | **Ported** |
| 4 | brahma.py | brahma.ts | **Ported** |
| 5 | moola.py | moola.ts | **Ported** |
| 6 | drig.py | drig.ts | **Ported** |
| 7 | nirayana.py | nirayana.ts | **Ported** |
| 8 | shoola.py | shoola.ts | **Ported** |
| 9 | kendradhi_rasi.py | kendradhi.ts | **Ported** |
| 10 | sudasa.py | sudasa.ts | **Ported** |
| 11 | sthira.py | sthira.ts | **Ported** |
| 12 | trikona.py | trikona.ts | **Ported** |
| 13 | tara_lagna.py | tara-lagna.ts | **Ported** |
| 14 | mandooka.py | mandooka.ts | **Ported** |
| 15 | lagnamsaka.py | lagnamsaka.ts | **Ported** |
| 16 | navamsa.py | navamsa.ts | **Ported** |
| 17 | padhanadhamsa.py | padhanadhamsa.ts | **Ported** |
| 18 | paryaaya.py | paryaaya.ts | **Ported** |
| 19 | varnada.py | varnada.ts | **Ported** |
| 20 | yogardha.py | yogardha.ts | **Ported** |
| 21 | chakra.py | chakra.ts | **Ported** |
| 22 | sandhya.py | sandhya.ts | **Ported** |

### 22/22 raasi dhasa systems ported (100%).

---

## 5. TEST PARITY ANALYSIS

### Python Tests: ~170+ test functions in `pvr_tests.py`
### TypeScript Tests: 29 test files in `tests/core/`

### 5.1 Tests Present in Both (TS has coverage)

| Python Test | TS Test File | Notes |
|------------|-------------|-------|
| vimsottari_tests (11 tests) | vimsottari.test.ts | Covered |
| ashtottari_tests (9 tests) | ashtottari.test.ts, dasha-systems.test.ts | Covered |
| yoga_vimsottari_tests | yoga-vimsottari.test.ts | Covered |
| yogini_test | yogini.test.ts, dasha-systems.test.ts | Covered |
| chathuraseethi_sama_tests | dasha-systems.test.ts | Covered |
| karana_chathuraseethi_sama_test | karana-chathuraaseethi.test.ts | Covered |
| dwadasottari_test | dasha-systems.test.ts | Covered |
| dwisatpathi_test | dasha-systems.test.ts | Covered |
| naisargika_test | dasha-systems.test.ts | Covered |
| saptharishi_nakshathra_test | dasha-systems.test.ts | Covered |
| panchottari_test | dasha-systems.test.ts | Covered |
| sataatbika_test | dasha-systems.test.ts | Covered |
| shastihayani_test | dasha-systems.test.ts | Covered |
| shattrimsa_sama_test | dasha-systems.test.ts | Covered |
| shodasottari_test | dasha-systems.test.ts | Covered |
| tara_dhasa_test | dasha-systems.test.ts | Covered |
| tithi_yogini_test | tithi-yogini.test.ts | Covered |
| tithi_ashtottari_tests | tithi-ashtottari.test.ts | Covered |
| buddhi_gathi_test | buddhi-gathi.test.ts | Covered |
| kaala_test | kaala.test.ts | Covered |
| karaka_dhasa_test | karaka.test.ts | Covered |
| narayana_dhasa_tests | narayana.test.ts | Covered |
| drig_dhasa_tests | drig-trikona.test.ts | Covered |
| nirayana_shoola_dhasa_tests | kendradhi-nirayana.test.ts | Covered |
| shoola_dhasa_tests | mandooka-shoola.test.ts | Covered |
| kalachakra_dhasa_tests | (in raasi tests) | Covered |
| brahma_dhasa_test | (covered) | Covered |
| chara_dhasa_test | chara.test.ts | Covered |
| kendradhi_rasi_test | kendradhi-nirayana.test.ts | Covered |
| lagnamsaka_dhasa_test | navamsa-lagnamsaka.test.ts | Covered |
| mandooka_dhasa_test | mandooka-shoola.test.ts | Covered |
| moola_dhasa_test | moola.test.ts | Covered |
| navamsa_dhasa_test | navamsa-lagnamsaka.test.ts | Covered |
| trikona_dhasa_test | drig-trikona.test.ts | Covered |
| chakra_test | chakra-yogardha.test.ts | Covered |
| _ashtaka_varga_tests | ashtakavarga.test.ts | Covered |
| divisional_chart_tests | charts.test.ts | Partial |
| _graha_drishti_tests | house.test.ts | Partial |
| _raasi_drishti_tests | house.test.ts | Partial |
| stronger_rasi_tests | raasi_strength.test.ts | Partial |
| shadbala tests | strength.test.ts | Covered |
| panchanga basic tests | drik.test.ts | Partial |

### 5.2 MISSING TESTS (Python tests with NO TS equivalent)

#### Panchanga Tests (6 missing)
- [ ] `_tithi_tests` - Specific tithi validation with expected values
- [ ] `_nakshatra_tests` - Specific nakshatra validation
- [ ] `_yogam_tests` - Specific yogam validation
- [ ] `_masa_tests` - Lunar month validation
- [ ] `panchanga_tests` - Comprehensive panchanga output
- [ ] `ayanamsa_tests` - Ayanamsa value validation

#### Lagna Tests (2 missing)
- [ ] `special_lagna_tests` - Ghati, Bhava, Vighati, Hora, Pranapada, Indu, Sree, Bhrigu Bindhu, Kunda lagnas
- [ ] `varnada_lagna_tests` - Varnada lagna calculations

#### Yoga Tests (9 missing)
- [ ] `raja_yoga_tests` - Raja yoga calculations
- [ ] `ravi_yoga_tests` - Sun-based yogas
- [ ] `chandra_yoga_tests` - Moon-based yogas
- [ ] `pancha_mahapurusha_yogas` - Five great person yogas
- [ ] `naabhasa_aasrya_yogas` - Naabhasa yogas
- [ ] `dala_yogas` - Dala yoga patterns
- [ ] `aakriti_yogas` - Aakriti (shape) yogas
- [ ] `sankhya_yoga_tests` - Sankhya yogas
- [ ] `other_yoga_tests` - Miscellaneous yogas

#### Strength Tests (3 missing)
- [ ] `_uccha_rashmi_test` - Uccha rashmi specific test
- [ ] `harsha_bala_tests` - Harsha bala validation (TS has harsha bala functions but limited tests)
- [ ] `pancha_vargeeya_bala_tests` / `dwadhasa_vargeeya_bala_tests` - Specific validation

#### Transit/Tajaka Tests (15 missing)
- [ ] `saham_tests` - All 35 saham calculations
- [ ] `lord_of_the_year_test` - Annual lord calculation
- [ ] `lord_of_the_month_test` - Monthly lord calculation
- [ ] `_ishkavala_yoga_test` - Ishkavala yoga
- [ ] `_induvara_yoga_test` - Induvara yoga
- [ ] `tajaka_yoga_tests` - Tajaka yoga suite
- [ ] `combustion_tests` - Planet combustion
- [ ] `retrograde_combustion_tests` - Retrograde combustion
- [ ] `_tajaka_aspect_test` - Tajaka aspects
- [ ] `ithasala_yoga_tests` - Ithasala yoga
- [ ] `eesarpa_yoga_tests` - Eesarpa yoga
- [ ] `nakta_yoga_tests` - Nakta yoga
- [ ] `yamaya_yoga_tests` - Yamaya yoga
- [ ] `planet_transit_tests` - Planet transit calculations
- [ ] `conjunction_tests` / `conjunction_tests_1` / `conjunction_tests_2` - Planetary conjunctions

#### Raasi Dhasa Tests (9 missing)
- [ ] `sudasa_tests` - Sudasa dhasa
- [ ] `sthira_dhasa_test` - Sthira dhasa
- [ ] `tara_lagna_dhasa_test` - Tara lagna dhasa
- [ ] `padhanadhamsa_dhasa_test` - Padhanadhamsa dhasa
- [ ] `paryaaya_dhasa_test` - Paryaaya dhasa
- [ ] `varnada_dhasa_test` - Varnada dhasa
- [ ] `sandhya_test` - Sandhya dhasa
- [ ] `narayana_dhasa_tests_1` - Additional narayana tests
- [ ] `yogardha_dhasa_test` - Yogardha dhasa (TS has chakra-yogardha.test.ts but may not cover all)

#### Graha Dhasa Tests (2 missing)
- [ ] `aayu_test` / `_aayu_santhanam_test` - Aayu/longevity dhasa
- [ ] (applicability tests if any)

#### Annual Dhasa Tests (3 missing)
- [ ] `patyayini_tests` - Patyayini dasa
- [ ] `varsha_narayana_tests` - Varsha narayana dasa
- [ ] `mudda_varsha_vimsottari_tests` - Mudda varsha vimsottari

#### Sudharsana Tests (1 missing)
- [ ] `sudharsana_chakra_dhasa_tests` - Sudharsana chakra dasa

#### Dosha Tests (2 missing)
- [ ] `sarpa_dosha_tests` - Kala sarpa dosha
- [ ] `manglik_dosha_tests` - Manglik dosha

#### Sphuta Tests (1 missing)
- [ ] `sphuta_tests` - All sphuta calculations

#### House Tests (2 missing)
- [ ] `bhaava_house_tests` - Bhava house calculations
- [ ] `_stronger_planet_tests` - Stronger planet determination

#### Other Tests (7 missing)
- [ ] `tithi_pravesha_tests` - Tithi pravesha (solar return)
- [ ] `vakra_gathi_change_tests` - Retrograde direction changes
- [ ] `nisheka_lagna_tests` - Conception time calculations
- [ ] `graha_yudh_test` - Planetary war
- [ ] `mrityu_bhaga_test` - Death degree
- [ ] `lattha_test` - Lattha calculations
- [ ] `kshaya_maasa_tests` - Intercalary month tests
- [ ] `div_chart_16_test` - D-16 specific test
- [ ] `amsa_deity_tests` - Amsa deity calculations

### 5.3 Summary of Missing Tests

| Category | Missing Test Count |
|----------|-------------------|
| Panchanga | 6 |
| Lagnas | 2 |
| Yogas | 9 |
| Strength | 3 |
| Transit/Tajaka | 15 |
| Raasi Dhasas | 9 |
| Graha Dhasas | 2 |
| Annual Dhasas | 3 |
| Sudharsana | 1 |
| Doshas | 2 |
| Sphutas | 1 |
| House | 2 |
| Other | 9 |
| **TOTAL** | **~64 test groups** |

---

## 6. KNOWN SYSTEMIC ISSUES (from previous analysis)

1. **No sync ascendant**: TS uses Sun as Lagna proxy (affects 17/22 raasi dhasas)
2. **Sync path inaccurate**: TS sync functions use crude approximations vs Python's Swiss Ephemeris
3. **Missing `inverse_lagrange()`**: Critical for accurate panchanga timing
4. **~130 functions missing from drik.ts** vs Python's drik.py

---

## 7. PRIORITY RECOMMENDATIONS

### P0 - Critical (Core functionality gaps)
1. Port remaining ~180 drik.py functions to drik.ts
2. Port dosha.py (kala sarpa, manglik - commonly used features)
3. Port sphuta.py (essential for horoscope analysis)
4. Add missing panchanga tests with Python-matching expected values

### P1 - High (Feature completeness)
5. Port raja_yoga.py
6. Port transit/tajaka.py and tajaka_yoga.py
7. Port transit/saham.py
8. Port aayu.py (longevity dhasa)
9. Add missing yoga tests (9 test groups)
10. Add missing raasi dhasa tests (9 test groups)

### P2 - Medium (Full parity)
11. Port annual dhasas (patyayini, mudda)
12. Port sudharsana_chakra.py
13. Port applicability.py
14. Add remaining transit/tajaka tests (15 test groups)
15. Expand yoga.ts coverage to match Python's 551 functions

### P3 - Lower (Nice to have)
16. Port compatibility/match module
17. Port prediction modules
18. Port vratha.py, pancha_paksha.py
19. Add all remaining "other" tests
