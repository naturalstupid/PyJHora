/**
 * Trikona Dasha System
 * Ported from PyJHora trikona.py
 * 
 * Raasi-based dasha using trine signs as seed
 * Uses Narayana-style duration calculation
 */

import { EVEN_FOOTED_SIGNS, RASI_NAMES_EN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface TrikonaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TrikonaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TrikonaResult {
  mahadashas: TrikonaDashaPeriod[];
  bhuktis?: TrikonaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get planet positions as PlanetPosition array
 */
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
 * Get trines (1st, 5th, 9th) of a sign
 */
function getTrines(sign: number): [number, number, number] {
  return [
    sign,
    (sign + 4) % 12,  // 5th from sign
    (sign + 8) % 12   // 9th from sign
  ];
}

/**
 * Calculate Narayana-style duration based on lord position
 */
function getDhasaDuration(
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
    dhasaPeriod = ((sign - houseOfLord) % 12 + 12) % 12;
  } else {
    dhasaPeriod = ((houseOfLord - sign) % 12 + 12) % 12;
  }
  
  dhasaPeriod = dhasaPeriod === 0 ? 12 : dhasaPeriod;
  
  return dhasaPeriod;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Trikona Dasha periods
 * Uses the strongest of the trine signs as seed
 */
export function getTrikonaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): TrikonaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  
  // Get ascendant
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  
  // Get trines of ascendant
  const trikonas = getTrines(ascHouse);
  
  // Find strongest of trines
  const ds1 = getStrongerRasi(planetPositions, trikonas[0], trikonas[1]);
  const dhasaSeedSign = getStrongerRasi(planetPositions, ds1, trikonas[2]);
  
  // Build dasha progression
  let dhasaLords: number[];
  if (EVEN_SIGNS.includes(dhasaSeedSign)) {
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeedSign - h + 12) % 12);
  } else {
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeedSign + h) % 12);
  }
  
  const mahadashas: TrikonaDashaPeriod[] = [];
  const bhuktis: TrikonaBhuktiPeriod[] = [];
  let startJd = jd;
  
  for (const dhasaLord of dhasaLords) {
    const duration = getDhasaDuration(planetPositions, dhasaLord);
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });
    
    if (includeBhuktis) {
      // Bhuktis based on even/odd sign direction
      let bhuktiLords: number[];
      if (EVEN_SIGNS.includes(dhasaLord)) {
        bhuktiLords = Array.from({ length: 12 }, (_, h) => (dhasaLord - h + 12) % 12);
      } else {
        bhuktiLords = Array.from({ length: 12 }, (_, h) => (dhasaLord + h) % 12);
      }
      
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
