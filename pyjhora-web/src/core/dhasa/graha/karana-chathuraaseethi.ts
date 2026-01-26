/**
 * Karana Chathuraaseethi Sama Dasha System
 * Ported from PyJHora karana_chathuraaseethi_sama.py
 *
 * A 84-year dasha system (Chathuraaseethi = 84) based on Karana.
 * 7 lords with 12 years each = 84 years total.
 * Excludes Rahu and Ketu from the lords.
 */

import {
  PLANET_NAMES_EN,
  SIDEREAL_YEAR
} from '../../constants';
import { calculateKarana } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface KaranaChathuraaseethiDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KaranaChathuraaseetihBhuktiPeriod {
  dashaLord: number;
  dashaLordName: string;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KaranaChathuraaseethiResult {
  karanaNumber: number;
  karanaName: string;
  karanaFraction: number;
  dashaBalance: number;
  mahadashas: KaranaChathuraaseethiDashaPeriod[];
  bhuktis?: KaranaChathuraaseetihBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const DASHA_DURATION = 12; // Each lord has 12 years

// Karana lords (7 lords, excluding Rahu and Ketu)
// Index 0-6: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
const KARANA_LORDS = [0, 1, 2, 3, 4, 5, 6];

// Karana to lord mapping
// Each lord rules certain karanas (60 karanas total, repeating cycle)
// The mapping is based on karana groups
const KARANA_TO_LORD: Record<number, number> = {};

// Initialize karana to lord mapping
// Karanas: 2,9,16,23,30,37,44,51,58 -> Sun (0)
// Karanas: 3,10,17,24,31,38,45,52,59 -> Moon (1)
// Karanas: 4,11,18,25,32,39,46,53,60 -> Mars (2)
// Karanas: 5,12,19,26,33,40,47,54,1 -> Mercury (3)
// Karanas: 6,13,20,27,34,41,48,55 -> Jupiter (4)
// Karanas: 7,14,21,28,35,42,49,56 -> Venus (5)
// Karanas: 8,15,22,29,36,43,50,57 -> Saturn (6)

[2, 9, 16, 23, 30, 37, 44, 51, 58].forEach(k => KARANA_TO_LORD[k] = 0);     // Sun
[3, 10, 17, 24, 31, 38, 45, 52, 59].forEach(k => KARANA_TO_LORD[k] = 1);    // Moon
[4, 11, 18, 25, 32, 39, 46, 53, 60].forEach(k => KARANA_TO_LORD[k] = 2);    // Mars
[5, 12, 19, 26, 33, 40, 47, 54, 1].forEach(k => KARANA_TO_LORD[k] = 3);     // Mercury
[6, 13, 20, 27, 34, 41, 48, 55].forEach(k => KARANA_TO_LORD[k] = 4);        // Jupiter
[7, 14, 21, 28, 35, 42, 49, 56].forEach(k => KARANA_TO_LORD[k] = 5);        // Venus
[8, 15, 22, 29, 36, 43, 50, 57].forEach(k => KARANA_TO_LORD[k] = 6);        // Saturn

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
 * Get next lord in sequence
 */
function getNextLord(lord: number, direction: number = 1): number {
  const index = KARANA_LORDS.indexOf(lord);
  if (index === -1) return KARANA_LORDS[0]!;
  const nextIndex = (index + direction + KARANA_LORDS.length) % KARANA_LORDS.length;
  return KARANA_LORDS[nextIndex]!;
}

/**
 * Get karana lord from karana number
 */
function getKaranaLord(karanaNumber: number): number {
  return KARANA_TO_LORD[karanaNumber] ?? 0; // Default to Sun
}

/**
 * Calculate fraction of karana elapsed
 * Using approximate calculation since karana endTime is available
 */
function getKaranaFraction(endTime: number, birthTimeHrs: number): number {
  // Karana spans about 6 degrees of moon-sun elongation
  // Approximate duration is about 12 hours
  const approxDuration = 12; // hours
  const startTime = endTime - approxDuration;

  let adjustedEnd = endTime;
  let adjustedStart = startTime;
  let adjustedBirth = birthTimeHrs;

  // Handle midnight crossings
  if (adjustedStart < 0) {
    adjustedStart += 24;
    if (birthTimeHrs > adjustedStart || birthTimeHrs < adjustedEnd) {
      if (birthTimeHrs > adjustedStart) {
        adjustedBirth = birthTimeHrs;
        adjustedEnd += 24;
      }
    }
  }

  const total = approxDuration;
  const elapsed = adjustedBirth - adjustedStart;

  if (total <= 0) return 0.5;
  return Math.max(0, Math.min(1, elapsed / total));
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Karana Chathuraaseethi Sama Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Karana Chathuraaseethi dasha result with mahadashas and optional bhuktis
 */
export function getKaranaChathuraaseethiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    includeBhuktis?: boolean;
    antardhasaOption?: 1 | 2 | 3 | 4 | 5 | 6;
    useTribhagiVariation?: boolean;
  } = {}
): KaranaChathuraaseethiResult {
  const {
    includeBhuktis = true,
    antardhasaOption = 1,
    useTribhagiVariation = false
  } = options;

  // Get karana information
  const karanaResult = calculateKarana(jd, place);
  const karanaNumber = karanaResult.number;
  const karanaName = karanaResult.name;

  // Get birth time hours
  const { time } = julianDayToGregorian(jd);
  const birthTimeHrs = time.hour + time.minute / 60 + time.second / 3600;

  // Calculate karana fraction
  const karanaFraction = getKaranaFraction(karanaResult.endTime, birthTimeHrs);

  // Get starting lord
  const startingLord = getKaranaLord(karanaNumber);

  // Calculate dasha start
  const fractionRemaining = 1 - karanaFraction;
  const periodElapsed = fractionRemaining * DASHA_DURATION * YEAR_DURATION;
  let startJd = jd - periodElapsed;

  // Calculate dasha balance
  const dashaBalance = fractionRemaining * DASHA_DURATION;

  // Tribhagi variation
  const tribhagiFactor = useTribhagiVariation ? 1 / 3 : 1;
  const cycles = useTribhagiVariation ? 3 : 1;

  const mahadashas: KaranaChathuraaseethiDashaPeriod[] = [];
  const bhuktis: KaranaChathuraaseetihBhuktiPeriod[] = [];

  for (let cycle = 0; cycle < cycles; cycle++) {
    let currentLord = startingLord;

    for (let i = 0; i < KARANA_LORDS.length; i++) {
      const durationYears = DASHA_DURATION * tribhagiFactor;

      if (includeBhuktis) {
        // Determine bhukti starting lord and direction
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
        const bhuktiDuration = durationYears / KARANA_LORDS.length;

        for (let j = 0; j < KARANA_LORDS.length; j++) {
          bhuktis.push({
            dashaLord: currentLord,
            dashaLordName: PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`,
            bhuktiLord,
            bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`,
            startJd: bhuktiStart,
            startDate: formatJdAsDate(bhuktiStart),
            durationYears: bhuktiDuration
          });

          bhuktiStart += bhuktiDuration * YEAR_DURATION;
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
    karanaNumber,
    karanaName,
    karanaFraction,
    dashaBalance,
    mahadashas,
    bhuktis: includeBhuktis ? bhuktis : undefined
  };
}
