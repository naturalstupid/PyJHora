/**
 * Panchanga calculation engine
 * Ported from PyJHora drik.py
 * 
 * Calculates tithi, nakshatra, yogam, karana, and other panchanga elements
 */

import {
    AMRITA_GADIYA_VARJYAM_STAR_MAP,
    AMRITA_SIDDHA_YOGA_DICT,
    ANANDHAADHI_YOGA_DAY_STAR_LIST,
    ASCENDANT_SYMBOL,
    AVAILABLE_HOUSE_SYSTEMS,
    BHAAVA_MADHYA_METHOD,
    CONJUNCTION_INCREMENT,
    DAGHDA_YOGA_DICT,
    DAY_RULERS,
    DISHA_SHOOL_MAP,
    DREKKANA_TABLE,
    DREKKANA_TABLE_BVRAMAN,
    DUAL_SIGNS,
    FIXED_SIGNS,
    FORCE_KALI_START_YEAR_FOR_YEARS_BEFORE_KALI_YEAR_4009,
    GAURI_CHOGHADIYA_DAY_TABLE,
    GAURI_CHOGHADIYA_NIGHT_TABLE,
    GRAHA_YUDH_CRITERIA_1,
    GRAHA_YUDH_CRITERIA_2,
    GRAHA_YUDH_CRITERIA_3,
    HOUSE_OWNERS,
    IL_FACTORS,
    JUPITER,
    KALI_START_YEAR,
    KETU,
    MAHABHARATHA_TITHI_JULIAN_DAY,
    MARS, MERCURY,
    MOON,
    MRITYU_YOGA_DICT,
    MUHURTHAS_OF_THE_DAY,
    NAKSHATHRA_LORDS,
    NIGHT_RULERS,
    RAHU,
    SARVARTHA_SIDDHA_YOGA,
    SATURN,
    SHUBHA_HORA_DAY_TABLE,
    SHUBHA_HORA_NIGHT_TABLE,
    SIDEREAL_YEAR,
    SPECIAL_THAARA_LORDS_1,
    SPECIAL_THAARA_MAP,
    SUN,
    TAMIL_BASIC_YOGA_LIST,
    TAMIL_BASIC_YOGA_SRINGERI_LIST,
    TAMIL_YOGA_NAMES,
    TRIGUNA_DAYS_DICT,
    TROPICAL_YEAR,
    USE_AHARGHANA_FOR_VAARA_CALCULATION,
    UTPATA_YOGA_DICT,
    VENUS,
    WESTERN_HOUSE_SYSTEMS,
    YAMAGHATA_YOGA_DICT,
    INCREASE_TITHI_BY_ONE_BEFORE_KALI_YUGA,
    YOGINI_VAASA_TITHI_MAP,
} from '../constants';
import {
    ascendantFullAsync,
    getAyanamsaValue,
    houseCuspsAsync,
    ketuFromRahu,
    lunarLongitude,
    lunarLongitudeAsync,
    moonrise as _moonrise,
    moonriseAsync as _moonriseAsync,
    moonset as _moonset,
    moonsetAsync as _moonsetAsync,
    nextLunarEclipseLocAsync,
    nextSolarEclipseLocAsync,
    planetSpeedInfo as _planetSpeedInfo,
    planetSpeedInfoAsync as _planetSpeedInfoAsync,
    planetsInRetrograde as _planetsInRetrograde,
    planetsInRetrogradeAsync as _planetsInRetrogradeAsync,
    setAyanamsaMode,
    siderealLongitude,
    siderealLongitudeAsync,
    solarEclipseHowAsync,
    solarLongitude,
    solarLongitudeAsync,
    sunrise,
    sunriseAsync,
    sunset,
    sunsetAsync,
    SWE_PLANETS
} from '../ephemeris/swe-adapter';
import type { Place } from '../types';
import { normalizeDegrees } from '../utils/angle';
import { extendAngleRange, inverseLagrange, unwrapAngles } from '../utils/interpolation';
import { gregorianToJulianDay, julianDayToGregorian, toUtc } from '../utils/julian';
import { getMixedDivisionalChart, getDivisionalChart } from '../horoscope/charts';
import type { PlanetPosition } from '../horoscope/charts';
import { getCharaKarakas, getRelativeHouseOfPlanet } from '../horoscope/house';

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
  const dayOfWeek = Math.ceil(jd + 1) % 7;
  
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
// MIDDAY / MIDNIGHT (Async)
// ============================================================================

/**
 * Calculate midday time (async) — midpoint of sunrise and sunset.
 * Python: drik.midday(jd, place)
 *
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Object with localTime (float hours) and jd (midday JD)
 */
export async function middayAsync(
  jd: number,
  place: Place
): Promise<{ localTime: number; jd: number }> {
  const sr = await sunriseAsync(jd, place);
  const ss = await sunsetAsync(jd, place);
  const localTime = 0.5 * (sr.localTime + ss.localTime);
  const midJd = 0.5 * (sr.jd + ss.jd);
  return { localTime, jd: midJd };
}

/**
 * Calculate midnight time (async) — midpoint of previous sunset and sunrise.
 * Python: drik.midnight(jd, place)
 *
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Midnight local time as float hours
 */
export async function midnightAsync(
  jd: number,
  place: Place
): Promise<number> {
  const sr = await sunriseAsync(jd, place);
  const prevSs = await sunsetAsync(jd - 1, place);
  // Midnight is midpoint between previous sunset and current sunrise
  let mnhl = 0.5 * (sr.localTime + prevSs.localTime);
  // Adjust: if > 12, subtract 12; if < 12, do 12 - value
  // This gives hours past midnight (0-based)
  if (mnhl < 12) {
    mnhl = 12 - mnhl;
  } else {
    mnhl -= 12;
  }
  return mnhl;
}

// ============================================================================
// ASYNC PANCHANGA FUNCTIONS (using inverseLagrange + swe_rise_trans)
// ============================================================================

/**
 * Normalize angle to range [start, start+360)
 * Python: utils.normalize_angle(angle, start=0)
 */
function normalizeAngle(angle: number, start: number = 0): number {
  while (angle >= start + 360) angle -= 360;
  while (angle < start) angle += 360;
  return angle;
}

/**
 * Internal: get tithi data (tithi number + end time in hours) using inverse Lagrange.
 * Python: _get_tithi(jd, place) — core algorithm
 *
 * Uses UT JD from sunrise (matching Python's `rise = sunrise(jd, place)[2]` which is UT JD).
 *
 * @returns [tithiNo, endTimeHours, ...optionally skippedTithiNo, skippedEndTimeHours]
 */
async function _getTithiAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });

  // 1. Find time of sunrise — use jdUt (UT JD) for longitude calculations
  const riseData = await sunriseAsync(jd, place);
  const rise = riseData.jd; // Local-time-encoded JD, matching Python's sunrise()[2]

  // 2. Find tithi at sunrise: moon_phase = (moon_long - sun_long) % 360
  const moonLong = await siderealLongitudeAsync(rise, 1); // Moon
  const sunLong = await siderealLongitudeAsync(rise, 0);   // Sun
  const moonPhase = ((moonLong - sunLong) % 360 + 360) % 360;
  const today = Math.ceil(moonPhase / 12) || 30; // avoid 0
  const degreesLeft = today * 12 - moonPhase;

  // 3. Compute longitudinal differences at intervals from sunrise
  const offsets = [0.25, 0.5, 0.75, 1.0];
  const moonAtRise = moonLong;
  const sunAtRise = sunLong;

  const relativeMotion: number[] = [];
  for (const t of offsets) {
    const moonAtT = await siderealLongitudeAsync(rise + t, 1);
    const sunAtT = await siderealLongitudeAsync(rise + t, 0);
    const moonDiff = ((moonAtT - moonAtRise) % 360 + 360) % 360;
    const sunDiff = ((sunAtT - sunAtRise) % 360 + 360) % 360;
    relativeMotion.push(((moonDiff - sunDiff) % 360 + 360) % 360);
  }

  // 4. Find end time by inverse Lagrange interpolation
  const approxEnd = inverseLagrange(offsets, relativeMotion, degreesLeft);
  const ends = (rise + approxEnd - jdUtc) * 24 + tz;
  const tithiNo = today;
  const answer: number[] = [tithiNo, ends];

  // 5. Check for skipped tithi
  const moonTmrw = await siderealLongitudeAsync(rise + 1, 1);
  const sunTmrw = await siderealLongitudeAsync(rise + 1, 0);
  const moonPhaseTmrw = ((moonTmrw - sunTmrw) % 360 + 360) % 360;
  const tomorrow = Math.ceil(moonPhaseTmrw / 12) || 30;
  const isSkipped = ((tomorrow - today) % 30 + 30) % 30 > 1;
  if (isSkipped) {
    const leapTithi = today + 1;
    const leapDegreesLeft = leapTithi * 12 - moonPhase;
    const leapApproxEnd = inverseLagrange(offsets, relativeMotion, leapDegreesLeft);
    const leapEnds = (rise + leapApproxEnd - jdUtc) * 24 + tz;
    answer.push(leapTithi === 31 ? 1 : leapTithi, leapEnds);
  }

  return answer;
}

/**
 * Generic tithi calculation with custom planets.
 * Python: _get_tithi(jd, place, tithi_index, planet1, planet2, cycle)
 * Uses sidereal_longitude for arbitrary planets (not just Moon/Sun).
 */
async function _getTithiGenericAsync(
  jd: number,
  place: Place,
  planet1: number = 1,  // Moon
  planet2: number = 0,  // Sun
  tithiIndex: number = 1,
  cycle: number = 1
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });

  const riseData = await sunriseAsync(jd, place);
  const rise = riseData.jd;

  // _special_tithi_phase: (tithi_index*(p1_long - p2_long)+(cycle-1)*180) % 360
  const p1AtRise = await siderealLongitudeAsync(rise, planet1);
  const p2AtRise = await siderealLongitudeAsync(rise, planet2);
  const moonPhase = ((tithiIndex * (p1AtRise - p2AtRise) + (cycle - 1) * 180) % 360 + 360) % 360;
  const today = Math.ceil(moonPhase / 12) || 30;
  const degreesLeft = today * 12 - moonPhase;

  const offsets = [0.25, 0.5, 0.75, 1.0];
  const relativeMotion: number[] = [];
  for (const t of offsets) {
    const p1AtT = await siderealLongitudeAsync(rise + t, planet1);
    const p2AtT = await siderealLongitudeAsync(rise + t, planet2);
    const p1Diff = ((p1AtT - p1AtRise) % 360 + 360) % 360;
    const p2Diff = ((p2AtT - p2AtRise) % 360 + 360) % 360;
    relativeMotion.push(((tithiIndex * (p1Diff - p2Diff) + (cycle - 1) * 180) % 360 + 360) % 360);
  }

  const approxEnd = inverseLagrange(offsets, relativeMotion, degreesLeft);
  const ends = (rise + approxEnd - jdUtc) * 24 + tz;
  const tithiNo = today;
  const answer: number[] = [tithiNo, ends];

  // Check for skipped tithi
  const p1Tmrw = await siderealLongitudeAsync(rise + 1, planet1);
  const p2Tmrw = await siderealLongitudeAsync(rise + 1, planet2);
  const moonPhaseTmrw = ((tithiIndex * (p1Tmrw - p2Tmrw) + (cycle - 1) * 180) % 360 + 360) % 360;
  const tomorrow = Math.ceil(moonPhaseTmrw / 12) || 30;
  const isSkipped = ((tomorrow - today) % 30 + 30) % 30 > 1;
  if (isSkipped) {
    const leapTithi = today + 1;
    const leapDegreesLeft = leapTithi * 12 - moonPhase;
    const leapApproxEnd = inverseLagrange(offsets, relativeMotion, leapDegreesLeft);
    const leapEnds = (rise + leapApproxEnd - jdUtc) * 24 + tz;
    answer.push(leapTithi === 31 ? 1 : leapTithi, leapEnds);
  }

  return answer;
}

/**
 * Generic yogam calculation with custom planets.
 * Python: _get_yogam(jd, place, planet1, planet2, tithi_index, cycle)
 * Uses sidereal_longitude for arbitrary planets (not just Moon/Sun).
 */
async function _getYogamGenericAsync(
  jd: number,
  place: Place,
  planet1: number = 1,  // Moon
  planet2: number = 0,  // Sun
  tithiIndex: number = 1,
  cycle: number = 1
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });

  const riseData = await sunriseAsync(jd, place);
  const rise = riseData.jd;
  const oneYoga = 360 / 27;

  // _special_yoga_phase: (tithi_index*(p1_long + p2_long)+(cycle-1)*180) % 360
  const p1AtRise = await siderealLongitudeAsync(rise, planet1);
  const p2AtRise = await siderealLongitudeAsync(rise, planet2);
  const total = ((tithiIndex * (p1AtRise + p2AtRise) + (cycle - 1) * 180) % 360 + 360) % 360;
  const yog = Math.ceil(total / oneYoga) || 27;
  const yogamNo = yog;
  const degreesLeft = yog * oneYoga - total;

  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const totalMotion: number[] = [];
  for (const t of offsets) {
    const p1AtT = await siderealLongitudeAsync(rise + t, planet1);
    const p2AtT = await siderealLongitudeAsync(rise + t, planet2);
    const p1Diff = ((p1AtT - p1AtRise) % 360 + 360) % 360;
    const p2Diff = ((p2AtT - p2AtRise) % 360 + 360) % 360;
    totalMotion.push(((tithiIndex * (p1Diff + p2Diff) + (cycle - 1) * 180) % 360 + 360) % 360);
  }

  const approxEnd = inverseLagrange(offsets, totalMotion, degreesLeft);
  const ends = (rise + approxEnd - jdUtc) * 24 + tz;
  const answer: number[] = [yogamNo, ends];

  // Check for skipped yoga
  const p1Tmrw = await siderealLongitudeAsync(rise + 1, planet1);
  const p2Tmrw = await siderealLongitudeAsync(rise + 1, planet2);
  const totalTmrw = ((tithiIndex * (p1Tmrw + p2Tmrw) + (cycle - 1) * 180) % 360 + 360) % 360;
  const tomorrow = Math.ceil(totalTmrw / oneYoga) || 27;
  const isSkipped = ((tomorrow - yog) % 27 + 27) % 27 > 1;
  if (isSkipped) {
    const leapYog = yog + 1;
    const leapDegreesLeft = leapYog * oneYoga - total;
    const leapApproxEnd = inverseLagrange(offsets, totalMotion, leapDegreesLeft);
    const leapEnds = (rise + leapApproxEnd - jdUtc) * 24 + tz;
    answer.push(leapYog === 28 ? 1 : leapYog, leapEnds);
  }

  return answer;
}

/**
 * Calculate tithi with accurate end times (async).
 * Uses inverse Lagrange interpolation on WASM-calculated longitudes.
 * Python: tithi_using_inverse_lagrange(jd, place)
 *
 * @returns [tithiNo, startTime, endTime, ...optional nextTithiNo, nextStartTime, nextEndTime]
 */
export async function calculateTithiAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const _tithi = await _getTithiAsync(jd, place);
  const _tithiPrev = await _getTithiAsync(jd - 1, place);

  const tithiNo = _tithi[0]!;
  let tithiStart = _tithiPrev[1]!;
  const tithiEnd = _tithi[1]!;

  if (tithiStart < 24.0) {
    tithiStart = -tithiStart;
  } else if (tithiStart > 24) {
    tithiStart -= 24.0;
  }

  const result: number[] = [tithiNo, tithiStart, tithiEnd];

  // Check if next tithi also falls on same day (end < 24)
  if (tithiEnd < 24.0) {
    const _tithi1 = await _getTithiAsync(jd + tithiEnd / 24, place);
    const nextTithiNo = (tithiNo % 30) + 1;
    const nextTithiStart = tithiEnd;
    const nextTithiEnd = tithiEnd + _tithi1[1]!;
    result.push(nextTithiNo, nextTithiStart, nextTithiEnd);
  }

  return result;
}

/**
 * Internal: get nakshatra data using inverse Lagrange.
 * Python: _get_nakshathra(jd, place)
 *
 * @returns [nakNo, padamNo, endTimeHours, nextNakNo, nextPadamNo, nextEndTimeHours]
 */
async function _getNakshatraAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUt = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });
  const jdUtc = jd - tz / 24;

  // 1. Get sunrise — Python _get_nakshathra passes jd_utc to sunrise (line 658)
  const riseData = await sunriseAsync(jdUtc, place);
  const rise = riseData.jd; // Local-time-encoded JD

  // 2. Get lunar longitudes at 5 offsets from sunrise
  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const longitudes: number[] = [];
  for (const t of offsets) {
    longitudes.push(await siderealLongitudeAsync(rise + t, 1));
  }

  const unwrappedLongitudes = unwrapAngles(longitudes);
  const extendedLongitudes = extendAngleRange(unwrappedLongitudes, 360);
  const x = Array.from({ length: extendedLongitudes.length }, (_, i) =>
    offsets[i % offsets.length]!
  );

  // 3. Get current nakshatra/pada from lunar longitude at jd_utc
  const nirayana = await lunarLongitudeAsync(jdUtc);
  const [nakNo, padamNo] = nakshatraPada(nirayana);

  // 4. Find end time of current nakshatra
  let yCheck = nakNo * 360 / 27;
  yCheck = normalizeAngle(yCheck, Math.min(...extendedLongitudes));
  let approxEnd = inverseLagrange(x, extendedLongitudes, yCheck);
  let ends = (rise - jdUt + approxEnd) * 24 + tz;
  const answer: number[] = [nakNo, padamNo, ends];

  // 5. Find end time of next nakshatra
  let leapNak = nakNo + 1;
  yCheck = leapNak * 360 / 27;
  yCheck = normalizeAngle(yCheck, Math.min(...extendedLongitudes));
  approxEnd = inverseLagrange(x, extendedLongitudes, yCheck);
  ends = (rise - jdUt + approxEnd) * 24 + tz;
  leapNak = nakNo === 27 ? 1 : leapNak;
  answer.push(leapNak, padamNo, ends);

  return answer;
}

/**
 * Calculate nakshatra with accurate end times (async).
 * Python: nakshathra(jd, place)
 *
 * @returns [nakNo, padamNo, endTimeHours, nextNakNo, nextPadamNo, nextEndTimeHours]
 */
export async function calculateNakshatraAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  return _getNakshatraAsync(jd, place);
}

/**
 * Internal: get yogam data using inverse Lagrange.
 * Python: _get_yogam(jd, place)
 *
 * @returns [yogamNo, endTimeHours, ...optional skippedYogamNo, skippedEndTimeHours]
 */
async function _getYogamAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });

  // 1. Sunrise
  const riseData = await sunriseAsync(jd, place);
  const rise = riseData.jd; // Local-time-encoded JD
  const oneYoga = 360 / 27;

  // 2. Moon + Sun at sunrise (using lunar_longitude / solar_longitude like Python)
  const moonAtRise = await lunarLongitudeAsync(rise);
  const sunAtRise = await solarLongitudeAsync(rise);
  const total = ((moonAtRise + sunAtRise) % 360 + 360) % 360;
  const yog = Math.ceil(total / oneYoga) || 27;
  const yogamNo = yog;
  const degreesLeft = yog * oneYoga - total;

  // 3. Longitudinal sums at offsets (Python uses lunar_longitude/solar_longitude, not sidereal)
  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const totalMotion: number[] = [];
  for (const t of offsets) {
    const moonAtT = await lunarLongitudeAsync(rise + t);
    const sunAtT = await solarLongitudeAsync(rise + t);
    const moonDiff = ((moonAtT - moonAtRise) % 360 + 360) % 360;
    const sunDiff = ((sunAtT - sunAtRise) % 360 + 360) % 360;
    totalMotion.push(((moonDiff + sunDiff) % 360 + 360) % 360);
  }

  // 4. Inverse Lagrange interpolation
  const approxEnd = inverseLagrange(offsets, totalMotion, degreesLeft);
  const ends = (rise + approxEnd - jdUtc) * 24 + tz;
  const answer: number[] = [yogamNo, ends];

  // 5. Check for skipped yoga
  const moonTmrw = await lunarLongitudeAsync(rise + 1);
  const sunTmrw = await solarLongitudeAsync(rise + 1);
  const totalTmrw = ((moonTmrw + sunTmrw) % 360 + 360) % 360;
  const tomorrow = Math.ceil(totalTmrw / oneYoga) || 27;
  const isSkipped = ((tomorrow - yog) % 27 + 27) % 27 > 1;
  if (isSkipped) {
    const leapYog = yog + 1;
    const leapDegreesLeft = leapYog * oneYoga - total;
    const leapApproxEnd = inverseLagrange(offsets, totalMotion, leapDegreesLeft);
    const leapEnds = (rise + leapApproxEnd - jdUtc) * 24 + tz;
    answer.push(leapYog === 28 ? 1 : leapYog, leapEnds);
  }

  return answer;
}

/**
 * Calculate yogam with accurate end times (async).
 * Python: yogam_old(jd, place)
 *
 * @returns [yogamNo, startTime, endTime, ...optional next yogam data]
 */
export async function calculateYogaAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const _yoga = await _getYogamAsync(jd, place);
  const _yogaPrev = await _getYogamAsync(jd - 1, place);

  const yogaNo = _yoga[0]!;
  let yogaStart = _yogaPrev[1]!;
  const yogaEnd = _yoga[1]!;

  if (yogaStart < 24.0) {
    yogaStart = -yogaStart;
  } else if (yogaStart > 24) {
    yogaStart -= 24.0;
  }

  const result: number[] = [yogaNo, yogaStart, yogaEnd];
  return result;
}

/**
 * Calculate karana with accurate end times (async).
 * Python: karana(jd, place)
 * Karana is half a tithi — derived from tithi calculation.
 *
 * @returns [karanaNo, startTime, endTime]
 */
export async function calculateKaranaAsync(
  jd: number,
  place: Place
): Promise<[number, number, number]> {
  const { time } = julianDayToGregorian(jd);
  const birthTimeHrs = time.hour + time.minute / 60 + time.second / 3600;

  const _tithi = await calculateTithiAsync(jd, place);
  const tStart = _tithi[1]!;
  const tEnd = _tithi[2]!;
  const tMid = 0.5 * (tStart + tEnd);
  let karana = _tithi[0]! * 2 - 1;

  let kStart: number;
  let kEnd: number;
  if (birthTimeHrs > tMid) {
    // second half of tithi
    karana += 1;
    kStart = tMid;
    kEnd = tEnd;
  } else {
    // first half of tithi
    kStart = tStart;
    kEnd = tMid;
  }

  return [karana, kStart, kEnd];
}

/**
 * Calculate raasi (Moon's zodiac sign) with end time (async).
 * Python: raasi(jd, place)
 *
 * @returns [raasiNo (1-12), endTimeHours, fracLeft, ...optional next raasi data]
 */
export async function raasiAsync(
  jd: number,
  place: Place
): Promise<number[]> {
  const tz = place.timezone;
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });

  const riseData = await sunriseAsync(jd, place);
  const rise = riseData.jd; // Local-time-encoded JD

  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const longitudes: number[] = [];
  for (const t of offsets) {
    longitudes.push(await lunarLongitudeAsync(rise + t));
  }

  // Moon's longitude at jd (Python uses jd directly, V4.4.0 changed from jd_ut to jd)
  const nirayana = await lunarLongitudeAsync(jd);
  const raasiNo = Math.floor(nirayana / 30) + 1;
  const fracLeft = 1.0 - (nirayana / 30) % 1;

  // 3. Find end time by 5-point inverse Lagrange interpolation
  const y = unwrapAngles(longitudes);
  const approxEnd = inverseLagrange(offsets, y, raasiNo * 30);
  const ends = (rise - jdUtc + approxEnd) * 24 + tz;
  const answer: number[] = [raasiNo, ends, fracLeft];

  // 4. Check for skipped raasi
  const raasiTmrw = Math.ceil(longitudes[longitudes.length - 1]! / 30);
  const fracLeftTmrw = 1.0 - (longitudes[longitudes.length - 1]! / 30) % 1;
  const isSkipped = ((raasiTmrw - raasiNo) % 12 + 12) % 12 > 1;
  if (isSkipped) {
    const leapRaasi = raasiNo + 1;
    const leapApproxEnd = inverseLagrange(offsets, y, leapRaasi * 30);
    const leapEnds = (rise + 1 - jdUtc + leapApproxEnd) * 24 + tz;
    const finalRaasi = raasiNo === 12 ? 1 : leapRaasi;
    answer.push(finalRaasi, leapEnds, fracLeftTmrw);
  }

  return answer;
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
  // Use Sun as ascendant proxy until sync ascendant calculation is implemented
  const ascLong = getPlanetLongitude(jd, place, SUN);
  return sreeLagnaFromLongitudes(moonLong, ascLong);
}

/**
 * Calculate Hora Lagna (special ascendant with rate factor 0.5)
 * Formula: sun_longitude_at_sunrise + (time_since_sunrise_in_minutes * 0.5)
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @returns [rasi (0-11), longitude within rasi]
 */
export function getHoraLagna(jd: number, place: Place): [number, number] {
  // Get time of birth in hours from JD
  const { time } = julianDayToGregorian(jd);
  const timeOfBirthInHours = time.hour + time.minute / 60 + time.second / 3600;

  // Get sunrise time in hours
  const sunriseData = sunrise(jd, place);
  const sunRiseHours = sunriseData.localTime;

  // Time elapsed since sunrise in minutes
  const timeDiffMins = (timeOfBirthInHours - sunRiseHours) * 60;

  // Get sun's sidereal longitude at sunrise
  const sunriseJdUtc = toUtc(sunriseData.jd, place.timezone);
  const sunLong = solarLongitude(sunriseJdUtc);

  // Hora Lagna = sun_longitude + (elapsed_minutes * 0.5), normalized to 0-360
  const horaLong = normalizeDegrees(sunLong + (timeDiffMins * 0.5));
  const rasi = Math.floor(horaLong / 30);
  const longitude = horaLong % 30;
  return [rasi, longitude];
}

// ============================================================================
// UTILITY EXPORTS
// ============================================================================

// ============================================================================
// PURE CALCULATION FUNCTIONS (No Swiss Ephemeris dependency)
// ============================================================================

/**
 * Ahargana - days elapsed since Mahabharata epoch (Kali Yuga start).
 * Python: ahargana = lambda jd: jd - const.mahabharatha_tithi_julian_day
 *
 * @param jd - Julian day number
 * @returns Number of days since epoch
 */
export function ahargana(jd: number): number {
  return jd - MAHABHARATHA_TITHI_JULIAN_DAY;
}

/**
 * Kali Ahargana days - integer days since Kali Yuga start.
 *
 * @param jd - Julian day number
 * @returns Integer days
 */
export function kaliAharganaDays(jd: number): number {
  return Math.floor(ahargana(jd));
}

/**
 * Calculate elapsed year indices for Indian eras.
 * Returns Kali year, Vikrama year, and Saka year numbers.
 *
 * Python: elapsed_year(jd, maasa_index)
 *
 * @param jd - Julian day number
 * @param maasaIndex - Lunar month index (1-12)
 * @returns [kaliYear, vikramaYear, sakaYear]
 */
export function elapsedYear(jd: number, maasaIndex: number): [number, number, number] {
  const ahar = ahargana(jd);
  const kali = Math.floor((ahar + (4 - maasaIndex) * 30) / SIDEREAL_YEAR);
  const saka = kali - 3179;
  const vikrama = saka + 135;
  return [kali, vikrama, saka];
}

/**
 * Calculate ritu (season) from lunar month index.
 * Python: ritu(maasa_index)
 *
 * @param maasaIndex - Lunar month index (1-12)
 * @returns Ritu index: 0=Vasanta, 1=Greeshma, 2=Varsha, 3=Sharath, 4=Hemantha, 5=Shishira
 */
export function ritu(maasaIndex: number): number {
  return Math.floor((maasaIndex - 1) / 2);
}

/**
 * Cyclic count of stars including Abhijit (28 stars).
 * Python: utils.cyclic_count_of_stars_with_abhijit
 *
 * @param fromStar - Starting star (1-based)
 * @param count - Number of steps
 * @param direction - 1 for forward, -1 for backward
 * @param starCount - Total number of stars (28 with Abhijit, 27 without)
 * @returns Star number (1-based)
 */
export function cyclicCountOfStarsWithAbhijit(
  fromStar: number,
  count: number,
  direction: number = 1,
  starCount: number = 28
): number {
  return ((fromStar - 1 + (count - 1) * direction) % starCount + starCount) % starCount + 1;
}

/**
 * Cyclic count of stars without Abhijit (27 stars).
 * Python: utils.cyclic_count_of_stars
 */
export function cyclicCountOfStars(
  fromStar: number,
  count: number,
  direction: number = 1
): number {
  return cyclicCountOfStarsWithAbhijit(fromStar, count, direction, 27);
}

// ============================================================================
// SPECIAL LAGNAS
// ============================================================================

/**
 * Compute Indu Lagna (BV Raman method).
 * Uses IL_FACTORS for 9th lord from Asc and 9th lord from Moon,
 * sums modulo 12, then offsets from Moon's house.
 * @param planetPositions - D1 (or varga) planet positions; index 0 = Lagna, index 2 = Moon
 * @returns [rasiNumber, longitudeInRasi]
 */
export function getInduLagna(
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): [number, number] {
  const moonPos = planetPositions[2]!;
  const ascPos = planetPositions[0]!;
  const moonHouse = moonPos.rasi;
  const ascHouse = ascPos.rasi;

  const ninthLord = HOUSE_OWNERS[(ascHouse + 8) % 12]!;
  const ninthLordFromMoon = HOUSE_OWNERS[(moonHouse + 8) % 12]!;

  let il = (IL_FACTORS[ninthLord]! + IL_FACTORS[ninthLordFromMoon]!) % 12;
  if (il === 0) il = 12;

  const induRasi = (moonHouse + il - 1) % 12;
  return [induRasi, moonPos.longitude];
}

/**
 * Compute Bhrigu Bindhu Lagna.
 * Midpoint of Moon and Rahu absolute longitudes.
 * @param planetPositions - D1 (or varga) planet positions; index 2 = Moon, index 8 = Rahu
 * @returns [rasiNumber, longitudeInRasi]
 */
export function getBhriguBindhu(
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>
): [number, number] {
  const moonPos = planetPositions[2]!;
  const rahuPos = planetPositions[8]!;

  const moonLong = moonPos.rasi * 30 + moonPos.longitude;
  const rahuLong = rahuPos.rasi * 30 + rahuPos.longitude;

  const moonAdd = moonLong > rahuLong ? 0 : 360;
  const bb = ((rahuLong + moonLong + moonAdd) * 0.5) % 360;

  const rasi = Math.floor(bb / 30) % 12;
  const longInRasi = bb % 30;
  return [rasi, longInRasi];
}

// ============================================================================
// LUNAR PHASE & MOON EVENTS — Phase 4
// ============================================================================

/**
 * Calculate lunar phase (moon - sun longitude difference).
 * Python: lunar_phase(jd, tithi_index=1)
 *
 * NOTE: Python uses `solar_longitude(jd)` and `lunar_longitude(jd)` which
 * call `sidereal_longitude(jd, planet)` — these use the JD directly as UTC.
 *
 * @param jd - Julian Day Number (treated as UTC by the underlying SWE call)
 * @returns Lunar phase angle in degrees (0-360)
 */
export async function lunarPhaseAsync(jd: number): Promise<number> {
  const sunLong = await solarLongitudeAsync(jd);
  const moonLong = await lunarLongitudeAsync(jd);
  return ((moonLong - sunLong) % 360 + 360) % 360;
}

/**
 * Sync version of lunar phase.
 */
export function lunarPhase(jd: number): number {
  const sunLong = solarLongitude(jd);
  const moonLong = lunarLongitude(jd);
  return ((moonLong - sunLong) % 360 + 360) % 360;
}

/**
 * Find JD of new moon (lunar phase = 360°).
 * Python: new_moon(jd, tithi_, opt=-1)
 *
 * @param jd - Julian Day Number
 * @param tithi_ - Current tithi number (1-30)
 * @param opt - -1 for previous new moon, +1 for next new moon
 * @returns Julian Day Number of the new moon
 */
export async function newMoonAsync(
  jd: number,
  tithi_: number,
  opt: -1 | 1 = -1
): Promise<number> {
  let start: number;
  if (opt === -1) {
    start = jd - tithi_;        // previous new moon
  } else {
    start = jd + (30 - tithi_); // next new moon
  }

  // Search within a span of (start ± 2) days with 17 sample points
  const x: number[] = [];
  for (let offset = 0; offset < 17; offset++) {
    x.push(-2 + offset / 4);
  }

  const y: number[] = [];
  for (const xi of x) {
    y.push(await lunarPhaseAsync(start + xi));
  }

  const yUnwrapped = unwrapAngles(y);
  const y0 = inverseLagrange(x, yUnwrapped, 360);
  return start + y0;
}

/**
 * Find JD of full moon (lunar phase = 180°).
 * Python: full_moon(jd, tithi_, opt=-1)
 *
 * @param jd - Julian Day Number
 * @param tithi_ - Current tithi number (1-30)
 * @param opt - -1 for previous full moon, +1 for next full moon
 * @returns Julian Day Number of the full moon
 */
export async function fullMoonAsync(
  jd: number,
  tithi_: number,
  opt: -1 | 1 = -1
): Promise<number> {
  let start: number;
  if (tithi_ <= 15) {
    start = opt === -1 ? jd - tithi_ - 15 : jd + (15 - tithi_);
  } else {
    start = opt === -1 ? jd - (tithi_ - 15) : jd + (45 - tithi_);
  }

  const x: number[] = [];
  for (let offset = 0; offset < 17; offset++) {
    x.push(-2 + offset / 4);
  }

  const y: number[] = [];
  for (const xi of x) {
    y.push(await lunarPhaseAsync(start + xi));
  }

  const yUnwrapped = unwrapAngles(y);
  const y0 = inverseLagrange(x, yUnwrapped, 180);
  return start + y0;
}

/**
 * Find the next (or previous) date when a planet enters a zodiac sign.
 * Python: next_planet_entry_date(planet, jd, place, direction=1, increment_days=0.01, precision=0.1, raasi=None)
 *
 * @param planet - Planet index (0-8, PyJHora convention)
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param direction - 1 for next entry, -1 for previous entry
 * @param raasi - Target raasi (1-12). null = next sign boundary.
 * @returns [jd, planetLongitude] - JD of entry and planet longitude at that point
 */
export async function nextPlanetEntryDateAsync(
  planet: number,
  jd: number,
  place: Place,
  direction: 1 | -1 = 1,
  raasi: number | null = null
): Promise<[number, number]> {
  // Handle Ketu by delegating to Rahu
  if (planet === 8) {
    const rahuRaasi = raasi !== null ? ((raasi - 1 + 6) % 12 + 1) : null;
    const ret = await nextPlanetEntryDateAsync(7, jd, place, direction, rahuRaasi);
    const pLong = (ret[1] + 180) % 360;
    return [ret[0], pLong];
  }

  const incrementDays = planet === 1 ? 1.0 / 24 / 60 : 0.01; // Moon: minute steps
  const precision = 0.1;

  let jdCur = jd;
  let jdUtc = jdCur - place.timezone / 24;
  let sl = await siderealLongitudeAsync(jdUtc, planet);

  // Determine target longitude
  let multiple: number;
  if (raasi === null) {
    if (planet === 7) {
      // Rahu moves retrograde
      multiple = (Math.floor(sl / 30) % 12) * 30;
      if (direction === -1) {
        multiple = ((Math.floor(sl / 30) + 1) % 12) * 30;
      }
    } else {
      multiple = ((Math.floor(sl / 30) + 1) % 12) * 30;
      if (direction === -1) {
        multiple = (Math.floor(sl / 30) % 12) * 30;
      }
    }
  } else {
    multiple = (raasi - 1) * 30;
  }

  // Iterative search until planet is within precision of target
  let iterations = 0;
  const maxIterations = 100000;
  while (iterations < maxIterations) {
    if (sl < (multiple + precision) && sl > (multiple - precision)) {
      break;
    }
    jdCur += incrementDays * direction;
    jdUtc = jdCur - place.timezone / 24;
    sl = await siderealLongitudeAsync(jdUtc, planet);
    iterations++;
  }

  // Refine with inverseLagrange using 5-point interpolation
  const { date: sankDate } = julianDayToGregorian(jdUtc);
  const sankSunrise = await sunriseAsync(jdUtc, place);
  const rise = sankSunrise.jd;

  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const planetLongs: number[] = [];
  for (const t of offsets) {
    planetLongs.push(await siderealLongitudeAsync(rise + t, planet));
  }

  const planetHour = inverseLagrange(offsets, planetLongs, multiple);
  const sankJdUtc = gregorianToJulianDay(sankDate, { hour: 0, minute: 0, second: 0 });
  let planetHour1 = (rise + planetHour - sankJdUtc) * 24 + place.timezone;
  const finalJdUtc = sankJdUtc + planetHour1 / 24;
  const finalLong = await siderealLongitudeAsync(finalJdUtc - place.timezone / 24, planet);

  return [finalJdUtc, finalLong];
}

/**
 * Detect next retrograde direction change for a planet.
 * Python: next_planet_retrograde_change_date(planet, panchanga_date, place, increment_days=1, direction=1)
 *
 * @param planet - Planet index (2-6: Mars to Saturn only)
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param direction - 1 for next change, -1 for previous change
 * @returns [jd, speedSign] where speedSign is 1 (direct) or -1 (retrograde), or null if planet doesn't retrograde
 */
export async function nextPlanetRetrogradeChangeDateAsync(
  planet: number,
  jd: number,
  place: Place,
  direction: 1 | -1 = 1
): Promise<[number, number] | null> {
  if (planet < 2 || planet > 6) return null; // Only Mars-Saturn retrograde

  const { planetSpeedInfoAsync } = await import('../ephemeris/swe-adapter');

  const getSpeedSign = async (jdCheck: number): Promise<number> => {
    const info = await planetSpeedInfoAsync(jdCheck, place, planet);
    return info.longitudeSpeed < 0 ? -1 : 1;
  };

  let jdUtc = jd - place.timezone / 24;
  let slSign = await getSpeedSign(jd);
  let slSignNext = slSign;

  // Coarse search: 1-day increments
  while (slSign === slSignNext) {
    jdUtc += 1 * direction;
    slSignNext = await getSpeedSign(jdUtc + place.timezone / 24);
  }

  // Fine search: 0.01-day (≈14.4 min) increments
  jdUtc -= 1 * direction;
  slSignNext = slSign;
  const fineIncrement = 0.01;
  while (slSign === slSignNext) {
    jdUtc += fineIncrement * direction;
    slSignNext = await getSpeedSign(jdUtc + place.timezone / 24);
  }

  jdUtc += place.timezone / 24;
  return [jdUtc, slSignNext];
}

// ============================================================================
// SPECIAL LAGNAS (Async) — Phase 5
// ============================================================================

/**
 * Calculate special ascendant (Bhava, Hora, Ghati, Vighati Lagnas) — async.
 * Python: special_ascendant(jd, place, lagna_rate_factor=1.0, divisional_chart_factor=1)
 *
 * For D1 chart: sunLong = Sun's sidereal longitude at sunrise,
 * specialLagna = sunLong + (elapsed_minutes_since_sunrise * rateFactor)
 *
 * @param jd - Julian Day Number (local time, including birth time)
 * @param place - Place data
 * @param lagnaRateFactor - Rate factor: 0.25=Bhava, 0.5=Hora, 1.25=Ghati, 15.0=Vighati
 * @returns [constellation (0-11), longitude_within_sign]
 */
export async function specialAscendantAsync(
  jd: number,
  place: Place,
  lagnaRateFactor: number = 1.0
): Promise<[number, number]> {
  const { time } = julianDayToGregorian(jd);
  const timeOfBirthInHours = time.hour + time.minute / 60 + time.second / 3600;

  const srise = await sunriseAsync(jd, place);
  const sunRiseHours = srise.localTime;
  const timeDiffMins = (timeOfBirthInHours - sunRiseHours) * 60;

  // Get Sun's position at sunrise (using local-time JD + tz for charts convention)
  const jdAtSunrise = srise.jd + place.timezone / 24;
  const jdUtcSunrise = jdAtSunrise - place.timezone / 24;
  const sunLong = await siderealLongitudeAsync(jdUtcSunrise, 0);

  const splLong = (sunLong + timeDiffMins * lagnaRateFactor) % 360;
  return dasavargaFromLong(splLong, 1);
}

/** Bhava Lagna (rate = 0.25) */
export async function bhavaLagnaAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  return specialAscendantAsync(jd, place, 0.25);
}

/** Hora Lagna (rate = 0.5) */
export async function horaLagnaAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  return specialAscendantAsync(jd, place, 0.5);
}

/** Ghati Lagna (rate = 1.25) */
export async function ghatiLagnaAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  return specialAscendantAsync(jd, place, 1.25);
}

/** Vighati Lagna (rate = 15.0) */
export async function vighatiLagnaAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  return specialAscendantAsync(jd, place, 15.0);
}

/**
 * Calculate Kunda Lagna — async.
 * Python: kunda_lagna(jd, place)
 * Formula: (ascendant_full_longitude * 81) % 360
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns [constellation (0-11), longitude_within_sign]
 */
export async function kundaLagnaAsync(
  jd: number,
  place: Place
): Promise<[number, number]> {
  const [ascConst, ascLong] = await ascendantFullAsync(jd, place);
  const al = ascConst * 30 + ascLong;
  const al1 = (al * 81) % 360;
  return dasavargaFromLong(al1, 1);
}

// ============================================================================
// PANCHANGA DISPLAY — Phase 6
// ============================================================================

/**
 * Calculate trikalam (Raahu Kaalam, Yamagandam, Gulikai Kaalam) — async.
 * Python: trikalam(jd, place, option='raahu kaalam')
 *
 * @param jd - Julian Day Number (date only, midnight)
 * @param place - Place data
 * @param option - 'raahu kaalam', 'yamagandam', or 'gulikai'
 * @returns [startTimeHours, endTimeHours] as float hours
 */
export async function trikalamAsync(
  jd: number,
  place: Place,
  option: 'raahu kaalam' | 'yamagandam' | 'gulikai' = 'raahu kaalam'
): Promise<[number, number]> {
  const srise = await sunriseAsync(jd, place);
  const sset = await sunsetAsync(jd, place);
  const dayDur = sset.localTime - srise.localTime;
  const weekday = calculateVara(jd).number;

  const offsets: Record<string, number[]> = {
    'raahu kaalam': [0.875, 0.125, 0.75, 0.5, 0.625, 0.375, 0.25],
    'gulikai':      [0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0],
    'yamagandam':   [0.5, 0.375, 0.25, 0.125, 0.0, 0.75, 0.625],
  };

  const offset = offsets[option]?.[weekday] ?? 0;
  const startTime = srise.localTime + dayDur * offset;
  const endTime = startTime + 0.125 * dayDur;

  return [startTime, endTime];
}

/**
 * Calculate Abhijit Muhurta — the auspicious mid-day period.
 * Python: abhijit_muhurta(jd, place)
 * 8th of 15 muhurtas during daytime.
 *
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns [startTimeHours, endTimeHours] as float hours
 */
export async function abhijitMuhurtaAsync(
  jd: number,
  place: Place
): Promise<[number, number]> {
  const srise = await sunriseAsync(jd, place);
  const sset = await sunsetAsync(jd, place);
  const dayDur = sset.localTime - srise.localTime;

  const startTime = srise.localTime + (7 / 15) * dayDur;
  const endTime = srise.localTime + (8 / 15) * dayDur;

  return [startTime, endTime];
}

/**
 * Calculate Durmuhurtam — inauspicious periods.
 * Python: durmuhurtam(jd, place)
 *
 * @param jd - Julian Day Number
 * @param place - Place data
 * @returns Array of [startTimeHours, endTimeHours] pairs (1 or 2 periods)
 */
export async function durmuhurtamAsync(
  jd: number,
  place: Place
): Promise<[number, number][]> {
  const srise = await sunriseAsync(jd, place);
  const sset = await sunsetAsync(jd, place);
  const dayDur = sset.localTime - srise.localTime;

  const nextSr = await sunriseAsync(jd + 1, place);
  const nightDur = 24.0 + nextSr.localTime - sset.localTime;

  const weekday = calculateVara(jd).number;

  // Offsets from sunrise (in 12ths of day duration)
  const durOffsets: [number, number][] = [
    [10.4, 0.0],  // Sunday
    [6.4, 8.8],   // Monday
    [2.4, 4.8],   // Tuesday (2nd uses night_dur)
    [5.6, 0.0],   // Wednesday
    [4.0, 8.8],   // Thursday
    [2.4, 6.4],   // Friday
    [1.6, 0.0],   // Saturday
  ];

  const answer: [number, number][] = [];
  const offPair = durOffsets[weekday]!;

  for (let i = 0; i < 2; i++) {
    const offset = offPair[i]!;
    if (offset !== 0.0) {
      const dur = (weekday === 2 && i === 1) ? nightDur : dayDur;
      const base = (weekday === 2 && i === 1) ? sset.localTime : srise.localTime;
      const startTime = base + dur * offset / 12;
      const endTime = startTime + dayDur * 0.8 / 12;
      answer.push([startTime, endTime]);
    }
  }

  return answer;
}

// ============================================================================
// ECLIPSE FUNCTIONS — Phase 7
// ============================================================================

/**
 * Check if a solar eclipse occurs on the given JD at the given location.
 * Python: is_solar_eclipse(jd, place)
 *
 * @param jd - Julian Day Number (local-time encoded)
 * @param place - Place
 * @returns attr array with eclipse properties (attr[0] = fraction covered), or null
 */
export async function isSolarEclipseAsync(
  jd: number,
  place: Place
): Promise<{ retflag: number; attr: number[] } | null> {
  const { date } = julianDayToGregorian(jd);
  const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });
  return solarEclipseHowAsync(jdUtc, place);
}

/**
 * Find the next solar eclipse visible at the given location.
 * Python: next_solar_eclipse(jd, place)
 *
 * @param jd - Julian Day Number (local-time encoded)
 * @param place - Place
 * @returns [retflag, tret, attr] matching Python format
 *   tret[0] = greatest eclipse, tret[1] = first contact, tret[2-4] = 2nd/3rd/4th contact
 *   attr[0] = fraction of solar diameter covered, attr[2] = obscuration
 */
export async function nextSolarEclipseAsync(
  jd: number,
  place: Place
): Promise<[number, number[], number[]]> {
  const result = await nextSolarEclipseLocAsync(jd, place, 0);
  return [result.retflag, result.tret, result.attr];
}

/**
 * Find the next lunar eclipse visible at the given location.
 * Python: next_lunar_eclipse(jd, place)
 *
 * @param jd - Julian Day Number (local-time encoded)
 * @param place - Place
 * @returns [retflag, tret, attr] matching Python format
 *   tret[0] = greatest eclipse, tret[1] = first contact, tret[2-4] = 2nd/3rd/4th contact
 *   attr[0] = fraction covered, attr[2] = obscuration
 */
export async function nextLunarEclipseAsync(
  jd: number,
  place: Place
): Promise<[number, number[], number[]]> {
  const result = await nextLunarEclipseLocAsync(jd, place, 0);
  return [result.retflag, result.tret, result.attr];
}

// ============================================================================
// BHAVA (HOUSE) CALCULATIONS — Phase 3
// ============================================================================

/**
 * Calculate dasavarga sign from absolute longitude.
 * Python: dasavarga_from_long(longitude, divisional_chart_factor=1)
 *
 * @param longitude - Absolute sidereal longitude (0-360)
 * @param divisionalChartFactor - Chart division factor (1=Rasi, 9=Navamsa, etc.)
 * @returns [constellation (0-11), longitude_within_rasi]
 */
export function dasavargaFromLong(
  longitude: number,
  divisionalChartFactor: number = 1
): [number, number] {
  const onePada = 360.0 / (12 * divisionalChartFactor);
  const oneSign = 12.0 * onePada;
  const signsElapsed = longitude / oneSign;
  const fractionLeft = signsElapsed % 1;
  let constellation = Math.floor(fractionLeft * 12);
  let longInRaasi = (longitude - constellation * 30) % 30;

  // Handle boundary: if long_in_raasi ≈ 30, wrap to 0 and advance constellation
  const oneSecondInDeg = 1.0 / 3600;
  if (Math.floor(longInRaasi + oneSecondInDeg) === 30) {
    longInRaasi = 0;
    constellation = (constellation + 1) % 12;
  }
  return [constellation, longInRaasi];
}

/**
 * Calculate planet positions for a given divisional chart (async).
 * Python: dhasavarga(jd, place, divisional_chart_factor=1)
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param divisionalChartFactor - Chart division factor
 * @returns Array of [planet_id, [rasi, longitude]] tuples
 */
export async function dhasavargaAsync(
  jd: number,
  place: Place,
  divisionalChartFactor: number = 1
): Promise<Array<[number, [number, number]]>> {
  const jdUtc = jd - place.timezone / 24;
  const positions: Array<[number, [number, number]]> = [];

  for (let p = 0; p <= 8; p++) {
    let nirayanLong: number;
    if (p === 8) {
      // Ketu = Rahu + 180
      const rahuLong = await siderealLongitudeAsync(jdUtc, 7);
      nirayanLong = normalizeDegrees(rahuLong + 180);
    } else {
      nirayanLong = await siderealLongitudeAsync(jdUtc, p);
    }
    const divisionalChart = dasavargaFromLong(nirayanLong, divisionalChartFactor);
    positions.push([p, divisionalChart]);
  }

  return positions;
}

/**
 * Bhava Madhya KP (Placidus house cusps) — async.
 * Python: bhaava_madhya_kp(jd, place)
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Array of 12 sidereal house cusp longitudes
 */
export async function bhaavaMadhyaKP(
  jd: number,
  place: Place
): Promise<number[]> {
  return houseCuspsAsync(jd, place, 'P');
}

/**
 * Bhava Madhya SWE — house cusps for any western house system.
 * Python: bhaava_madhya_swe(jd, place, house_code='P')
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param houseCode - Single-character house system code ('P', 'K', 'O', etc.)
 * @returns Array of 12 sidereal house cusp longitudes
 */
export async function bhaavaMadhyaSwe(
  jd: number,
  place: Place,
  houseCode: string = 'P'
): Promise<number[]> {
  if (!(houseCode in WESTERN_HOUSE_SYSTEMS)) {
    console.warn(`house_code should be one of WESTERN_HOUSE_SYSTEMS keys. Value 'P' assumed`);
    houseCode = 'P';
  }
  return houseCuspsAsync(jd, place, houseCode);
}

/**
 * Bhava Madhya Sripathi — Sripathi trisection of KP quadrant cusps.
 * Python: bhaava_madhya_sripathi(jd, place)
 *
 * Takes the KP (Placidus) cusps and trisects the quadrants:
 * Quadrant points: cusps[0], cusps[3], cusps[6], cusps[9], cusps[0] (wrap)
 * Intermediate cusps (1,2), (4,5), (7,8), (10,11) are evenly spaced within each quadrant.
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @returns Array of 12 sidereal house cusp longitudes
 */
export async function bhaavaMadhyaSripathi(
  jd: number,
  place: Place
): Promise<number[]> {
  const bm = await bhaavaMadhyaKP(jd, place);
  const bmf = [0, 3, 6, 9, 12]; // quadrant boundary indices

  for (let ib = 1; ib < bmf.length; ib++) {
    const bi1 = bmf[ib - 1]! % 12;
    const bi2 = bmf[ib]! % 12;
    let b1 = bm[bi1]!;
    let b2 = bm[bi2]!;
    if (b2 < b1) b2 += 360;
    const bd = Math.abs(b2 - b1) / 3.0;
    bm[(bi1 + 1) % 12] = (bm[bi1 % 12]! + bd) % 360;
    bm[(bi2 + 11) % 12] = (bm[bi2 % 12]! - bd + 360) % 360; // (bi2-1)%12
  }

  return bm;
}

/**
 * Assign planets to bhava houses based on cusp boundaries.
 * Python: _assign_planets_to_houses(planet_positions, bhava_houses, bhava_madhya_method=1)
 *
 * @param planetPositions - Array of [planet_id, [rasi, longitude]] (includes Lagna as 'L')
 * @param bhavaHouses - Array of [start, mid, end] tuples for each house
 * @param bhavaMadhyaMethod - House system method (1-5 or western code)
 * @returns Array of [rasi, [start, mid, end], planetsInHouse[]] for each house
 */
export function assignPlanetsToHouses(
  planetPositions: Array<[number | string, [number, number]]>,
  bhavaHouses: Array<[number, number, number]>,
  bhavaMadhyaMethod: number | string = 1
): Array<[number, [number, number, number], (number | string)[]]> {
  const result: Array<[number, [number, number, number], (number | string)[]]> = [];

  for (const [bhavaStart, bhavaMid, bhavaEnd0] of bhavaHouses) {
    let bhavaEnd = bhavaEnd0;
    const planetsInHouse: (number | string)[] = [];
    if (bhavaEnd < bhavaStart) bhavaEnd += 360;

    for (const [p, [h, long]] of planetPositions) {
      const pLong = h * 30 + long;
      if (
        (pLong >= bhavaStart && pLong < bhavaEnd) ||
        (pLong + 360 >= bhavaStart && pLong + 360 < bhavaEnd)
      ) {
        planetsInHouse.push(p);
      }
    }

    let houseRasi: number;
    if (bhavaMadhyaMethod === 1 || bhavaMadhyaMethod === 5) {
      // Rasi based on bhava cusp (mid)
      houseRasi = Math.floor(bhavaMid / 30);
    } else if (bhavaMadhyaMethod === 2) {
      // Rasi based on bhava start
      houseRasi = Math.floor(bhavaStart / 30);
    } else {
      // Sripati / KP / Western: rasi based on bhava start, mod 360 applied to tuple
      houseRasi = Math.floor(bhavaStart / 30);
    }

    if (bhavaMadhyaMethod === 3 || bhavaMadhyaMethod === 4 ||
        typeof bhavaMadhyaMethod === 'string') {
      result.push([
        houseRasi,
        [bhavaStart % 360, bhavaMid % 360, bhavaEnd % 360],
        planetsInHouse,
      ]);
    } else {
      result.push([houseRasi, [bhavaStart, bhavaMid, bhavaEnd], planetsInHouse]);
    }
  }

  return result;
}

/**
 * Unified bhava madhya calculation supporting all 5 Indian + Western house systems.
 * Python: _bhaava_madhya_new(jd, place, bhava_madhya_method=1)
 *
 * @param jd - Julian Day Number (local time)
 * @param place - Place data
 * @param bhavaMadhyaMethod - House system method:
 *   1 = Equal Housing (Lagna in middle)
 *   2 = Equal Housing (Lagna as start)
 *   3 = Sripathi
 *   4 = KP (Placidus)
 *   5 = Each Rasi is the house
 *   'P','K','O','R','C','A','V','X','H','T','B','M' = Western systems
 * @returns Array of [rasi, [start, mid, end], planetsInHouse[]] for each house
 */
export async function bhaavaMadhyaNew(
  jd: number,
  place: Place,
  bhavaMadhyaMethod: number | string = BHAAVA_MADHYA_METHOD
): Promise<Array<[number, [number, number, number], (number | string)[]]>> {
  if (!(bhavaMadhyaMethod in AVAILABLE_HOUSE_SYSTEMS)) {
    console.warn('bhava_madhya_method should be one of AVAILABLE_HOUSE_SYSTEMS keys. Value 1 assumed');
    bhavaMadhyaMethod = 1;
  }

  // Get ascendant
  const [ascConstellation, ascLongitude, , ] = await ascendantFullAsync(jd, place);
  const ascFullLong = (ascConstellation * 30 + ascLongitude) % 360;

  // Get planet positions (D1)
  const planetPositionsRaw = await dhasavargaAsync(jd, place, 1);
  // Prepend Lagna (ascendant)
  const planetPositions: Array<[number | string, [number, number]]> = [
    [ASCENDANT_SYMBOL, [ascConstellation, ascLongitude]],
    ...planetPositionsRaw,
  ];

  const bhavaHouses: Array<[number, number, number]> = [];

  if (bhavaMadhyaMethod === 1) {
    // Equal Housing — Lagna in the middle
    let bhavaMid = ascFullLong;
    for (let h = 0; h < 12; h++) {
      const bhavaStart = (bhavaMid - 15.0 + 360) % 360;
      const bhavaEnd = (bhavaMid + 15.0) % 360;
      bhavaHouses.push([bhavaStart, bhavaMid, bhavaEnd]);
      bhavaMid = normalizeDegrees(bhavaMid + 30);
    }
  } else if (bhavaMadhyaMethod === 2) {
    // Equal Housing — Lagna as start
    let bhavaMidStart = ascFullLong;
    for (let h = 0; h < 12; h++) {
      const bhavaStart = bhavaMidStart;
      const bhavaMid = (bhavaStart + 15.0) % 360;
      const bhavaEnd = (bhavaMid + 15.0) % 360;
      bhavaHouses.push([bhavaStart, bhavaMid, bhavaEnd]);
      bhavaMidStart = normalizeDegrees(bhavaStart + 30);
    }
  } else if (bhavaMadhyaMethod === 3) {
    // Sripathi
    const bm = await bhaavaMadhyaSripathi(jd, place);
    const bmExt = [...bm, bm[0]!];
    for (let h = 0; h < 12; h++) {
      const bhavaStart = bmExt[h]!;
      const bhavaMid = 0.5 * (bmExt[h]! + bmExt[h + 1]!);
      const bhavaEnd = bmExt[h + 1]!;
      bhavaHouses.push([bhavaStart % 360, bhavaMid % 360, bhavaEnd % 360]);
    }
  } else if (bhavaMadhyaMethod === 4 || typeof bhavaMadhyaMethod === 'string') {
    // KP or Western house systems
    const bm = bhavaMadhyaMethod === 4
      ? await bhaavaMadhyaKP(jd, place)
      : await bhaavaMadhyaSwe(jd, place, bhavaMadhyaMethod as string);
    const bmExt = [...bm, bm[0]!];
    for (let h = 0; h < 12; h++) {
      let bmh = bmExt[h]!;
      let bmh1 = bmExt[h + 1]!;
      if (bmh1 < bmh) bmh1 += 360;
      const bhavaStart = bmh;
      const bhavaMid = 0.5 * (bmh + bmh1);
      const bhavaEnd = bmh1;
      bhavaHouses.push([bhavaStart % 360, bhavaMid % 360, bhavaEnd % 360]);
    }
  } else if (bhavaMadhyaMethod === 5) {
    // Each Rasi is the house
    for (let h = 0; h < 12; h++) {
      const h1 = (h + ascConstellation) % 12;
      const bhavaStart = h1 * 30;
      const bhavaMid = bhavaStart + ascLongitude;
      const bhavaEnd = ((h1 + 1) % 12) * 30;
      bhavaHouses.push([bhavaStart % 360, bhavaMid % 360, bhavaEnd % 360]);
    }
  }

  return assignPlanetsToHouses(planetPositions, bhavaHouses, bhavaMadhyaMethod);
}

// ============================================================================
// PLANET SPEED & RETROGRADE
// ============================================================================

/**
 * Lunar daily motion (sync).
 * Python: _lunar_daily_motion(jd)
 */
export function lunarDailyMotion(jd: number): number {
  const today = lunarLongitude(jd);
  let tomorrow = lunarLongitude(jd + 1);
  if (tomorrow < today) tomorrow += 360;
  return tomorrow - today;
}

/**
 * Solar daily motion (sync).
 * Python: _solar_daily_motion(jd)
 */
export function solarDailyMotion(jd: number): number {
  const today = solarLongitude(jd);
  let tomorrow = solarLongitude(jd + 1);
  if (tomorrow < today) tomorrow += 360;
  return tomorrow - today;
}

/** Planets in retrograde (sync). Python: planets_in_retrograde(jd, place) */
export const planetsInRetrograde = _planetsInRetrograde;
/** Planets in retrograde (async). */
export const planetsInRetrogradeAsync = _planetsInRetrogradeAsync;
/** Planet speed info (sync). Python: _planet_speed_info(jd, place, planet) */
export const planetSpeedInfo = _planetSpeedInfo;
/** Planet speed info (async). */
export const planetSpeedInfoAsync = _planetSpeedInfoAsync;

/**
 * Daily Moon speed.
 * Python: daily_moon_speed(jd, place)
 */
export function dailyMoonSpeed(jd: number, place: Place): number {
  return _planetSpeedInfo(jd, place, MOON).longitudeSpeed;
}

/**
 * Daily Sun speed.
 * Python: daily_sun_speed(jd, place)
 */
export function dailySunSpeed(jd: number, place: Place): number {
  return _planetSpeedInfo(jd, place, SUN).longitudeSpeed;
}

/**
 * Daily speed of any planet.
 * Python: daily_planet_speed(jd, place, planet)
 */
export function dailyPlanetSpeed(jd: number, place: Place, planet: number): number {
  return _planetSpeedInfo(jd, place, planet).longitudeSpeed;
}

/**
 * All planets speed info (sync).
 * Python: planets_speed_info(jd, place)
 */
export function planetsSpeedInfo(jd: number, place: Place): Record<number, number[]> {
  const result: Record<number, number[]> = {};
  const planets = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU];
  for (const p of planets) {
    if (p === KETU) {
      result[p] = result[RAHU]!.slice();
      continue;
    }
    const info = _planetSpeedInfo(jd, place, p);
    result[p] = [info.longitude, info.latitude, info.distance, info.longitudeSpeed, info.latitudeSpeed, info.distanceSpeed];
  }
  return result;
}

/**
 * Planets in Graha Yudh (planetary war).
 * Python: planets_in_graha_yudh(jd, place)
 */
export function planetsInGrahaYudh(jd: number, place: Place): Array<[number, number, number]> {
  const psi = planetsSpeedInfo(jd, place);
  const longLatList: Array<[number, number]> = [];
  for (const p of [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU]) {
    const info = psi[p]!;
    longLatList.push([info[0]!, info[1]!]);
  }

  const result: Array<[number, number, number]> = [];
  const n = longLatList.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const [long1, lat1] = longLatList[i]!;
      const [long2, lat2] = longLatList[j]!;
      if (long1 === long2) {
        if (lat1 === lat2) {
          result.push([i, j, 0]); // Bhed-yuti
        } else {
          const latDist = Math.abs(lat2 - lat1);
          if (lat1 * lat2 > 0 && latDist * 3600 <= GRAHA_YUDH_CRITERIA_1) {
            result.push([i, j, 1]); // Ullekh-yuti
          } else if (lat1 * lat2 > 0 && latDist <= GRAHA_YUDH_CRITERIA_2) {
            result.push([i, j, 2]); // Apsavya-yuti
          } else if (latDist <= GRAHA_YUDH_CRITERIA_3) {
            result.push([i, j, 3]); // Anshumard-yuti
          }
        }
      }
    }
  }
  return result;
}

// ============================================================================
// VAARA (WEEKDAY) - sync
// ============================================================================

/**
 * Vaara/weekday using ahargana.
 * Python: vaara(jd)
 */
export function vaara(jd: number): number {
  if (USE_AHARGHANA_FOR_VAARA_CALCULATION) {
    return (kaliAharganaDays(jd) % 7 + 5) % 7;
  }
  return Math.ceil(jd + 1) % 7;
}

// ============================================================================
// LUNAR MONTH & VEDIC DATE
// ============================================================================

/**
 * Lunar year index (samvatsara index from Kali year).
 * Python: lunar_year_index(jd, maasa_index)
 */
export function lunarYearIndex(jd: number, maasaIndex: number): number {
  let kali = elapsedYear(jd, maasaIndex)[0];
  const kaliBase = 14;
  let kaliStart = KALI_START_YEAR;
  if (kali < 4009 && FORCE_KALI_START_YEAR_FOR_YEARS_BEFORE_KALI_YEAR_4009) {
    kaliStart = KALI_START_YEAR;
  }
  if (kali >= 4009) kali = (kali - kaliBase) % 60;
  const samvatIndex = (kali + kaliStart + Math.floor((kali * 211 - 108) / 18000)) % 60;
  return samvatIndex - 1;
}

// ============================================================================
// DECLINATION OF PLANETS
// ============================================================================

/**
 * Declination of planets (Sun to Saturn).
 * Python: declination_of_planets(jd, place)
 */
export function declinationOfPlanets(jd: number, place: Place): number[] {
  const ayaVal = getAyanamsaValue(jd);
  const pp = getAllPlanetPositionsSync(jd, place).slice(0, 7);
  const bhujas: number[] = new Array(7).fill(0);
  const northSouthSign: number[] = new Array(7).fill(1);

  for (let p = 0; p < 7; p++) {
    const [h, long] = pp[p]!;
    const pLong = h * 30 + long + ayaVal;
    if (pLong >= 0 && pLong < 180) {
      northSouthSign[p] = [0, 2, 4, 5].includes(p) ? 1 : -1;
    } else {
      northSouthSign[p] = [1, 6].includes(p) ? 1 : -1;
    }
    bhujas[p] = pLong % 360;
    if (pLong > 90 && pLong < 180) bhujas[p] = 180 - pLong;
    else if (pLong > 180 && pLong < 270) bhujas[p] = pLong - 180;
    else if (pLong > 270 && pLong < 360) bhujas[p] = 360 - pLong;
    bhujas[p] = Math.round(bhujas[p]! * 100) / 100;
  }
  northSouthSign[3] = 1; // Mercury always North

  const bd = [0, 362 / 60, 703 / 60, 1002 / 60, 1238 / 60, 1388 / 60, 1440 / 60];
  const bx = [0, 15, 30, 45, 60, 75, 90];

  const declinations: number[] = [];
  for (let p = 0; p < 7; p++) {
    declinations.push(northSouthSign[p]! * inverseLagrange(bd, bx, bhujas[p]!));
  }
  return declinations;
}

// Helper to get all planet positions sync (rasi, longitude pairs)
function getAllPlanetPositionsSync(jd: number, place: Place): Array<[number, number]> {
  const jdUtc = jd - place.timezone / 24;
  const result: Array<[number, number]> = [];
  const planets = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU];
  for (const p of planets) {
    let long: number;
    if (p === KETU) {
      long = ketuFromRahu(siderealLongitude(jdUtc, SWE_PLANETS.RAHU));
    } else {
      const sweP = p <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p]! : SWE_PLANETS.RAHU;
      long = siderealLongitude(jdUtc, sweP);
    }
    const rasi = Math.floor(long / 30);
    const longInSign = long % 30;
    result.push([rasi, longInSign]);
  }
  return result;
}

// ============================================================================
// SOLAR UPAGRAHA LONGITUDES (already partially done in charts.ts, but adding to drik too)
// ============================================================================

/** Dhuma longitude from Sun longitude */
export function dhumaLongitude(sunLong: number): number {
  return (sunLong + 133 + 20 / 60) % 360;
}

/** Vyatipaata longitude */
export function vyatipaataLongitude(sunLong: number): number {
  return (360 - dhumaLongitude(sunLong)) % 360;
}

/** Parivesha longitude */
export function pariveshaLongitude(sunLong: number): number {
  return (vyatipaataLongitude(sunLong) + 180) % 360;
}

/** Indrachaapa longitude */
export function indrachaapLongitude(sunLong: number): number {
  return (360 - pariveshaLongitude(sunLong)) % 360;
}

/** Upaketu longitude */
export function upaketuLongitude(sunLong: number): number {
  return (sunLong - 30) % 360;
}

/**
 * Solar upagraha longitudes.
 * Python: solar_upagraha_longitudes(solar_longitude, upagraha, divisional_chart_factor)
 */
export function solarUpagrahaLongitudes(
  solarLong: number,
  upagraha: string,
  divisionalChartFactor: number = 1
): [number, number] | undefined {
  const upagrahaFns: Record<string, (sl: number) => number> = {
    dhuma: dhumaLongitude,
    vyatipaata: vyatipaataLongitude,
    parivesha: pariveshaLongitude,
    indrachaapa: indrachaapLongitude,
    upaketu: upaketuLongitude,
  };
  const fn = upagrahaFns[upagraha.toLowerCase()];
  if (!fn) return undefined;
  const long = fn(solarLong);
  return dasavargaFromLong(long, divisionalChartFactor);
}

// ============================================================================
// UPAGRAHA LONGITUDE (Gulika, Maandi, Kaala, Mrityu, etc.)
// ============================================================================

/**
 * Upagraha longitude calculation.
 * Python: upagraha_longitude(dob, tob, place, planet_index, ...)
 *
 * @param jd - Julian day for the date
 * @param place - Place
 * @param planetIndex - 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn
 * @param upagrahaPartMiddle - true for 'middle', false for 'begin'
 * @returns [constellation, longitude_in_sign]
 */
export function upagrahaLongitude(
  jd: number, place: Place, tobHours: number,
  planetIndex: number, upagrahaPartMiddle: boolean = true
): [number, number] {
  const dayNumber = vaara(jd);
  const sr = sunrise(jd, place);
  const ss = sunset(jd, place);
  let srise = sr.localTime;
  let sset = ss.localTime;

  let planetPart: number;
  if (tobHours < srise) {
    // Night: previous day sunset to today's sunrise
    const prevSs = sunset(jd - 1, place);
    sset = prevSs.localTime;
    planetPart = DAY_RULERS[dayNumber]!.indexOf(planetIndex);
    // Use night rulers
    planetPart = NIGHT_RULERS[dayNumber]!.indexOf(planetIndex);
  } else if (tobHours > sset) {
    // Night: today's sunset to next sunrise
    const nextSr = sunrise(jd + 1, place);
    srise = nextSr.localTime;
    planetPart = NIGHT_RULERS[dayNumber]!.indexOf(planetIndex);
  } else {
    planetPart = DAY_RULERS[dayNumber]!.indexOf(planetIndex);
  }

  if (planetPart === -1) return [0, 0]; // Planet not found in rulers

  const dayDur = Math.abs(sset - srise);
  const onePart = dayDur / 8;
  const planetStartTime = srise + planetPart * onePart;

  let jdKaala: number;
  if (upagrahaPartMiddle) {
    const planetEndTime = srise + (planetPart + 1) * onePart;
    const planetMiddleTime = 0.5 * (planetStartTime + planetEndTime);
    jdKaala = gregorianToJulianDay(
      julianDayToGregorian(jd).date,
      { hour: Math.floor(planetMiddleTime), minute: Math.floor((planetMiddleTime % 1) * 60), second: 0 }
    );
  } else {
    jdKaala = gregorianToJulianDay(
      julianDayToGregorian(jd).date,
      { hour: Math.floor(planetStartTime), minute: Math.floor((planetStartTime % 1) * 60), second: 0 }
    );
  }

  // For upagraha, we need the lagna (ascendant) at the specific time.
  // Sync version uses Sun as a rough proxy since we don't have sync ascendant.
  const jdUtc = jdKaala - place.timezone / 24;
  const upagrahaLong = solarLongitude(jdUtc);
  return dasavargaFromLong(normalizeDegrees(upagrahaLong), 1);
}

/**
 * Async version of upagraha longitude (accurate, uses async ascendant).
 */
export async function upagrahaLongitudeAsync(
  jd: number, place: Place, tobHours: number,
  planetIndex: number, upagrahaPartMiddle: boolean = true
): Promise<[number, number]> {
  const dayNumber = vaara(jd);
  const sr = await sunriseAsync(jd, place);
  const ss = await sunsetAsync(jd, place);
  let srise = sr.localTime;
  let sset = ss.localTime;

  let planetPart: number;
  if (tobHours < srise) {
    const prevSs = await sunsetAsync(jd - 1, place);
    sset = prevSs.localTime;
    planetPart = NIGHT_RULERS[dayNumber]!.indexOf(planetIndex);
  } else if (tobHours > sset) {
    const nextSr = await sunriseAsync(jd + 1, place);
    srise = nextSr.localTime;
    planetPart = NIGHT_RULERS[dayNumber]!.indexOf(planetIndex);
  } else {
    planetPart = DAY_RULERS[dayNumber]!.indexOf(planetIndex);
  }

  if (planetPart === -1) return [0, 0];

  const dayDur = Math.abs(sset - srise);
  const onePart = dayDur / 8;
  const planetStartTime = srise + planetPart * onePart;

  let timeForAsc: number;
  if (upagrahaPartMiddle) {
    const planetEndTime = srise + (planetPart + 1) * onePart;
    timeForAsc = 0.5 * (planetStartTime + planetEndTime);
  } else {
    timeForAsc = planetStartTime;
  }

  const { date } = julianDayToGregorian(jd);
  const jdKaala = gregorianToJulianDay(date, {
    hour: Math.floor(timeForAsc),
    minute: Math.floor((timeForAsc % 1) * 60),
    second: Math.round(((timeForAsc % 1) * 60 % 1) * 60),
  });

  const asc = await ascendantFullAsync(jdKaala, place);
  const upagrahaLong = asc.constellation * 30 + asc.longitude;
  return dasavargaFromLong(normalizeDegrees(upagrahaLong), 1);
}

/** Kaala longitude - rises at middle of Sun's part */
export async function kaalaLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, SUN, true);
}

/** Mrityu longitude - rises at middle of Mars's part */
export async function mrityuLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, MARS, true);
}

/** Artha Praharaka longitude - rises at middle of Mercury's part */
export async function arthaPraharakaLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, MERCURY, true);
}

/** Yama Ghantaka longitude - rises at middle of Jupiter's part */
export async function yamaGhantakaLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, JUPITER, true);
}

/** Gulika longitude - rises at begin of Saturn's part */
export async function gulikaLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, SATURN, false);
}

/** Maandi longitude - rises at middle of Saturn's part */
export async function maandiLongitudeAsync(
  jd: number, place: Place, tobHours: number
): Promise<[number, number]> {
  return upagrahaLongitudeAsync(jd, place, tobHours, SATURN, true);
}

// ============================================================================
// PRANAPADA LAGNA
// ============================================================================

/**
 * Pranapada Lagna (async).
 * Python: pranapada_lagna(jd, place, ...)
 */
export async function pranapadaLagnaAsync(
  jd: number, place: Place, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  // birth_long = (udhayadhi_nazhikai(jd, place)[1]*4)%12
  const sr = await sunriseAsync(jd, place);
  const { time } = julianDayToGregorian(jd);
  const tobHours = time.hour + time.minute / 60 + time.second / 3600;
  const ghatiSinceSunrise = (tobHours - sr.localTime) * 2.5; // 1 hour = 2.5 ghati
  const vighati = ghatiSinceSunrise * 60;
  const birthLong = (vighati * 4) % 12;

  // Sun longitude at birth time (not sunrise)
  const jdUtc = jd - place.timezone / 24;
  const sunLong = await solarLongitudeAsync(jdUtc);

  const pl1Base = birthLong * 30 + sunLong;
  const sl = dasavargaFromLong(sunLong, divisionalChartFactor);
  let x: number;
  if (FIXED_SIGNS.includes(sl[0])) {
    x = 240;
  } else if (DUAL_SIGNS.includes(sl[0])) {
    x = 120;
  } else {
    x = 0;
  }
  const splLong = (pl1Base + x) % 360;
  return dasavargaFromLong(splLong, divisionalChartFactor);
}

// ============================================================================
// NEXT SOLAR DATE (critical for Kaala dhasa / annual charts)
// ============================================================================

/**
 * Find the JD when Sun returns to the same longitude after N years/months.
 * Python: next_solar_date(jd_at_dob, place, years, months, sixty_hours)
 */
export async function nextSolarDateAsync(
  jdAtDob: number, place: Place, years: number = 1, months: number = 1, sixtyHours: number = 1
): Promise<number> {
  if (years === 1 && months === 1 && sixtyHours === 1) return jdAtDob;

  const dv = await dhasavargaAsync(jdAtDob, place, 1);
  const sunPos = dv[0]![1] as [number, number];
  const sunLongAtDob = sunPos[0] * 30 + sunPos[1];

  const sunLongExtra = ((years - 1) * 360 + (months - 1) * 30 + (sixtyHours - 1) * 2.5) % 360;
  const jdExtra = Math.floor(((years - 1) + (months - 1) / 12 + (sixtyHours - 1) / 144) * TROPICAL_YEAR);
  const jdNext = jdAtDob + jdExtra;
  const sunLongNext = (sunLongAtDob + sunLongExtra) % 360;

  return nextSolarJdAsync(jdNext, place, sunLongNext);
}

async function nextSolarJdAsync(jd: number, place: Place, sunLong: number): Promise<number> {
  let jdNext = jd;
  let sl = await solarLongitudeAsync(jdNext - place.timezone / 24);
  let maxIter = 400;
  while (maxIter-- > 0) {
    if (sl < sunLong + 1 && sl > sunLong) {
      jdNext -= 1;
      break;
    }
    jdNext += 1;
    sl = await solarLongitudeAsync(jdNext - place.timezone / 24);
  }

  const sr = await sunriseAsync(jdNext, place);
  const sankSunrise = sr.jd;
  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const solarLongs: number[] = [];
  for (const t of offsets) {
    solarLongs.push(await solarLongitudeAsync(sankSunrise + t));
  }
  const solarHour = inverseLagrange(offsets, solarLongs, sunLong);
  const { date } = julianDayToGregorian(jdNext);
  const sankJdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });
  const solarHour1 = (sankSunrise + solarHour - sankJdUtc) * 24 + place.timezone;
  return gregorianToJulianDay(date, {
    hour: Math.floor(solarHour1),
    minute: Math.floor((solarHour1 % 1) * 60),
    second: Math.round(((solarHour1 % 1) * 60 % 1) * 60),
  });
}

// ============================================================================
// CONJUNCTION OF PLANET PAIRS
// ============================================================================

/**
 * Find next conjunction of two planets.
 * Python: next_conjunction_of_planet_pair(jd, place, p1, p2, direction, separation_angle, ...)
 */
export async function nextConjunctionOfPlanetPairAsync(
  jd: number, place: Place, p1: number, p2: number,
  direction: number = 1, separationAngle: number = 0
): Promise<[number, number, number] | null> {
  if ((p1 === RAHU && p2 === KETU) || (p1 === KETU && p2 === RAHU)) {
    return null; // Rahu and Ketu never conjoin
  }

  const incrementSpeedFactor = 0.25;
  // Simplified version - use fixed increment
  let incrementDays = 0.25 * direction;
  const maxDaysToSearch = 100000;
  let curJd = jd;
  let searchCounter = 0;

  while (searchCounter < maxDaysToSearch) {
    curJd += incrementDays;
    const curJdUtc = curJd - place.timezone / 24;

    let p1Long: number, p2Long: number;

    if (p1 === KETU) {
      p1Long = ketuFromRahu(await siderealLongitudeAsync(curJdUtc, SWE_PLANETS.RAHU));
    } else {
      const sweP1 = p1 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p1]! : SWE_PLANETS.RAHU;
      p1Long = await siderealLongitudeAsync(curJdUtc, sweP1);
    }
    if (p2 === KETU) {
      p2Long = ketuFromRahu(await siderealLongitudeAsync(curJdUtc, SWE_PLANETS.RAHU));
    } else {
      const sweP2 = p2 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p2]! : SWE_PLANETS.RAHU;
      p2Long = await siderealLongitudeAsync(curJdUtc, sweP2);
    }

    const longDiff = (360 + p1Long - p2Long - separationAngle) % 360;
    if (longDiff < 0.5) {
      // Fine-tune with inverse Lagrange
      const jdList = Array.from({ length: 20 }, (_, i) => curJd + (i - 10) * incrementDays);
      const longDiffList: number[] = [];
      for (const jdt of jdList) {
        const jutc = jdt - place.timezone / 24;
        let pl1: number, pl2: number;
        if (p1 === KETU) {
          pl1 = ketuFromRahu(await siderealLongitudeAsync(jutc, SWE_PLANETS.RAHU));
        } else {
          const sp1 = p1 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p1]! : SWE_PLANETS.RAHU;
          pl1 = await siderealLongitudeAsync(jutc, sp1);
        }
        if (p2 === KETU) {
          pl2 = ketuFromRahu(await siderealLongitudeAsync(jutc, SWE_PLANETS.RAHU));
        } else {
          const sp2 = p2 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p2]! : SWE_PLANETS.RAHU;
          pl2 = await siderealLongitudeAsync(jutc, sp2);
        }
        longDiffList.push((360 + pl1 - pl2 - separationAngle) % 360);
      }
      try {
        const conjJd = inverseLagrange(jdList, longDiffList, 0.0);
        const cjdUtc = conjJd - place.timezone / 24;
        let fp1: number, fp2: number;
        if (p1 === KETU) fp1 = ketuFromRahu(await siderealLongitudeAsync(cjdUtc, SWE_PLANETS.RAHU));
        else {
          const sp = p1 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p1]! : SWE_PLANETS.RAHU;
          fp1 = await siderealLongitudeAsync(cjdUtc, sp);
        }
        if (p2 === KETU) fp2 = ketuFromRahu(await siderealLongitudeAsync(cjdUtc, SWE_PLANETS.RAHU));
        else {
          const sp = p2 <= 6 ? [SWE_PLANETS.SUN, SWE_PLANETS.MOON, SWE_PLANETS.MARS, SWE_PLANETS.MERCURY, SWE_PLANETS.JUPITER, SWE_PLANETS.VENUS, SWE_PLANETS.SATURN][p2]! : SWE_PLANETS.RAHU;
          fp2 = await siderealLongitudeAsync(cjdUtc, sp);
        }
        return [conjJd, normalizeDegrees(fp1), normalizeDegrees(fp2)];
      } catch {
        // Fallback
        return [curJd, normalizeDegrees(p1Long), normalizeDegrees(p2Long)];
      }
    }
    searchCounter++;
  }
  return null;
}

/** Previous conjunction */
export async function previousConjunctionOfPlanetPairAsync(
  jd: number, place: Place, p1: number, p2: number, separationAngle: number = 0
): Promise<[number, number, number] | null> {
  return nextConjunctionOfPlanetPairAsync(jd, place, p1, p2, -1, separationAngle);
}

// ============================================================================
// PREVIOUS PLANET ENTRY DATE
// ============================================================================

/**
 * Previous planet entry date (async wrapper).
 * Python: previous_planet_entry_date(planet, jd, place, ...)
 */
export async function previousPlanetEntryDateAsync(
  planet: number, jd: number, place: Place, raasi?: number
): Promise<[number, number]> {
  return nextPlanetEntryDateAsync(planet, jd, place, -1, raasi);
}

// ============================================================================
// NEXT SOLAR MONTH / YEAR (simple wrappers)
// ============================================================================

/** Next solar month (Sun enters next sign) */
export async function nextSolarMonthAsync(
  jd: number, place: Place, raasi?: number
): Promise<[number, number]> {
  return nextPlanetEntryDateAsync(SUN, jd, place, 1, raasi);
}

/** Previous solar month */
export async function previousSolarMonthAsync(
  jd: number, place: Place, raasi?: number
): Promise<[number, number]> {
  return previousPlanetEntryDateAsync(SUN, jd, place, raasi);
}

/** Next solar year (Sun enters Aries) */
export async function nextSolarYearAsync(jd: number, place: Place): Promise<[number, number]> {
  return nextPlanetEntryDateAsync(SUN, jd, place, 1, 1);
}

/** Previous solar year */
export async function previousSolarYearAsync(jd: number, place: Place): Promise<[number, number]> {
  return previousPlanetEntryDateAsync(SUN, jd, place, 1);
}

// ============================================================================
// GRAHA DREKKANA
// ============================================================================

/**
 * Graha Drekkana.
 * Python: graha_drekkana(jd, place, use_bv_raman_table)
 */
export function grahaDrekkana(jd: number, place: Place, useBvRamanTable: boolean = false): number[] {
  const pp = getAllPlanetPositionsSync(jd, place);
  const table = useBvRamanTable ? DREKKANA_TABLE_BVRAMAN : DREKKANA_TABLE;
  return pp.map(([h, long]) => table[h]![Math.floor(long / 10)]!);
}

// ============================================================================
// MUHURTHA FUNCTIONS
// ============================================================================

/**
 * Brahma Muhurtha.
 * Python: brahma_muhurtha(jd, place) -> (start, end) in float hours
 */
export async function brahmaMuhurthaAsync(jd: number, place: Place): Promise<[number, number]> {
  const dl = dayLength(jd, place);
  const nl = nightLength(jd, place);
  const nm = nl / 15;
  const sr = sunrise(jd, place).localTime;
  return [sr - 2 * nm, sr - nm];
}

/**
 * Godhuli Muhurtha.
 * Python: godhuli_muhurtha(jd, place)
 */
export async function godhuliMuhurthaAsync(jd: number, place: Place): Promise<[number, number]> {
  const dl = dayLength(jd, place);
  const nl = nightLength(jd, place);
  const dm = dl / 15;
  const nm = nl / 15;
  const ss = sunset(jd, place).localTime;
  return [ss - 0.25 * dm, ss + 0.25 * nm];
}

/**
 * Sandhya periods (3 periods).
 * Python: sandhya_periods(jd, place) -> (pratah, madhyaahna, saayam)
 */
export async function sandhyaPeriodsAsync(
  jd: number, place: Place
): Promise<[[number, number], [number, number], [number, number]]> {
  const dl = dayLength(jd, place);
  const ghati = dl / 30;
  const sr = sunrise(jd, place).localTime;
  const ss = sunset(jd, place).localTime;
  const noon = sr + 0.5 * dl;
  return [
    [sr - 2 * ghati, sr + ghati],        // Pratah
    [noon - 1.5 * ghati, noon + 1.5 * ghati], // Madhyaahna
    [ss - ghati, ss + 2 * ghati],         // Saayam
  ];
}

/**
 * Vijaya Muhurtha (day and night).
 * Python: vijaya_muhurtha(jd, place) -> (day_period, night_period)
 */
export async function vijayaMuhurthaAsync(
  jd: number, place: Place
): Promise<[[number, number], [number, number]]> {
  const dl = dayLength(jd, place);
  const gd = dl / 30;
  const nl = nightLength(jd, place);
  const gn = nl / 30;
  const sr = sunrise(jd, place).localTime;
  const ss = sunset(jd, place).localTime;
  const noon = sr + 0.5 * dl;
  const midnight = ss + 0.5 * nl;
  return [
    [noon - gd, noon + gd],
    [midnight - gn, midnight + gn],
  ];
}

/**
 * Nishita Kaala (8th muhurtha of night).
 * Python: nishita_kaala(jd, place) -> (start, end)
 */
export async function nishitaKaalaAsync(jd: number, place: Place): Promise<[number, number]> {
  const nl = nightLength(jd, place);
  const gn = nl / 30;
  const ss = sunset(jd, place).localTime;
  return [ss + 7 * gn, ss + 8 * gn];
}

/**
 * Nishita Muhurtha (2 ghatis around midnight).
 * Python: nishita_muhurtha(jd, place)
 */
export async function nishitaMuhurthaAsync(jd: number, place: Place): Promise<[number, number]> {
  const nl = nightLength(jd, place);
  const gn = nl / 30;
  const ss = sunset(jd, place).localTime;
  const midnight = ss + 0.5 * nl;
  return [midnight - gn, midnight + gn];
}

/**
 * Tamil Jaamam (10 equal divisions of day+night).
 * Python: tamil_jaamam(jd, place)
 */
export function tamilJaamam(jd: number, place: Place): Array<[number, number]> {
  const dl = dayLength(jd, place);
  const dayJaamam = dl / 5;
  const nl = nightLength(jd, place);
  const nightJaamam = nl / 5;
  const sr = sunrise(jd, place).localTime;
  const ss = sunset(jd, place).localTime;
  const jaamam: Array<[number, number]> = [];
  for (let j = 0; j < 5; j++) {
    jaamam.push([sr + j * dayJaamam, sr + (j + 1) * dayJaamam]);
  }
  for (let j = 0; j < 5; j++) {
    jaamam.push([ss + j * nightJaamam, ss + (j + 1) * nightJaamam]);
  }
  return jaamam;
}

// ============================================================================
// FRACTION MOON YET TO TRAVERSE
// ============================================================================

/**
 * Fraction of nakshatra Moon has yet to traverse.
 * Python: fraction_moon_yet_to_traverse(jd, place, round_to_digits)
 */
export function fractionMoonYetToTraverse(jd: number, place: Place, roundToDigits: number = 5): number {
  const jdUtc = jd - place.timezone / 24;
  const oneStar = 360 / 27;
  const moonLong = lunarLongitude(jdUtc);
  const [, , rem] = nakshatraPada(moonLong);
  const fraction = (oneStar - rem) / oneStar;
  return parseFloat(fraction.toFixed(roundToDigits));
}

// ============================================================================
// DISHA SHOOL
// ============================================================================

/**
 * Disha Shool for the day.
 * Python: disha_shool(jd)
 * @returns direction index: 0=North, 1=South, 2=West, 3=North (matches Python const.disha_shool_map)
 */
export function dishaShool(jd: number): number {
  return DISHA_SHOOL_MAP[vaara(jd)]!;
}

// ============================================================================
// SHIVA VAASA / AGNI VAASA
// ============================================================================

/**
 * Shiva Vaasa index.
 * Python: shiva_vaasa(jd, place, method)
 */
export function shivaVaasa(jd: number, place: Place, method: number = 2): [number, number] {
  const tit = calculateTithi(jd, place);
  const tithiIndex = tit.number;
  const tEnd = tit.endTime;

  if (method === 1) {
    const placeDict1: Record<number, number> = {
      1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7,
      8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 13: 6, 14: 7,
      16: 1, 17: 2, 18: 3, 19: 4, 20: 5, 21: 6, 22: 7,
      23: 1, 24: 2, 25: 3, 26: 4, 27: 5, 28: 6, 29: 7,
      15: 1, 30: 2,
    };
    return [placeDict1[tithiIndex] ?? 1, tEnd];
  }

  const placeDict2: Record<number, number> = { 0: 1, 1: 5, 2: 2, 3: 6, 4: 3, 5: 7, 6: 4 };
  return [placeDict2[(tithiIndex * 2 + 5) % 7] ?? 1, tEnd];
}

/**
 * Agni Vaasa index.
 * Python: agni_vaasa(jd, place)
 */
export function agniVaasa(jd: number, place: Place): [number, number] {
  const tit = calculateTithi(jd, place);
  const tithiIndex = tit.number;
  const tEnd = tit.endTime;
  const day = vaara(jd) + 1;
  const avList = [1, 2, 3, 1];
  return [avList[(tithiIndex + 1 + day) % 4]!, tEnd];
}

// ============================================================================
// NEXT TITHI
// ============================================================================

/**
 * Find the JD when a specific tithi occurs.
 * Python: next_tithi(jd, place, required_tithi, opt, start_of_tithi)
 */
export async function nextTithiAsync(
  jd: number, place: Place, requiredTithi: number, opt: number = 1, startOfTithi: boolean = true
): Promise<number> {
  const tithi_ = (await calculateTithiAsync(jd, place))[0];
  const tithiAngle = startOfTithi ? (requiredTithi - 1) * 12 : requiredTithi * 12;

  let incDays: number;
  if (tithi_ <= requiredTithi) {
    incDays = opt === -1 ? -tithi_ - requiredTithi : requiredTithi - tithi_;
  } else {
    incDays = opt === -1 ? -(tithi_ - requiredTithi) : 30 + requiredTithi - tithi_;
  }

  const start = jd + incDays;
  const x = Array.from({ length: 17 }, (_, i) => -2 + i / 4);
  const y: number[] = [];
  for (const xi of x) {
    y.push(await lunarPhaseAsync(start + xi));
  }
  const y0 = inverseLagrange(x, y, tithiAngle);
  return start + y0 + place.timezone / 24;
}

// ============================================================================
// SAHASRA CHANDRODAYAM
// ============================================================================

/**
 * 1000th full moon from birth date.
 * Python: sahasra_chandrodayam(jd, place) -> (year, month, day)
 */
export async function sahasraChandrodayamAsync(
  jd: number, place: Place
): Promise<{ year: number; month: number; day: number }> {
  let fullMoonsCount = 0;
  let tithi_ = (await calculateTithiAsync(jd, place))[0];
  let fullMoonJd = jd;
  while (fullMoonsCount < 1000) {
    fullMoonJd = await fullMoonAsync(jd, tithi_, 1);
    fullMoonsCount++;
    jd = fullMoonJd + 0.25;
    tithi_ = (await calculateTithiAsync(jd, place))[0];
  }
  const { date } = julianDayToGregorian(fullMoonJd);
  return date;
}

// ============================================================================
// VEDIC TIME CONVERSION
// ============================================================================

/**
 * Convert float hours to Vedic time (ghati, phala, vighati).
 * Python: float_hours_to_vedic_time(jd, place, float_hours, force_equal, vedic_hours_per_day)
 */
export function floatHoursToVedicTime(
  jd: number, place: Place, floatHours?: number, vedicHoursPerDay: number = 60
): [number, number, number] {
  if (![30, 60].includes(vedicHoursPerDay)) vedicHoursPerDay = 60;
  if (floatHours === undefined) {
    const { time } = julianDayToGregorian(jd);
    floatHours = time.hour + time.minute / 60 + time.second / 3600;
  }

  const todaySunrise = sunrise(jd, place).localTime;
  const tomorrowSunrise = 24 + sunrise(jd + 1, place).localTime;
  const ghatiPerHour = vedicHoursPerDay / (tomorrowSunrise - todaySunrise);
  let localHoursSinceSunrise = floatHours - todaySunrise;
  if (localHoursSinceSunrise < 0) localHoursSinceSunrise += 24;

  let totalGhati = localHoursSinceSunrise * ghatiPerHour;
  totalGhati = totalGhati % vedicHoursPerDay;

  const ghati = Math.floor(totalGhati);
  const phala = Math.floor((totalGhati - ghati) * vedicHoursPerDay);
  const vighati = Math.floor(((totalGhati - ghati) * vedicHoursPerDay - phala) * vedicHoursPerDay);

  return [ghati, phala, vighati];
}

/**
 * Convert float hours to Vedic time with equal day/night ghatis.
 * Python: float_hours_to_vedic_time_equal_day_night_ghati(...)
 */
export function floatHoursToVedicTimeEqualDayNightGhati(
  jd: number, place: Place, floatHours?: number, vedicHoursPerDay: number = 60
): [number, number, number] {
  if (![30, 60].includes(vedicHoursPerDay)) vedicHoursPerDay = 60;
  const halfVedicHour = vedicHoursPerDay / 2;

  if (floatHours === undefined) {
    const { time } = julianDayToGregorian(jd);
    floatHours = time.hour + time.minute / 60 + time.second / 3600;
  }

  const todaySunrise = sunrise(jd, place).localTime;
  const todaySunset = sunset(jd, place).localTime;
  const dl = dayLength(jd, place);
  const nl = nightLength(jd, place);
  const dayGhatiPerHour = halfVedicHour / dl;
  const nightGhatiPerHour = halfVedicHour / nl;

  let totalGhati: number;
  if (floatHours <= todaySunset && floatHours >= todaySunrise) {
    let ghatiHours = floatHours - todaySunrise;
    if (ghatiHours < 0) ghatiHours += 24;
    totalGhati = ghatiHours * dayGhatiPerHour;
  } else {
    totalGhati = floatHours >= todaySunset
      ? halfVedicHour + (floatHours - todaySunset) * nightGhatiPerHour
      : vedicHoursPerDay - (todaySunrise - floatHours) * nightGhatiPerHour;
  }

  totalGhati = totalGhati % vedicHoursPerDay;
  const ghati = Math.floor(totalGhati);
  const phala = Math.floor((totalGhati - ghati) * vedicHoursPerDay);
  const vighati = Math.floor(((totalGhati - ghati) * vedicHoursPerDay - phala) * vedicHoursPerDay);

  return [ghati, phala, vighati];
}

// ============================================================================
// CHANDRASHTAMA
// ============================================================================

/**
 * Chandrashtama rasi and next Moon entry JD.
 * Python: chandrashtama(jd, place)
 */
export async function chandrashtamaAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  const jdUtc = jd - place.timezone / 24;
  const moonLong = await lunarLongitudeAsync(jdUtc);
  const moon = dasavargaFromLong(moonLong)[0];
  const chandrashtamaRasi = (moon - 7 + 12) % 12 + 1;
  const [nextMoonJd] = await nextPlanetEntryDateAsync(MOON, jd, place, 1);
  return [chandrashtamaRasi, nextMoonJd];
}

// ============================================================================
// NEXT PANCHAKA DAYS
// ============================================================================

/**
 * Next panchaka nakshatra period.
 * Python: next_panchaka_days(jd, place)
 */
export async function nextPanchakaDaysAsync(
  jd: number, place: Place
): Promise<[number, number]> {
  const [startJd] = await nextPlanetEntryDateAsync(MOON, jd, place, 1, 11);
  const [endJd] = await nextPlanetEntryDateAsync(MOON, jd, place, 1, 1);
  return [startJd, endJd];
}

// ============================================================================
// SPECIAL TITHIS
// ============================================================================

/**
 * Special tithis (12 tithis x 3 cycles).
 * Python: special_tithis = lambda jd,place: ...
 */
export function specialTithis(jd: number, place: Place): number[][][] {
  const result: number[][][] = [];
  for (let c = 1; c <= 3; c++) {
    const cycleResult: number[][] = [];
    for (let t = 1; t <= 12; t++) {
      // Would need full tithi() with tithi_index and cycle params
      // Simplified: return tithi number for the default
      const tit = calculateTithi(jd, place);
      cycleResult.push([tit.number, tit.startTime, tit.endTime]);
    }
    result.push(cycleResult);
  }
  return result;
}

// ============================================================================
// GAURI CHOGHADIYA
// ============================================================================

/**
 * Gauri Choghadiya - North Indian time division (8 parts day + 8 parts night).
 * Python: gauri_choghadiya(jd, place)
 * @returns Array of [choghadiya_type, start_hours, end_hours]
 */
export function gauriChoghadiya(jd: number, place: Place): Array<[number, number, number]> {
  const sr = sunrise(jd, place);
  const ss = sunset(jd, place);
  const dayDur = ss.localTime - sr.localTime;
  const _vaara = vaara(jd);
  const result: Array<[number, number, number]> = [];

  // Day choghadiyas
  for (let i = 0; i < 8; i++) {
    const start = sr.localTime + i * dayDur / 8;
    const end = sr.localTime + (i + 1) * dayDur / 8;
    const gcType = GAURI_CHOGHADIYA_DAY_TABLE[_vaara]![i]!;
    result.push([gcType, start, end]);
  }

  // Night choghadiyas: sunset to next sunrise
  const nextSr = sunrise(jd + 1, place);
  const nightDur = 24 + nextSr.localTime - ss.localTime;
  for (let i = 0; i < 8; i++) {
    const start = ss.localTime + i * nightDur / 8;
    const end = ss.localTime + (i + 1) * nightDur / 8;
    const gcType = GAURI_CHOGHADIYA_NIGHT_TABLE[_vaara]![i]!;
    result.push([gcType, start, end]);
  }

  return result;
}

/**
 * Amrit Kaalam - periods where gauri choghadiya type is 3 (Amrit).
 * Python: amrit_kaalam(jd, place)
 */
export function amritKaalam(jd: number, place: Place): Array<[number, number]> {
  return gauriChoghadiya(jd, place)
    .filter(([gc]) => gc === 3)
    .map(([, start, end]) => [start, end]);
}

// ============================================================================
// SHUBHA HORA
// ============================================================================

/**
 * Shubha Hora - South Indian time division (12 parts day + 12 parts night).
 * Python: shubha_hora(jd, place)
 * @returns Array of [hora_planet, start_hours, end_hours]
 */
export function shubhaHora(jd: number, place: Place): Array<[number, number, number]> {
  const sr = sunrise(jd, place);
  const ss = sunset(jd, place);
  const dayDur = ss.localTime - sr.localTime;
  const _vaara = vaara(jd);
  const result: Array<[number, number, number]> = [];

  for (let i = 0; i < 12; i++) {
    const start = sr.localTime + i * dayDur / 12;
    const end = sr.localTime + (i + 1) * dayDur / 12;
    const gcType = SHUBHA_HORA_DAY_TABLE[i]![_vaara]!;
    result.push([gcType, start, end]);
  }

  const nextSr = sunrise(jd + 1, place);
  const nightDur = 24 + nextSr.localTime - ss.localTime;
  for (let i = 0; i < 12; i++) {
    const start = ss.localTime + i * nightDur / 12;
    const end = ss.localTime + (i + 1) * nightDur / 12;
    const gcType = SHUBHA_HORA_NIGHT_TABLE[i]![_vaara]!;
    result.push([gcType, start, end]);
  }

  return result;
}

// ============================================================================
// AMRITA GADIYA & VARJYAM
// ============================================================================

/**
 * Amrita Gadiya timing.
 * Python: amrita_gadiya(jd, place)
 * @returns [start_hours, end_hours]
 */
export function amritaGadiya(jd: number, place: Place): [number, number] {
  const nak = calculateNakshatra(jd, place);
  const nakNo = nak.number;
  const nakBeg = nak.startTime;
  const nakEnd = nak.endTime;
  const nakDurn = nakEnd - nakBeg;
  const nakFac = (AMRITA_GADIYA_VARJYAM_STAR_MAP[nakNo - 1]![0] as number) / 24;
  const agStart = nakBeg + nakFac * nakDurn;
  const agDurn = nakDurn * 1.6 / 24;
  return [agStart, agStart + agDurn];
}

/**
 * Varjyam timing.
 * Python: varjyam(jd, place)
 * @returns [start_hours, end_hours] or [start1, end1, start2, end2] for Moolam
 */
export function varjyam(jd: number, place: Place): number[] {
  const nak = calculateNakshatra(jd, place);
  const nakNo = nak.number;
  const nakBeg = nak.startTime;
  const nakEnd = nak.endTime;
  const nakDurn = nakEnd - nakBeg;
  const agDurn = nakDurn * 1.6 / 24;

  if (nakNo === 19) {
    // Moolam has two Varjyam timings
    const varjyamFactor = AMRITA_GADIYA_VARJYAM_STAR_MAP[nakNo - 1]![1] as [number, number];
    const nakFac1 = varjyamFactor[0] / 24;
    const nakFac2 = varjyamFactor[1] / 24;
    const agStart1 = nakBeg + nakFac1 * nakDurn;
    const agStart2 = nakBeg + nakFac2 * nakDurn;
    return [agStart1, agStart1 + agDurn, agStart2, agStart2 + agDurn];
  }

  const nakFac = (AMRITA_GADIYA_VARJYAM_STAR_MAP[nakNo - 1]![1] as number) / 24;
  const agStart = nakBeg + nakFac * nakDurn;
  return [agStart, agStart + agDurn];
}

// ============================================================================
// ANANDHAADHI YOGA
// ============================================================================

/**
 * Anandhaadhi Yoga index.
 * Python: anandhaadhi_yoga(jd, place)
 * @returns [yoga_index, nak_start_time]
 */
export function anandhaadhiYoga(jd: number, place: Place): [number, number] {
  const nak = calculateNakshatra(jd, place);
  const day = vaara(jd);
  const starList = ANANDHAADHI_YOGA_DAY_STAR_LIST[day]!;
  const yogaIndex = starList.indexOf(nak.number - 1);
  return [yogaIndex, nak.startTime];
}

// ============================================================================
// TRIGUNA
// ============================================================================

/**
 * Triguna of the day/time.
 * Python: triguna(jd, place)
 * @returns triguna index: 0=Sathva, 1=Rajas, 2=Thamas
 */
export function triguna(jd: number, place: Place): number {
  const { time } = julianDayToGregorian(jd);
  const fh = time.hour + time.minute / 60 + time.second / 3600;
  const day = vaara(jd);
  // Find the time boundary
  const boundaries = Object.keys(TRIGUNA_DAYS_DICT).map(Number).sort((a, b) => a - b);
  for (const boundary of boundaries) {
    if (fh <= boundary) {
      return TRIGUNA_DAYS_DICT[boundary]![day]!;
    }
  }
  return TRIGUNA_DAYS_DICT[24]![day]!;
}

// ============================================================================
// VIVAHA CHAKRA PALAN
// ============================================================================

/**
 * Vivaha Chakra Palan.
 * Python: vivaha_chakra_palan(jd, place)
 */
export function vivahChakraPalan(jd: number, place: Place): number | null {
  const jdUtc = jd - place.timezone / 24;
  const sunLong = solarLongitude(jdUtc);
  const sunStar = nakshatraPada(sunLong)[0];
  const moonLong = lunarLongitude(jdUtc);
  const moonStar = nakshatraPada(moonLong)[0];

  // Initialize 3x3 grid
  const grid: number[][] = Array.from({ length: 3 }, () => Array(3).fill(0));
  const positions: [number, number][] = [[1,2],[2,2],[2,1],[2,0],[1,0],[0,0],[0,1],[0,2]];
  const allStars = Array.from({ length: 27 }, (_, i) => (sunStar + i - 2 + 27) % 27 + 1);

  grid[1]![1] = sunStar;
  for (let i = 0; i < positions.length; i++) {
    const [r, c] = positions[i]!;
    // Each position gets 3 stars
    grid[r]![c] = allStars[3 * (i + 1)]!;
  }

  // Find moon star position
  const mapping: Record<string, number> = {
    '1,1':1,'1,2':2,'2,2':3,'2,1':4,'2,0':5,'1,0':6,'0,0':7,'0,1':8,'0,2':9,
  };

  // Simplified: find which group moon belongs to
  for (let i = 0; i < positions.length; i++) {
    const starsInGroup = allStars.slice(3 * (i + 1), 3 * (i + 2));
    if (starsInGroup.includes(moonStar)) {
      const [r, c] = positions[i]!;
      return mapping[`${r},${c}`] ?? null;
    }
  }
  if (moonStar === sunStar) return 1;
  return null;
}

// ============================================================================
// TAMIL YOGAM
// ============================================================================

/**
 * Tamil Yogam.
 * Python: tamil_yogam(jd, place, check_special_yogas, use_sringeri_panchanga_version)
 * @returns [yoga_index, nak_start, nak_end, ...optional original_yoga]
 */
export function tamilYogam(
  jd: number, place: Place,
  checkSpecialYogas: boolean = true,
  useSringeriVersion: boolean = false
): number[] {
  const panchang = useSringeriVersion ? TAMIL_BASIC_YOGA_SRINGERI_LIST : TAMIL_BASIC_YOGA_LIST;
  const nak = calculateNakshatra(jd, place);
  const naks = nak.number - 1;
  const wday = vaara(jd);
  const yi = panchang[wday]![naks]!;

  if (!checkSpecialYogas) return [yi, nak.startTime, nak.endTime];

  // Check special yogas
  const ad = [AMRITA_SIDDHA_YOGA_DICT, MRITYU_YOGA_DICT, DAGHDA_YOGA_DICT, YAMAGHATA_YOGA_DICT, UTPATA_YOGA_DICT];
  for (let idx = 0; idx < ad.length; idx++) {
    if (ad[idx]![wday] === naks) {
      return [4 + idx, nak.startTime, nak.endTime, yi];
    }
  }
  if (SARVARTHA_SIDDHA_YOGA[wday]?.includes(naks)) {
    return [TAMIL_YOGA_NAMES.length - 1, nak.startTime, nak.endTime];
  }
  return [yi, nak.startTime, nak.endTime, yi];
}

// ============================================================================
// THAARABALAM
// ============================================================================

/**
 * Thaarabalam calculation.
 * Python: thaaraabalam(jd, place, return_only_good_stars)
 */
export function thaarabalam(jd: number, place: Place, returnOnlyGoodStars: boolean = true): number[] | number[][] {
  const goodThaarabalam = [0, 2, 4, 6, 8];
  const gtb: number[] = [];
  const nak = calculateNakshatra(jd, place);
  const todaysStar = nak.number;

  const tbDict: number[][] = Array.from({ length: 9 }, () => []);
  for (let birthStar = 1; birthStar <= 27; birthStar++) {
    const tbDiv = cyclicCountOfStars(birthStar, todaysStar) % 9;
    if (returnOnlyGoodStars && goodThaarabalam.includes(tbDiv)) gtb.push(birthStar);
    tbDict[tbDiv]!.push(birthStar);
  }
  return returnOnlyGoodStars ? gtb : tbDict;
}

// ============================================================================
// MUHURTHAS (30 periods of day)
// ============================================================================

/**
 * 30 muhurthas of the day (15 day + 15 night).
 * Python: muhurthas(jd, place)
 * @returns Array of [muhurtha_name, auspicious(0/1), [start_hours, end_hours]]
 */
export function muhurthas(jd: number, place: Place): Array<[string, number, [number, number]]> {
  const dl = dayLength(jd, place);
  const dayMuhurtha = dl / 15;
  const nl = nightLength(jd, place);
  const nightMuhurtha = nl / 15;
  const sr = sunrise(jd, place).localTime;
  const ss = sunset(jd, place).localTime;

  const periods: [number, number][] = [];
  for (let j = 0; j < 15; j++) {
    periods.push([sr + j * dayMuhurtha, sr + (j + 1) * dayMuhurtha]);
  }
  for (let j = 0; j < 15; j++) {
    periods.push([ss + j * nightMuhurtha, ss + (j + 1) * nightMuhurtha]);
  }

  const muhurthaKeys = Object.keys(MUHURTHAS_OF_THE_DAY);
  return muhurthaKeys.map((name, i) => [name, MUHURTHAS_OF_THE_DAY[name]!, periods[i]!]);
}

// ============================================================================
// YOGINI VAASA
// ============================================================================

/**
 * Yogini Vaasa from tithi.
 * Python: yogini_vaasa(jd, place)
 */
export function yoginiVaasa(jd: number, place: Place): number {
  const tithiIndex = calculateTithi(jd, place).number;
  return YOGINI_VAASA_TITHI_MAP[tithiIndex - 1]!;
}

// ============================================================================
// PUSHKARA YOGA
// ============================================================================

/**
 * Pushkara Yoga (dwi/tri pushkara).
 * Python: pushkara_yoga(jd, place)
 * @returns [type, start, end] or empty array. type: 1=dwi, 2=tri
 */
export function pushkaraYoga(jd: number, place: Place): number[] {
  const tithiList = [2, 17, 7, 22, 12, 27];
  const dayList = [1, 3, 7];
  const dwiStarList = [5, 14, 23];
  const triStarList = [16, 7, 3, 11, 21, 25];

  const tit = calculateTithi(jd, place);
  const tNo = tit.number;
  const day = vaara(jd) + 1;
  const nak = calculateNakshatra(jd, place);
  const nakNo = nak.number;
  const nStart = nak.startTime;
  const srise1 = sunrise(jd, place).localTime;
  const srise2 = sunrise(jd + 1, place).localTime + 24;

  const chkd = dayList.includes(day);
  const chkt = tithiList.includes(tNo) || tithiList.includes((tNo + 29) % 30);
  if (chkd && chkt) {
    const chkn11 = dwiStarList.includes(nakNo);
    const chkn12 = dwiStarList.includes((nakNo + 26) % 27);
    if (chkn11 || chkn12) {
      return chkn11 ? [1, nStart, srise2] : [1, srise1, nStart];
    }
    const chkn21 = triStarList.includes(nakNo);
    const chkn22 = triStarList.includes((nakNo + 26) % 27);
    if (chkn21 || chkn22) {
      return chkn21 ? [2, nStart, srise2] : [2, srise1, nStart];
    }
  }
  return [];
}

// ============================================================================
// AADAL YOGA & VIDAAL YOGA
// ============================================================================

/**
 * Aadal Yoga.
 * Python: aadal_yoga(jd, place)
 * @returns [sunrise_hours, star_end] if yoga exists, else empty array
 */
export function aadalYoga(jd: number, place: Place): number[] {
  const jdUtc = jd - place.timezone / 24;
  const nak = calculateNakshatra(jd, place);
  const starEnd = nak.endTime;
  const moonStar = nakshatraPada(lunarLongitude(jdUtc))[0];
  const sunStar = nakshatraPada(solarLongitude(jdUtc))[0];
  const srise = sunrise(jd, place).localTime;
  const knt = cyclicCountOfStarsWithAbhijit(sunStar - 1, moonStar - 1);
  return [2, 7, 9, 14, 16, 21, 23, 28].includes(knt) ? [srise, starEnd] : [];
}

/**
 * Vidaal Yoga.
 * Python: vidaal_yoga(jd, place)
 */
export function vidaalYoga(jd: number, place: Place): number[] {
  const jdUtc = jd - place.timezone / 24;
  const nak = calculateNakshatra(jd, place);
  const starEnd = nak.endTime;
  const moonStar = nakshatraPada(lunarLongitude(jdUtc))[0];
  const sunStar = nakshatraPada(solarLongitude(jdUtc))[0];
  const srise = sunrise(jd, place).localTime;
  const knt = cyclicCountOfStarsWithAbhijit(sunStar - 1, moonStar - 1);
  return [3, 6, 10, 13, 17, 20, 24, 27].includes(knt) ? [srise, starEnd] : [];
}

// ============================================================================
// NAVA THAARA & SPECIAL THAARA
// ============================================================================

/**
 * Nava Thaara.
 * Python: nava_thaara(jd, place, from_lagna_or_moon)
 * @param fromLagnaOrMoon 0=from lagna, 1=from moon star
 */
export function navaThaara(jd: number, place: Place, fromLagnaOrMoon: number = 0): Array<[number, number[]]> {
  const nak = calculateNakshatra(jd, place);
  // fromLagnaOrMoon==1: use moon star. Otherwise we'd need ascendant star (approximation: use moon)
  const baseStar = nak.number - 1;
  const result: Array<[number, number[]]> = [];
  for (const [lordStr, starList] of Object.entries(NAKSHATHRA_LORDS)) {
    const lord = parseInt(lordStr);
    const mappedStars = starList.map(s => (baseStar + s) % 27);
    result.push([lord, mappedStars]);
  }
  return result;
}

/**
 * Special Thaara.
 * Python: special_thaara(jd, place, from_lagna_or_moon)
 */
export function specialThaara(jd: number, place: Place, fromLagnaOrMoon: number = 0): Array<[number, number]> {
  const nak = calculateNakshatra(jd, place);
  const baseStar = nak.number - 1;
  const baseInc = fromLagnaOrMoon === 1 ? -1 : 0;
  const stl = SPECIAL_THAARA_MAP.map(s => (baseStar + s + baseInc) % 28);

  const result: Array<[number, number]> = [];
  for (const star of stl) {
    for (const [lordStr, csl] of Object.entries(SPECIAL_THAARA_LORDS_1)) {
      if (csl.includes(star)) {
        result.push([parseInt(lordStr), star]);
        break;
      }
    }
  }
  return result;
}

// ============================================================================
// LUNAR MONTH & SAMVATSARA (async)
// ============================================================================

/**
 * Lunar month with adhika masa detection.
 * Python: lunar_month(jd, place)
 * @returns [month_index(1-12), is_leap_month, is_nija_month]
 */
export async function lunarMonthAsync(jd: number, place: Place, _depth: number = 0): Promise<[number, boolean, boolean]> {
  const ti = (await calculateTithiAsync(jd, place))[0];
  const srData = await sunriseAsync(jd, place);
  const critical = srData.jd;
  const lastNewMoon = await newMoonAsync(critical, ti, -1);
  const nextNewMoon = await newMoonAsync(critical, ti, 1);
  const thisSolarMonth = (await raasiAsync(lastNewMoon, place))[0];
  const nextSolarMonth = (await raasiAsync(nextNewMoon, place))[0];
  const isLeapMonth = thisSolarMonth === nextSolarMonth;
  const lunarMonth = (thisSolarMonth + 1) % 12;

  let isNijaMonth = false;
  if (!isLeapMonth && _depth < 1) {
    const [pm, pa] = await lunarMonthAsync(jd - 30, place, _depth + 1);
    isNijaMonth = pm === lunarMonth && pa;
  }
  return [lunarMonth, isLeapMonth, isNijaMonth];
}

/**
 * Next lunar month boundary (new moon or full moon).
 * Python: next_lunar_month(jd, place, lunar_month_type, direction)
 */
export async function nextLunarMonthAsync(
  jd: number, place: Place, lunarMonthType: number = 0, direction: number = 1
): Promise<[{ year: number; month: number; day: number }, number]> {
  if (lunarMonthType === 2) {
    // Solar month
    const [entryJd] = direction === 1
      ? await nextPlanetEntryDateAsync(SUN, jd, place, 1)
      : await previousPlanetEntryDateAsync(SUN, jd, place);
    const { date, time } = julianDayToGregorian(entryJd);
    return [date, time.hour + time.minute / 60 + time.second / 3600];
  }

  const tithiToCheck = lunarMonthType === 0 ? 30 : 15;
  const ti = (await calculateTithiAsync(jd, place))[0];
  const lmJd = lunarMonthType === 0
    ? await newMoonAsync(jd, ti, direction)
    : await fullMoonAsync(jd, ti, direction);
  const tit = await calculateTithiAsync(lmJd, place);
  let lmh = tit.number === tithiToCheck ? tit.endTime : tit.startTime;
  const { date } = julianDayToGregorian(lmJd);
  let { year: lmy, month: lmm, day: lmd } = date;

  if (lmh > 24) {
    const extraDays = Math.floor(lmh / 24);
    lmh = lmh % 24;
    const d = new Date(lmy, lmm - 1, lmd + extraDays);
    lmy = d.getFullYear(); lmm = d.getMonth() + 1; lmd = d.getDate();
  } else if (lmh < 0) {
    lmh = lmh + 24;
    const d = new Date(lmy, lmm - 1, lmd - 1);
    lmy = d.getFullYear(); lmm = d.getMonth() + 1; lmd = d.getDate();
  }
  return [{ year: lmy, month: lmm, day: lmd }, lmh];
}

/**
 * Previous lunar month boundary.
 * Python: previous_lunar_month(jd, place, lunar_month_type)
 */
export async function previousLunarMonthAsync(
  jd: number, place: Place, lunarMonthType: number = 0
): Promise<[{ year: number; month: number; day: number }, number]> {
  return nextLunarMonthAsync(jd, place, lunarMonthType, -1);
}

/**
 * Next lunar year start.
 * Python: next_lunar_year(jd, place, lunar_month_type, direction)
 */
export async function nextLunarYearAsync(
  jd: number, place: Place, lunarMonthType: number = 0, direction: number = 1
): Promise<[{ year: number; month: number; day: number }, number] | null> {
  if (lunarMonthType === 2) {
    const [entryJd] = await nextSolarYearAsync(jd, place);
    const { date, time } = julianDayToGregorian(entryJd);
    return [date, time.hour + time.minute / 60 + time.second / 3600];
  }

  let curJd = jd;
  for (let i = 0; i < 13; i++) {
    const [lmDate, lmh] = direction === 1
      ? await nextLunarMonthAsync(curJd, place, lunarMonthType)
      : await previousLunarMonthAsync(curJd, place, lunarMonthType);
    curJd = gregorianToJulianDay(lmDate, { hour: Math.floor(lmh), minute: Math.floor((lmh % 1) * 60), second: 0 });
    const lm = await lunarMonthAsync(curJd, place);
    const lunarMonthNumber = lm[0];
    if (lunarMonthNumber === 1) {
      return [lmDate, lmh];
    }
    curJd += direction * 14;
  }
  return null;
}

/**
 * Previous lunar year start.
 * Python: previous_lunar_year(jd, place, lunar_month_type)
 */
export async function previousLunarYearAsync(
  jd: number, place: Place, lunarMonthType: number = 0
): Promise<[{ year: number; month: number; day: number }, number] | null> {
  if (lunarMonthType === 2) {
    const [entryJd] = await previousSolarYearAsync(jd, place);
    const { date, time } = julianDayToGregorian(entryJd);
    return [date, time.hour + time.minute / 60 + time.second / 3600];
  }
  return nextLunarYearAsync(jd, place, lunarMonthType, -1);
}

// ============================================================================
// TAMIL SOLAR MONTH AND DATE
// ============================================================================

/**
 * Tamil solar month and date.
 * Python: tamil_solar_month_and_date(panchanga_date, place, tamil_month_method, base_time, use_utc)
 * @returns [tamil_month (0-11), day_count]
 */
export function tamilSolarMonthAndDate(
  jd: number, place: Place, baseTime: number = 0, useUtc: boolean = true
): [number, number] {
  let jdBase: number;
  if (baseTime === 0) {
    jdBase = sunset(jd, place).jd;
  } else if (baseTime === 1) {
    jdBase = sunrise(jd, place).jd;
  } else {
    // midday
    const sr = sunrise(jd, place);
    const ss = sunset(jd, place);
    jdBase = (sr.jd + ss.jd) / 2;
  }
  const jdUtc = useUtc ? jdBase - place.timezone / 24 : jdBase;
  let sr = solarLongitude(jdUtc);
  const tamilMonth = Math.floor(sr / 30);
  let daycount = 1;
  let curJd = jd;

  while (true) {
    if (sr % 30 < 1 && sr % 30 > 0) break;
    curJd -= 1;
    let jdB: number;
    if (baseTime === 0) {
      jdB = sunset(curJd, place).jd;
    } else if (baseTime === 1) {
      jdB = sunrise(curJd, place).jd;
    } else {
      const srise = sunrise(curJd, place);
      const sset = sunset(curJd, place);
      jdB = (srise.jd + sset.jd) / 2;
    }
    const ju = useUtc ? jdB - place.timezone / 24 : jdB;
    sr = solarLongitude(ju);
    daycount++;
    if (daycount > 40) break; // Safety
  }
  return [tamilMonth, daycount];
}

/**
 * Samvatsara (solar year name index).
 * Python: samvatsara(panchanga_date, place, zodiac)
 * @returns samvatsara index [0..59]
 */
export function samvatsara(jd: number, place: Place, zodiac: number = 0): number {
  // Find previous sankranti
  const [psd] = previousSankrantiDate(jd, place, zodiac);
  let year = psd.year;
  if (year > 0) year -= 1;
  return (year - 1926 + 60) % 60;
}

/**
 * Previous Sankranti Date.
 * Python: _previous_sankranti_date_new(panchanga_date, place, zodiac)
 * @returns [sankranti_date, solar_hour, tamil_month, tamil_day]
 */
export function previousSankrantiDate(
  jd: number, place: Place, zodiac?: number
): [{ year: number; month: number; day: number }, number, number, number] {
  let multiple: number;
  if (zodiac !== undefined) {
    multiple = zodiac * 30;
  } else {
    const [tMonth] = tamilSolarMonthAndDate(jd - 1, place);
    multiple = tMonth * 30;
  }

  let curJd = jd - 1;
  const ssJd = sunset(curJd, place).jd;
  let sl = solarLongitude(ssJd - place.timezone / 24);
  let sankJd = ssJd;

  // Walk backward to find sankranti
  let maxIter = 60;
  while (maxIter-- > 0) {
    const slr = sl % 30;
    if (slr < 1 && slr > 0) {
      if (zodiac === undefined) break;
      if (Math.floor(sl / 30) === zodiac) break;
    }
    sankJd -= 1;
    sl = solarLongitude(sankJd - place.timezone / 24);
  }

  const { date: sankDate } = julianDayToGregorian(sankJd);
  const srJd = sunrise(sankJd, place).jd;
  const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
  const solarLongs = offsets.map(t => solarLongitude(srJd + t) % 360);
  const solarHour = inverseLagrange(offsets, solarLongs, multiple % 360);
  const sankJdUtc = gregorianToJulianDay(sankDate, { hour: 0, minute: 0, second: 0 });
  const solarHour1 = (srJd + solarHour - sankJdUtc) * 24 + place.timezone;
  const [tMonth, tDay] = tamilSolarMonthAndDate(sankJd, place);

  return [sankDate, solarHour1, tMonth, tDay];
}

// ============================================================================
// NEXT ASCENDANT ENTRY DATE
// ============================================================================

/**
 * Next ascendant entry date.
 * Python: next_ascendant_entry_date(jd, place, direction, precision, raasi, divisional_chart_factor)
 */
export async function nextAscendantEntryDateAsync(
  jd: number, place: Place, direction: number = 1, precision: number = 1.0,
  raasi?: number, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  const incrementDays = 1.0 / 24 / 60 / divisionalChartFactor;
  let asc = await ascendantFullAsync(jd, place);
  let sl = asc.constellation * 30 + asc.longitude;

  let multiple: number;
  if (raasi === undefined) {
    multiple = direction === 1
      ? ((Math.floor(sl * divisionalChartFactor / 30) + 1) % 12) * 30
      : (Math.floor(sl * divisionalChartFactor / 30) % 12) * 30;
  } else {
    multiple = (raasi - 1) * 30;
  }

  let curJd = jd;
  let maxIter = 10000;
  while (maxIter-- > 0) {
    if (sl < multiple + precision && sl > multiple - precision) break;
    curJd += incrementDays * direction;
    asc = await ascendantFullAsync(curJd, place);
    sl = (asc.constellation * 30 + asc.longitude) * divisionalChartFactor % 360;
  }

  const offsets = Array.from({ length: 20 }, (_, i) => (i - 10) * incrementDays);
  const ascLongs: number[] = [];
  for (const t of offsets) {
    const a = await ascendantFullAsync(curJd + t, place);
    ascLongs.push((a.constellation * 30 + a.longitude) * divisionalChartFactor % 360);
  }
  const ascHour = inverseLagrange(offsets, ascLongs, multiple);
  curJd += ascHour;
  asc = await ascendantFullAsync(curJd, place);
  const ascLong = (asc.constellation * 30 + asc.longitude) * divisionalChartFactor % 360;
  return [curJd, ascLong];
}

/**
 * Previous ascendant entry date.
 * Python: previous_ascendant_entry_date(jd, place, ...)
 */
export async function previousAscendantEntryDateAsync(
  jd: number, place: Place, precision: number = 1.0,
  raasi?: number, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  return nextAscendantEntryDateAsync(jd, place, -1, precision, raasi, divisionalChartFactor);
}

// ============================================================================
// UDHAYA LAGNA MUHURTHA
// ============================================================================

/**
 * Udhaya Lagna Muhurtha - ascendant entry JD into each of 12 rasis.
 * Python: udhaya_lagna_muhurtha(jd, place)
 * @returns [(rasi, start_hours, end_hours), ...]
 */
export async function udhayaLagnaMuhurthaAsync(
  jd: number, place: Place
): Promise<Array<[number, number, number]>> {
  const asc = await ascendantFullAsync(jd, place);
  const ascRasi = asc.constellation;

  let [jdStart] = await nextAscendantEntryDateAsync(jd, place, -1);
  let curJd = jdStart + CONJUNCTION_INCREMENT;
  const ulm: Array<[number, number, number]> = [];

  for (let l = 0; l < 12; l++) {
    const [jdEnd] = await nextAscendantEntryDateAsync(curJd, place, 1);
    const { time: tStart } = julianDayToGregorian(jdStart);
    const { time: tEnd } = julianDayToGregorian(jdEnd);
    const fhs = tStart.hour + tStart.minute / 60 + tStart.second / 3600;
    const fhe = tEnd.hour + tEnd.minute / 60 + tEnd.second / 3600;
    ulm.push([(ascRasi + l) % 12, fhs, fhe]);
    jdStart = jdEnd;
    curJd = jdEnd + CONJUNCTION_INCREMENT;
  }
  return ulm;
}

// ============================================================================
// CHANDRABALAM & PANCHAKA RAHITHA
// ============================================================================

/**
 * Chandrabalam - auspicious ascendant positions relative to Moon.
 * Python: chandrabalam(jd, place)
 */
export async function chandrabalamAsync(jd: number, place: Place): Promise<number[]> {
  const ulm = await udhayaLagnaMuhurthaAsync(jd, place);
  const jdUtc = jd - place.timezone / 24;
  const moon = Math.floor(lunarLongitude(jdUtc) / 30) + 1;
  const nextSr = sunrise(jd + 1, place).localTime;
  const cbGood = [1, 3, 6, 7, 10];

  let cb: number[] = [];
  for (const [asc, , at] of ulm) {
    const count = ((moon - asc) % 12 + 12) % 12 + 1;
    if (cbGood.includes(count) && at < nextSr) {
      cb.push(asc);
    }
  }
  return cb;
}

/**
 * Panchaka Rahitha.
 * Python: panchaka_rahitha(jd, place)
 */
export async function panchakaRahithaAsync(
  jd: number, place: Place
): Promise<Array<[number, number, number]>> {
  const ulm = await udhayaLagnaMuhurthaAsync(jd, place);
  const badPanchakas = [1, 2, 4, 6, 8];
  const tithiNo = calculateTithi(jd, place).number + 1;
  const nakNo = calculateNakshatra(jd, place).number;
  const day = vaara(jd) + 1;

  const pr: Array<[number, number, number]> = [];
  for (const [asc, ascBeg, ascEnd] of ulm) {
    const ascRasi = asc + 1;
    const rem = (tithiNo + nakNo + day + ascRasi) % 9;
    if (badPanchakas.includes(rem)) {
      pr.push([rem, ascBeg, ascEnd]);
    } else {
      pr.push([0, ascBeg, ascEnd]);
    }
  }
  return pr;
}

// ============================================================================
// NEXT PLANET RETROGRADE CHANGE DATE
// (already in file but adding the non-async wrapper for completeness)
// ============================================================================

// ============================================================================
// PLANETARY POSITIONS (sync, matching Python format)
// ============================================================================

/**
 * Planetary positions matching Python format.
 * Python: planetary_positions(jd, place)
 * @returns [[planet_id, [rasi, long_in_sign]], ...]
 */
export function planetaryPositions(jd: number, place: Place): Array<[number, [number, number]]> {
  const pp = getAllPlanetPositionsSync(jd, place);
  const planets = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU];
  return planets.map((p, i) => [p, pp[i]!]);
}

// ============================================================================
// ASCENDANT (sync, matching Python format)
// ============================================================================

/**
 * Ascendant calculation (sync approximation).
 * Python: ascendant(jd, place)
 * @returns [constellation, longitude_in_sign, nakshatra, pada]
 */
export function ascendant(jd: number, place: Place): [number, number, number, number] {
  // Sync version: approximate using Sun longitude (known limitation)
  const jdUtc = jd - place.timezone / 24;
  const long = solarLongitude(jdUtc);
  const constellation = Math.floor(long / 30);
  const longInSign = long % 30;
  const [nak, pada] = nakshatraPada(long);
  return [constellation, longInSign, nak, pada];
}

// ============================================================================
// VEDIC DATE (async)
// ============================================================================

/**
 * Vedic date (solar or lunar calendar).
 * Python: vedic_date(jd, place, calendar_type, tamil_month_method, base_time, use_utc)
 * @param calendarType 0=Solar, 1=Amantha Lunar, 2=Purnimantha Lunar
 */
export async function vedicDateAsync(
  jd: number, place: Place, calendarType: number = 0,
  baseTime: number = 0, useUtc: boolean = true
): Promise<[number, number, number, boolean, boolean]> {
  if (calendarType === 0) {
    const [month, day] = tamilSolarMonthAndDate(jd, place, baseTime, useUtc);
    const year = samvatsara(jd, place, 0);
    return [month + 1, day, year, false, false];
  }
  return lunarMonthDateAsync(jd, place, calendarType === 2);
}

/**
 * Lunar month date.
 * Python: lunar_month_date(jd, place, use_purnimanta_system)
 */
export async function lunarMonthDateAsync(
  jd: number, place: Place, usePurnimantaSystem: boolean = false
): Promise<[number, number, number, boolean, boolean]> {
  const srData = await sunriseAsync(jd, place);
  const critical = srData.jd;
  const ti = (await calculateTithiAsync(critical, place))[0];
  const lastNewMoon = await newMoonAsync(critical, ti, -1);
  const nextNewMoon = await newMoonAsync(critical, ti, 1);
  const thisSolarMonth = (await raasiAsync(lastNewMoon, place))[0] - 1;
  const nextSolarMonth = (await raasiAsync(nextNewMoon, place))[0] - 1;
  const isLeapMonth = thisSolarMonth === nextSolarMonth;
  let lunarMonth = (thisSolarMonth + 1) % 12;
  let lunarDay = ((ti - 1) % 30) + 1;

  if (usePurnimantaSystem) {
    if (lunarDay > 15) lunarMonth = (lunarMonth + 1) % 12;
    lunarDay = ((lunarDay - 16 + 30) % 30) + 1;
  }

  let isNijaMonth = false;
  if (!isLeapMonth) {
    const [pm, pa] = await lunarMonthAsync(jd - 30, place);
    isNijaMonth = pm === lunarMonth && pa;
  }
  const lunarYear = lunarYearIndex(jd, lunarMonth + 1);
  return [lunarMonth + 1, lunarDay, lunarYear, isLeapMonth, isNijaMonth];
}

// ============================================================================
// NEXT ANNUAL SOLAR DATE APPROXIMATE
// ============================================================================

/**
 * Next annual solar date (approximate, no ephemeris needed).
 * Python: next_annual_solar_date_approximate(dob, tob, years)
 */
export function nextAnnualSolarDateApproximate(
  jd: number, years: number
): { weekday: number; hours: number } {
  // Simplified version - just add tropical years
  const newJd = jd + (years - 1) * TROPICAL_YEAR;
  const weekday = Math.ceil(newJd + 1) % 7;
  const { time } = julianDayToGregorian(newJd);
  return { weekday, hours: time.hour + time.minute / 60 + time.second / 3600 };
}

// ============================================================================
// SREE LAGNA (async version)
// ============================================================================

/**
 * Sree Lagna from JD (async).
 * Python: sree_lagna(jd, place, ...)
 */
export async function sreeLagnaAsync(
  jd: number, place: Place, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  const jdUtc = jd - place.timezone / 24;
  const moonLong = await lunarLongitudeAsync(jdUtc);
  const asc = await ascendantFullAsync(jd, place);
  const ascLong = asc.constellation * 30 + asc.longitude;
  return sreeLagnaFromLongitudes(moonLong, ascLong, divisionalChartFactor);
}

// ============================================================================
// INDU LAGNA (async version)
// ============================================================================

/**
 * Indu Lagna (async).
 * Python: indu_lagna(jd, place, ...)
 */
export async function induLagnaAsync(
  jd: number, place: Place, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  const positions = getAllPlanetPositionsSync(jd, place);
  const moonPos = positions[1]!;
  const moonRasi = moonPos[0];
  const ninthFromMoon = (moonRasi + 8) % 12;
  const ninthLord = HOUSE_OWNERS[ninthFromMoon]![0]!;
  const asc = await ascendantFullAsync(jd, place);
  const ascRasi = asc.constellation;
  const ninthFromAsc = (ascRasi + 8) % 12;
  const ninthLordAsc = HOUSE_OWNERS[ninthFromAsc]![0]!;

  const il9thMoon = IL_FACTORS[ninthLord] ?? 0;
  const il9thAsc = IL_FACTORS[ninthLordAsc] ?? 0;
  const ilSum = il9thMoon + il9thAsc;
  const ilRasi = (ilSum % 12 + moonRasi) % 12;
  const ilLong = ilRasi * 30 + moonPos[1];
  return dasavargaFromLong(normalizeDegrees(ilLong), divisionalChartFactor);
}

// ============================================================================
// BHRIGU BINDHU (async version)
// ============================================================================

/**
 * Bhrigu Bindhu (async).
 * Python: bhrigu_bindhu_lagna(jd, place, ...)
 */
export async function bhriguBindhuAsync(
  jd: number, place: Place, divisionalChartFactor: number = 1
): Promise<[number, number]> {
  const positions = getAllPlanetPositionsSync(jd, place);
  const moonPos = positions[1]!;
  const rahuPos = positions[7]!;
  const moonLong = moonPos[0] * 30 + moonPos[1];
  const rahuLong = rahuPos[0] * 30 + rahuPos[1];
  const bb = (moonLong + rahuLong) / 2;
  return dasavargaFromLong(normalizeDegrees(bb), divisionalChartFactor);
}

// ============================================================================
// RE-EXPORTS from swe-adapter
// ============================================================================

/** Re-export sunrise/sunset/moonrise/moonset from swe-adapter */
export {
  sunrise, sunriseAsync, sunset, sunsetAsync,
  solarLongitude, solarLongitudeAsync,
  lunarLongitude, lunarLongitudeAsync,
  siderealLongitude, siderealLongitudeAsync,
  getAyanamsaValue, setAyanamsaMode,
};
export const moonrise = _moonrise;
export const moonriseAsync = _moonriseAsync;
export const moonset = _moonset;
export const moonsetAsync = _moonsetAsync;

/** Reset ayanamsa mode to default (Lahiri) */
export function resetAyanamsaMode(): void {
  setAyanamsaMode('LAHIRI');
}

// ============================================================================
// SIMPLE UTILITY FUNCTIONS
// ============================================================================

/** navamsa_from_long = dasavarga_from_long(longitude, 9) */
export function navamsaFromLong(longitude: number): [number, number] {
  return dasavargaFromLong(longitude, 9);
}

/** Old navamsa calculation - returns just the sign index */
export function navamsaFromLongOld(longitude: number): number {
  const onePada = 360 / (12 * 9);
  const oneSign = 12 * onePada;
  const signsElapsed = longitude / oneSign;
  const fractionLeft = signsElapsed % 1;
  return Math.floor(fractionLeft * 12);
}

/** Get Rahu longitude (alias for siderealLongitude with RAHU) */
export function rahu(jd: number): number {
  const jdUtc = jd; // caller handles UTC
  return siderealLongitude(jdUtc, RAHU);
}

/** Get Ketu longitude (180 degrees from Rahu) */
export function ketu(jd: number): number {
  return normalizeDegrees(rahu(jd) + 180);
}

/** Map planet constant to Swiss Ephemeris planet index */
export function ephemerisPlanetIndex(planet: number): number {
  return SWE_PLANETS[planet] ?? planet;
}

/** raahu_kaalam — convenience wrapper for trikalamAsync */
export async function raahuKaalamAsync(jd: number, place: Place): Promise<[number, number]> {
  return trikalamAsync(jd, place, 'raahu kaalam');
}

/** yamaganda_kaalam — convenience wrapper for trikalamAsync */
export async function yamagandaKaalamAsync(jd: number, place: Place): Promise<[number, number]> {
  return trikalamAsync(jd, place, 'yamagandam');
}

/** gulikai_kaalam — convenience wrapper for trikalamAsync */
export async function gulikaiKaalamAsync(jd: number, place: Place): Promise<[number, number]> {
  return trikalamAsync(jd, place, 'gulikai');
}

/** next_sankranti_date — find next sun entry to a rasi */
export async function nextSankrantiDateAsync(
  jd: number, place: Place
): Promise<{ jd: number; rasi: number }> {
  const jdUtc = jd - place.timezone / 24;
  const sunLong = solarLongitude(jdUtc);
  const currentRasi = Math.floor(sunLong / 30);
  const nextRasi = (currentRasi + 1) % 12;
  const result = await nextPlanetEntryDateAsync(SUN, jd, place, nextRasi);
  return { jd: result, rasi: nextRasi };
}

/** days_in_tamil_month — count days remaining in current Tamil month */
export function daysInTamilMonth(jd: number, place: Place): number {
  const [, dayCount] = tamilSolarMonthAndDate(jd, place);
  const sunsetJdStart = sunset(jd, place).jd;
  let sunsetJd = sunsetJdStart;
  let sl = solarLongitude(sunsetJd - place.timezone / 24);
  let count = dayCount;
  while (true) {
    const rem = sl % 30;
    if (rem < 30 && rem > 29) break;
    sunsetJd += 1;
    sl = solarLongitude(sunsetJd - place.timezone / 24);
    count += 1;
    if (count > 35) break; // safety limit
  }
  return count;
}

// ============================================================================
// SET TROPICAL / SIDERAL PLANETS
// ============================================================================

/** Switch planet list to tropical (includes Uranus, Neptune, Pluto, excludes Rahu/Ketu) */
export function setTropicalPlanets(): void {
  // In the TS port, planet lists are managed differently per context.
  // This is a compatibility stub matching Python's set_tropical_planets().
  // The actual planet list used depends on function parameters, not global state.
}

/** Switch planet list to sidereal (default: Sun..Ketu, optionally Uranus..Pluto) */
export function setSiderealPlanets(): void {
  // Compatibility stub matching Python's set_sideral_planets().
}

// ============================================================================
// MIXED CHART LAGNA FUNCTIONS
// ============================================================================

/**
 * Build D-1 PlanetPosition[] from sync positions for charts module.
 * Maps planetaryPositions() + ascendant() into the PlanetPosition format.
 */
function buildD1Positions(jd: number, place: Place): PlanetPosition[] {
  const asc = ascendant(jd, place);
  const pp = planetaryPositions(jd, place);
  const positions: PlanetPosition[] = [
    { planet: -1, rasi: asc[0], longitude: asc[1] }, // Ascendant as planet -1
  ];
  for (const [pid, [rasi, long]] of pp) {
    positions.push({ planet: pid, rasi, longitude: long });
  }
  return positions;
}

/**
 * Special ascendant for mixed chart.
 * Python: special_ascendant_mixed_chart(jd, place, vf1, cm1, vf2, cm2, lagna_rate_factor)
 */
export function specialAscendantMixedChart(
  jd: number, place: Place,
  vargaFactor1: number = 1, chartMethod1: number = 1,
  vargaFactor2: number = 1, chartMethod2: number = 1,
  lagnaRateFactor: number = 1.0
): [number, number] {
  const mixedDvf = vargaFactor1 * vargaFactor2;
  const { date, time } = julianDayToGregorian(jd);
  const tobHours = time.hour + time.minute / 60 + time.second / 3600;
  const srise = sunrise(jd, place);
  const sunRiseHours = srise.localTime;
  const timeDiffMins = (tobHours - sunRiseHours) * 60;

  // Get sun position at sunrise in mixed chart
  const jdAtSunrise = srise.jd + place.timezone / 24;
  const d1Pos = buildD1Positions(jdAtSunrise, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vargaFactor1, chartMethod1, vargaFactor2, chartMethod2);
  const sunPos = mixedPos[1]; // Sun is index 1 (after Asc)
  const sunLong = sunPos!.rasi * 30 + sunPos!.longitude;
  const splLong = (sunLong + timeDiffMins * lagnaRateFactor) % 360;
  return [Math.floor(splLong / (30 / mixedDvf)) % 12, splLong % 30];
}

/** Bhava lagna for mixed chart */
export function bhavaLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  return specialAscendantMixedChart(jd, place, vf1, cm1, vf2, cm2, 0.25);
}

/** Hora lagna for mixed chart */
export function horaLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  return specialAscendantMixedChart(jd, place, vf1, cm1, vf2, cm2, 0.5);
}

/** Ghati lagna for mixed chart */
export function ghatiLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  return specialAscendantMixedChart(jd, place, vf1, cm1, vf2, cm2, 1.25);
}

/** Vighati lagna for mixed chart */
export function vighatiLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  return specialAscendantMixedChart(jd, place, vf1, cm1, vf2, cm2, 15.0);
}

/** Indu lagna for mixed chart */
export function induLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  const d1Pos = buildD1Positions(jd, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vf1, cm1, vf2, cm2);
  const moonHouse = mixedPos[2]!.rasi; // Moon is index 2
  const ascHouse = mixedPos[0]!.rasi;  // Asc is index 0
  const ninthLord = HOUSE_OWNERS[(ascHouse + 8) % 12]!;
  const ninthLordFromMoon = HOUSE_OWNERS[(moonHouse + 8) % 12]!;
  let il1 = (IL_FACTORS[ninthLord]! + IL_FACTORS[ninthLordFromMoon]!) % 12;
  if (il1 === 0) il1 = 12;
  const induRasi = (moonHouse + il1 - 1) % 12;
  return [induRasi, mixedPos[2]!.longitude];
}

/** Kunda lagna for mixed chart */
export function kundaLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  const mixedDvf = vf1 * vf2;
  const d1Pos = buildD1Positions(jd, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vf1, cm1, vf2, cm2);
  const asc = mixedPos[0]!;
  const al = asc.rasi * 30 + asc.longitude;
  const al1 = (al * 81) % 360;
  return dasavargaFromLong(al1, mixedDvf);
}

/** Bhrigu Bindhu lagna for mixed chart */
export function bhriguBindhuLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  const d1Pos = buildD1Positions(jd, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vf1, cm1, vf2, cm2);
  const moonLong = mixedPos[2]!.rasi * 30 + mixedPos[2]!.longitude;
  const rahuLong = mixedPos[8]!.rasi * 30 + mixedPos[8]!.longitude; // Rahu is index 8
  const moonAdd = moonLong > rahuLong ? 0 : 360;
  const bb = (0.5 * (rahuLong + moonLong + moonAdd)) % 360;
  return dasavargaFromLong(bb);
}

/** Sree lagna for mixed chart */
export function sreeLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  const mixedDvf = vf1 * vf2;
  const d1Pos = buildD1Positions(jd, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vf1, cm1, vf2, cm2);
  const ascLong = mixedPos[0]!.rasi * 30 + mixedPos[0]!.longitude;
  const moonLong = mixedPos[2]!.rasi * 30 + mixedPos[2]!.longitude;
  return sreeLagnaFromLongitudes(moonLong, ascLong, mixedDvf);
}

/** Pranapada lagna for mixed chart */
export function pranapadaLagnaMixedChart(
  jd: number, place: Place,
  vf1: number = 1, cm1: number = 1, vf2: number = 1, cm2: number = 1
): [number, number] {
  const mixedDvf = vf1 * vf2;
  // Pranapada requires udhayadhi nazhikai. Approximate using sunrise-based calculation.
  const sr = sunrise(jd, place);
  const tobHours = (jd - Math.floor(jd)) * 24;
  const sunriseHours = sr.localTime;
  const elapsed = tobHours - sunriseHours;
  // 1 ghati = dayLength/30, 1 vighati = ghati/60
  const dl = dayLength(jd, place);
  const ghatis = elapsed * 30 / dl;
  const vighatis = ghatis * 60;
  const birthLong = (vighatis * 4) % 12;

  const d1Pos = buildD1Positions(jd, place);
  const mixedPos = getMixedDivisionalChart(d1Pos, vf1, cm1, vf2, cm2);
  const sunLong = mixedPos[1]!.rasi * 30 + mixedPos[1]!.longitude;
  let pl1 = birthLong * 30 + sunLong;
  const sl = dasavargaFromLong(sunLong, mixedDvf);
  if (FIXED_SIGNS.includes(sl[0])) {
    pl1 += 240;
  } else if (DUAL_SIGNS.includes(sl[0])) {
    pl1 += 120;
  }
  const splLong = pl1 % 360;
  return dasavargaFromLong(splLong, mixedDvf);
}

// ============================================================================
// TITHI USING PLANET SPEED
// ============================================================================

/**
 * Tithi calculation using planet speed method.
 * Python: tithi_using_planet_speed(jd, place, tithi_index, planet1, planet2, cycle)
 */
export function tithiUsingPlanetSpeed(
  jd: number, place: Place,
  tithiIndex: number = 1, planet1: number = MOON, planet2: number = SUN,
  cycle: number = 1
): number[] {
  const { time } = julianDayToGregorian(jd);
  const jdHours = time.hour + time.minute / 60 + time.second / 3600;

  function getTithiUsingPlanetSpeed(jd_: number, place_: Place): number[] {
    const jdUtc = jd_ - place_.timezone / 24;
    // Compute tithi phase using planet longitudes
    const p1Long = siderealLongitude(jdUtc, planet1);
    const p2Long = siderealLongitude(jdUtc, planet2);
    const totalPhase = ((p1Long - p2Long) * tithiIndex * cycle % 360 + 360) % 360;
    const oneTithi = 360 / 30;
    const tit = Math.ceil(totalPhase / oneTithi);
    let tithiNo = tit;
    const degreesLeft = tit * oneTithi - totalPhase;
    const oneDayHours = dayLength(jd_, place_) + nightLength(jd_, place_);
    const dailyPlanet1Motion = dailyMoonSpeed(jd_, place_);
    const dailyPlanet2Motion = dailySunSpeed(jd_, place_);
    const endTime = jdHours + (degreesLeft / (dailyPlanet1Motion - dailyPlanet2Motion)) * oneDayHours;
    const fracLeft = degreesLeft / oneTithi;
    const startTime = endTime - (endTime - jdHours) / fracLeft;
    if (INCREASE_TITHI_BY_ONE_BEFORE_KALI_YUGA && jd_ < MAHABHARATHA_TITHI_JULIAN_DAY) {
      tithiNo = tithiNo % 30 + 1;
    }
    return [tithiNo, startTime, endTime];
  }

  const ret = getTithiUsingPlanetSpeed(jd, place);
  if (ret[2]! < 24) {
    const ret1 = getTithiUsingPlanetSpeed(jd + ret[2]! / 24, place);
    const nextTithi = ret[0]! % 30 + 1;
    const nextTithiStart = ret[2]!;
    const nextTithiEnd = ret[2]! + ret1[2]!;
    ret.push(nextTithi, nextTithiStart, nextTithiEnd);
  }
  return ret;
}

// ============================================================================
// YOGAM OLD
// ============================================================================

/**
 * Legacy yogam calculation (using internal _get_yogam equivalent).
 * Python: yogam_old(jd, place, planet1, planet2, tithi_index, cycle)
 */
export function yogamOld(
  jd: number, place: Place,
  planet1: number = MOON, planet2: number = SUN,
  tithiIndex: number = 1, cycle: number = 1
): number[] {
  // Internal _get_yogam equivalent
  function getYogam(jd_: number, place_: Place): number[] {
    const tz = place_.timezone;
    const { date } = julianDayToGregorian(jd_);
    const jdUtc = gregorianToJulianDay(date, { hour: 0, minute: 0, second: 0 });
    const rise = sunrise(jd_, place_).jd;
    const offsets = [0.0, 0.25, 0.5, 0.75, 1.0];
    const longitudes: number[] = [];
    for (const t of offsets) {
      const p1 = siderealLongitude(rise + t, planet1);
      const p2 = siderealLongitude(rise + t, planet2);
      longitudes.push(((p1 + p2) * tithiIndex * cycle) % 360);
    }
    const y = unwrapAngles(longitudes);
    const totalNow = longitudes[0]!;
    const oneYoga = 360 / 27;
    const yogaNo = Math.floor(totalNow / oneYoga) + 1;
    const approxEnd = inverseLagrange(offsets, y, yogaNo * oneYoga);
    const ends = (rise - jdUtc + approxEnd) * 24 + tz;
    return [yogaNo, ends];
  }

  const yoga = getYogam(jd, place);
  const yogaPrev = getYogam(jd - 1, place);
  const yogaNo = yoga[0]!;
  let yogaStart = yogaPrev[1]!;
  const yogaEnd = yoga[1]!;

  if (yogaStart < 24.0) {
    yogaStart = -yogaStart;
  } else if (yogaStart > 24) {
    yogaStart -= 24.0;
  }

  return [yogaNo, yogaStart, yogaEnd];
}

// ============================================================================
// KARAKA TITHI / KARAKA YOGAM
// ============================================================================

/**
 * Karaka tithi (sync fallback) — uses standard tithi.
 * Python: karaka_tithi(jd, place)
 */
export function karakaTithi(jd: number, place: Place): number[] {
  const t = calculateTithi(jd, place);
  return [t.number, t.startTime, t.endTime];
}

/**
 * Karaka tithi (async) — tithi using chara karaka planets (AK and AmK).
 * Python: karaka_tithi(jd, place)
 * Gets chara karakas from dhasavarga positions, then computes tithi
 * using AmK (planet1) and AK (planet2).
 */
export async function karakaTithiAsync(jd: number, place: Place): Promise<number[]> {
  const pp = await dhasavargaAsync(jd, place);
  const positions = pp.map(([planet, [rasi, longitude]]) => ({
    planet,
    rasi,
    longitude
  }));
  // Add dummy lagna position at index 0 (Python adds ['L',(0,-10)])
  const positionsWithLagna = [{ planet: -1, rasi: 0, longitude: -10 }, ...positions];
  const ks = getCharaKarakas(positionsWithLagna);
  const p1 = ks[1]!; // AmK (Amatya Karaka)
  const p2 = ks[0]!; // AK (Atma Karaka)

  const _tithi = await _getTithiGenericAsync(jd, place, p1, p2, 1, 1);
  const _tithiPrev = await _getTithiGenericAsync(jd - 1, place, p1, p2, 1, 1);

  const tithiNo = _tithi[0]!;
  let tithiStart = _tithiPrev[1]!;
  const tithiEnd = _tithi[1]!;

  if (tithiStart < 24.0) {
    tithiStart = -tithiStart;
  } else if (tithiStart > 24) {
    tithiStart -= 24.0;
  }

  const result: number[] = [tithiNo, tithiStart, tithiEnd];

  if (tithiEnd < 24.0) {
    const _tithi1 = await _getTithiGenericAsync(jd + tithiEnd / 24, place, p1, p2, 1, 1);
    const nextTithiNo = (tithiNo % 30) + 1;
    const nextTithiStart = tithiEnd;
    const nextTithiEnd = tithiEnd + _tithi1[1]!;
    result.push(nextTithiNo, nextTithiStart, nextTithiEnd);
  }

  return result;
}

/**
 * Karaka yogam (sync fallback) — uses standard yogam.
 * Python: karaka_yogam(jd, place)
 */
export function karakaYogam(jd: number, place: Place): number[] {
  const y = calculateYoga(jd, place);
  return [y.number, y.startTime, y.endTime];
}

/**
 * Karaka yogam (async) — yogam using chara karaka planets (AK and AmK).
 * Python: karaka_yogam(jd, place)
 */
export async function karakaYogamAsync(jd: number, place: Place): Promise<number[]> {
  const pp = await dhasavargaAsync(jd, place);
  const positions = pp.map(([planet, [rasi, longitude]]) => ({
    planet,
    rasi,
    longitude
  }));
  const positionsWithLagna = [{ planet: -1, rasi: 0, longitude: -10 }, ...positions];
  const ks = getCharaKarakas(positionsWithLagna);
  const p1 = ks[1]!; // AmK
  const p2 = ks[0]!; // AK

  const _yoga = await _getYogamGenericAsync(jd, place, p1, p2, 1, 1);
  const _yogaPrev = await _getYogamGenericAsync(jd - 1, place, p1, p2, 1, 1);

  const yogaNo = _yoga[0]!;
  let yogaStart = _yogaPrev[1]!;
  const yogaEnd = _yoga[1]!;

  if (yogaStart < 24.0) {
    yogaStart = -yogaStart;
  } else if (yogaStart > 24) {
    yogaStart -= 24.0;
  }

  const result: number[] = [yogaNo, yogaStart, yogaEnd];
  return result;
}

// ============================================================================
// TAMIL SOLAR MONTH VARIANTS
// ============================================================================

/**
 * Tamil solar month and date (V4.3.8 method — uses solar longitude at JD).
 * Python: tamil_solar_month_and_date_V4_3_8(panchanga_date, place)
 */
export function tamilSolarMonthAndDateV438(
  jd: number, place: Place
): [number, number] {
  let startJd = jd;
  let sl = solarLongitude(startJd);
  const tamilMonth = Math.floor(sl / 30);
  let dayCount = 1;
  while (true) {
    const rem = sl % 30;
    if (rem < 1 && rem > 0) break;
    startJd -= 1;
    sl = solarLongitude(startJd);
    dayCount++;
    if (dayCount > 35) break; // safety
  }
  return [tamilMonth, dayCount];
}

/**
 * Tamil solar month and date (V4.3.5 method — uses sunset JD).
 * Python: tamil_solar_month_and_date_V4_3_5(panchanga_date, place)
 */
export function tamilSolarMonthAndDateV435(
  jd: number, place: Place
): [number, number] {
  let sunsetJd = sunset(jd, place).jd;
  let sl = solarLongitude(sunsetJd);
  const tamilMonth = Math.floor(sl / 30);
  let dayCount = 1;
  while (true) {
    const rem = sl % 30;
    if (rem < 1 && rem > 0) break;
    sunsetJd -= 1;
    sl = solarLongitude(sunsetJd);
    dayCount++;
    if (dayCount > 35) break; // safety
  }
  return [tamilMonth, dayCount];
}

/**
 * Tamil solar month and date (Ravi Annaswamy method).
 * Python: tamil_solar_month_and_date_RaviAnnnaswamy(panchanga_date, place)
 */
export function tamilSolarMonthAndDateRaviAnnaswamy(
  jd: number, place: Place
): [number, number] {
  const jdSet = sunset(jd, place).jd;
  const jdUtc = jdSet - place.timezone / 24;
  let sr = solarLongitude(jdUtc);
  const tamilMonth = Math.floor(sr / 30);
  let dayCount = 1;
  let searchJd = jdUtc;
  while (true) {
    const rem = sr % 30;
    if (rem < 1 && rem > 0) break;
    searchJd -= 1;
    sr = solarLongitude(searchJd);
    dayCount++;
    if (dayCount > 35) break; // safety
  }
  return [tamilMonth, dayCount];
}

/**
 * Tamil solar month and date (new V4.4.0 method).
 * Python: tamil_solar_month_and_date_new(panchanga_date, place, base_time, use_utc)
 */
export function tamilSolarMonthAndDateNew(
  jd: number, place: Place, baseTime: number = 0, useUtc: boolean = true
): [number, number] {
  let jdBase: number;
  if (baseTime === 0) {
    jdBase = sunset(jd, place).jd;
  } else if (baseTime === 1) {
    jdBase = sunrise(jd, place).jd;
  } else {
    // midday
    const sr = sunrise(jd, place);
    const ss = sunset(jd, place);
    jdBase = (sr.jd + ss.jd) / 2;
  }
  let jdUtc = useUtc ? jdBase - place.timezone / 24 : jdBase;
  let sr = solarLongitude(jdUtc);
  const tamilMonth = Math.floor(sr / 30);
  let dayCount = 1;
  let searchJd = jd;
  while (true) {
    const rem = sr % 30;
    if (rem < 1 && rem > 0) break;
    searchJd -= 1;
    if (baseTime === 0) {
      jdBase = sunset(searchJd, place).jd;
    } else if (baseTime === 1) {
      jdBase = sunrise(searchJd, place).jd;
    } else {
      const srr = sunrise(searchJd, place);
      const sss = sunset(searchJd, place);
      jdBase = (srr.jd + sss.jd) / 2;
    }
    jdUtc = useUtc ? jdBase - place.timezone / 24 : jdBase;
    sr = solarLongitude(jdUtc);
    dayCount++;
    if (dayCount > 35) break; // safety
  }
  return [tamilMonth, dayCount];
}

/**
 * Tamil solar month and date from JD.
 * Python: tamil_solar_month_and_date_from_jd(jd, place)
 */
export function tamilSolarMonthAndDateFromJd(
  jd: number, place: Place
): [number, number] {
  const jdSet = sunset(jd, place).jd;
  let jdUtc = jdSet - place.timezone / 24;
  let sr = solarLongitude(jdUtc);
  const tamilMonth = Math.floor(sr / 30);
  let dayCount = 1;
  while (true) {
    const rem = sr % 30;
    if (rem < 1 && rem > 0) break;
    jdUtc -= 1;
    sr = solarLongitude(jdUtc);
    dayCount++;
    if (dayCount > 35) break; // safety
  }
  return [tamilMonth, dayCount];
}

// ============================================================================
// SAHASRA CHANDRODAYAM OLD (legacy — uses ephem library, stub only)
// ============================================================================

/**
 * Legacy sahasra chandrodayam using ephem library.
 * Python: sahasra_chandrodayam_old(dob, tob, place)
 * NOTE: The Python version uses the `ephem` library which is not available in TS.
 * This is a stub that returns [-1, -1, -1] to indicate unsupported.
 */
export function sahasraChandrodayamOld(
  _dob: [number, number, number], _tob: [number, number], _place: Place
): [number, number, number] {
  return [-1, -1, -1];
}

// ============================================================================
// UDHAYADHI NAZHIKAI (helper for birth rectification)
// ============================================================================

/**
 * Computes nazhikai (ghatikas) from sunrise to the given JD's time.
 * Python: utils.udhayadhi_nazhikai(jd, place)
 *
 * @returns [formattedString, nazhikaiAsFloat]
 */
export function udhayadhiNazhikai(jd: number, place: Place): [string, number] {
  const { time: { hour: _h, minute: _m, second: _s } } = julianDayToGregorian(jd);
  const birthTimeHrs = _h + _m / 60 + _s / 3600;
  let sunriseTimeHrs = sunrise(jd, place).localTime;

  let timeDiff = birthTimeHrs - sunriseTimeHrs;
  if (birthTimeHrs < sunriseTimeHrs) {
    sunriseTimeHrs = sunrise(jd - 1, place).localTime;
    timeDiff = 24.0 + birthTimeHrs - sunriseTimeHrs;
  }

  const totalSecs = Math.abs(timeDiff) * 3600;
  const hours = Math.floor(totalSecs / 3600);
  const minutes = Math.floor((totalSecs - hours * 3600) / 60);
  const seconds = Math.floor(totalSecs - hours * 3600 - minutes * 60);

  const tharparai1 = hours * 9000 + minutes * 150 + seconds;
  const naazhigai = Math.floor(tharparai1 / 3600);
  const vinadigal = Math.floor((tharparai1 - naazhigai * 3600) / 60);
  const tharparai = Math.floor(tharparai1 - naazhigai * 3600 - vinadigal * 60);

  return [`${naazhigai}:${vinadigal}:${tharparai}`, tharparai1 / 3600.0];
}

// ============================================================================
// BIRTH TIME RECTIFICATION (Experimental)
// ============================================================================

/**
 * Nakshatra Suddhi birth time rectification.
 * Python: _birthtime_rectification_nakshathra_suddhi(jd, place)
 *
 * EXPERIMENTAL — results may not be accurate.
 *
 * @returns adjustMinutes (number) if no rectification needed (0),
 *          [hour, minute, second] if rectified,
 *          [true, closestNakshatra] if could not converge
 */
export function birthtimeRectificationNakshatraSuddhi(
  jd: number, place: Place
): number | [number, number, number] | [boolean, number] {
  const stepMinutes = 0.25;
  const loopCount = 120;
  const nak = calculateNakshatra(jd, place)[0];

  function getEstimatedNakshatra(jdTest: number): [boolean, number] {
    const ud = udhayadhiNazhikai(jdTest, place);
    const ud1d = Math.floor(ud[1] * 4 % 9);
    const ud2 = [0, 1, 2].map(n => (ud1d + n * 9) % 27 + 1);
    const rectificationRequired = !ud2.includes(nak);
    let nakClose = nak;
    if (rectificationRequired) {
      // closest element from list
      nakClose = ud2.reduce((closest, v) =>
        Math.abs(v - nak) < Math.abs(closest - nak) ? v : closest, ud2[0]!);
    }
    return [rectificationRequired, nakClose];
  }

  const [rectRequired] = getEstimatedNakshatra(jd);
  if (!rectRequired) return 0;

  for (let l = 1; l <= loopCount; l++) {
    // Try +adjustment
    let adjustMinutes = l * stepMinutes;
    let jd1 = jd + adjustMinutes / 1440.0;
    let [reqd] = getEstimatedNakshatra(jd1);
    if (!reqd) {
      const { time: { hour, minute, second } } = julianDayToGregorian(jd1);
      return [hour, minute, second];
    }

    // Try -adjustment
    adjustMinutes = -l * stepMinutes;
    jd1 = jd + adjustMinutes / 1440.0;
    [reqd] = getEstimatedNakshatra(jd1);
    if (!reqd) {
      const { time: { hour, minute, second } } = julianDayToGregorian(jd1);
      return [hour, minute, second];
    }
  }

  const [, nakClose] = getEstimatedNakshatra(jd);
  return [true, nakClose];
}

/**
 * Lagna Suddhi birth time rectification.
 * Python: _birthtime_rectification_lagna_suddhi(jd, place)
 *
 * EXPERIMENTAL — checks if lagna is [1,5,7,9] from Moon or Maandi in Rasi and Navamsa.
 *
 * @returns true if rectification IS required, false if not
 */
export async function birthtimeRectificationLagnaSuddhiAsync(
  jd: number, place: Place
): Promise<boolean> {
  const ppr = await dhasavargaAsync(jd, place, 1); // Rasi chart
  const ppn = await dhasavargaAsync(jd, place, 9); // Navamsa chart

  const { time: { hour, minute, second } } = julianDayToGregorian(jd);
  const tobHours = hour + minute / 60 + second / 3600;

  // Rasi chart checks
  const lagnaRasi = ppr[0]![1][0];
  const moonRasi = ppr[2]![1][0];
  const maandiRasiResult = upagrahaLongitude(jd, place, tobHours, 6, true); // Maandi
  const maandiRasi = maandiRasiResult[0];

  if ([1, 5, 7, 9].includes(getRelativeHouseOfPlanet(lagnaRasi, moonRasi))) return false;
  if ([1, 5, 7, 9].includes(getRelativeHouseOfPlanet(lagnaRasi, maandiRasi))) return false;

  // Navamsa chart checks
  const lagnaNavamsa = ppn[0]![1][0];
  const moonNavamsa = ppn[2]![1][0];
  const maandiNavResult = upagrahaLongitude(jd, place, tobHours, 6, true);
  const maandiNavLong = maandiNavResult[0] * 30 + maandiNavResult[1];
  const [maandiNavRasi] = dasavargaFromLong(maandiNavLong, 9);

  if ([1, 5, 7, 9].includes(getRelativeHouseOfPlanet(lagnaNavamsa, moonNavamsa))) return false;
  if ([1, 5, 7, 9].includes(getRelativeHouseOfPlanet(lagnaNavamsa, maandiNavRasi))) return false;

  return true;
}

/**
 * Janma Suddhi birth time rectification.
 * Python: _birthtime_rectification_janma_suddhi(jd, place, gender)
 *
 * EXPERIMENTAL — checks if gender matches expected from Ishtakaal Ghatikas.
 *
 * @param gender - 0 for male, 1 for female
 * @returns true if rectification IS required, false if not
 */
export function birthtimeRectificationJanmaSuddhi(
  jd: number, place: Place, gender: number
): boolean {
  const ud = udhayadhiNazhikai(jd, place);
  const ud1d = Math.floor(ud[1] * 60 % 225);
  const janmaSuddhiDict: Record<number, [number, number][]> = {
    0: [[0, 15], [46, 90], [151, 224]],
    1: [[16, 45], [91, 150]]
  };
  const ranges = janmaSuddhiDict[gender] ?? [];
  const matchesGender = ranges.some(([low, high]) => ud1d > low && ud1d < high);
  return !matchesGender;
}

// ============================================================================
// NISHEKA (Conception) TIME CALCULATION (Experimental)
// ============================================================================

/**
 * Nisheka (conception) time calculation — method 1.
 * Python: _nisheka_time(jd, place)
 *
 * EXPERIMENTAL — formula may not be fully accurate. May differ from JHora by up to 15 days.
 *
 * @returns Julian day number of estimated nisheka time
 */
export async function nishekaTimeAsync(jd: number, place: Place): Promise<number> {
  const pp = await dhasavargaAsync(jd, place, 1);
  const { time: { hour, minute, second } } = julianDayToGregorian(jd);
  const tobHours = hour + minute / 60 + second / 3600;

  const satLong = pp[7]![1][0] * 30 + pp[7]![1][1]; // Saturn
  const moonLong = pp[2]![1][0] * 30 + pp[2]![1][1]; // Moon
  const lagnaLong = pp[0]![1][0] * 30 + pp[0]![1][1]; // Lagna (Sun proxy)
  const ninthHouseLong = (240 + lagnaLong + 15) % 360;

  const gl = upagrahaLongitude(jd, place, tobHours, 6, false); // Gulika (begin)
  const gulikaLong = gl[0] * 30 + gl[1];
  const ml = upagrahaLongitude(jd, place, tobHours, 6, true);  // Maandi (middle)
  const maandiLong = ml[0] * 30 + ml[1];

  const a = 0.5 * (((satLong - gulikaLong) % 30 + 30) % 30 + ((satLong - maandiLong) % 30 + 30) % 30);
  const b = ((ninthHouseLong - lagnaLong) % 360 + 360) % 360;
  const c = (a + b) % 360;
  const c1 = c % 30;
  const bm = Math.floor(c / 30);
  const d = c1 + moonLong % 30;

  return jd - (bm * SIDEREAL_YEAR / 12 + d);
}

/**
 * Nisheka (conception) time calculation — method 2.
 * Python: _nisheka_time_1(jd, place)
 *
 * EXPERIMENTAL — alternative formula.
 *
 * @returns Julian day number of estimated nisheka time
 */
export async function nishekaTime1Async(jd: number, place: Place): Promise<number> {
  const pp = await dhasavargaAsync(jd, place, 1);
  const { time: { hour, minute, second } } = julianDayToGregorian(jd);
  const tobHours = hour + minute / 60 + second / 3600;

  const ascHouse = pp[0]![1][0];
  const lagnaLong = ascHouse * 30 + pp[0]![1][1];

  // Determine drishya (visible/invisible)
  // In Python, lagna lord is computed, but here we simplify:
  // Use planet 0 (Sun) as lagna lord proxy
  const lagnaLordLong = pp[1]![1][0] * 30 + pp[1]![1][1]; // Sun's position as proxy
  let drishya = 1.0;
  if (lagnaLordLong < (lagnaLong + 15) || lagnaLordLong > (lagnaLong + 195)) {
    drishya = -1;
  }

  const satLong = pp[7]![1][0] * 30 + pp[7]![1][1]; // Saturn
  const gl = upagrahaLongitude(jd, place, tobHours, 6, false); // Gulika
  const gulikaLong = gl[0] * 30 + gl[1];
  const moonLong = pp[2]![1][1]; // Moon longitude within sign

  const a = Math.abs(satLong - gulikaLong) % 30;
  const c = (a + moonLong) % 30;

  return jd - (273 + drishya * c * 27.3217 / 30);
}

/** nakshatra_new — newer algorithm using planet speed */
export function nakshatraNew(jd: number, place: Place): number[] {
  const jdUtc = jd - place.timezone / 24;
  const oneStar = 360 / 27;
  const moonLong = lunarLongitude(jdUtc);
  const [nakNo, padamNo] = nakshatraPada(moonLong);
  const degreesLeft = nakNo * oneStar - moonLong;
  const sr = sunrise(jd, place);
  const jdHours = (jd - Math.floor(jd)) * 24;
  const moonSpeed = dailyMoonSpeed(jd, place);
  const endTime = jdHours + (degreesLeft / moonSpeed) * 24;

  // Previous day
  const prevJdUtc = (jd - 1) - place.timezone / 24;
  const prevMoonLong = lunarLongitude(prevJdUtc);
  const [prevNakNo, prevPadamNo] = nakshatraPada(prevMoonLong);
  const prevDegreesLeft = prevNakNo * oneStar - prevMoonLong;
  const prevMoonSpeed = dailyMoonSpeed(jd - 1, place);
  const prevJdHours = ((jd - 1) - Math.floor(jd - 1)) * 24;
  let prevEndTime = prevJdHours + (prevDegreesLeft / prevMoonSpeed) * 24;

  let nakStart = prevEndTime;
  if (nakStart < 24.0) {
    nakStart = -nakStart;
  } else if (nakStart > 24) {
    nakStart -= 24.0;
  }

  return [nakNo, padamNo, nakStart, endTime];
}

