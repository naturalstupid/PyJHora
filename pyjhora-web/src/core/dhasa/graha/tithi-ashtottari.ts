/**
 * Tithi Ashtottari Dasha System
 * Ported from PyJHora tithi_ashtottari.py
 *
 * Ashtottari (108 year) dasha based on Tithi instead of Nakshatra.
 * 8 lords with different year durations summing to 108 years.
 */

import {
  PLANET_NAMES_EN,
  SIDEREAL_YEAR
} from '../../constants';
import { calculateTithi } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface TithiAshtottariDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TithiAshtottariBhuktiPeriod {
  dashaLord: number;
  dashaLordName: string;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TithiAshtottariResult {
  tithiNumber: number;
  tithiName: string;
  tithiFraction: number;
  dashaBalance: number;
  mahadashas: TithiAshtottariDashaPeriod[];
  bhuktis?: TithiAshtottariBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 108;

// Tithi Ashtottari adhipati list in order
const ASHTOTTARI_LORDS = [0, 1, 2, 3, 6, 4, 7, 5]; // Sun, Moon, Mars, Mercury, Saturn, Jupiter, Rahu, Venus

// Tithi to lord mapping: tithi -> [lord, duration]
// Tithis 1,9,16,24 -> Sun (6 years)
// Tithis 2,10,17,25 -> Moon (15 years)
// Tithis 3,11,18,26 -> Mars (8 years)
// Tithis 4,12,19,27 -> Mercury (17 years)
// Tithis 7,15,22 -> Saturn (10 years)
// Tithis 5,13,20,28 -> Jupiter (19 years)
// Tithis 8,23,30 -> Rahu (12 years)
// Tithis 6,14,21,29 -> Venus (21 years)

const TITHI_TO_LORD: Record<number, [number, number]> = {};

// Initialize the mapping
[1, 9, 16, 24].forEach(t => TITHI_TO_LORD[t] = [0, 6]);     // Sun
[2, 10, 17, 25].forEach(t => TITHI_TO_LORD[t] = [1, 15]);   // Moon
[3, 11, 18, 26].forEach(t => TITHI_TO_LORD[t] = [2, 8]);    // Mars
[4, 12, 19, 27].forEach(t => TITHI_TO_LORD[t] = [3, 17]);   // Mercury
[7, 15, 22].forEach(t => TITHI_TO_LORD[t] = [6, 10]);       // Saturn
[5, 13, 20, 28].forEach(t => TITHI_TO_LORD[t] = [4, 19]);   // Jupiter
[8, 23, 30].forEach(t => TITHI_TO_LORD[t] = [7, 12]);       // Rahu
[6, 14, 21, 29].forEach(t => TITHI_TO_LORD[t] = [5, 21]);   // Venus

// Duration for each lord
const LORD_DURATIONS: Record<number, number> = {
  0: 6,   // Sun
  1: 15,  // Moon
  2: 8,   // Mars
  3: 17,  // Mercury
  4: 19,  // Jupiter
  5: 21,  // Venus
  6: 10,  // Saturn
  7: 12,  // Rahu
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Get next lord in Ashtottari sequence
 */
function getNextLord(lord: number, direction: number = 1): number {
  const index = ASHTOTTARI_LORDS.indexOf(lord);
  if (index === -1) return ASHTOTTARI_LORDS[0]!;
  const nextIndex = (index + direction + ASHTOTTARI_LORDS.length) % ASHTOTTARI_LORDS.length;
  return ASHTOTTARI_LORDS[nextIndex]!;
}

/**
 * Get tithi lord from tithi number
 */
function getTithiLord(tithiNumber: number): [number, number] {
  return TITHI_TO_LORD[tithiNumber] ?? [0, 6]; // Default to Sun
}

/**
 * Calculate fraction of tithi elapsed
 */
function getTithiFraction(startTime: number, endTime: number, birthTimeHrs: number): number {
  // Handle case where tithi spans midnight
  let adjustedEnd = endTime;
  if (endTime < startTime) {
    adjustedEnd = endTime + 24;
  }
  let adjustedBirth = birthTimeHrs;
  if (birthTimeHrs < startTime) {
    adjustedBirth = birthTimeHrs + 24;
  }

  const total = adjustedEnd - startTime;
  const elapsed = adjustedBirth - startTime;

  if (total <= 0) return 0.5; // Default if calculation fails
  return Math.max(0, Math.min(1, elapsed / total));
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Tithi Ashtottari Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Tithi Ashtottari dasha result with mahadashas and optional bhuktis
 */
export function getTithiAshtottariDashaBhukti(
  jd: number,
  place: Place,
  options: {
    includeBhuktis?: boolean;
    antardhasaOption?: 1 | 2 | 3 | 4 | 5 | 6;
    useTribhagiVariation?: boolean;
    tithiIndex?: number; // 1-12 for different tithi calculations
  } = {}
): TithiAshtottariResult {
  const {
    includeBhuktis = true,
    antardhasaOption = 3, // Default: next lord, forward
    useTribhagiVariation = false
  } = options;

  // Get tithi information
  const tithiResult = calculateTithi(jd, place);
  const tithiNumber = tithiResult.number;
  const tithiName = tithiResult.name;

  // Get birth time hours
  const { time } = julianDayToGregorian(jd);
  const birthTimeHrs = time.hour + time.minute / 60 + time.second / 3600;

  // Calculate tithi fraction (how much has elapsed)
  const tithiFraction = getTithiFraction(
    tithiResult.startTime,
    tithiResult.endTime,
    birthTimeHrs
  );

  // Get starting lord and duration
  const [startingLord, startingDuration] = getTithiLord(tithiNumber);

  // Calculate dasha start (how many days before birth the dasha began)
  const fractionRemaining = 1 - tithiFraction;
  const periodElapsed = fractionRemaining * startingDuration * YEAR_DURATION;
  let startJd = jd - periodElapsed;

  // Calculate dasha balance
  const dashaBalance = fractionRemaining * startingDuration;

  // Tribhagi variation
  const tribhagiFactor = useTribhagiVariation ? 1 / 3 : 1;
  const cycles = useTribhagiVariation ? 3 : 1;

  const mahadashas: TithiAshtottariDashaPeriod[] = [];
  const bhuktis: TithiAshtottariBhuktiPeriod[] = [];

  for (let cycle = 0; cycle < cycles; cycle++) {
    let currentLord = startingLord;

    for (let i = 0; i < ASHTOTTARI_LORDS.length; i++) {
      const durationYears = LORD_DURATIONS[currentLord]! * tribhagiFactor;

      if (includeBhuktis) {
        // Determine bhukti starting lord and direction based on option
        let bhuktiLord = currentLord;
        let direction = 1;

        if (antardhasaOption === 2) {
          direction = -1;
        } else if (antardhasaOption === 3) {
          bhuktiLord = getNextLord(currentLord, 1);
          direction = 1;
        } else if (antardhasaOption === 4) {
          bhuktiLord = getNextLord(currentLord, 1);
          direction = -1;
        } else if (antardhasaOption === 5) {
          bhuktiLord = getNextLord(currentLord, -1);
          direction = 1;
        } else if (antardhasaOption === 6) {
          bhuktiLord = getNextLord(currentLord, -1);
          direction = -1;
        }

        let bhuktiStart = startJd;
        for (let j = 0; j < ASHTOTTARI_LORDS.length; j++) {
          const bhuktiDuration = (LORD_DURATIONS[bhuktiLord]! * durationYears) / HUMAN_LIFE_SPAN;

          bhuktis.push({
            dashaLord: currentLord,
            dashaLordName: PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`,
            bhuktiLord,
            bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`,
            startJd: bhuktiStart,
            startDate: formatJdAsDate(bhuktiStart),
            durationYears: bhuktiDuration * tribhagiFactor
          });

          bhuktiStart += bhuktiDuration * tribhagiFactor * YEAR_DURATION;
          bhuktiLord = getNextLord(bhuktiLord, direction);
        }
      }

      mahadashas.push({
        lord: currentLord,
        lordName: PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`,
        startJd,
        startDate: formatJdAsDate(startJd),
        durationYears
      });

      startJd += durationYears * YEAR_DURATION;
      currentLord = getNextLord(currentLord, 1);
    }
  }

  return {
    tithiNumber,
    tithiName,
    tithiFraction,
    dashaBalance,
    mahadashas,
    bhuktis: includeBhuktis ? bhuktis : undefined
  };
}
