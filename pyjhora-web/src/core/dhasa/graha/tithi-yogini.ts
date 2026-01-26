/**
 * Tithi Yogini Dasha System
 * Ported from PyJHora tithi_yogini.py
 *
 * Yogini dasha (36 year cycle, 3 cycles = 108 years) based on Tithi instead of Nakshatra.
 * 8 lords with durations 1-8 years summing to 36 years.
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

export interface TithiYoginiDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TithiYoginiBhuktiPeriod {
  dashaLord: number;
  dashaLordName: string;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TithiYoginiResult {
  tithiNumber: number;
  tithiName: string;
  tithiFraction: number;
  dashaBalance: number;
  mahadashas: TithiYoginiDashaPeriod[];
  bhuktis?: TithiYoginiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

// Tithi Yogini adhipati list in order: {planet: duration}
// Moon=1, Sun=2, Jupiter=3, Mars=4, Mercury=5, Saturn=6, Venus=7, Rahu=8
// Total = 36 years
const YOGINI_LORDS = [1, 0, 4, 2, 3, 6, 5, 7]; // Moon, Sun, Jupiter, Mars, Mercury, Saturn, Venus, Rahu

const LORD_DURATIONS: Record<number, number> = {
  1: 1,   // Moon
  0: 2,   // Sun
  4: 3,   // Jupiter
  2: 4,   // Mars
  3: 5,   // Mercury
  6: 6,   // Saturn
  5: 7,   // Venus
  7: 8,   // Rahu
};

// Tithi to lord mapping
// Same pattern as ashtottari but with yogini durations
const TITHI_TO_LORD: Record<number, [number, number]> = {};

// Initialize the mapping (same tithi groups as ashtottari, different durations)
[1, 9, 16, 24].forEach(t => TITHI_TO_LORD[t] = [0, 2]);     // Sun
[2, 10, 17, 25].forEach(t => TITHI_TO_LORD[t] = [1, 1]);    // Moon
[3, 11, 18, 26].forEach(t => TITHI_TO_LORD[t] = [2, 4]);    // Mars
[4, 12, 19, 27].forEach(t => TITHI_TO_LORD[t] = [3, 5]);    // Mercury
[7, 15, 22].forEach(t => TITHI_TO_LORD[t] = [6, 6]);        // Saturn
[5, 13, 20, 28].forEach(t => TITHI_TO_LORD[t] = [4, 3]);    // Jupiter
[8, 23, 30].forEach(t => TITHI_TO_LORD[t] = [7, 8]);        // Rahu
[6, 14, 21, 29].forEach(t => TITHI_TO_LORD[t] = [5, 7]);    // Venus

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
 * Get next lord in Yogini sequence
 */
function getNextLord(lord: number, direction: number = 1): number {
  const index = YOGINI_LORDS.indexOf(lord);
  if (index === -1) return YOGINI_LORDS[0]!;
  const nextIndex = (index + direction + YOGINI_LORDS.length) % YOGINI_LORDS.length;
  return YOGINI_LORDS[nextIndex]!;
}

/**
 * Get tithi lord from tithi number
 */
function getTithiLord(tithiNumber: number): [number, number] {
  return TITHI_TO_LORD[tithiNumber] ?? [0, 2]; // Default to Sun
}

/**
 * Calculate fraction of tithi elapsed
 */
function getTithiFraction(startTime: number, endTime: number, birthTimeHrs: number): number {
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

  if (total <= 0) return 0.5;
  return Math.max(0, Math.min(1, elapsed / total));
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Tithi Yogini Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Tithi Yogini dasha result with mahadashas and optional bhuktis
 */
export function getTithiYoginiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    includeBhuktis?: boolean;
    antardhasaOption?: 1 | 2 | 3 | 4 | 5 | 6;
    useTribhagiVariation?: boolean;
    tithiIndex?: number;
  } = {}
): TithiYoginiResult {
  const {
    includeBhuktis = true,
    antardhasaOption = 1, // Default: dasha lord, forward
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

  // Calculate dasha start
  const fractionRemaining = 1 - tithiFraction;
  const periodElapsed = fractionRemaining * startingDuration * YEAR_DURATION;
  let startJd = jd - periodElapsed;

  // Calculate dasha balance
  const dashaBalance = fractionRemaining * startingDuration;

  // Tribhagi variation
  const tribhagiFactor = useTribhagiVariation ? 1 / 3 : 1;
  // 3 cycles for 108 year total (or 9 cycles if tribhagi)
  const baseCycles = 3;
  const cycles = useTribhagiVariation ? baseCycles * 3 : baseCycles;

  const mahadashas: TithiYoginiDashaPeriod[] = [];
  const bhuktis: TithiYoginiBhuktiPeriod[] = [];

  for (let cycle = 0; cycle < cycles; cycle++) {
    let currentLord = startingLord;

    for (let i = 0; i < YOGINI_LORDS.length; i++) {
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
        const bhuktiDurationBase = durationYears / YOGINI_LORDS.length;

        for (let j = 0; j < YOGINI_LORDS.length; j++) {
          bhuktis.push({
            dashaLord: currentLord,
            dashaLordName: PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`,
            bhuktiLord,
            bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`,
            startJd: bhuktiStart,
            startDate: formatJdAsDate(bhuktiStart),
            durationYears: bhuktiDurationBase
          });

          bhuktiStart += bhuktiDurationBase * YEAR_DURATION;
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
