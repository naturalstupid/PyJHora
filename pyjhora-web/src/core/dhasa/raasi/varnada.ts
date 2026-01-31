/**
 * Varnada Dasha System
 * Ported from PyJHora varnada.py
 *
 * Varnada uses the stronger of Lagna and Hora Lagna as seed.
 * Duration is calculated as (dasha_lord - varnada_lagna) % 12.
 *
 * Note: Python code mentions periods don't match JHora.
 */

import {
  RASI_NAMES_EN,
  SIDEREAL_YEAR,
  EVEN_SIGNS,
  ODD_SIGNS
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude, getHoraLagna } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface VarnadaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface VarnadaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface VarnadaResult {
  mahadashas: VarnadaDashaPeriod[];
  bhuktis?: VarnadaBhuktiPeriod[];
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
 * Count rasis from start to end
 * @param start - Start rasi (0-11)
 * @param end - End rasi (0-11)
 * @param direction - 1 for forward, -1 for backward
 * @returns Count (1-12)
 */
function countRasis(start: number, end: number, direction: number): number {
  if (direction === 1) {
    return ((end - start + 12) % 12) + 1;
  } else {
    return ((start - end + 12) % 12) + 1;
  }
}

/**
 * Calculate Varnada Lagna using BV Raman method (simplified)
 * @param lagna - Lagna rasi (0-11)
 * @param horaLagna - Hora Lagna rasi (0-11)
 * @returns Varnada Lagna rasi (0-11)
 */
function getVarnadaLagna(lagna: number, horaLagna: number): number {
  const lagnaIsOdd = ODD_SIGNS.includes(lagna);
  const horaLagnaIsOdd = ODD_SIGNS.includes(horaLagna);

  // Count from Aries (0) or Pisces (11) based on oddity
  const count1 = lagnaIsOdd
    ? countRasis(0, lagna, 1)
    : countRasis(11, lagna, -1);

  const count2 = horaLagnaIsOdd
    ? countRasis(0, horaLagna, 1)
    : countRasis(11, horaLagna, -1);

  // Combine counts based on same/different oddity
  let count: number;
  if (lagnaIsOdd === horaLagnaIsOdd) {
    count = (count1 + count2) % 12;
  } else {
    count = (Math.max(count1, count2) - Math.min(count1, count2)) % 12;
  }

  // Calculate varnada lagna
  let varnadaLagna: number;
  if (lagnaIsOdd) {
    varnadaLagna = countRasis(1, count, 1);
  } else {
    varnadaLagna = countRasis(12, count, -1);
  }

  // Keep in 0-11 range
  return (varnadaLagna - 1 + 12) % 12;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Varnada Dasha periods
 * Uses stronger of Lagna and Hora Lagna as seed
 * Duration = (dasha_lord - varnada_lagna) % 12
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getVarnadaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): VarnadaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get Lagna
  const lagna = planetPositions[0]?.rasi ?? 0;

  // Get Hora Lagna
  const [horaLagna] = getHoraLagna(jd, place);

  // Get Varnada Lagna
  const varnadaLagna = getVarnadaLagna(lagna, horaLagna);

  // Determine seed: stronger of lagna and hora_lagna
  const dhasaSeed = getStrongerRasi(planetPositions, lagna, horaLagna);

  // Build progression based on even/odd sign of seed
  let dhasaLords: number[];
  if (EVEN_SIGNS.includes(dhasaSeed)) {
    // For even signs: reverse direction
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed - h + 12) % 12);
  } else {
    // For odd signs: forward direction
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  }

  const mahadashas: VarnadaDashaPeriod[] = [];
  const bhuktis: VarnadaBhuktiPeriod[] = [];
  let startJd = jd;

  for (const dhasaLord of dhasaLords) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    // Duration = (dasha_lord - varnada_lagna) % 12
    const duration = ((dhasaLord - varnadaLagna) % 12 + 12) % 12;

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
