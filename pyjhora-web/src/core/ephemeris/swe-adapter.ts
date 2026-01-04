/**
 * Swiss Ephemeris adapter interface
 * This provides a TypeScript interface to the Swiss Ephemeris WASM module (swisseph-js)
 * 
 * Initially stubbed - will be connected to actual swisseph-js when available
 */

import { AYANAMSA_MODES, DEFAULT_AYANAMSA_MODE } from '../constants';
import type { Place } from '../types';
import { normalizeDegrees } from '../utils/angle';
import { toUtc } from '../utils/julian';

// ============================================================================
// SWISS EPHEMERIS FLAGS (matching pyswisseph)
// ============================================================================

export const SWE_FLAGS = {
  FLG_SWIEPH: 2,
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

// ============================================================================
// EPHEMERIS STATE
// ============================================================================

let _ayanamsaMode = DEFAULT_AYANAMSA_MODE;
let _ayanamsaValue: number | null = null;
let _ephemerisPath = '/ephe/';
let _isInitialized = false;

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the Swiss Ephemeris
 * @param ephemerisPath - Path to ephemeris data files
 */
export async function initializeEphemeris(ephemerisPath = '/ephe/'): Promise<void> {
  _ephemerisPath = ephemerisPath;
  // TODO: Initialize swisseph-js WASM module
  // await swe.init(ephemerisPath);
  _isInitialized = true;
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
 * @param mode - Ayanamsa mode name
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
    // Will be passed to Swiss Ephemeris when connected
    _ayanamsaValue = null;
  }
  
  _ayanamsaMode = key;
}

/**
 * Get the current ayanamsa value for a given Julian Day
 * @param jd - Julian Day Number
 * @returns Ayanamsa value in degrees
 */
export function getAyanamsaValue(jd: number): number {
  const key = _ayanamsaMode.toLowerCase();
  
  if (key === 'sidm_user' || key === 'senthil' || key === 'sundar_ss') {
    return _ayanamsaValue ?? 0;
  }
  
  // Default Lahiri ayanamsa calculation (approximate formula)
  // Real implementation will use swisseph-js
  return calculateLahiriAyanamsa(jd);
}

/**
 * Calculate Lahiri ayanamsa (approximate)
 * This is a simplified formula - real calculation uses Swiss Ephemeris
 */
function calculateLahiriAyanamsa(jd: number): number {
  // Reference: Lahiri ayanamsa at J2000.0 = 23°51'
  const J2000 = 2451545.0;
  const ayanamsaAtJ2000 = 23.85; // degrees
  const precessionRate = 50.2388475 / 3600; // degrees per year
  const yearsSinceJ2000 = (jd - J2000) / 365.25;
  
  return ayanamsaAtJ2000 + precessionRate * yearsSinceJ2000;
}

/**
 * Calculate Senthil ayanamsa
 */
function calculateAyanamsaSenthil(jd: number): number {
  const referenceJd = 2451545.0; // J2000
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
  const kaliYugaJd = 588465.5; // Approximate JD for Kali Yuga start
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
 * Calculate sidereal longitude of a planet
 * @param jdUtc - Julian Day Number (UTC)
 * @param planet - Planet index (SWE constant)
 * @returns Sidereal longitude in degrees (0-360)
 */
export function siderealLongitude(jdUtc: number, planet: number): number {
  // TODO: Replace with actual swisseph-js call
  // const result = swe.calc_ut(jdUtc, planet, flags);
  // return normalizeDegrees(result.longitude);
  
  // Stub: Return approximate position based on mean motion
  const tropicalLong = calculateTropicalLongitudeStub(jdUtc, planet);
  const ayanamsa = getAyanamsaValue(jdUtc);
  return normalizeDegrees(tropicalLong - ayanamsa);
}

/**
 * Stub function for tropical longitude
 * Will be replaced with actual Swiss Ephemeris calculations
 */
function calculateTropicalLongitudeStub(jd: number, planet: number): number {
  const J2000 = 2451545.0;
  const daysSinceJ2000 = jd - J2000;
  
  // Mean daily motions (approximate, in degrees)
  const meanDailyMotions: Record<number, number> = {
    [SWE_PLANETS.SUN]: 0.9856,
    [SWE_PLANETS.MOON]: 13.1764,
    [SWE_PLANETS.MERCURY]: 1.3833,
    [SWE_PLANETS.VENUS]: 1.6021,
    [SWE_PLANETS.MARS]: 0.5240,
    [SWE_PLANETS.JUPITER]: 0.0831,
    [SWE_PLANETS.SATURN]: 0.0335
  };
  
  // Starting longitudes at J2000 (approximate)
  const startLongitudes: Record<number, number> = {
    [SWE_PLANETS.SUN]: 280.46,
    [SWE_PLANETS.MOON]: 218.32,
    [SWE_PLANETS.MERCURY]: 252.25,
    [SWE_PLANETS.VENUS]: 181.98,
    [SWE_PLANETS.MARS]: 355.45,
    [SWE_PLANETS.JUPITER]: 34.40,
    [SWE_PLANETS.SATURN]: 50.08
  };
  
  const motion = meanDailyMotions[planet] ?? 0;
  const start = startLongitudes[planet] ?? 0;
  
  return normalizeDegrees(start + motion * daysSinceJ2000);
}

/**
 * Get solar longitude
 */
export function solarLongitude(jdUtc: number): number {
  return siderealLongitude(jdUtc, SWE_PLANETS.SUN);
}

/**
 * Get lunar longitude
 */
export function lunarLongitude(jdUtc: number): number {
  return siderealLongitude(jdUtc, SWE_PLANETS.MOON);
}

/**
 * Calculate Ketu longitude from Rahu
 */
export function ketuFromRahu(rahuLongitude: number): number {
  return (rahuLongitude + 180) % 360;
}

// ============================================================================
// RISE/SET CALCULATIONS
// ============================================================================

/**
 * Calculate sunrise time
 * @param jd - Julian Day Number (local)
 * @param place - Place data
 * @returns Object with local time and JD
 */
export function sunrise(jd: number, place: Place): { 
  localTime: number; 
  timeString: string; 
  jd: number 
} {
  // TODO: Replace with actual swisseph-js rise_trans
  // Stub: Approximate sunrise at 6:00 AM local time
  const approximateHour = 6.0; // Simple approximation
  
  // Adjust for latitude (very rough approximation)
  const latitudeEffect = (place.latitude / 90) * 0.5; // up to 30 min adjustment
  const localTime = approximateHour + latitudeEffect;
  
  const jdSunrise = jd + (localTime - 12) / 24;
  
  return {
    localTime,
    timeString: formatHoursToTime(localTime),
    jd: jdSunrise
  };
}

/**
 * Calculate sunset time
 */
export function sunset(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  // Stub: Approximate sunset at 6:00 PM local time
  const approximateHour = 18.0;
  const latitudeEffect = -(place.latitude / 90) * 0.5;
  const localTime = approximateHour + latitudeEffect;
  
  const jdSunset = jd + (localTime - 12) / 24;
  
  return {
    localTime,
    timeString: formatHoursToTime(localTime),
    jd: jdSunset
  };
}

/**
 * Calculate moonrise time
 */
export function moonrise(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  // Stub: Moonrise varies significantly
  const approximateHour = 8.0;
  
  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
}

/**
 * Calculate moonset time
 */
export function moonset(jd: number, place: Place): {
  localTime: number;
  timeString: string;
  jd: number
} {
  // Stub
  const approximateHour = 20.0;
  
  return {
    localTime: approximateHour,
    timeString: formatHoursToTime(approximateHour),
    jd: jd + (approximateHour - 12) / 24
  };
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Format hours as time string
 */
function formatHoursToTime(hours: number): string {
  const h = Math.floor(hours);
  const m = Math.floor((hours - h) * 60);
  const s = Math.floor(((hours - h) * 60 - m) * 60);
  const ampm = h < 12 ? 'AM' : 'PM';
  const h12 = h % 12 || 12;
  return `${h12.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')} ${ampm}`;
}

/**
 * Get planet speed info
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
  
  // Approximate speeds (stub)
  const dailyMotions: Record<number, number> = {
    [SWE_PLANETS.SUN]: 0.9856,
    [SWE_PLANETS.MOON]: 13.1764,
    [SWE_PLANETS.MERCURY]: 1.3833,
    [SWE_PLANETS.VENUS]: 1.6021,
    [SWE_PLANETS.MARS]: 0.5240,
    [SWE_PLANETS.JUPITER]: 0.0831,
    [SWE_PLANETS.SATURN]: 0.0335
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
 * Check if planets are in retrograde
 */
export function planetsInRetrograde(jd: number, place: Place): number[] {
  // Stub: Will use actual ephemeris speed data
  // Returns empty array for now
  return [];
}
