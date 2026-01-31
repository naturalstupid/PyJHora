/**
 * Panchanga calculation engine
 * Ported from PyJHora drik.py
 * 
 * Calculates tithi, nakshatra, yogam, karana, and other panchanga elements
 */

import {
    JUPITER,
    KETU,
    MARS, MERCURY,
    MOON,
    RAHU,
    SATURN,
    SUN,
    VENUS
} from '../constants';
import {
    getAyanamsaValue,
    ketuFromRahu,
    lunarLongitude,
    setAyanamsaMode,
    siderealLongitude,
    solarLongitude,
    sunrise,
    sunset,
    SWE_PLANETS
} from '../ephemeris/swe-adapter';
import type { Place } from '../types';
import { normalizeDegrees } from '../utils/angle';
import { toUtc } from '../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface TithiResult {
  number: number;
  name: string;
  paksha: 'shukla' | 'krishna';
  startTime: number;
  endTime: number;
}

export interface NakshatraResult {
  number: number;
  name: string;
  pada: number;
  startTime: number;
  endTime: number;
}

export interface YogaResult {
  number: number;
  name: string;
  endTime: number;
}

export interface KaranaResult {
  number: number;
  name: string;
  endTime: number;
}

// ============================================================================
// NAKSHATRA PADA
// ============================================================================

/**
 * Calculate nakshatra and pada from longitude
 * @param longitude - Longitude in degrees (0-360)
 * @returns [nakshatra (1-27), pada (1-4), remainder]
 */
export function nakshatraPada(longitude: number): [number, number, number] {
  const oneStar = 360 / 27; // 13°20'
  const onePada = 360 / 108; // 3°20'
  
  const normalized = normalizeDegrees(longitude);
  const quotient = Math.floor(normalized / oneStar);
  const remainder = normalized % oneStar;
  const pada = Math.floor(remainder / onePada);
  
  // Convert 0-based to 1-based
  return [1 + quotient, 1 + pada, remainder];
}

// ============================================================================
// TITHI CALCULATION
// ============================================================================

/**
 * Calculate the moon phase for tithi
 */
function tithiPhase(jd: number): number {
  const moonLong = lunarLongitude(jd);
  const sunLong = solarLongitude(jd);
  return normalizeDegrees(moonLong - sunLong);
}

/**
 * Calculate tithi for given date and place
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Tithi information
 */
export function calculateTithi(jd: number, place: Place): TithiResult {
  const jdUtc = toUtc(jd, place.timezone);
  const sunriseData = sunrise(jd, place);
  const sunriseJd = sunriseData.jd;
  
  // Calculate moon phase at sunrise
  const phase = tithiPhase(toUtc(sunriseJd, place.timezone));
  
  // Each tithi spans 12 degrees
  const tithiNumber = Math.ceil(phase / 12);
  const adjustedNumber = tithiNumber === 0 ? 30 : tithiNumber;
  
  // Determine paksha (lunar fortnight)
  const paksha = adjustedNumber <= 15 ? 'shukla' : 'krishna';
  
  // Tithi names
  const tithiNames = [
    'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
    'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
    'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi',
    'Purnima', // or Amavasya for krishna paksha
    'Pratipada', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami',
    'Shashthi', 'Saptami', 'Ashtami', 'Navami', 'Dashami',
    'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi',
    'Amavasya'
  ];
  
  const name = tithiNames[adjustedNumber - 1] ?? `Tithi ${adjustedNumber}`;
  
  // Calculate approximate end time
  const degreesLeft = adjustedNumber * 12 - phase;
  const moonDailyMotion = 13.176; // Average lunar daily motion
  const sunDailyMotion = 0.986; // Average solar daily motion
  const relativeDailyMotion = moonDailyMotion - sunDailyMotion;
  const hoursToEnd = (degreesLeft / relativeDailyMotion) * 24;
  const endTime = sunriseData.localTime + hoursToEnd;
  
  return {
    number: adjustedNumber,
    name,
    paksha,
    startTime: sunriseData.localTime,
    endTime
  };
}

// ============================================================================
// NAKSHATRA CALCULATION
// ============================================================================

const NAKSHATRA_NAMES = [
  'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
  'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
  'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
  'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
  'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
];

/**
 * Calculate nakshatra for given date and place
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Nakshatra information
 */
export function calculateNakshatra(jd: number, place: Place): NakshatraResult {
  const jdUtc = toUtc(jd, place.timezone);
  const moonLong = lunarLongitude(jdUtc);
  
  const [nakNumber, pada, remainder] = nakshatraPada(moonLong);
  const name = NAKSHATRA_NAMES[nakNumber - 1] ?? `Nakshatra ${nakNumber}`;
  
  // Calculate approximate end time
  const sunriseData = sunrise(jd, place);
  const oneStar = 360 / 27;
  const degreesLeft = nakNumber * oneStar - moonLong;
  const moonDailyMotion = 13.176;
  const hoursToEnd = ((degreesLeft + 360) % oneStar) / moonDailyMotion * 24;
  const endTime = sunriseData.localTime + hoursToEnd;
  
  return {
    number: nakNumber,
    name,
    pada,
    startTime: sunriseData.localTime,
    endTime
  };
}

// ============================================================================
// YOGA CALCULATION (Sun-Moon Yoga, not Astrological Yoga)
// ============================================================================

const YOGA_NAMES = [
  'Vishkumbha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana',
  'Atiganda', 'Sukarman', 'Dhriti', 'Shula', 'Ganda',
  'Vriddhi', 'Dhruva', 'Vyaghata', 'Harshana', 'Vajra',
  'Siddhi', 'Vyatipata', 'Variyan', 'Parigha', 'Shiva',
  'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma',
  'Indra', 'Vaidhriti'
];

/**
 * Calculate yoga (sun-moon combination) for given date
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Yoga information
 */
export function calculateYoga(jd: number, place: Place): YogaResult {
  const jdUtc = toUtc(jd, place.timezone);
  const sunriseData = sunrise(jd, place);
  
  const moonLong = lunarLongitude(jdUtc);
  const sunLong = solarLongitude(jdUtc);
  
  // Yoga = sum of sun and moon longitudes divided by 13°20'
  const total = normalizeDegrees(moonLong + sunLong);
  const oneYoga = 360 / 27;
  const yogaNumber = Math.ceil(total / oneYoga);
  const adjustedNumber = yogaNumber === 0 ? 27 : yogaNumber;
  
  const name = YOGA_NAMES[adjustedNumber - 1] ?? `Yoga ${adjustedNumber}`;
  
  // Calculate approximate end time
  const degreesLeft = adjustedNumber * oneYoga - total;
  const combinedDailyMotion = 13.176 + 0.986; // Moon + Sun
  const hoursToEnd = (degreesLeft / combinedDailyMotion) * 24;
  const endTime = sunriseData.localTime + hoursToEnd;
  
  return {
    number: adjustedNumber,
    name,
    endTime
  };
}

// ============================================================================
// KARANA CALCULATION
// ============================================================================

const KARANA_NAMES = [
  'Bava', 'Balava', 'Kaulava', 'Taitila', 'Garija', 'Vanija', 'Vishti',
  'Shakuni', 'Chatushpada', 'Naga', 'Kimstughna'
];

/**
 * Calculate karana (half-tithi) for given date
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Karana information
 */
export function calculateKarana(jd: number, place: Place): KaranaResult {
  const jdUtc = toUtc(jd, place.timezone);
  const sunriseData = sunrise(jd, place);
  
  const phase = tithiPhase(jdUtc);
  
  // Each karana spans 6 degrees (half a tithi)
  const karanaNumber = Math.ceil(phase / 6);
  const adjustedNumber = karanaNumber === 0 ? 60 : karanaNumber;
  
  // Karana cycle: 7 repeating karanas (Bava to Vishti) + 4 fixed
  let name: string;
  if (adjustedNumber === 1) {
    name = 'Kimstughna';
  } else if (adjustedNumber >= 58) {
    name = KARANA_NAMES[adjustedNumber - 58 + 7] ?? `Karana ${adjustedNumber}`;
  } else {
    name = KARANA_NAMES[(adjustedNumber - 2) % 7] ?? `Karana ${adjustedNumber}`;
  }
  
  // Calculate approximate end time
  const degreesLeft = adjustedNumber * 6 - phase;
  const relativeDailyMotion = 13.176 - 0.986;
  const hoursToEnd = (degreesLeft / relativeDailyMotion) * 24;
  const endTime = sunriseData.localTime + hoursToEnd;
  
  return {
    number: adjustedNumber,
    name,
    endTime
  };
}

// ============================================================================
// VARA (WEEKDAY)
// ============================================================================

const VARA_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const VARA_LORDS = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN];

/**
 * Calculate vara (weekday) for given date
 * @param jd - Julian Day Number
 * @returns Vara information
 */
export function calculateVara(jd: number): { number: number; name: string; lord: number } {
  const dayOfWeek = Math.floor(jd + 1.5) % 7;
  
  return {
    number: dayOfWeek,
    name: VARA_NAMES[dayOfWeek] ?? 'Unknown',
    lord: VARA_LORDS[dayOfWeek] ?? SUN
  };
}

// ============================================================================
// PLANET POSITIONS
// ============================================================================

/**
 * Get planet longitude
 * @param jd - Julian Day Number
 * @param place - Place data
 * @param planet - Planet index (0-8 for Sun to Ketu)
 * @returns Sidereal longitude in degrees
 */
export function getPlanetLongitude(jd: number, place: Place, planet: number): number {
  const jdUtc = toUtc(jd, place.timezone);
  
  // Map our planet indices to SWE constants
  const planetMap: Record<number, number> = {
    [SUN]: SWE_PLANETS.SUN,
    [MOON]: SWE_PLANETS.MOON,
    [MARS]: SWE_PLANETS.MARS,
    [MERCURY]: SWE_PLANETS.MERCURY,
    [JUPITER]: SWE_PLANETS.JUPITER,
    [VENUS]: SWE_PLANETS.VENUS,
    [SATURN]: SWE_PLANETS.SATURN,
    [RAHU]: SWE_PLANETS.MEAN_NODE
  };
  
  if (planet === KETU) {
    const rahuLong = siderealLongitude(jdUtc, SWE_PLANETS.MEAN_NODE);
    return ketuFromRahu(rahuLong);
  }
  
  const swePlanet = planetMap[planet];
  if (swePlanet === undefined) {
    throw new Error(`Unknown planet index: ${planet}`);
  }
  
  return siderealLongitude(jdUtc, swePlanet);
}

/**
 * Get all planet positions
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Object with planet positions
 */
export function getAllPlanetPositions(
  jd: number,
  place: Place
): Record<number, { longitude: number; rasi: number; nakshatraData: [number, number, number] }> {
  const positions: Record<number, { longitude: number; rasi: number; nakshatraData: [number, number, number] }> = {};
  
  for (let planet = 0; planet <= 8; planet++) {
    const longitude = getPlanetLongitude(jd, place, planet);
    const rasi = Math.floor(longitude / 30);
    const nakshatraData = nakshatraPada(longitude);
    
    positions[planet] = { longitude, rasi, nakshatraData };
  }
  
  return positions;
}

// ============================================================================
// DAY/NIGHT LENGTH
// ============================================================================

/**
 * Calculate day length
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Day length in hours
 */
export function dayLength(jd: number, place: Place): number {
  const sunriseData = sunrise(jd, place);
  const sunsetData = sunset(jd, place);
  return sunsetData.localTime - sunriseData.localTime;
}

/**
 * Calculate night length
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Night length in hours
 */
export function nightLength(jd: number, place: Place): number {
  const sunsetData = sunset(jd, place);
  const nextSunrise = sunrise(jd + 1, place);
  return 24.0 + nextSunrise.localTime - sunsetData.localTime;
}

// ============================================================================
// SPECIAL LAGNAS
// ============================================================================

/**
 * Calculate Sree Lagna from Moon and Ascendant longitudes
 * Sree Lagna = Ascendant + (Moon's nakshatra remainder * 27)
 *
 * @param moonLongitude - Moon's longitude in degrees
 * @param ascendantLongitude - Ascendant longitude in degrees
 * @returns [rasi (0-11), longitude within rasi]
 */
export function sreeLagnaFromLongitudes(
  moonLongitude: number,
  ascendantLongitude: number
): [number, number] {
  const [, , remainder] = nakshatraPada(moonLongitude);
  const reminderFraction = remainder * 27;
  const sreeLong = normalizeDegrees(ascendantLongitude + reminderFraction);
  const rasi = Math.floor(sreeLong / 30);
  const longitude = sreeLong % 30;
  return [rasi, longitude];
}

/**
 * Calculate Sree Lagna for a given Julian day and place
 * @param jd - Julian day number
 * @param place - Birth place
 * @returns [rasi (0-11), longitude within rasi]
 */
export function getSreeLagna(jd: number, place: Place): [number, number] {
  const moonLong = getPlanetLongitude(jd, place, MOON);
  const ascLong = getPlanetLongitude(jd, place, -1); // -1 for ascendant
  return sreeLagnaFromLongitudes(moonLong, ascLong);
}

/**
 * Calculate Hora Lagna (simplified version)
 * Hora Lagna is a special ascendant with rate factor 0.5
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @returns [rasi (0-11), longitude within rasi]
 */
export function getHoraLagna(jd: number, place: Place): [number, number] {
  // Simplified calculation:
  // Hora Lagna advances at half the rate of regular ascendant
  // This is an approximation - full calculation requires sunrise time
  const ascLong = getPlanetLongitude(jd, place, -1);
  const sunLong = solarLongitude(jd);

  // Time factor approximation using sun position
  const horaLong = normalizeDegrees(ascLong + (sunLong * 0.5));
  const rasi = Math.floor(horaLong / 30);
  const longitude = horaLong % 30;
  return [rasi, longitude];
}

// ============================================================================
// UTILITY EXPORTS
// ============================================================================

export { getAyanamsaValue, setAyanamsaMode };

