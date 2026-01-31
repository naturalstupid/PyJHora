/**
 * Sudasa Dasha System
 * Ported from PyJHora sudasa.py
 *
 * Sudasa uses Sree Lagna as the seed. Duration is calculated using
 * Narayana dasha logic. Two cycles are used to cover the life span.
 *
 * Note: Python code mentions that book examples match but JHora differs.
 */

import {
  RASI_NAMES_EN,
  SIDEREAL_YEAR,
  EVEN_SIGNS,
  ODD_SIGNS,
  SATURN,
  KETU
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getPlanetToHouseDict } from '../../horoscope/house';
import { getPlanetLongitude, getSreeLagna } from '../../panchanga/drik';
import { getNarayanaDashaDuration } from './narayana';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface SudasaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SudasaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SudasaResult {
  mahadashas: SudasaDashaPeriod[];
  bhuktis?: SudasaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 120; // Standard paramayush

// Kendra progression: 1,4,7,10,2,5,8,11,3,6,9,12
const KENDRA_PROGRESSION = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12];

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
 * Get antardhasa progression based on seed rasi and planet positions
 */
function getAntardhasa(
  antardhasaSeedRasi: number,
  planetPositions: PlanetPosition[]
): number[] {
  const pToH = getPlanetToHouseDict(planetPositions);

  let direction = -1;
  // Forward if Saturn is in seed or if seed is odd sign
  if (pToH[SATURN] === antardhasaSeedRasi || ODD_SIGNS.includes(antardhasaSeedRasi)) {
    direction = 1;
  }
  // Reverse if Ketu is in seed
  if (pToH[KETU] === antardhasaSeedRasi) {
    direction *= -1;
  }

  return Array.from({ length: 12 }, (_, i) =>
    ((antardhasaSeedRasi + direction * i) % 12 + 12) % 12
  );
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Sudasa Dasha periods
 * Uses Sree Lagna as seed with Narayana-style duration calculation
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getSudasaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): SudasaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseDict(planetPositions);

  // Get Sree Lagna
  const [sreeLagnaHouse, sreeLagnaLongitude] = getSreeLagna(jd, place);

  // Fraction remaining at birth for first dasha
  const slFracLeft = (30 - sreeLagnaLongitude) / 30;

  // Determine direction based on even/odd sign
  let direction = 1;
  if (EVEN_SIGNS.includes(sreeLagnaHouse)) {
    direction = -1;
  }

  // Saturn/Ketu exceptions
  if (pToH[SATURN] === sreeLagnaHouse) {
    direction = 1;
  } else if (pToH[KETU] === sreeLagnaHouse) {
    direction *= -1;
  }

  // Build progression using kendra pattern
  const dhasaProgression = KENDRA_PROGRESSION.map(k =>
    ((sreeLagnaHouse + direction * (k - 1)) % 12 + 12) % 12
  );

  const mahadashas: SudasaDashaPeriod[] = [];
  const bhuktis: SudasaBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  const firstCycleDurations: number[] = [];

  // First cycle
  for (let s = 0; s < dhasaProgression.length; s++) {
    const dhasaLord = dhasaProgression[s]!;
    let duration = getNarayanaDashaDuration(planetPositions, dhasaLord);

    // First dasha uses fraction remaining
    if (s === 0) {
      duration *= slFracLeft;
    }

    duration = Math.round(duration * 100) / 100;
    firstCycleDurations.push(duration);

    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });

    if (includeBhuktis) {
      const bhuktiLords = getAntardhasa(dhasaLord, planetPositions);
      const bhuktiDuration = duration / 12;
      let bhuktiStartJd = startJd;

      for (const bhuktiLord of bhuktiLords) {
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
    totalDuration += duration;
  }

  // Second cycle (complement to 12 years each)
  for (let c = 0; c < dhasaProgression.length; c++) {
    if (totalDuration >= HUMAN_LIFE_SPAN) break;

    const dhasaLord = dhasaProgression[c]!;
    const firstDuration = c === 0
      ? getNarayanaDashaDuration(planetPositions, dhasaLord)
      : firstCycleDurations[c]!;

    let duration = 12 - firstDuration;
    duration = Math.round(duration * 100) / 100;

    if (duration <= 0) continue;

    totalDuration += duration;

    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });

    if (includeBhuktis) {
      const bhuktiLords = getAntardhasa(dhasaLord, planetPositions);
      const bhuktiDuration = duration / 12;
      let bhuktiStartJd = startJd;

      for (const bhuktiLord of bhuktiLords) {
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
