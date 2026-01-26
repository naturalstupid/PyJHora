/**
 * Mandooka Dasha System
 * Ported from PyJHora mandooka.py
 * 
 * Raasi-based dasha with frog-like jumping progression
 * Uses KN Rao method for duration calculation
 */

import { RASI_NAMES_EN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface MandookaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface MandookaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface MandookaResult {
  mahadashas: MandookaDashaPeriod[];
  bhuktis?: MandookaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

// Even signs
const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];
// Even-footed signs (for backward counting)
const EVEN_FOOTED_SIGNS = [1, 2, 4, 5, 7, 8, 10, 11];

/**
 * Mandooka dasha order based on seed sign
 * Format: { seedSign: [forwardOrder, backwardOrder] }
 */
const DHASA_ORDER: Record<number, [number[], number[]]> = {
  0: [[0, 3, 6, 9, 2, 5, 8, 11, 1, 4, 7, 10], [0, 9, 6, 3, 2, 11, 8, 5, 1, 10, 7, 4]],
  3: [[3, 6, 9, 0, 2, 5, 8, 11, 1, 4, 7, 10], [3, 0, 9, 6, 2, 11, 8, 5, 1, 10, 7, 4]],
  6: [[6, 9, 0, 3, 2, 5, 8, 11, 1, 4, 7, 10], [6, 3, 0, 9, 2, 11, 8, 5, 1, 10, 7, 4]],
  9: [[9, 0, 3, 6, 2, 5, 8, 11, 1, 4, 7, 10], [9, 6, 3, 0, 2, 11, 8, 5, 1, 10, 7, 4]],
  2: [[2, 5, 8, 11, 1, 4, 7, 10, 0, 3, 6, 9], [2, 11, 8, 5, 1, 10, 7, 4, 0, 9, 6, 3]],
  5: [[5, 8, 11, 2, 1, 4, 7, 10, 0, 3, 6, 9], [5, 2, 11, 8, 1, 10, 7, 4, 0, 9, 6, 3]],
  8: [[8, 11, 2, 5, 1, 4, 7, 10, 0, 3, 6, 9], [8, 5, 2, 11, 1, 10, 7, 4, 0, 9, 6, 3]],
  11: [[11, 2, 5, 8, 1, 4, 7, 10, 0, 3, 6, 9], [11, 8, 5, 2, 1, 10, 7, 4, 0, 9, 6, 3]],
  1: [[1, 4, 7, 10, 0, 3, 6, 9, 2, 5, 8, 11], [1, 10, 7, 4, 0, 9, 6, 3, 2, 11, 8, 5]],
  4: [[4, 7, 10, 1, 0, 3, 6, 9, 2, 5, 8, 11], [4, 1, 10, 7, 0, 9, 6, 3, 2, 11, 8, 5]],
  7: [[7, 10, 1, 4, 0, 3, 6, 9, 2, 5, 8, 11], [7, 4, 1, 10, 0, 9, 6, 3, 2, 11, 8, 5]],
  10: [[10, 1, 4, 7, 0, 3, 6, 9, 2, 5, 8, 11], [10, 7, 4, 1, 0, 9, 6, 3, 2, 11, 8, 5]]
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get planet positions as PlanetPosition array
 */
function getPlanetPositionsArray(jd: number, place: Place, divisionalChartFactor: number): PlanetPosition[] {
  const d1Positions: PlanetPosition[] = [];
  
  // Get D1 positions for planets 0-8
  for (let planet = 0; planet <= 8; planet++) {
    const longitude = getPlanetLongitude(jd, place, planet);
    d1Positions.push({
      planet,
      rasi: Math.floor(longitude / 30),
      longitude: longitude % 30
    });
  }
  
  // Apply divisional chart if needed
  if (divisionalChartFactor > 1) {
    return getDivisionalChart(d1Positions, divisionalChartFactor);
  }
  
  return d1Positions;
}

/**
 * Format Julian Day as date string
 */
function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Calculate dasha duration using KN Rao method
 */
function getDhasaDurationKNRao(
  planetPositions: PlanetPosition[],
  sign: number
): number {
  const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, false);
  
  const lordPosition = planetPositions.find(p => p.planet === lordOfSign);
  if (!lordPosition) {
    return 12;
  }
  
  const houseOfLord = lordPosition.rasi;
  
  let dhasaPeriod: number;
  if (EVEN_FOOTED_SIGNS.includes(sign)) {
    dhasaPeriod = ((sign - houseOfLord + 1) % 12 + 12) % 12;
  } else {
    dhasaPeriod = ((houseOfLord - sign + 1) % 12 + 12) % 12;
  }
  
  if (dhasaPeriod <= 0 || houseOfLord === sign) {
    dhasaPeriod = 12;
  }
  if (houseOfLord === (sign + 6) % 12) {
    dhasaPeriod = 10;
  }
  
  return dhasaPeriod;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Mandooka Dasha periods
 */
export function getMandookaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): MandookaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  
  // Find ascendant (first position is Sun, but we need Asc)
  // For Raasi dashas, we use lagna which needs separate calculation
  // Simplified: use the first planet's rasi as a proxy
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  const seventhHouse = (ascHouse + 6) % 12;
  
  const dhasaSeed = getStrongerRasi(planetPositions, ascHouse, seventhHouse);
  
  const dir = EVEN_SIGNS.includes(dhasaSeed) ? 1 : 0;
  const dhasaLords = DHASA_ORDER[dhasaSeed]?.[dir] ?? DHASA_ORDER[0]![0];
  
  const mahadashas: MandookaDashaPeriod[] = [];
  const bhuktis: MandookaBhuktiPeriod[] = [];
  let startJd = jd;
  
  for (let i = 0; i < dhasaLords.length; i++) {
    const dhasaLord = dhasaLords[i]!;
    const duration = getDhasaDurationKNRao(planetPositions, dhasaLord);
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
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
      
      for (let j = 0; j < 12; j++) {
        const bhuktiLord = dhasaLords[(i + j) % 12]!;
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
