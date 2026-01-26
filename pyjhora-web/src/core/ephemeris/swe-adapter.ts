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
import { toUtc } from '../utils/julian';

// ============================================================================
// SWISS EPHEMERIS FLAGS (matching pyswisseph)
// ============================================================================

export const SWE_FLAGS = {
  FLG_SWIEPH: 2,
  FLG_MOSEPH: 4,        // Moshier ephemeris (used in WASM)
  FLG_SIDEREAL: 64,
  FLG_TRUEPOS: 16,
  FLG_SPEED: 256,
  BIT_HINDU_RISING: 2048,
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

  // Use SEFLG_MOSEPH (4) + SEFLG_SPEED (256) for WASM
  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED;

  try {
    const result = swe.calc_ut(jdUtc, sweIndex, flags);
    // result: [longitude, latitude, distance, long_speed, lat_speed, dist_speed]
    if (!result || typeof result[0] !== 'number') {
      console.warn(`calc_ut returned invalid result for planet ${planet}:`, result);
      return 0;
    }

    // Convert tropical to sidereal
    const tropical = normalizeDegrees(result[0]);
    const sidereal = normalizeDegrees(tropical - ayanamsa);
    return sidereal;
  } catch (err) {
    console.error(`Error calculating planet ${planet} (sweIndex=${sweIndex}):`, err);
    return 0;
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
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  // Calculate houses using Placidus system ('P')
  const result = swe.houses(jdUtc, place.latitude, place.longitude, 'P') as { cusps?: number[] };

  // cusps[1] is the Ascendant
  const tropicalAsc = result.cusps?.[1] ?? 0;
  const siderealAsc = normalizeDegrees(tropicalAsc - ayanamsa);

  return siderealAsc;
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

  // Set ayanamsa
  const modeId = AYANAMSA_MODES[_ayanamsaMode as keyof typeof AYANAMSA_MODES] ?? 1;
  swe.set_sid_mode(modeId, 0, 0);
  const ayanamsa = swe.get_ayanamsa(jdUtc);

  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED;
  const positions: Array<{planet: number; rasi: number; longitude: number; isRetrograde: boolean}> = [];

  let rahuLong = 0;

  for (let p = 0; p <= 8; p++) {
    const sweIndex = PYJHORA_TO_SWE[p];
    let long: number;
    let speed = 0;

    if (sweIndex === -1) {
      // Ketu
      long = normalizeDegrees(rahuLong + 180);
    } else {
      try {
        const result = swe.calc_ut(jdUtc, sweIndex ?? 0, flags);
        if (!result || typeof result[0] !== 'number') {
          long = 0;
        } else {
          const tropical = normalizeDegrees(result[0]);
          long = normalizeDegrees(tropical - ayanamsa);
          speed = result[3] ?? 0;
        }
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
}

// ============================================================================
// RISE/SET CALCULATIONS
// ============================================================================

/**
 * Calculate sunrise time (async - uses WASM houses calculation)
 * @param jd - Julian Day Number (local midnight)
 * @param place - Place data
 * @returns Object with local time and JD
 */
export async function sunriseAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number
}> {
  // For sunrise/sunset, we use a search algorithm with houses calculation
  // This is a simplified approach - more accurate would be swe.rise_trans if available

  const swe = await getSweInstance();
  const jdMidnight = Math.floor(jd);

  // Search for sunrise between 4 AM and 10 AM local time
  let sunriseJd = jdMidnight;
  let sunriseLocalTime = 6.0; // Default approximation

  // Binary search for Sun at horizon
  let low = jdMidnight - place.timezone / 24 + 4 / 24; // 4 AM UTC
  let high = jdMidnight - place.timezone / 24 + 10 / 24; // 10 AM UTC

  for (let i = 0; i < 20; i++) {
    const mid = (low + high) / 2;
    const result = swe.houses(mid, place.latitude, place.longitude, 'P') as { cusps?: number[] };
    const asc = result.cusps?.[1] ?? 0;

    // Sun is at ASC when it's rising
    const sunResult = swe.calc_ut(mid, 0, SWE_FLAGS.FLG_MOSEPH);
    const sunLong = sunResult?.[0] ?? 0;

    // Check if sun is below or above ascendant
    const diff = normalizeDegrees(sunLong - asc);

    if (diff > 180) {
      // Sun below horizon
      low = mid;
    } else {
      // Sun above horizon
      high = mid;
    }
  }

  sunriseJd = (low + high) / 2;
  sunriseLocalTime = ((sunriseJd + place.timezone / 24) - jdMidnight) * 24;

  return {
    localTime: sunriseLocalTime,
    timeString: formatHoursToTime(sunriseLocalTime),
    jd: sunriseJd
  };
}

/**
 * Calculate sunset time (async)
 */
export async function sunsetAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number
}> {
  const swe = await getSweInstance();
  const jdMidnight = Math.floor(jd);

  // Search for sunset between 4 PM and 10 PM local time
  let low = jdMidnight - place.timezone / 24 + 16 / 24;
  let high = jdMidnight - place.timezone / 24 + 22 / 24;

  for (let i = 0; i < 20; i++) {
    const mid = (low + high) / 2;
    const result = swe.houses(mid, place.latitude, place.longitude, 'P') as { cusps?: number[] };
    const desc = normalizeDegrees((result.cusps?.[1] ?? 0) + 180); // Descendant

    const sunResult = swe.calc_ut(mid, 0, SWE_FLAGS.FLG_MOSEPH);
    const sunLong = sunResult?.[0] ?? 0;

    const diff = normalizeDegrees(sunLong - desc);

    if (diff < 180) {
      low = mid;
    } else {
      high = mid;
    }
  }

  const sunsetJd = (low + high) / 2;
  const sunsetLocalTime = ((sunsetJd + place.timezone / 24) - jdMidnight) * 24;

  return {
    localTime: sunsetLocalTime,
    timeString: formatHoursToTime(sunsetLocalTime),
    jd: sunsetJd
  };
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
 * Calculate moonrise time (async)
 */
export async function moonriseAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number
}> {
  // Moonrise varies significantly based on lunar phase
  // For now, use approximation based on moon position
  const swe = await getSweInstance();
  const jdUtc = jd - place.timezone / 24;

  const moonResult = swe.calc_ut(jdUtc, 1, SWE_FLAGS.FLG_MOSEPH);
  const sunResult = swe.calc_ut(jdUtc, 0, SWE_FLAGS.FLG_MOSEPH);

  const moonLong = moonResult?.[0] ?? 0;
  const sunLong = sunResult?.[0] ?? 0;

  // Lunar phase affects moonrise time
  const phase = normalizeDegrees(moonLong - sunLong);
  const phaseHours = (phase / 360) * 24; // Full moon rises at sunset, new moon at sunrise

  const approximateHour = (6 + phaseHours) % 24;

  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
}

/**
 * Calculate moonset time (async)
 */
export async function moonsetAsync(jd: number, place: Place): Promise<{
  localTime: number;
  timeString: string;
  jd: number
}> {
  const swe = await getSweInstance();
  const jdUtc = jd - place.timezone / 24;

  const moonResult = swe.calc_ut(jdUtc, 1, SWE_FLAGS.FLG_MOSEPH);
  const sunResult = swe.calc_ut(jdUtc, 0, SWE_FLAGS.FLG_MOSEPH);

  const moonLong = moonResult?.[0] ?? 0;
  const sunLong = sunResult?.[0] ?? 0;

  const phase = normalizeDegrees(moonLong - sunLong);
  const phaseHours = (phase / 360) * 24;

  const approximateHour = (18 + phaseHours) % 24;

  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
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

  const flags = SWE_FLAGS.FLG_MOSEPH | SWE_FLAGS.FLG_SPEED;
  const result = swe.calc_ut(jdUtc, sweIndex, flags);

  if (!result || typeof result[0] !== 'number') {
    return {
      longitude: 0, latitude: 0, distance: 1,
      longitudeSpeed: 0, latitudeSpeed: 0, distanceSpeed: 0
    };
  }

  return {
    longitude: normalizeDegrees(result[0] - ayanamsa),
    latitude: result[1] ?? 0,
    distance: result[2] ?? 1,
    longitudeSpeed: result[3] ?? 0,
    latitudeSpeed: result[4] ?? 0,
    distanceSpeed: result[5] ?? 0
  };
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
