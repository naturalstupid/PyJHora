/**
 * Swiss Ephemeris adapter interface
 * This provides a TypeScript interface to the Swiss Ephemeris WASM module (swisseph-wasm)
 *
 * Fully integrated with swisseph-wasm for accurate astronomical calculations
 */

import SwissEph from 'swisseph-wasm';
import { AYANAMSA_MODES, DEFAULT_AYANAMSA_MODE } from '../constants';
import type { Place } from '../types';
import { normalizeDegrees } from '../utils/angle';
import { gregorianToJulianDay, julianDayToGregorian, toUtc } from '../utils/julian';

// ============================================================================
// SWISS EPHEMERIS FLAGS (matching pyswisseph)
// ============================================================================

export const SWE_FLAGS = {
  FLG_SWIEPH: 2,
  FLG_MOSEPH: 4,        // Moshier ephemeris (used in WASM)
  FLG_SIDEREAL: 65536,  // 0x10000 - sidereal coordinate system
  FLG_TRUEPOS: 16,
  FLG_SPEED: 256,
  FLG_NONUT: 64,        // 0x40 - no nutation
  BIT_HINDU_RISING: 896, // SE_BIT_DISC_CENTER(256) | SE_BIT_NO_REFRACTION(512) | SE_BIT_GEOCTR_NO_ECL_LAT(128)
  CALC_RISE: 1,
  CALC_SET: 2
} as const;

// Planet constants matching Swiss Ephemeris
export const SWE_PLANETS = {
  SUN: 0,
  MOON: 1,
  MERCURY: 2,
  VENUS: 3,
  MARS: 4,
  JUPITER: 5,
  SATURN: 6,
  URANUS: 7,
  NEPTUNE: 8,
  PLUTO: 9,
  MEAN_NODE: 10, // Rahu
  TRUE_NODE: 11
} as const;

// PyJHora planet indices to Swiss Ephemeris planet indices
// PyJHora: Sun=0, Moon=1, Mars=2, Mercury=3, Jupiter=4, Venus=5, Saturn=6, Rahu=7, Ketu=8
// SWE:     Sun=0, Moon=1, Mercury=2, Venus=3, Mars=4, Jupiter=5, Saturn=6, Uranus=7, Neptune=8, Pluto=9, MeanNode=10
const PYJHORA_TO_SWE: Record<number, number> = {
  0: 0,   // Sun -> Sun
  1: 1,   // Moon -> Moon
  2: 4,   // Mars -> Mars (SWE index 4)
  3: 2,   // Mercury -> Mercury (SWE index 2)
  4: 5,   // Jupiter -> Jupiter (SWE index 5)
  5: 3,   // Venus -> Venus (SWE index 3)
  6: 6,   // Saturn -> Saturn
  7: 10,  // Rahu -> Mean Node
  8: -1,  // Ketu (calculated as Rahu + 180)
  9: 7,   // Uranus
  10: 8,  // Neptune
  11: 9   // Pluto
};

// ============================================================================
// EPHEMERIS STATE
// ============================================================================

let _sweInstance: SwissEph | null = null;
let _ayanamsaMode = DEFAULT_AYANAMSA_MODE;
let _ayanamsaValue: number | null = null;
let _isInitialized = false;

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the Swiss Ephemeris WASM module
 * Must be called before any calculations
 */
export async function initializeEphemeris(): Promise<void> {
  if (_isInitialized && _sweInstance) {
    return;
  }

  try {
    _sweInstance = new SwissEph();
    await _sweInstance.initSwissEph();
    _isInitialized = true;
  } catch (error) {
    console.error('Failed to initialize Swiss Ephemeris:', error);
    throw error;
  }
}

/**
 * Get the SwissEph instance (initializes if needed)
 */
async function getSweInstance(): Promise<SwissEph> {
  if (!_sweInstance || !_isInitialized) {
    await initializeEphemeris();
  }
  return _sweInstance!;
}

/**
 * Check if ephemeris is initialized
 */
export function isInitialized(): boolean {
  return _isInitialized;
}

// ============================================================================
// AYANAMSA FUNCTIONS
// ============================================================================

/**
 * Set the ayanamsa mode
 * @param mode - Ayanamsa mode name (LAHIRI, RAMAN, KP, etc.)
 * @param value - Custom value for SIDM_USER mode
 * @param jd - Julian day for time-dependent modes
 */
export function setAyanamsaMode(
  mode: string = DEFAULT_AYANAMSA_MODE,
  value?: number,
  jd?: number
): void {
  const key = mode.toUpperCase();

  if (key === 'SIDM_USER' && value !== undefined) {
    _ayanamsaValue = value;
  } else if (key === 'SENTHIL' && jd !== undefined) {
    _ayanamsaValue = calculateAyanamsaSenthil(jd);
  } else if (key === 'SUNDAR_SS' && jd !== undefined) {
    _ayanamsaValue = calculateAyanamsaSuryaSiddhanta(jd);
  } else if (key in AYANAMSA_MODES) {
    _ayanamsaValue = null; // Use SWE built-in
  }

  _ayanamsaMode = key;
}

/**
 * Get the current ayanamsa value for a given Julian Day
 * @param jd - Julian Day Number (UTC)
 * @returns Ayanamsa value in degrees
 */
export async function getAyanamsaValueAsync(jd: number): Promise<number> {
  const key = _ayanamsaMode.toLowerCase();

  // Custom ayanamsa modes
  if (key === 'sidm_user' || key === 'senthil' || key === 'sundar_ss') {
    return _ayanamsaValue ?? 0;
  }

  // Use Swiss Ephemeris for standard modes
  const swe = await getSweInstance();
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1; // Default to Lahiri
  swe.set_sid_mode(modeId, 0, 0);
  return swe.get_ayanamsa(jd);
}

/**
 * Synchronous version - uses cached/approximate value
 * For backwards compatibility
 */
export function getAyanamsaValue(jd: number): number {
  const key = _ayanamsaMode.toLowerCase();

  if (key === 'sidm_user' || key === 'senthil' || key === 'sundar_ss') {
    return _ayanamsaValue ?? 0;
  }

  // Approximate Lahiri calculation for sync calls
  return calculateLahiriAyanamsa(jd);
}

/**
 * Calculate Lahiri ayanamsa (approximate for sync calls)
 */
function calculateLahiriAyanamsa(jd: number): number {
  const J2000 = 2451545.0;
  const ayanamsaAtJ2000 = 23.85;
  const precessionRate = 50.2388475 / 3600;
  const yearsSinceJ2000 = (jd - J2000) / 365.25;
  return ayanamsaAtJ2000 + precessionRate * yearsSinceJ2000;
}

/**
 * Calculate Senthil ayanamsa
 */
function calculateAyanamsaSenthil(jd: number): number {
  const referenceJd = 2451545.0;
  const siderealYear = 365.242198781;
  const p0 = 50.27972324;
  const m = 0.0002225;
  const a0 = 85591.25323;
  const q = m / 2;
  const diffDays = jd - referenceJd;
  const t = diffDays / siderealYear;
  const ayanamsa = a0 + p0 * t + q * t * t;
  return ayanamsa / 3600;
}

/**
 * Calculate Surya Siddhanta ayanamsa
 */
function calculateAyanamsaSuryaSiddhanta(jd: number): number {
  const cycleOfEquinoxes = 7200;
  const ayanamsaPeakDegrees = 27.0;
  const kaliYugaJd = 588465.5;
  const ssSiderealYear = 365.256363;
  const diffDays = jd - kaliYugaJd;
  const siderealDiffDays = diffDays / ssSiderealYear;
  const ayanamsaCycleFraction = siderealDiffDays / cycleOfEquinoxes;
  const ayanamsa = Math.sin(ayanamsaCycleFraction * 2.0 * Math.PI) * ayanamsaPeakDegrees;
  return ayanamsa;
}

// ============================================================================
// PLANET POSITION CALCULATIONS
// ============================================================================

/**
 * Calculate sidereal longitude of a planet (async - uses WASM)
 * @param jdUtc - Julian Day Number (UTC)
 * @param planet - Planet index (PyJHora convention: 0=Sun, 1=Moon, 2=Mars, etc.)
 * @returns Sidereal longitude in degrees (0-360)
 */
export async function siderealLongitudeAsync(jdUtc: number, planet: number): Promise<number> {
  const swe = await getSweInstance();

  // Set ayanamsa mode
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  // Handle Ketu specially
  if (planet === 8) {
    const rahuLong = await siderealLongitudeAsync(jdUtc, 7);
    return normalizeDegrees(rahuLong + 180);
  }

  // Map PyJHora planet index to SWE index
  const sweIndex = PYJHORA_TO_SWE[planet];
  if (sweIndex === undefined || sweIndex === -1) {
    throw new Error(`Unknown planet index: ${planet}`);
  }

  // Call swe_calc_ut via direct ccall to avoid the buggy JS wrapper.
  // The wrapper intermittently returns zeroed data due to WASM buffer issues.
  // C signature: int swe_calc_ut(double tjd_ut, int ipl, int iflag, double *xx, char *serr)
  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED | SWE_FLAGS.FLG_TRUEPOS;
  const SweModule = (swe as any).SweModule;
  const xxPtr = SweModule._malloc(6 * Float64Array.BYTES_PER_ELEMENT);
  const serrPtr = SweModule._malloc(256);

  try {
    SweModule.ccall(
      'swe_calc_ut',
      'number',
      ['number', 'number', 'number', 'number', 'number'],
      [jdUtc, sweIndex, flags, xxPtr, serrPtr]
    );

    // Read result immediately and copy before any other WASM call
    const xx = new Float64Array(SweModule.HEAPF64.buffer, xxPtr, 6);
    const tropical = normalizeDegrees(xx[0]);
    const sidereal = normalizeDegrees(tropical - ayanamsa);
    return sidereal;
  } catch (err) {
    console.error(`Error calculating planet ${planet} (sweIndex=${sweIndex}):`, err);
    return 0;
  } finally {
    SweModule._free(xxPtr);
    SweModule._free(serrPtr);
  }
}

/**
 * Synchronous version - uses approximation for backwards compatibility
 */
export function siderealLongitude(jdUtc: number, planet: number): number {
  // For sync calls, use approximation
  const tropicalLong = calculateTropicalLongitudeApprox(jdUtc, planet);
  const ayanamsa = getAyanamsaValue(jdUtc);
  return normalizeDegrees(tropicalLong - ayanamsa);
}

/**
 * Approximate tropical longitude calculation (for sync calls)
 */
function calculateTropicalLongitudeApprox(jd: number, planet: number): number {
  const J2000 = 2451545.0;
  const daysSinceJ2000 = jd - J2000;

  // Mean daily motions (approximate)
  const meanDailyMotions: Record<number, number> = {
    0: 0.9856,   // Sun
    1: 13.1764,  // Moon
    2: 0.5240,   // Mars
    3: 1.3833,   // Mercury
    4: 0.0831,   // Jupiter
    5: 1.6021,   // Venus
    6: 0.0335,   // Saturn
    7: -0.0529,  // Rahu (retrograde)
    8: -0.0529   // Ketu
  };

  // Starting longitudes at J2000
  const startLongitudes: Record<number, number> = {
    0: 280.46,   // Sun
    1: 218.32,   // Moon
    2: 355.45,   // Mars
    3: 252.25,   // Mercury
    4: 34.40,    // Jupiter
    5: 181.98,   // Venus
    6: 50.08,    // Saturn
    7: 125.04,   // Rahu (approximate)
    8: 305.04    // Ketu
  };

  const motion = meanDailyMotions[planet] ?? 0;
  const start = startLongitudes[planet] ?? 0;

  return normalizeDegrees(start + motion * daysSinceJ2000);
}

/**
 * Get solar longitude (async)
 */
export async function solarLongitudeAsync(jdUtc: number): Promise<number> {
  return siderealLongitudeAsync(jdUtc, 0);
}

/**
 * Get solar longitude (sync - approximate)
 */
export function solarLongitude(jdUtc: number): number {
  return siderealLongitude(jdUtc, 0);
}

/**
 * Get lunar longitude (async)
 */
export async function lunarLongitudeAsync(jdUtc: number): Promise<number> {
  return siderealLongitudeAsync(jdUtc, 1);
}

/**
 * Get lunar longitude (sync - approximate)
 */
export function lunarLongitude(jdUtc: number): number {
  return siderealLongitude(jdUtc, 1);
}

/**
 * Calculate Ketu longitude from Rahu
 */
export function ketuFromRahu(rahuLongitude: number): number {
  return normalizeDegrees(rahuLongitude + 180);
}

// ============================================================================
// ASCENDANT CALCULATION
// ============================================================================

/**
 * Calculate the ascendant (Lagna) for a given time and place
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Sidereal longitude of ascendant in degrees
 */
export async function ascendantAsync(jd: number, place: Place): Promise<number> {
  const swe = await getSweInstance();

  // Set ayanamsa
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);

  // Convert to UTC
  const jdUtc = jd - place.timezone / 24;

  // The swisseph-wasm houses() and houses_ex() functions don't return cusps properly.
  // We need to call the underlying WASM module directly with swe_houses_ex
  // Using SEFLG_SIDEREAL flag (65536) to get sidereal ascendant directly
  const SweModule = (swe as any).SweModule;
  const cuspsPtr = SweModule._malloc(13 * Float64Array.BYTES_PER_ELEMENT);
  const ascmcPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);

  try {
    // Call swe_houses_ex with sidereal flag
    // C signature: int swe_houses_ex(double tjd_ut, int32 iflag, double geolat, double geolon, int hsys, double *cusps, double *ascmc)
    const retCode = SweModule.ccall(
      'swe_houses_ex',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'pointer', 'pointer'],
      [jdUtc, SWE_FLAGS.FLG_SIDEREAL, place.latitude, place.longitude, 'P'.charCodeAt(0), cuspsPtr, ascmcPtr]
    );

    // Read the ascmc array using Float64Array view
    const ascmcArray = new Float64Array(SweModule.HEAPF64.buffer, ascmcPtr, 10);
    const siderealAsc = ascmcArray[0];

    // Check if we got a valid result
    if (retCode < 0 || !isFinite(siderealAsc) || siderealAsc === 0) {
      // Fallback: calculate using tropical ascendant and ayanamsa
      const ayanamsa = swe.get_ayanamsa(jdUtc);
      const cuspsArray = new Float64Array(SweModule.HEAPF64.buffer, cuspsPtr, 13);
      const tropicalAsc = cuspsArray[1]; // cusps[1] is 1st house cusp
      const fallbackAsc = ((tropicalAsc - ayanamsa) % 360 + 360) % 360;
      return fallbackAsc;
    }

    return normalizeDegrees(siderealAsc);
  } finally {
    // Free allocated memory
    SweModule._free(cuspsPtr);
    SweModule._free(ascmcPtr);
  }
}

// ============================================================================
// ALL PLANET POSITIONS
// ============================================================================

/**
 * Get all planet positions (async - uses WASM)
 * @param jdUtc - Julian Day Number (UTC)
 * @returns Array of planet positions with rasi, longitude, and retrograde info
 */
export async function getAllPlanetPositionsAsync(jdUtc: number): Promise<Array<{
  planet: number;
  rasi: number;
  longitude: number;
  isRetrograde: boolean;
}>> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;

  // Set ayanamsa
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED | SWE_FLAGS.FLG_TRUEPOS;
  const positions: Array<{planet: number; rasi: number; longitude: number; isRetrograde: boolean}> = [];

  // Pre-allocate WASM buffers for calc_ut (reused across loop iterations)
  const xxPtr = SweModule._malloc(6 * Float64Array.BYTES_PER_ELEMENT);
  const serrPtr = SweModule._malloc(256);
  let rahuLong = 0;

  try {
    for (let p = 0; p <= 8; p++) {
      const sweIndex = PYJHORA_TO_SWE[p];
      let long: number;
      let speed = 0;

      if (sweIndex === -1) {
        // Ketu
        long = normalizeDegrees(rahuLong + 180);
      } else {
        try {
          SweModule.ccall(
            'swe_calc_ut',
            'number',
            ['number', 'number', 'number', 'number', 'number'],
            [jdUtc, sweIndex ?? 0, flags, xxPtr, serrPtr]
          );
          const xx = new Float64Array(SweModule.HEAPF64.buffer, xxPtr, 6);
          const tropical = normalizeDegrees(xx[0]);
          long = normalizeDegrees(tropical - ayanamsa);
          speed = xx[3];
          if (p === 7) rahuLong = long;
        } catch (err) {
          console.error(`Error calculating planet ${p}:`, err);
          long = 0;
        }
      }

      positions.push({
        planet: p,
        rasi: Math.floor(long / 30),
        longitude: long % 30,
        isRetrograde: p < 7 && speed < 0
      });
    }

    return positions;
  } finally {
    SweModule._free(xxPtr);
    SweModule._free(serrPtr);
  }
}

// ============================================================================
// RISE/SET CALCULATIONS
// ============================================================================

/**
 * Helper function to properly call swe_houses_ex with output arrays
 * The swisseph-wasm houses() function doesn't return cusps properly,
 * so we need to call the underlying WASM module directly.
 * Returns TROPICAL coordinates (for use with sunrise/sunset calculations)
 */
async function getHouseCusps(jdUtc: number, latitude: number, longitude: number): Promise<{
  cusps: number[];
  ascmc: number[];
}> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;
  const cuspsPtr = SweModule._malloc(13 * Float64Array.BYTES_PER_ELEMENT);
  const ascmcPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);

  try {
    // Call swe_houses_ex with iflag=0 for tropical coordinates
    // C signature: int swe_houses_ex(double tjd_ut, int32 iflag, double geolat, double geolon, int hsys, double *cusps, double *ascmc)
    SweModule.ccall(
      'swe_houses_ex',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'pointer', 'pointer'],
      [jdUtc, 0, latitude, longitude, 'P'.charCodeAt(0), cuspsPtr, ascmcPtr]
    );

    // Read cusps array using Float64Array view (13 elements, cusps[1-12] are houses)
    const cuspsView = new Float64Array(SweModule.HEAPF64.buffer, cuspsPtr, 13);
    const cusps: number[] = Array.from(cuspsView);

    // Read ascmc array using Float64Array view (10 elements: asc, mc, armc, vertex, etc.)
    const ascmcView = new Float64Array(SweModule.HEAPF64.buffer, ascmcPtr, 10);
    const ascmc: number[] = Array.from(ascmcView);

    return { cusps, ascmc };
  } finally {
    SweModule._free(cuspsPtr);
    SweModule._free(ascmcPtr);
  }
}

/**
 * Rise/set flags matching Python: BIT_HINDU_RISING | FLG_TRUEPOS | FLG_SPEED
 * Hindu rising: center of disc at geometric horizon, no refraction.
 * Python: _rise_flags = swe.BIT_HINDU_RISING | swe.FLG_TRUEPOS | swe.FLG_SPEED
 */
const RISE_FLAGS = SWE_FLAGS.BIT_HINDU_RISING | SWE_FLAGS.FLG_TRUEPOS | SWE_FLAGS.FLG_SPEED;

/**
 * Internal helper: call swe_rise_trans via direct WASM ccall.
 * The swisseph-wasm JS wrapper for rise_trans has incorrect parameter mapping,
 * so we call the C function directly with the correct 10-parameter signature:
 *
 * int swe_rise_trans(double tjd_ut, int32 ipl, char *starname, int32 epheflag,
 *                    int32 rsmi, double *geopos, double atpress, double attemp,
 *                    double *tret, char *serr)
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param planet - SWE planet index (0=Sun, 1=Moon)
 * @param riseOrSet - CALC_RISE (1) or CALC_SET (2)
 * @returns Object with localTime (float hours), timeString, and jd (local JD)
 */
async function riseTransHelper(
  jd: number,
  place: Place,
  planet: number,
  riseOrSet: number
): Promise<{ localTime: number; timeString: string; jd: number; jdUt: number }> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;

  // Extract date, create JD at midnight (0:00 UT) — matching Python's gregorian_to_jd(Date(y,m,d))
  const { date } = julianDayToGregorian(jd);
  const jdMidnight = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });
  const jdStart = jdMidnight - place.timezone / 24; // UT of midnight local time

  // Ephemeris flags (separate from rsmi in C API)
  const epheflag = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_TRUEPOS | SWE_FLAGS.FLG_SPEED;
  // Rise/set method flags
  const rsmi = RISE_FLAGS | riseOrSet;

  // Allocate geopos array (3 doubles: longitude, latitude, altitude)
  const geoposPtr = SweModule._malloc(3 * Float64Array.BYTES_PER_ELEMENT);
  const geopos = new Float64Array(SweModule.HEAPF64.buffer, geoposPtr, 3);
  geopos[0] = place.longitude;
  geopos[1] = place.latitude;
  geopos[2] = 0.0; // altitude

  // Allocate tret (1 double output)
  const tretPtr = SweModule._malloc(Float64Array.BYTES_PER_ELEMENT);

  try {
    const retFlag = SweModule.ccall(
      'swe_rise_trans',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number', 'number'],
      [jdStart, planet, 0 /* starname=NULL */, epheflag, rsmi, geoposPtr, 0.0 /* atpress */, 0.0 /* attemp */, tretPtr, 0 /* serr=NULL */]
    );

    if (retFlag < 0) {
      // Fallback to approximate calculation
      const approxHour = riseOrSet === SWE_FLAGS.CALC_RISE ? 6.0 : 18.0;
      const approxJd = gregorianToJulianDay(date, { hour: Math.floor(approxHour), minute: Math.round((approxHour % 1) * 60), second: 0 });
      return {
        localTime: approxHour,
        timeString: formatHoursToTime(approxHour),
        jd: approxJd,
        jdUt: approxJd - place.timezone / 24
      };
    }

    const tret = new Float64Array(SweModule.HEAPF64.buffer, tretPtr, 1);
    const eventJdUt = tret[0]; // UT JD of the event

    // Convert to local time: (event_jd_ut - jd_midnight_ut) * 24 + tz
    const localTime = (eventJdUt - jdMidnight) * 24 + place.timezone;

    // Recalculate JD from local time (matching Python's behavior for sunrise)
    const h = Math.floor(localTime);
    const remMin = (localTime - h) * 60;
    const m = Math.floor(remMin);
    const s = Math.floor((remMin - m) * 60);
    const eventJdLocal = gregorianToJulianDay(date, { hour: h, minute: m, second: s });

    return {
      localTime,
      timeString: formatHoursToTime(localTime),
      jd: eventJdLocal,
      jdUt: eventJdUt
    };
  } finally {
    SweModule._free(geoposPtr);
    SweModule._free(tretPtr);
  }
}

/**
 * Calculate sunrise time using swe_rise_trans (async - uses WASM)
 * Uses Hindu rising: center of sun's disc at geometric horizon, no refraction.
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Object with local time (float hours), formatted time string, and JD
 */
export async function sunriseAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number;
  jdUt: number;
}> {
  return riseTransHelper(jd, place, SWE_PLANETS.SUN, SWE_FLAGS.CALC_RISE);
}

/**
 * Calculate sunset time using swe_rise_trans (async - uses WASM)
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Object with local time (float hours), formatted time string, and JD
 */
export async function sunsetAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number;
  jdUt: number;
}> {
  return riseTransHelper(jd, place, SWE_PLANETS.SUN, SWE_FLAGS.CALC_SET);
}

/**
 * Synchronous sunrise (approximate)
 */
export function sunrise(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  // Approximate based on latitude and time of year
  const jdMidnight = Math.floor(jd);
  const dayOfYear = (jd - 2451545) % 365.25; // Days since J2000

  // Basic approximation with seasonal variation
  const latEffect = (place.latitude / 90) * 2; // Up to 2 hours effect
  const seasonalEffect = Math.sin((dayOfYear - 80) * 2 * Math.PI / 365.25) * 1.5;
  const localTime = 6.0 + latEffect * seasonalEffect;

  return {
    localTime,
    timeString: formatHoursToTime(localTime),
    jd: jdMidnight + (localTime - 12) / 24
  };
}

/**
 * Synchronous sunset (approximate)
 */
export function sunset(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  const jdMidnight = Math.floor(jd);
  const dayOfYear = (jd - 2451545) % 365.25;

  const latEffect = (place.latitude / 90) * 2;
  const seasonalEffect = Math.sin((dayOfYear - 80) * 2 * Math.PI / 365.25) * 1.5;
  const localTime = 18.0 - latEffect * seasonalEffect;

  return {
    localTime,
    timeString: formatHoursToTime(localTime),
    jd: jdMidnight + (localTime - 12) / 24
  };
}

/**
 * Calculate moonrise time using swe_rise_trans (async - uses WASM)
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Object with local time (float hours), formatted time string, and JD
 */
export async function moonriseAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number;
  jdUt: number;
}> {
  return riseTransHelper(jd, place, SWE_PLANETS.MOON, SWE_FLAGS.CALC_RISE);
}

/**
 * Calculate moonset time using swe_rise_trans (async - uses WASM)
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Object with local time (float hours), formatted time string, and JD
 */
export async function moonsetAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number;
  jdUt: number;
}> {
  return riseTransHelper(jd, place, SWE_PLANETS.MOON, SWE_FLAGS.CALC_SET);
}

/**
 * Synchronous moonrise (approximate)
 */
export function moonrise(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  const approximateHour = 8.0;
  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
}

/**
 * Synchronous moonset (approximate)
 */
export function moonset(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  const approximateHour = 20.0;
  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
}

// ============================================================================
// PLANET SPEED AND RETROGRADE
// ============================================================================

/**
 * Get planet speed info (async)
 */
export async function planetSpeedInfoAsync(jd: number, place: Place, planet: number): Promise<{
  longitude: number;
  latitude: number;
  distance: number;
  longitudeSpeed: number;
  latitudeSpeed: number;
  distanceSpeed: number;
}> {
  const swe = await getSweInstance();
  const jdUtc = toUtc(jd, place.timezone);

  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  const sweIndex = PYJHORA_TO_SWE[planet];
  if (sweIndex === undefined || sweIndex === -1) {
    // Ketu
    const rahuInfo = await planetSpeedInfoAsync(jd, place, 7);
    return {
      longitude: normalizeDegrees(rahuInfo.longitude + 180),
      latitude: -rahuInfo.latitude,
      distance: rahuInfo.distance,
      longitudeSpeed: rahuInfo.longitudeSpeed,
      latitudeSpeed: -rahuInfo.latitudeSpeed,
      distanceSpeed: rahuInfo.distanceSpeed
    };
  }

  // Use direct ccall to avoid buggy JS wrapper buffer issues
  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED | SWE_FLAGS.FLG_TRUEPOS;
  const SweModule = (swe as any).SweModule;
  const xxPtr = SweModule._malloc(6 * Float64Array.BYTES_PER_ELEMENT);
  const serrPtr = SweModule._malloc(256);

  try {
    SweModule.ccall(
      'swe_calc_ut',
      'number',
      ['number', 'number', 'number', 'number', 'number'],
      [jdUtc, sweIndex, flags, xxPtr, serrPtr]
    );

    const xx = new Float64Array(SweModule.HEAPF64.buffer, xxPtr, 6);
    return {
      longitude: normalizeDegrees(xx[0] - ayanamsa),
      latitude: xx[1],
      distance: xx[2],
      longitudeSpeed: xx[3],
      latitudeSpeed: xx[4],
      distanceSpeed: xx[5]
    };
  } catch (err) {
    console.error(`Error calculating planet speed ${planet}:`, err);
    return {
      longitude: 0, latitude: 0, distance: 1,
      longitudeSpeed: 0, latitudeSpeed: 0, distanceSpeed: 0
    };
  } finally {
    SweModule._free(xxPtr);
    SweModule._free(serrPtr);
  }
}

/**
 * Synchronous planet speed info (approximate)
 */
export function planetSpeedInfo(jd: number, place: Place, planet: number): {
  longitude: number;
  latitude: number;
  distance: number;
  longitudeSpeed: number;
  latitudeSpeed: number;
  distanceSpeed: number;
} {
  const jdUtc = toUtc(jd, place.timezone);
  const longitude = siderealLongitude(jdUtc, planet);

  const dailyMotions: Record<number, number> = {
    0: 0.9856,   // Sun
    1: 13.1764,  // Moon
    2: 0.5240,   // Mars
    3: 1.3833,   // Mercury
    4: 0.0831,   // Jupiter
    5: 1.6021,   // Venus
    6: 0.0335,   // Saturn
    7: -0.0529,  // Rahu
    8: -0.0529   // Ketu
  };

  return {
    longitude,
    latitude: 0,
    distance: 1,
    longitudeSpeed: dailyMotions[planet] ?? 0,
    latitudeSpeed: 0,
    distanceSpeed: 0
  };
}

/**
 * Check if planets are in retrograde (async)
 */
export async function planetsInRetrogradeAsync(jd: number, place: Place): Promise<number[]> {
  const positions = await getAllPlanetPositionsAsync(toUtc(jd, place.timezone));
  return positions.filter(p => p.isRetrograde).map(p => p.planet);
}

/**
 * Check if planets are in retrograde (sync - returns empty for now)
 */
export function planetsInRetrograde(jd: number, place: Place): number[] {
  // Would need async call to properly determine
  // Return empty for backwards compatibility
  return [];
}

// ============================================================================
// ECLIPSE FUNCTIONS
// ============================================================================

/**
 * Eclipse result structure matching Python's return format.
 */
export interface EclipseResult {
  retflag: number;
  tret: number[];   // timing array (JDs in UT): [greatest, first_contact, second, third, fourth, ...]
  attr: number[];   // attribute array: [fraction_covered, diameter_ratio, obscuration, ...]
}

/**
 * Check if a solar eclipse occurs at the given JD for the given location.
 * Uses swe_sol_eclipse_how.
 *
 * Python: swe.sol_eclipse_how(jd_utc, geopos=(lon,lat,0), flags=flags)
 *
 * @param jdUtc - Julian Day in UT
 * @param place - Place
 * @returns attr array (8 doubles) with eclipse properties, or null if no eclipse
 */
export async function solarEclipseHowAsync(jdUtc: number, place: Place): Promise<{ retflag: number; attr: number[] } | null> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;

  const flags = SWE_FLAGS.FLG_MOSEPH;
  const geoposPtr = SweModule._malloc(3 * Float64Array.BYTES_PER_ELEMENT);
  const attrPtr = SweModule._malloc(20 * Float64Array.BYTES_PER_ELEMENT);

  try {
    const geo = new Float64Array(SweModule.HEAPF64.buffer, geoposPtr, 3);
    geo[0] = place.longitude;
    geo[1] = place.latitude;
    geo[2] = 0.0;

    const retflag = SweModule.ccall(
      'swe_sol_eclipse_how',
      'number',
      ['number', 'number', 'pointer', 'pointer', 'number'],
      [jdUtc, flags, geoposPtr, attrPtr, 0 /* serr=NULL */]
    );

    const attrView = new Float64Array(SweModule.HEAPF64.buffer, attrPtr, 20);
    const attr: number[] = Array.from(attrView);
    return { retflag, attr };
  } finally {
    SweModule._free(geoposPtr);
    SweModule._free(attrPtr);
  }
}

/**
 * Find the next solar eclipse visible at the given location.
 * Uses swe_sol_eclipse_when_loc.
 *
 * Python: swe.sol_eclipse_when_loc(jd, geopos)
 *
 * @param jdUtc - Julian Day in UT to search from
 * @param place - Place
 * @param backward - 0 = forward, 1 = backward
 * @returns EclipseResult with retflag, tret (10 doubles), attr (20 doubles)
 */
export async function nextSolarEclipseLocAsync(jdUtc: number, place: Place, backward: number = 0): Promise<EclipseResult> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;

  const flags = SWE_FLAGS.FLG_MOSEPH;
  const geoposPtr = SweModule._malloc(3 * Float64Array.BYTES_PER_ELEMENT);
  const tretPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);
  const attrPtr = SweModule._malloc(20 * Float64Array.BYTES_PER_ELEMENT);

  try {
    const geo = new Float64Array(SweModule.HEAPF64.buffer, geoposPtr, 3);
    geo[0] = place.longitude;
    geo[1] = place.latitude;
    geo[2] = 0.0;

    const retflag = SweModule.ccall(
      'swe_sol_eclipse_when_loc',
      'number',
      ['number', 'number', 'pointer', 'pointer', 'pointer', 'number', 'number'],
      [jdUtc, flags, geoposPtr, tretPtr, attrPtr, backward, 0 /* serr=NULL */]
    );

    const tretView = new Float64Array(SweModule.HEAPF64.buffer, tretPtr, 10);
    const attrView = new Float64Array(SweModule.HEAPF64.buffer, attrPtr, 20);
    return {
      retflag,
      tret: Array.from(tretView),
      attr: Array.from(attrView),
    };
  } finally {
    SweModule._free(geoposPtr);
    SweModule._free(tretPtr);
    SweModule._free(attrPtr);
  }
}

/**
 * Find the next lunar eclipse visible at the given location.
 * Uses swe_lun_eclipse_when_loc.
 *
 * Python: swe.lun_eclipse_when_loc(jd, geopos)
 *
 * @param jdUtc - Julian Day in UT to search from
 * @param place - Place
 * @param backward - 0 = forward, 1 = backward
 * @returns EclipseResult with retflag, tret (10 doubles), attr (20 doubles)
 */
export async function nextLunarEclipseLocAsync(jdUtc: number, place: Place, backward: number = 0): Promise<EclipseResult> {
  const swe = await getSweInstance();
  const SweModule = (swe as any).SweModule;

  const flags = SWE_FLAGS.FLG_MOSEPH;
  const geoposPtr = SweModule._malloc(3 * Float64Array.BYTES_PER_ELEMENT);
  const tretPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);
  const attrPtr = SweModule._malloc(20 * Float64Array.BYTES_PER_ELEMENT);

  try {
    const geo = new Float64Array(SweModule.HEAPF64.buffer, geoposPtr, 3);
    geo[0] = place.longitude;
    geo[1] = place.latitude;
    geo[2] = 0.0;

    const retflag = SweModule.ccall(
      'swe_lun_eclipse_when_loc',
      'number',
      ['number', 'number', 'pointer', 'pointer', 'pointer', 'number', 'number'],
      [jdUtc, flags, geoposPtr, tretPtr, attrPtr, backward, 0 /* serr=NULL */]
    );

    const tretView = new Float64Array(SweModule.HEAPF64.buffer, tretPtr, 10);
    const attrView = new Float64Array(SweModule.HEAPF64.buffer, attrPtr, 20);
    return {
      retflag,
      tret: Array.from(tretView),
      attr: Array.from(attrView),
    };
  } finally {
    SweModule._free(geoposPtr);
    SweModule._free(tretPtr);
    SweModule._free(attrPtr);
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

// ============================================================================
// HOUSE CUSP CALCULATIONS (Generalized)
// ============================================================================

/**
 * Calculate house cusps for any house system (async — uses WASM).
 * Wraps `swe_houses_ex` with the specified house system code and sidereal flag.
 *
 * Python: swe.houses_ex(jd_utc, lat, lon, hsys, flags=flags)[0]
 *
 * @param jd - Julian Day Number (local time; converted to UT internally)
 * @param place - Place data
 * @param houseCode - Single-character house system code ('P' Placidus, 'K' Koch, etc.)
 * @returns Array of 12 sidereal house cusp longitudes (cusps[1..12])
 */
export async function houseCuspsAsync(
  jd: number,
  place: Place,
  houseCode: string = 'P'
): Promise<number[]> {
  const swe = await getSweInstance();
  const jdUtc = jd - place.timezone / 24;

  // Set ayanamsa for sidereal mode
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);

  const flags = SWE_FLAGS.FLG_SIDEREAL;

  const SweModule = (swe as any).SweModule;
  const cuspsPtr = SweModule._malloc(13 * Float64Array.BYTES_PER_ELEMENT);
  const ascmcPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);

  try {
    SweModule.ccall(
      'swe_houses_ex',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'pointer', 'pointer'],
      [jdUtc, flags, place.latitude, place.longitude, houseCode.charCodeAt(0), cuspsPtr, ascmcPtr]
    );

    const cuspsView = new Float64Array(SweModule.HEAPF64.buffer, cuspsPtr, 13);
    // cusps[0] is unused by SWE; cusps[1..12] are the 12 house cusps
    const cusps: number[] = [];
    for (let i = 1; i <= 12; i++) {
      cusps.push(normalizeDegrees(cuspsView[i]!));
    }
    return cusps;
  } finally {
    SweModule._free(cuspsPtr);
    SweModule._free(ascmcPtr);
  }
}

/**
 * Full ascendant calculation (async — uses WASM).
 * Returns [constellation, longitude_in_sign, nakshatra_no, pada_no]
 * matching Python's ascendant(jd, place).
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns [constellation (0-11), longitude_in_sign, nak_no (1-27), pada_no (1-4)]
 */
export async function ascendantFullAsync(
  jd: number,
  place: Place
): Promise<[number, number, number, number]> {
  const swe = await getSweInstance();
  const jdUtc = jd - place.timezone / 24;

  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);

  const flags = SWE_FLAGS.FLG_SIDEREAL;

  const SweModule = (swe as any).SweModule;
  const cuspsPtr = SweModule._malloc(13 * Float64Array.BYTES_PER_ELEMENT);
  const ascmcPtr = SweModule._malloc(10 * Float64Array.BYTES_PER_ELEMENT);

  try {
    SweModule.ccall(
      'swe_houses_ex',
      'number',
      ['number', 'number', 'number', 'number', 'number', 'pointer', 'pointer'],
      [jdUtc, flags, place.latitude, place.longitude, 'P'.charCodeAt(0), cuspsPtr, ascmcPtr]
    );

    const ascmcView = new Float64Array(SweModule.HEAPF64.buffer, ascmcPtr, 10);
    const nirayanAsc = normalizeDegrees(ascmcView[0]!);

    const constellation = Math.floor(nirayanAsc / 30);
    const coordinates = nirayanAsc - constellation * 30;

    // Calculate nakshatra and pada
    const oneStar = 360 / 27;
    const onePada = 360 / 108;
    const quotient = Math.floor(nirayanAsc / oneStar);
    const remainder = nirayanAsc % oneStar;
    const nakNo = 1 + quotient;
    const padaNo = 1 + Math.floor(remainder / onePada);

    return [constellation, coordinates, nakNo, padaNo];
  } finally {
    SweModule._free(cuspsPtr);
    SweModule._free(ascmcPtr);
  }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Format hours as time string
 */
function formatHoursToTime(hours: number): string {
  const normalizedHours = ((hours % 24) + 24) % 24;
  const h = Math.floor(normalizedHours);
  const m = Math.floor((normalizedHours - h) * 60);
  const s = Math.floor(((normalizedHours - h) * 60 - m) * 60);
  const ampm = h < 12 ? 'AM' : 'PM';
  const h12 = h % 12 || 12;
  return `${h12.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')} ${ampm}`;
}
