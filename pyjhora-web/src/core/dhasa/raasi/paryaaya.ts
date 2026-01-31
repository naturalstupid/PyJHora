/**
 * Paryaaya Dasha System
 * Ported from PyJHora paryaaya.py
 *
 * Paryaaya has three variations based on sign type:
 * - Dual/Chara Paryaaya: for dual signs (Gemini, Virgo, Sagittarius, Pisces)
 * - Movable/Ubhaya Paryaaya: for movable signs (Aries, Cancer, Libra, Capricorn)
 * - Fixed/Sthira Paryaaya: for fixed signs (Taurus, Leo, Scorpio, Aquarius)
 *
 * Duration is calculated based on house lord's position.
 * Default uses D-6 (Shashthamsa) chart.
 */

import {
  RASI_NAMES_EN,
  SIDEREAL_YEAR,
  EVEN_SIGNS,
  EVEN_FOOTED_SIGNS,
  DUAL_SIGNS,
  MOVABLE_SIGNS
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import {
  getHouseOwnerFromPlanetPositions,
  getStrongerRasi,
  getTrinesOfRaasi,
  getQuadrantsOfRaasi
} from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ParyaayaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ParyaayaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ParyaayaResult {
  mahadashas: ParyaayaDashaPeriod[];
  bhuktis?: ParyaayaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

// Progression patterns for each variation
// Dual/Chara: 1,5,9,2,6,10,3,7,11,4,8,12
const DUAL_PROGRESSION = [1, 5, 9, 2, 6, 10, 3, 7, 11, 4, 8, 12];
// Movable/Ubhaya: 1,4,7,10,2,5,8,11,3,6,9,12
const MOVABLE_PROGRESSION = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12];
// Fixed/Sthira: 1,7,2,8,3,9,4,10,5,11,6,12
const FIXED_PROGRESSION = [1, 7, 2, 8, 3, 9, 4, 10, 5, 11, 6, 12];

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
 * Calculate dhasa duration based on house lord's position
 */
function getDhasaDuration(
  planetPositions: PlanetPosition[],
  dhasaLord: number
): number {
  const lordOwner = getHouseOwnerFromPlanetPositions(planetPositions, dhasaLord);
  const lordPosition = planetPositions.find(p => p.planet === lordOwner);
  const houseOfLord = lordPosition?.rasi ?? 0;

  let dhasaPeriod: number;
  if (EVEN_SIGNS.includes(dhasaLord)) {
    dhasaPeriod = (dhasaLord + 13 - houseOfLord) % 12;
  } else {
    dhasaPeriod = (houseOfLord + 13 - dhasaLord) % 12;
  }

  return dhasaPeriod;
}

/**
 * Get dasha lords based on seed sign type
 */
function getDhasaLords(
  planetPositions: PlanetPosition[],
  dhasaSeed: number
): number[] {
  let strongerRasi: number;
  let progression: number[];

  if (DUAL_SIGNS.includes(dhasaSeed)) {
    // Dual/Chara Paryaaya - use trines
    const trines = getTrinesOfRaasi(dhasaSeed);
    strongerRasi = getStrongerRasi(planetPositions, trines[0]!, trines[1]!);
    strongerRasi = getStrongerRasi(planetPositions, strongerRasi, trines[2]!);
    progression = DUAL_PROGRESSION;
  } else if (MOVABLE_SIGNS.includes(dhasaSeed)) {
    // Movable/Ubhaya Paryaaya - use quadrants
    const quadrants = getQuadrantsOfRaasi(dhasaSeed);
    strongerRasi = getStrongerRasi(planetPositions, quadrants[0]!, quadrants[1]!);
    strongerRasi = getStrongerRasi(planetPositions, strongerRasi, quadrants[2]!);
    strongerRasi = getStrongerRasi(planetPositions, strongerRasi, quadrants[3]!);
    progression = MOVABLE_PROGRESSION;
  } else {
    // Fixed/Sthira Paryaaya - use 1st and 7th
    const seventhHouse = (dhasaSeed + 6) % 12;
    strongerRasi = getStrongerRasi(planetPositions, dhasaSeed, seventhHouse);
    progression = FIXED_PROGRESSION;
  }

  // Build dasha lords based on stronger rasi and progression
  if (EVEN_FOOTED_SIGNS.includes(strongerRasi)) {
    // Reverse direction for even-footed signs
    return progression.map(h => ((strongerRasi - h + 13) % 12 + 12) % 12);
  } else {
    // Forward direction
    return progression.map(h => (strongerRasi + h - 1) % 12);
  }
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Paryaaya Dasha periods
 * Three variations based on sign type of seed
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 6 for D-6)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 * @param options.useTribhagiVariation - Use Tribhagi variation (1/3 durations)
 * @param options.cycles - Number of cycles (default 2)
 */
export function getParyaayaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
    useTribhagiVariation?: boolean;
    cycles?: number;
  } = {}
): ParyaayaResult {
  const {
    divisionalChartFactor = 6, // Default to D-6
    includeBhuktis = true,
    useTribhagiVariation = false,
    cycles = 2
  } = options;

  const tribhagiFactor = useTribhagiVariation ? 1/3 : 1;
  const actualCycles = useTribhagiVariation ? cycles * 3 : cycles;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get ascendant house
  const ascHouse = planetPositions[0]?.rasi ?? 0;

  // Calculate dhasa seed: (ascendant + divisional_chart_factor - 1) % 12
  const dhasaSeed = (ascHouse + divisionalChartFactor - 1) % 12;

  // Get dasha lords based on seed
  const dhasaLords = getDhasaLords(planetPositions, dhasaSeed);

  const mahadashas: ParyaayaDashaPeriod[] = [];
  const bhuktis: ParyaayaBhuktiPeriod[] = [];
  let startJd = jd;

  for (let cycle = 0; cycle < actualCycles; cycle++) {
    for (const dhasaLord of dhasaLords) {
      const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
      const duration = getDhasaDuration(planetPositions, dhasaLord) * tribhagiFactor;

      mahadashas.push({
        rasi: dhasaLord,
        rasiName,
        startJd,
        startDate: formatJdAsDate(startJd),
        durationYears: duration
      });

      if (includeBhuktis) {
        // Bhuktis use the same dasha lord calculation
        const bhuktiLords = getDhasaLords(planetPositions, dhasaLord);
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
  }

  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
