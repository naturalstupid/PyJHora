/**
 * Brahma Dasha System
 * Ported from PyJHora brahma.py
 *
 * Brahma Dasha uses the Brahma planet's sign as the seed.
 * Duration is calculated based on the 6th house lord's position from each sign.
 * Progression direction depends on whether seed is in even or odd sign.
 */

import {
  RASI_NAMES_EN,
  SIDEREAL_YEAR,
  EVEN_SIGNS,
  HOUSE_STRENGTHS_OF_PLANETS,
  STRENGTH_DEBILITATED,
  STRENGTH_EXALTED
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getBrahma, getHouseOwnerFromPlanetPositions } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface BrahmaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface BrahmaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface BrahmaResult {
  mahadashas: BrahmaDashaPeriod[];
  bhuktis?: BrahmaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

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
 * Calculate dasha duration based on 6th house lord's position
 * This is a complex calculation from PyJHora:
 * - Get lord of 6th house from the sign
 * - Calculate duration based on lord's house relative to sign
 * - Adjust for exalted/debilitated status
 */
function getDhasaDuration(
  planetPositions: PlanetPosition[],
  sign: number
): number {
  // Get lord of 6th house from this sign
  const house6th = (sign + 5) % 12;
  const lordOf6th = getHouseOwnerFromPlanetPositions(planetPositions, house6th);

  // Get the house where the 6th lord is placed
  const lordPosition = planetPositions.find(p => p.planet === lordOf6th);
  const lordHouse = lordPosition?.rasi ?? 0;

  // Calculate duration based on position
  let duration: number;
  if (EVEN_SIGNS.includes(sign)) {
    // For even signs: (sign + 13 - lordHouse) % 12
    duration = (sign + 13 - lordHouse) % 12;
  } else {
    // For odd signs: (lordHouse + 13 - sign) % 12
    duration = (lordHouse + 13 - sign) % 12;
  }

  duration -= 1;

  // Special cases
  if (lordHouse === sign) {
    // Lord in own sign
    duration = 0;
  } else {
    // Adjust for exalted/debilitated
    const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOf6th]?.[lordHouse] ?? 2;
    if (strength === STRENGTH_DEBILITATED) {
      duration -= 1;
    } else if (strength === STRENGTH_EXALTED) {
      duration += 1;
    }
  }

  return Math.max(0, duration);
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Brahma Dasha periods
 * Uses Brahma planet's sign as seed, complex duration calculation
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getBrahmaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): BrahmaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get Brahma planet and its sign
  const brahmaPlanet = getBrahma(planetPositions);
  const brahmaPosition = planetPositions.find(p => p.planet === brahmaPlanet);
  const dhasaSeed = brahmaPosition?.rasi ?? 0;

  // Build progression based on even/odd sign of seed
  let dhasaLords: number[];
  if (EVEN_SIGNS.includes(dhasaSeed)) {
    // For even signs: reverse direction from 7th house
    // (seed + 6 - h + 12) % 12 for h = 0 to 11
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + 6 - h + 12) % 12);
  } else {
    // For odd signs: forward direction
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  }

  const mahadashas: BrahmaDashaPeriod[] = [];
  const bhuktis: BrahmaBhuktiPeriod[] = [];
  let startJd = jd;

  for (const dhasaLord of dhasaLords) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    const duration = getDhasaDuration(planetPositions, dhasaLord);

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });

    if (includeBhuktis) {
      const bhuktiDuration = duration / 12;
      let bhuktiStartJd = startJd;

      for (let h = 0; h < 12; h++) {
        const bhuktiLord = (dhasaLord + h) % 12;
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
