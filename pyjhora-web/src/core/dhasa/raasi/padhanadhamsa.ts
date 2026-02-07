/**
 * Padhanadhamsa Dasha System
 * Ported from PyJHora padhanadhamsa.py
 *
 * Padhanadhamsa uses Navamsa Arudha calculations:
 * 1. Get Arudha Lagna (A1) from D-1
 * 2. Get lord of A1 sign
 * 3. Get that lord's sign in D-9 (Navamsa)
 * 4. Stronger of that sign and its 7th house becomes seed
 * 5. Apply Narayana dasha logic
 *
 * Note: Python code mentions logic not fully implemented.
 */

import {
  KETU,
  RASI_NAMES_EN,
  SATURN,
  SIDEREAL_YEAR
} from '../../constants';
import { PlanetPosition } from '../../horoscope/charts';
import {
  getHouseOwnerFromPlanetPositions,
  getStrongerRasi,
  getPlanetToHouseDict
} from '../../horoscope/house';
import {
  getNarayanaDashaDuration,
  getNarayanaAntardhasa,
  getPlanetPositionsArray,
  NARAYANA_DHASA_NORMAL_PROGRESSION,
  NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION,
  NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION
} from './narayana';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface PadhanadhamsaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface PadhanadhamsaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface PadhanadhamsaResult {
  mahadashas: PadhanadhamsaDashaPeriod[];
  bhuktis?: PadhanadhamsaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

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
 * Count rasis from start to end (forward, inclusive)
 */
function countRasis(from: number, to: number): number {
  return ((to - from + 12) % 12) + 1;
}

/**
 * Calculate Bhava Arudha for a given house
 * Arudha = Lord's house + (count from house to lord - 1)
 * If Arudha is in 1st or 7th from house, add 10 houses
 */
function getBhavaArudha(
  planetPositions: PlanetPosition[],
  house: number
): number {
  const pToH = getPlanetToHouseDict(planetPositions);

  // Get lord of the house
  const lordOfHouse = getHouseOwnerFromPlanetPositions(planetPositions, house, false);

  // Get house where lord is placed
  const houseOfLord = pToH[lordOfHouse] ?? 0;

  // Count signs from house to lord
  const signsBetween = countRasis(house, houseOfLord);

  // Arudha = lord's house + (count - 1)
  let arudha = (houseOfLord + signsBetween - 1) % 12;

  // If Arudha is in 1st or 7th from house, add 10
  const signsFromHouse = countRasis(house, arudha);
  if (signsFromHouse === 1 || signsFromHouse === 7) {
    arudha = (arudha + 10) % 12;
  }

  return arudha;
}

/**
 * Get all Bhava Arudhas (A1 to A12)
 */
function getBhavaArudhas(planetPositions: PlanetPosition[]): number[] {
  const ascendant = planetPositions[0]?.rasi ?? 0;
  const arudhas: number[] = [];

  for (let i = 0; i < 12; i++) {
    const house = (ascendant + i) % 12;
    arudhas.push(getBhavaArudha(planetPositions, house));
  }

  return arudhas;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Padhanadhamsa Dasha periods
 * Uses Navamsa Arudha as seed with Narayana duration
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getPadhanadhamsaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): PadhanadhamsaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  // Get D-1 chart positions
  const d1Positions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get Arudha Lagna (A1) from D-1
  const bhavaArudhas = getBhavaArudhas(d1Positions);
  const arudhaSign = bhavaArudhas[0]!; // A1 - Arudha Lagna

  // Get lord of Arudha sign
  const lordOfArudha = getHouseOwnerFromPlanetPositions(d1Positions, arudhaSign, false);

  // Get D-9 (Navamsa) chart positions
  const d9Positions = getPlanetPositionsArray(jd, place, 9);

  // Get navamsa sign of the lord
  const lordNavamsaPosition = d9Positions.find(p => p.planet === lordOfArudha);
  const navamsaArudhaSign = lordNavamsaPosition?.rasi ?? 0;

  // Find stronger of navamsa arudha sign and its 7th
  const seventhHouse = (navamsaArudhaSign + 6) % 12;
  const dhasaSeedSign = getStrongerRasi(d9Positions, navamsaArudhaSign, seventhHouse);

  // Apply Narayana dasha logic from the seed sign
  const mahadashas: PadhanadhamsaDashaPeriod[] = [];
  const bhuktis: PadhanadhamsaBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  const firstCycleDurations: number[] = [];

  // Use Narayana progression with Saturn/Ketu exceptions (matching Python)
  const pToH = getPlanetToHouseDict(d1Positions);
  let dhasaProgression: number[];
  if (pToH[KETU] === dhasaSeedSign) {
    dhasaProgression = NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION[dhasaSeedSign]!;
  } else if (pToH[SATURN] === dhasaSeedSign) {
    dhasaProgression = NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION[dhasaSeedSign]!;
  } else {
    dhasaProgression = NARAYANA_DHASA_NORMAL_PROGRESSION[dhasaSeedSign]!;
  }

  // First cycle
  for (const dhasaLord of dhasaProgression) {
    const duration = getNarayanaDashaDuration(d1Positions, dhasaLord);
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
      const bhuktiLords = getNarayanaAntardhasa(d1Positions, dhasaLord);
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
    if (totalDuration >= 120) break;

    const dhasaLord = dhasaProgression[c]!;
    const duration = 12 - (firstCycleDurations[c] ?? 0);

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
      const bhuktiLords = getNarayanaAntardhasa(d1Positions, dhasaLord);
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
