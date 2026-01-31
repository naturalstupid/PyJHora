/**
 * Kalachakra Dasha System
 * Ported from PyJHora kalachakra.py
 *
 * Kalachakra is a nakshatra-based dasha system with savya/apasavya
 * star classifications. Duration is based on fixed rasi values.
 *
 * Note: Python code mentions progression doesn't fully match JHora.
 */

import {
  RASI_NAMES_EN,
  SIDEREAL_YEAR,
  MOON
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getPlanetLongitude, nakshatraPada } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface KalachakraDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KalachakraBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KalachakraResult {
  mahadashas: KalachakraDashaPeriod[];
  bhuktis?: KalachakraBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

// Star classifications (0-indexed nakshatra numbers)
const SAVYA_STARS_1 = [0, 2, 6, 8, 12, 14, 18, 20, 24];
const SAVYA_STARS_2 = [1, 7, 13, 19, 25, 26];
const APASAVYA_STARS_1 = [3, 9, 15, 21];
const APASAVYA_STARS_2 = [4, 5, 10, 11, 16, 17, 22, 23];

// Duration in years for each rasi (indexed by rasi 0-11)
const KALACHAKRA_DHASA_DURATION = [7, 16, 9, 21, 5, 9, 16, 7, 10, 4, 4, 10];

// Rasi progressions for each star type and pada [starType][pada]
const SAVYA_STARS_1_RASIS = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8],
  [9, 10, 11, 7, 6, 5, 3, 4, 2],
  [1, 0, 11, 10, 9, 8, 0, 1, 2],
  [3, 4, 5, 6, 7, 8, 9, 10, 11]
];

const SAVYA_STARS_2_RASIS = [
  [7, 6, 5, 3, 4, 2, 1, 0, 11],
  [10, 9, 8, 0, 1, 2, 3, 4, 5],
  [6, 7, 8, 9, 10, 11, 7, 6, 5],
  [3, 4, 2, 1, 0, 11, 10, 9, 8]
];

const APASAVYA_STARS_1_RASIS = [
  [8, 9, 10, 11, 0, 1, 2, 4, 3],
  [5, 6, 7, 11, 10, 9, 8, 7, 6],
  [5, 4, 3, 2, 1, 0, 8, 9, 10],
  [11, 0, 1, 2, 4, 3, 5, 6, 7]
];

const APASAVYA_STARS_2_RASIS = [
  [11, 10, 9, 8, 7, 6, 5, 4, 3],
  [2, 1, 0, 8, 9, 10, 11, 0, 1],
  [2, 4, 3, 5, 6, 7, 11, 10, 9],
  [8, 7, 6, 5, 4, 3, 2, 1, 0]
];

const KALACHAKRA_RASIS = [
  SAVYA_STARS_1_RASIS,
  SAVYA_STARS_2_RASIS,
  APASAVYA_STARS_1_RASIS,
  APASAVYA_STARS_2_RASIS
];

// Paramayush for each star type and pada
const SAVYA_STARS_1_PARAMAYUSH = [100, 85, 83, 86];
const APASAVYA_STARS_1_PARAMAYUSH = [86, 83, 85, 100];

const KALACHAKRA_PARAMAYUSH = [
  SAVYA_STARS_1_PARAMAYUSH,
  SAVYA_STARS_1_PARAMAYUSH, // Same for savya_2
  APASAVYA_STARS_1_PARAMAYUSH,
  APASAVYA_STARS_1_PARAMAYUSH // Same for apasavya_2
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getPlanetPositionsArray(jd: number, place: Place, divisionalChartFactor: number): PlanetPosition[] {
  const d1Positions: PlanetPosition[] = [];

  for (let planet = 0; planet <= 8; planet++) {
    const longitude = getPlanetLongitude(jd, place, planet);
    d1Positions.push({
      planet,
      rasi: Math.floor(longitude / 30),
      longitude: longitude % 30
    });
  }

  if (divisionalChartFactor > 1) {
    return getDivisionalChart(d1Positions, divisionalChartFactor);
  }

  return d1Positions;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Get Kalachakra index based on nakshatra
 */
function getKalachakraIndex(nakshatra: number): number {
  // nakshatra is 0-indexed here
  if (SAVYA_STARS_1.includes(nakshatra)) return 0;
  if (SAVYA_STARS_2.includes(nakshatra)) return 1;
  if (APASAVYA_STARS_1.includes(nakshatra)) return 2;
  return 3; // APASAVYA_STARS_2
}

/**
 * Cumulative sum of array
 */
function cumSum(arr: number[]): number[] {
  const result: number[] = [];
  let sum = 0;
  for (const val of arr) {
    sum += val;
    result.push(sum);
  }
  return result;
}

/**
 * Get dasha progression from planet longitude
 */
function getDhasaProgression(planetLongitude: number): {
  progression: number[];
  durations: number[];
  remainingAtBirth: number;
} {
  const [nak, pada] = nakshatraPada(planetLongitude);

  // Convert to 0-indexed
  const nakshatra = nak - 1;
  const paadham = pada - 1;

  const kalachakraIndex = getKalachakraIndex(nakshatra);

  const dhasaProgressionBase = KALACHAKRA_RASIS[kalachakraIndex]![paadham]!;
  const paramayush = KALACHAKRA_PARAMAYUSH[kalachakraIndex]![paadham]!;
  const dhasaDurations = dhasaProgressionBase.map(r => KALACHAKRA_DHASA_DURATION[r]!);

  // Calculate how much has passed at birth
  const ONE_STAR = 360.0 / 27;
  const ONE_PAADHA = 360.0 / 108;

  const nakStartLong = nakshatra * ONE_STAR + paadham * ONE_PAADHA;
  const nakTravelFraction = (planetLongitude - nakStartLong) / ONE_PAADHA;

  // Find which dasha is running at birth
  const dhasaCumulative = cumSum(dhasaDurations);
  const paramayushCompleted = nakTravelFraction * paramayush;

  let dhasaIndexAtBirth = 0;
  for (let i = 0; i < dhasaCumulative.length; i++) {
    if (dhasaCumulative[i]! > paramayushCompleted) {
      dhasaIndexAtBirth = i;
      break;
    }
  }

  const dhasaRemainingAtBirth = dhasaCumulative[dhasaIndexAtBirth]! - paramayushCompleted;

  // Get next cycle params
  let kalachakraIndexNext = kalachakraIndex;
  const paadhamNext = (paadham + 1) % 4;

  if (paadham === 3) {
    // Toggle between savya/apasavya groups
    if (kalachakraIndex === 0) kalachakraIndexNext = 1;
    else if (kalachakraIndex === 1) kalachakraIndexNext = 0;
    else if (kalachakraIndex === 2) kalachakraIndexNext = 3;
    else kalachakraIndexNext = 2;
  }

  // Build full progression
  const nextProgression = KALACHAKRA_RASIS[kalachakraIndexNext]![paadhamNext]!;
  const fullProgression = [
    ...dhasaProgressionBase.slice(dhasaIndexAtBirth),
    ...nextProgression.slice(0, dhasaIndexAtBirth)
  ];

  const fullDurations = fullProgression.map(r => KALACHAKRA_DHASA_DURATION[r]!);
  fullDurations[0] = dhasaRemainingAtBirth;

  return {
    progression: fullProgression,
    durations: fullDurations,
    remainingAtBirth: dhasaRemainingAtBirth
  };
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Kalachakra Dasha periods
 * Nakshatra-based system with savya/apasavya classifications
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 * @param options.startingPlanet - Planet to use for longitude (default Moon = 1)
 */
export function getKalachakraDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
    startingPlanet?: number;
  } = {}
): KalachakraResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true,
    startingPlanet = MOON
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get starting planet's longitude
  const planetPosition = planetPositions.find(p => p.planet === startingPlanet);
  const planetLongitude = (planetPosition?.rasi ?? 0) * 30 + (planetPosition?.longitude ?? 0);

  // Get dasha progression
  const { progression, durations } = getDhasaProgression(planetLongitude);

  const mahadashas: KalachakraDashaPeriod[] = [];
  const bhuktis: KalachakraBhuktiPeriod[] = [];
  let startJd = jd;

  for (let i = 0; i < progression.length; i++) {
    const dhasaLord = progression[i]!;
    const duration = durations[i]!;
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });

    if (includeBhuktis) {
      // Simplified bhukti calculation - proportional division
      const bhuktiDuration = duration / 9;
      let bhuktiStartJd = startJd;

      // Use same progression for bhuktis
      for (let j = 0; j < 9; j++) {
        const bhuktiIndex = (i + j) % progression.length;
        const bhuktiLord = progression[bhuktiIndex] ?? dhasaLord;
        const bhuktiRasiName = RASI_NAMES_EN[bhuktiLord] ?? `Rasi ${bhuktiLord}`;

        bhuktis.push({
          dashaRasi: dhasaLord,
          bhuktiRasi: bhuktiLord,
          bhuktiRasiName,
          startJd: bhuktiStartJd,
          startDate: formatJdAsDate(bhuktiStartJd),
          durationYears: bhuktiDuration
        });

        bhuktiStartJd += bhuktiDuration * YEAR_DURATION;
      }
    }

    startJd += duration * YEAR_DURATION;
  }

  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
