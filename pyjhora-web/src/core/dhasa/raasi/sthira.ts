/**
 * Sthira Dasha System
 * Ported from PyJHora sthira.py
 *
 * Sthira Dasha uses the Brahma planet's sign as the seed.
 * Duration varies by sign type:
 * - Movable signs: 7 years
 * - Fixed signs: 8 years
 * - Dual signs: 9 years
 */

import { RASI_NAMES_EN, SIDEREAL_YEAR, MOVABLE_SIGNS, FIXED_SIGNS } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getBrahma } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface SthiraDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SthiraBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SthiraResult {
  mahadashas: SthiraDashaPeriod[];
  bhuktis?: SthiraBhuktiPeriod[];
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
 * Get dasha duration based on sign type
 * Movable: 7 years, Fixed: 8 years, Dual: 9 years
 */
function getDhasaDuration(sign: number): number {
  if (MOVABLE_SIGNS.includes(sign)) {
    return 7;
  } else if (FIXED_SIGNS.includes(sign)) {
    return 8;
  } else {
    return 9; // Dual signs
  }
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Sthira Dasha periods
 * Uses Brahma planet's sign as seed, duration varies by sign type
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getSthiraDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): SthiraResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get Brahma planet and its sign
  const brahmaPlanet = getBrahma(planetPositions);
  const brahmaPosition = planetPositions.find(p => p.planet === brahmaPlanet);
  const brahmaSign = brahmaPosition?.rasi ?? 0;

  // Build progression from Brahma sign - sequential
  const dhasaLords = Array.from({ length: 12 }, (_, h) => (brahmaSign + h) % 12);

  const mahadashas: SthiraDashaPeriod[] = [];
  const bhuktis: SthiraBhuktiPeriod[] = [];
  let startJd = jd;

  for (const dhasaLord of dhasaLords) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    const duration = getDhasaDuration(dhasaLord);

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
