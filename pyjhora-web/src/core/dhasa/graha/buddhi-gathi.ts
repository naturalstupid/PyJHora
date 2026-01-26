/**
 * Buddhi Gathi Dasha System
 * Ported from PyJHora buddhi_gathi.py
 *
 * A dasha system based on planet positions in houses.
 * Starts from the 4th house from ascendant and goes through planets
 * in order of decreasing longitude in each house.
 * Duration is based on house count from ascendant.
 */

import {
  PLANET_NAMES_EN,
  SIDEREAL_YEAR
} from '../../constants';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface BuddhiGathiDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface BuddhiGathiBhuktiPeriod {
  dashaLord: number;
  dashaLordName: string;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface BuddhiGathiResult {
  dashaProgression: Array<{ planet: number; durationYears: number }>;
  totalDuration: number;
  mahadashas: BuddhiGathiDashaPeriod[];
  bhuktis?: BuddhiGathiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 120; // Maximum lifespan to calculate

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
 * Get planets in a house from planet positions
 */
function getPlanetsInHouse(
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  houseRasi: number
): Array<{ planet: number; longitude: number }> {
  return planetPositions
    .filter(p => p.rasi === houseRasi && p.planet >= 0 && p.planet <= 8)
    .map(p => ({ planet: p.planet, longitude: p.longitude }))
    .sort((a, b) => b.longitude - a.longitude); // Sort by longitude descending
}

/**
 * Calculate house distance from ascendant
 */
function getHouseDistance(planetRasi: number, ascRasi: number): number {
  return (planetRasi - ascRasi + 12) % 12;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Buddhi Gathi Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data (kept for API consistency)
 * @param planetPositions - Array of planet positions
 * @param options - Calculation options
 * @returns Buddhi Gathi dasha result with mahadashas and optional bhuktis
 */
export function getBuddhiGathiDashaBhukti(
  jd: number,
  place: Place,
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  options: {
    includeBhuktis?: boolean;
  } = {}
): BuddhiGathiResult {
  const { includeBhuktis = true } = options;

  // Get ascendant house
  const ascEntry = planetPositions.find(p => p.planet === -1);
  const ascRasi = ascEntry?.rasi ?? planetPositions[0]?.rasi ?? 0;

  // Build dasha progression
  // Start from 4th house (index 3 from ascendant)
  const dashaProgression: Array<{ planet: number; durationYears: number }> = [];
  let houseIndex = 0;

  for (let h = 0; h < 12; h++) {
    // Calculate house starting from 4th house (ascendant + 3)
    const houseRasi = (ascRasi + 3 + h) % 12;

    // Get planets in this house, sorted by longitude descending
    const planetsInHouse = getPlanetsInHouse(planetPositions, houseRasi);

    for (const { planet } of planetsInHouse) {
      // Get planet's house for duration calculation
      const planetPos = planetPositions.find(p => p.planet === planet);
      if (planetPos) {
        const duration = ((ascRasi + houseIndex + 12) - planetPos.rasi) % 12;
        dashaProgression.push({
          planet,
          durationYears: duration
        });
        houseIndex++;
      }
    }
  }

  // If no planets found, return empty result
  if (dashaProgression.length === 0) {
    return {
      dashaProgression: [],
      totalDuration: 0,
      mahadashas: [],
      bhuktis: includeBhuktis ? [] : undefined
    };
  }

  const mahadashas: BuddhiGathiDashaPeriod[] = [];
  const bhuktis: BuddhiGathiBhuktiPeriod[] = [];

  let startJd = jd;
  const dashaLen = dashaProgression.length;
  let totalDuration = 0;

  // Run 2 cycles (or until human life span is reached)
  for (let cycle = 0; cycle < 2 && totalDuration < HUMAN_LIFE_SPAN; cycle++) {
    for (let di = 0; di < dashaLen && totalDuration < HUMAN_LIFE_SPAN; di++) {
      const { planet: dashaLord, durationYears: dashaDuration } = dashaProgression[di]!;
      totalDuration += dashaDuration;

      if (includeBhuktis) {
        const bhuktiDuration = dashaDuration / dashaLen;

        for (let bi = 0; bi < dashaLen; bi++) {
          const bhuktiLord = dashaProgression[(di + bi) % dashaLen]!.planet;

          bhuktis.push({
            dashaLord,
            dashaLordName: PLANET_NAMES_EN[dashaLord] ?? `Planet ${dashaLord}`,
            bhuktiLord,
            bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`,
            startJd,
            startDate: formatJdAsDate(startJd),
            durationYears: bhuktiDuration
          });

          startJd += bhuktiDuration * YEAR_DURATION;
        }
      } else {
        mahadashas.push({
          lord: dashaLord,
          lordName: PLANET_NAMES_EN[dashaLord] ?? `Planet ${dashaLord}`,
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears: dashaDuration
        });

        startJd += dashaDuration * YEAR_DURATION;
      }
    }
  }

  // If bhuktis were generated, create mahadashas from them
  if (includeBhuktis && bhuktis.length > 0) {
    let currentDashaLord = -1;
    let currentDashaStart = jd;

    for (let i = 0; i < bhuktis.length; i++) {
      const bhukti = bhuktis[i]!;
      if (bhukti.dashaLord !== currentDashaLord) {
        if (currentDashaLord !== -1 && i > 0) {
          const prevBhuktis = bhuktis.filter(b => b.dashaLord === currentDashaLord);
          const totalDur = prevBhuktis.reduce((sum, b) => sum + b.durationYears, 0);

          mahadashas.push({
            lord: currentDashaLord,
            lordName: PLANET_NAMES_EN[currentDashaLord] ?? `Planet ${currentDashaLord}`,
            startJd: currentDashaStart,
            startDate: formatJdAsDate(currentDashaStart),
            durationYears: totalDur
          });
        }
        currentDashaLord = bhukti.dashaLord;
        currentDashaStart = bhukti.startJd;
      }
    }

    // Add the last dasha
    if (currentDashaLord !== -1) {
      const lastBhuktis = bhuktis.filter(b => b.dashaLord === currentDashaLord);
      const totalDur = lastBhuktis.reduce((sum, b) => sum + b.durationYears, 0);

      mahadashas.push({
        lord: currentDashaLord,
        lordName: PLANET_NAMES_EN[currentDashaLord] ?? `Planet ${currentDashaLord}`,
        startJd: currentDashaStart,
        startDate: formatJdAsDate(currentDashaStart),
        durationYears: totalDur
      });
    }
  }

  return {
    dashaProgression,
    totalDuration,
    mahadashas,
    bhuktis: includeBhuktis ? bhuktis : undefined
  };
}
