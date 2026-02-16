/**
 * Varga (Divisional Chart) Calculation Utilities
 * Implements standard algorithms for calculating planetary positions in divisional charts.
 */

import {
  DUAL_SIGNS, EVEN_SIGNS, FIXED_SIGNS, ODD_SIGNS,
  HORA_LIST_RAMAN, DREKKANA_JAGANNATHA, KALACHAKRA_NAVAMSA,
  EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS,
} from '../constants';
import { longitudeInSign, rasiFromLongitude } from '../utils/angle';

/**
 * Calculate the part index (0 to N-1) of a planet in a sign for a given division factor D
 */
export const getVargaPart = (longitude: number, divisionFactor: number): number => {
  const longInSign = longitudeInSign(longitude);
  const partSpan = 30.0 / divisionFactor;
  // Use modulo-based calculation to match Python's floor division behavior.
  // JS and Python can disagree on `10 / (30/9)` (3.0 vs 2.999...) due to
  // IEEE 754 implementation differences. Using fmod avoids this:
  // Python: int(long // f1) is equivalent to round((long - fmod(long,f1)) / f1)
  const mod = longInSign % partSpan;
  return Math.round((longInSign - mod) / partSpan);
};

/**
 * Calculates the dasavarga-sign and longitude within it.
 * Replicates Python's `dasavarga_from_long` exactly, including 
 * rounding tolerance for sign transitions.
 */
export const dasavargaFromLong = (longitude: number, divisionFactor: number = 1): { rasi: number; longitude: number } => {
  const one_pada = 360.0 / (12 * divisionFactor);
  const one_sign = 12.0 * one_pada;
  const signs_elapsed = longitude / one_sign;
  const fraction_left = signs_elapsed % 1;
  let constellation = Math.floor(fraction_left * 12);
  let long_in_raasi = (longitude - (constellation * 30)) % 30;

  // Python logic: "if long_in_raasi 30 make it and zero and add a rasi"
  // Python uses a tolerance check: int(long_in_raasi + 1/3600) == 30
  // 1/3600 is approx 0.0002777...
  const one_second_longitude_in_degrees = 1.0 / 3600.0;

  if (Math.floor(long_in_raasi + one_second_longitude_in_degrees) === 30) {
    long_in_raasi = 0;
    constellation = (constellation + 1) % 12;
  }

  return { rasi: constellation, longitude: long_in_raasi };
};

/**
 * Standard Parivritti / Cyclic calculation (Cyclic from Aries)
 * Used in many charts where counting is continuous from Aries.
 * e.g. D-3 (Jagannatha), D-9 (Kalachakra), etc. if specified, but usually D-charts have specific rules.
 * This implements the "Cyclic" mapping:
 * Each sign is divided into N parts. The count starts from Aries 1st part -> Aries, 
 * continued through the zodiac.
 * Formula: (SignIndex * N + PartIndex) % 12
 */
export const calculateCyclicVarga = (longitude: number, divisionFactor: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, divisionFactor);
  return (rasi * divisionFactor + part) % 12;
};

/**
 * Parivritti with Even Signs Reverse
 * Odd signs: Cyclic forward (starts from somewhere?) usually from Aries?
 * Even signs: Cyclic backward?
 * This is less standard as a generic rule, usually specific to D-Chart.
 * We will implement specific charts instead of generic "Even Reverse" unless we know the exact anchor.
 */

// ============================================================================
// SPECIFIC VARGA CALCULATIONS (Standard Parashara / Jaimini)
// ============================================================================

/**
 * D-1 Rasi
 */
export const calculateD1_Rasi = (longitude: number): number => {
  return rasiFromLongitude(longitude);
};

/**
 * D-2 Hora (Parashara)
 * Odd signs: 1st half -> Sun (Leo), 2nd half -> Moon (Cancer)
 * Even signs: 1st half -> Moon (Cancer), 2nd half -> Sun (Leo)
 * Note: JHora uses Sun=Leo(4), Moon=Cancer(3).
 */
export const calculateD2_Hora_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 2); // 0 or 1
  
  // Sun's sign = Leo (4), Moon's sign = Cancer (3)
  const SUN_SIGN = 4;
  const MOON_SIGN = 3;

  if (ODD_SIGNS.includes(rasi)) {
    return part === 0 ? SUN_SIGN : MOON_SIGN;
  } else {
    return part === 0 ? MOON_SIGN : SUN_SIGN;
  }
};

/**
 * D-3 Drekkana (Parashara)
 * Part 1 (0-10): Sign itself
 * Part 2 (10-20): 5th from Sign
 * Part 3 (20-30): 9th from Sign
 */
export const calculateD3_Drekkana_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 3); // 0, 1, 2
  
  if (part === 0) return rasi;
  if (part === 1) return (rasi + 4) % 12; // 5th house
  return (rasi + 8) % 12; // 9th house
};

/**
 * D-4 Chaturthamsa (Parashara)
 * Part 1: Sign itself
 * Part 2: 4th from Sign
 * Part 3: 7th from Sign
 * Part 4: 10th from Sign
 */
export const calculateD4_Chaturthamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 4); // 0, 1, 2, 3
  
  // 1, 4, 7, 10 mapping
  // part 0 -> +0
  // part 1 -> +3
  // part 2 -> +6
  // part 3 -> +9
  return (rasi + (part * 3)) % 12;
};

/**
 * D-7 Saptamsa (Parashara)
 * Odd signs: count from Sign itself
 * Even signs: count from 7th from Sign
 */
export const calculateD7_Saptamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 7); // 0..6
  
  let startSign = rasi;
  if (EVEN_SIGNS.includes(rasi)) {
    startSign = (rasi + 6) % 12;
  }
  
  return (startSign + part) % 12;
};

/**
 * D-9 Navamsa (Parashara)
 * Movable: count from Sign itself
 * Fixed: count from 9th from Sign
 * Dual: count from 5th from Sign
 */
export const calculateD9_Navamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 9); // 0..8
  
  let startSign = rasi;
  if (FIXED_SIGNS.includes(rasi)) {
    startSign = (rasi + 8) % 12;
  } else if (DUAL_SIGNS.includes(rasi)) {
    startSign = (rasi + 4) % 12;
  }
  
  return (startSign + part) % 12;
};

/**
 * D-10 Dasamsa (Parashara)
 * Odd signs: count from Sign itself
 * Even signs: count from 9th from Sign
 */
export const calculateD10_Dasamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 10);
  
  let startSign = rasi;
  if (EVEN_SIGNS.includes(rasi)) {
    startSign = (rasi + 8) % 12;
  }
  
  return (startSign + part) % 12;
};

/**
 * D-12 Dwadasamsa (Parashara)
 * Count from Sign itself
 */
export const calculateD12_Dwadasamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 12);
  return (rasi + part) % 12;
};

/**
 * D-16 Shodasamsa (Parashara)
 * Movable: Starts from Aries
 * Fixed: Starts from Leo
 * Dual: Starts from Sagittarius
 * (This is counting 1, 5, 9 signs from Aries based on Move/Fix/Dual?
 * Parashara logic:
 * Movable -> Start from Aries
 * Fixed -> Start from Leo
 * Dual -> Start from Sagittarius
 * Then count part index.
 */
export const calculateD16_Shodasamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 16);
  
  let startSign = 0; // Aries
  if (FIXED_SIGNS.includes(rasi)) {
    startSign = 4; // Leo
  } else if (DUAL_SIGNS.includes(rasi)) {
    startSign = 8; // Sagittarius
  }
  
  return (startSign + part) % 12;
};

/**
 * D-20 Vimsamsa (Parashara)
 * Movable: Start from Aries
 * Fixed: Start from Sagittarius
 * Dual: Start from Leo
 * Note: Check order. Movable(1) -> Ar(1), Fixed(2) -> Sag(9), Dual(3) -> Leo(5) ??
 * JHora source says:
 * Movable: from Aries
 * Fixed: from Sagittarius
 * Dual: from Leo
 * (Wait, this is 1, 9, 5 order?)
 * 
 * Let's verify standard BPHS.
 * Movable: From Aries (1)
 * Fixed: From Sagittarius (9)
 * Dual: From Leo (5)
 * Yes, matches JHora implementation usually.
 */
export const calculateD20_Vimsamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 20);
  
  let startSign = 0; // Aries
  if (FIXED_SIGNS.includes(rasi)) {
    startSign = 8; // Sagittarius
  } else if (DUAL_SIGNS.includes(rasi)) {
    startSign = 4; // Leo
  }
  
  return (startSign + part) % 12;
};

/**
 * D-24 Chaturvimsamsa (Parashara)
 * Odd signs: Start from Leo
 * Even signs: Start from Cancer
 */
export const calculateD24_Chaturvimsamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 24);
  
  let startSign = 4; // Leo
  if (EVEN_SIGNS.includes(rasi)) {
    startSign = 3; // Cancer
  }
  
  return (startSign + part) % 12;
};

/**
 * D-27 Bhamsa / Saptavimsamsa (Parashara)
 * Fiery (1,5,9): Start from Aries
 * Earthy (2,6,10): Start from Cancer
 * Airy (3,7,11): Start from Libra
 * Watery (4,8,12): Start from Capricorn
 * (Basically start from 1, 4, 7, 10 based on element)
 */
export const calculateD27_Bhamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 27);
  
  // Element offset: 0 for Fire, 1 for Earth, 2 for Air, 3 for Water
  // Signs: 0(Fire), 1(Earth), 2(Air), 3(Water)... pattern repeats
  const element = rasi % 4; 
  
  let startSign = 0;
  if (element === 0) startSign = 0; // Aries
  if (element === 1) startSign = 3; // Cancer
  if (element === 2) startSign = 6; // Libra
  if (element === 3) startSign = 9; // Capricorn
  
  return (startSign + part) % 12;
};

/**
 * D-30 Trimsamsa (Parashara)
 * Odd Signs:
 * 0-5 deg (0-5 parts): Mars (Aries)
 * 5-10 deg (5-10 parts): Saturn (Aquarius)
 * 10-18 deg (10-18 parts): Jupiter (Sagittarius)
 * 18-25 deg (18-25 parts): Mercury (Gemini)
 * 25-30 deg (25-30 parts): Venus (Libra)
 * 
 * Even Signs:
 * 0-5 deg: Venus (Taurus)
 * 5-12 deg: Mercury (Virgo)
 * 12-20 deg: Jupiter (Pisces)
 * 20-25 deg: Saturn (Capricorn)
 * 25-30 deg: Mars (Scorpio)
 * 
 * Note: Parts are not equal size! Logic above is by degree spans.
 */
export const calculateD30_Trimsamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  
  if (ODD_SIGNS.includes(rasi)) {
    if (longInSign < 5) return 0; // Aries (Mars)
    if (longInSign < 10) return 10; // Aquarius (Saturn)
    if (longInSign < 18) return 8; // Sagittarius (Jupiter)
    if (longInSign < 25) return 2; // Gemini (Mercury)
    return 6; // Libra (Venus)
  } else {
    // Even Signs
    if (longInSign < 5) return 1; // Taurus (Venus)
    if (longInSign < 12) return 5; // Virgo (Mercury)
    if (longInSign < 20) return 11; // Pisces (Jupiter)
    if (longInSign < 25) return 9; // Capricorn (Saturn)
    return 7; // Scorpio (Mars)
  }
};

/**
 * D-40 Khavedamsa (Parashara)
 * Odd signs: Start from Aries
 * Even signs: Start from Libra
 */
export const calculateD40_Khavedamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 40);
  
  let startSign = 0; // Aries
  if (EVEN_SIGNS.includes(rasi)) {
    startSign = 6; // Libra
  }
  
  return (startSign + part) % 12;
};

/**
 * D-45 Akshavedamsa (Parashara)
 * Movable: Start from Aries
 * Fixed: Start from Leo
 * Dual: Start from Sagittarius
 */
export const calculateD45_Akshavedamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 45);
  
  let startSign = 0;
  if (FIXED_SIGNS.includes(rasi)) {
    startSign = 4; // Leo
  } else if (DUAL_SIGNS.includes(rasi)) {
    startSign = 8; // Sagittarius
  }
  
  return (startSign + part) % 12;
};

/**
 * D-60 Shashtiamsa (Parashara)
 * Ignore Shashtiamsa deities for now, just the sign.
 * Count from Sign itself?
 * Parashara: "To calculate Shashtiamsa... ignore sign, just (Part Index + Sign Index)?"
 * Standard Calculation:
 * (Sign Index * 60 + Part Index) % 12 ? No, that's cyclic.
 * 
 * JHora logic for D-60:
 * "The lord of the 60th part is determined by counting from the sign itself."
 * So: (Sign + Part) % 12.
 */
export const calculateD60_Shashtiamsa_Parashara = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 60);
  return (rasi + part) % 12;
};

// ============================================================================
// D-5, D-6, D-8, D-11 Parashara Methods
// ============================================================================

/**
 * D-5 Panchamsa (Parashara) — Lookup-based
 * Odd signs: [Aries, Aquarius, Sagittarius, Gemini, Libra]
 * Even signs: [Taurus, Virgo, Pisces, Capricorn, Scorpio]
 */
const PANCHAMSA_ODD = [0, 10, 8, 2, 6];
const PANCHAMSA_EVEN = [1, 5, 11, 9, 7];

export const calculateD5_Panchamsa_Parashara = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / 6.0); // 30/5 = 6
  return ODD_SIGNS.includes(sign) ? PANCHAMSA_ODD[l]! : PANCHAMSA_EVEN[l]! % 12;
};

/**
 * D-6 Shashthamsa (Parashara)
 * Odd signs: count from 0; Even signs: count from 6
 */
export const calculateD6_Shashthamsa_Parashara = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / 5.0); // 30/6 = 5
  return EVEN_SIGNS.includes(sign) ? (l + 6) % 12 : l % 12;
};

/**
 * D-8 Ashtamsa (Parashara)
 * Movable: count from 0; Dual: +4; Fixed: +8
 */
export const calculateD8_Ashtamsa_Parashara = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / 3.75); // 30/8 = 3.75
  if (DUAL_SIGNS.includes(sign)) return (l + 4) % 12;
  if (FIXED_SIGNS.includes(sign)) return (l + 8) % 12;
  return l % 12; // Movable
};

/**
 * D-11 Rudramsa (Parashara / Sanjay Rath)
 * r = (12 - sign + l) % 12
 */
export const calculateD11_Rudramsa_Parashara = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 11));
  return ((12 - sign + l) % 12 + 12) % 12;
};

/**
 * D-11 Rudramsa (BV Raman / Anti-zodiacal)
 * r = (11 - parasharaResult) % 12
 */
export const calculateD11_Rudramsa_BVRaman = (longitude: number): number => {
  const r = calculateD11_Rudramsa_Parashara(longitude);
  return ((11 - r) % 12 + 12) % 12;
};

// ============================================================================
// GENERIC PARIVRITTI METHODS
// ============================================================================

/**
 * Generate parivritti even-reverse lookup table.
 * Python: utils.parivritti_even_reverse(dcf, dirn=1)
 * For odd-indexed signs, part order is forward (0..dcf-1).
 * For even-indexed signs, part order is reversed (dcf-1..0).
 * Returns array of 12 arrays, each of length dcf: sign -> part -> varga_rasi
 */
export const generateParivrittiEvenReverse = (dcf: number, dirn: number = 1): number[][] => {
  const tuples: [number, number, number][] = [];
  let hs = 0;
  for (let r = 0; r < 12; r += 2) {
    // Odd sign (r): parts go forward
    for (let h = 0; h < dcf; h++) {
      tuples.push([r, h, hs]);
      hs = ((hs + dirn) % 12 + 12) % 12;
    }
    // Even sign (r+1): parts go backward
    for (let h = dcf - 1; h >= 0; h--) {
      tuples.push([r + 1, h, hs]);
      hs = ((hs + dirn) % 12 + 12) % 12;
    }
  }
  // Build lookup: result[rasi][part] = varga_sign
  const result: number[][] = Array.from({ length: 12 }, () => Array(dcf).fill(0));
  for (const [r, h, s] of tuples) {
    result[r][h] = s;
  }
  return result;
};

/**
 * Generate parivritti alternate (Somanatha) lookup table.
 * Python: utils.parivritti_alternate(dcf, dirn=1)
 * Odd rasis get increasing rasis from Aries. Even rasis get decreasing from Pisces.
 * Returns array of 12 tuples (arrays), each of length dcf.
 */
export const generateParivrittiAlternate = (dcf: number, dirn: number = 1): number[][] => {
  const pc: number[][] = [];
  let hs1 = 0;
  let hs2 = 11;
  for (let i = 0; i < 12; i += 2) {
    const t1: number[] = [];
    const t2: number[] = [];
    for (let j = 0; j < dcf; j++) {
      t1.push(((hs1 % 12) + 12) % 12);
      hs1 = ((hs1 + dirn) % 12 + 12) % 12;
      t2.push(((hs2 % 12) + 12) % 12);
      hs2 = ((hs2 - dirn) % 12 + 12) % 12;
    }
    pc.push(t1);
    pc.push(t2);
  }
  return pc;
};

/**
 * Parivritti Even Reverse varga sign calculation.
 * Python: __parivritti_even_reverse(planet_positions_in_rasi, dvf)
 */
export const calculateParivrittiEvenReverse = (longitude: number, dvf: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, dvf);
  const table = generateParivrittiEvenReverse(dvf);
  return table[rasi][part];
};

/**
 * Parivritti Alternate (Somanatha) varga sign calculation.
 * Python: __parivritti_alternate(planet_positions_in_rasi, dvf)
 */
export const calculateParivrittiAlternate = (longitude: number, dvf: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, dvf);
  const table = generateParivrittiAlternate(dvf);
  return table[rasi][part];
};

// ============================================================================
// CHART METHOD VARIANT FUNCTIONS
// ============================================================================

// --- D-2 Hora Variants ---

/**
 * D-2 Hora - Traditional Parasara (Only Leo & Cancer)
 * Python: _hora_traditional_parasara_chart (chart_method=2, default)
 * Sun's Hora = Leo(4), Moon's Hora = Cancer(3)
 */
export const calculateD2_Hora_Traditional = calculateD2_Hora_Parashara;

/**
 * D-2 Hora - Parivritti with Even Sign Reversal (Uma Shambu)
 * Python: hora_chart chart_method=1
 */
export const calculateD2_Hora_ParivrittiEvenReverse = (longitude: number): number => {
  return calculateParivrittiEvenReverse(longitude, 2);
};

/**
 * D-2 Hora - Raman Method
 * Python: _hora_chart_raman_method (chart_method=3)
 */
export const calculateD2_Hora_Raman = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 2);
  return HORA_LIST_RAMAN[rasi][part];
};

/**
 * D-2 Hora - Parivritti Dwaya (Bicyclical)
 * Python: hora_chart chart_method=4
 */
export const calculateD2_Hora_ParivrittiCyclic = (longitude: number): number => {
  return calculateCyclicVarga(longitude, 2);
};

/**
 * D-2 Hora - Somanatha (Parivritti Alternate)
 * Python: hora_chart chart_method=6
 */
export const calculateD2_Hora_Somanatha = (longitude: number): number => {
  return calculateParivrittiAlternate(longitude, 2);
};

// --- D-3 Drekkana Variants ---

/**
 * D-3 Drekkana - Parivritti Traya (Cyclic)
 * Python: drekkana_chart chart_method=2
 */
export const calculateD3_Drekkana_ParivrittiCyclic = (longitude: number): number => {
  return calculateCyclicVarga(longitude, 3);
};

/**
 * D-3 Drekkana - Somanatha (Parivritti Alternate)
 * Python: drekkana_chart chart_method=3
 */
export const calculateD3_Drekkana_Somanatha = (longitude: number): number => {
  return calculateParivrittiAlternate(longitude, 3);
};

/**
 * D-3 Drekkana - Jagannatha
 * Python: _drekkana_chart_jagannatha (chart_method=4)
 */
export const calculateD3_Drekkana_Jagannatha = (longitude: number): number => {
  const rasi = rasiFromLongitude(longitude);
  const part = getVargaPart(longitude, 3);
  return DREKKANA_JAGANNATHA[rasi][part];
};

/**
 * D-3 Drekkana - Parivritti Even Reverse
 * Python: drekkana_chart chart_method=5
 */
export const calculateD3_Drekkana_ParivrittiEvenReverse = (longitude: number): number => {
  return calculateParivrittiEvenReverse(longitude, 3);
};

// --- D-9 Navamsa Variants ---

/**
 * D-9 Navamsa - Parivritti Cyclic (UKM - Uniform Krishna Method)
 * Python: navamsa_chart chart_method=2
 */
export const calculateD9_Navamsa_ParivrittiCyclic = (longitude: number): number => {
  return calculateCyclicVarga(longitude, 9);
};

/**
 * D-9 Navamsa - Kalachakra
 * Python: navamsa_chart chart_method=3
 * Uses KALACHAKRA_NAVAMSA lookup keyed by nakshatra pada (0-26).
 */
export const calculateD9_Navamsa_Kalachakra = (longitude: number): number => {
  const longInSign = longitudeInSign(longitude);
  const rasi = rasiFromLongitude(longitude);
  const partSpan = 30.0 / 9;
  const mod = longInSign % partSpan;
  const part = Math.round((longInSign - mod) / partSpan);
  // nakshatra pada index: each sign has 9 navamsa parts,
  // but kalachakra maps by 27 nakshatra padas (each 3°20')
  // pada = (rasi * 9 + part) maps 0..107, but kalachakra uses 0..26 cyclically
  // Python logic: nakshatra_pada = rasi * 9 + hora
  // kalachakra_navamsa has keys 0-26, so we need (rasi*9 + part) which gives 0-107
  // Then the sub-index within the 4-element array uses part % 4
  // Actually, looking at Python: navamsa_chart chart_method=3 uses:
  //   hora = int(long // f1)  -> part index 0-8
  //   kn = const.kalachakra_navamsa
  //   nakshatra pada logic...
  // Let me re-read Python. The Kalachakra maps 27 nakshatras * 4 padas each.
  // For navamsa: 12 signs * 9 parts = 108 = 27 * 4
  // pada_index = rasi * 9 + part -> 0..107
  // nakshatra = pada_index // 4 -> 0..26
  // sub_pada = pada_index % 4 -> 0..3
  const padaIndex = rasi * 9 + part;
  const nakshatra = Math.floor(padaIndex / 4);
  const subPada = padaIndex % 4;
  return KALACHAKRA_NAVAMSA[nakshatra][subPada];
};

/**
 * D-9 Navamsa - Parivritti Even Reverse
 * Python: navamsa_chart chart_method=5
 */
export const calculateD9_Navamsa_ParivrittiEvenReverse = (longitude: number): number => {
  return calculateParivrittiEvenReverse(longitude, 9);
};

/**
 * D-9 Navamsa - Somanatha (Parivritti Alternate)
 * Python: navamsa_chart chart_method=6
 */
export const calculateD9_Navamsa_Somanatha = (longitude: number): number => {
  return calculateParivrittiAlternate(longitude, 9);
};

// --- Generic variants for remaining charts ---

/**
 * D-4 Chaturthamsa - Parivritti Cyclic
 */
export const calculateD4_ParivrittiCyclic = (longitude: number): number =>
  calculateCyclicVarga(longitude, 4);

/**
 * D-4 Chaturthamsa - Parivritti Even Reverse
 */
export const calculateD4_ParivrittiEvenReverse = (longitude: number): number =>
  calculateParivrittiEvenReverse(longitude, 4);

/**
 * D-4 Chaturthamsa - Somanatha
 */
export const calculateD4_Somanatha = (longitude: number): number =>
  calculateParivrittiAlternate(longitude, 4);

/**
 * D-7 Saptamsa - Parivritti Cyclic
 */
export const calculateD7_ParivrittiCyclic = (longitude: number): number =>
  calculateCyclicVarga(longitude, 7);

/**
 * D-7 Saptamsa - Parivritti Even Reverse
 */
export const calculateD7_ParivrittiEvenReverse = (longitude: number): number =>
  calculateParivrittiEvenReverse(longitude, 7);

/**
 * D-7 Saptamsa - Somanatha
 */
export const calculateD7_Somanatha = (longitude: number): number =>
  calculateParivrittiAlternate(longitude, 7);

/**
 * D-10 Dasamsa - Parivritti Cyclic
 */
export const calculateD10_ParivrittiCyclic = (longitude: number): number =>
  calculateCyclicVarga(longitude, 10);

/**
 * D-10 Dasamsa - Parivritti Even Reverse
 */
export const calculateD10_ParivrittiEvenReverse = (longitude: number): number =>
  calculateParivrittiEvenReverse(longitude, 10);

/**
 * D-10 Dasamsa - Somanatha
 */
export const calculateD10_Somanatha = (longitude: number): number =>
  calculateParivrittiAlternate(longitude, 10);

/**
 * D-12 Dwadasamsa - Parivritti Even Reverse
 */
export const calculateD12_ParivrittiEvenReverse = (longitude: number): number =>
  calculateParivrittiEvenReverse(longitude, 12);

/**
 * D-12 Dwadasamsa - Somanatha
 */
export const calculateD12_Somanatha = (longitude: number): number =>
  calculateParivrittiAlternate(longitude, 12);

// ============================================================================
// Parashara Direction Variants (even-sign backward/reverse counting)
// ============================================================================

/**
 * D-7 Saptamsa - Parashara Even Backward (chart_method=2)
 * Even signs: start from 7th and go backward
 */
export const calculateD7_Saptamsa_ParasharaEvenBackward = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 7));
  if (EVEN_SIGNS.includes(sign)) {
    return ((sign - (l + 6)) % 12 + 12) % 12;
  }
  return (sign + l) % 12;
};

/**
 * D-7 Saptamsa - Parashara Even Reverse End 7th (chart_method=3)
 * Even signs: backward then shift by -6
 */
export const calculateD7_Saptamsa_ParasharaReverseEnd7th = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 7));
  if (EVEN_SIGNS.includes(sign)) {
    const r = ((sign - (l + 6)) % 12 + 12) % 12;
    return ((r - 6) % 12 + 12) % 12;
  }
  return (sign + l) % 12;
};

/**
 * D-10 Dasamsa - Parashara Even Backward (chart_method=2)
 * Even signs: backward from 9th then shift by -8
 */
export const calculateD10_Dasamsa_ParasharaEvenBackward = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 10));
  if (EVEN_SIGNS.includes(sign)) {
    const r = ((sign - (l + 8)) % 12 + 12) % 12;
    return ((r - 8) % 12 + 12) % 12;
  }
  return (sign + l) % 12;
};

/**
 * D-10 Dasamsa - Parashara Even Reverse (chart_method=3)
 * Even signs: backward from 9th, no further shift
 */
export const calculateD10_Dasamsa_ParasharaEvenReverse = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 10));
  if (EVEN_SIGNS.includes(sign)) {
    return ((sign - (l + 8)) % 12 + 12) % 12;
  }
  return (sign + l) % 12;
};

/**
 * D-12 Dwadasamsa - Parashara Even Reversal (chart_method=2)
 * Even signs count backward
 */
export const calculateD12_Dwadasamsa_ParasharaEvenReverse = (longitude: number): number => {
  const sign = rasiFromLongitude(longitude);
  const longInSign = longitudeInSign(longitude);
  const l = Math.floor(longInSign / (30.0 / 12));
  const dirn = EVEN_SIGNS.includes(sign) ? -1 : 1;
  return ((sign + dirn * l) % 12 + 12) % 12;
};

