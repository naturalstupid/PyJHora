/**
 * Drig Dasha System
 * Ported from PyJHora drig.py
 * 
 * Raasi-based dasha starting from 9th house using aspected kendras
 * Uses Narayana-style duration calculation
 */

import { EVEN_FOOTED_SIGNS, KETU, RASI_NAMES_EN, SATURN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface DrigDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DrigBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DrigResult {
  mahadashas: DrigDashaPeriod[];
  bhuktis?: DrigBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 120;
const ODD_SIGNS = [0, 2, 4, 6, 8, 10];

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
 * Get planet to house mapping
 */
function getPlanetToHouseMap(planetPositions: PlanetPosition[]): Map<number, number> {
  const map = new Map<number, number>();
  for (const pos of planetPositions) {
    map.set(pos.planet, pos.rasi);
  }
  return map;
}

/**
 * Get aspected kendras of a rasi
 * For Drig Dasha: returns kendras that the sign aspects
 */
function getAspectedKendras(sign: number, isEvenFooted: boolean): number[] {
  // Kendras from a sign: 1st, 4th, 7th, 10th from that sign
  // But aspected kendras are those aspected, not occupied
  // For even-footed: backward aspect pattern
  // For odd-footed: forward aspect pattern
  
  const direction = isEvenFooted ? -1 : 1;
  
  // Return 4th, 7th, 10th from sign (not 1st as that's the sign itself)
  return [
    (sign + direction * 3 + 12) % 12,  // 4th 
    (sign + direction * 6 + 12) % 12,  // 7th
    (sign + direction * 9 + 12) % 12   // 10th
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
    // Count backward
    dhasaPeriod = ((sign - houseOfLord) % 12 + 12) % 12;
  } else {
    // Count forward
    dhasaPeriod = ((houseOfLord - sign) % 12 + 12) % 12;
  }
  
  // Subtract 1 as per Narayana logic
  dhasaPeriod = dhasaPeriod === 0 ? 12 : dhasaPeriod;
  
  return dhasaPeriod;
}

/**
 * Calculate antardhasa progression
 */
function getAntardhasa(antardhasaSeedRasi: number, pToH: Map<number, number>): number[] {
  let direction = -1;
  
  if (pToH.get(SATURN) === antardhasaSeedRasi || ODD_SIGNS.includes(antardhasaSeedRasi)) {
    direction = 1;
  }
  
  if (pToH.get(KETU) === antardhasaSeedRasi) {
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
 * Get Drig Dasha periods
 * Starts from 9th house and uses aspected kendras
 */
export function getDrigDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): DrigResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseMap(planetPositions);
  
  // Ascendant is first planet position (Sun's sign as proxy)
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  
  // 9th house from ascendant (0-indexed: +8)
  const ninthHouse = (ascHouse + 8) % 12;
  
  // Build dasha progression: 9th, 10th, 11th houses and their aspected kendras
  const dhasaProgression: number[] = [];
  
  for (let i = 0; i < 3; i++) {
    const sign = (ninthHouse + i) % 12;
    const isEvenFooted = EVEN_FOOTED_SIGNS.includes(sign);
    const aspectedKendras = getAspectedKendras(sign, isEvenFooted);
    
    dhasaProgression.push(sign, ...aspectedKendras);
  }
  
  const mahadashas: DrigDashaPeriod[] = [];
  const bhuktis: DrigBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  const firstCycleDurations: number[] = [];
  
  // First cycle
  for (const dhasaLord of dhasaProgression) {
    const duration = getDhasaDuration(planetPositions, dhasaLord);
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
      const bhuktiLords = getAntardhasa(dhasaLord, pToH);
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
  
  // Second cycle (remainder to complete lifespan)
  for (let c = 0; c < dhasaProgression.length && totalDuration < HUMAN_LIFE_SPAN; c++) {
    const dhasaLord = dhasaProgression[c]!;
    const secondDuration = 12 - firstCycleDurations[c]!;
    
    if (secondDuration <= 0) continue;
    
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: secondDuration
    });
    
    if (includeBhuktis) {
      const bhuktiLords = getAntardhasa(dhasaLord, pToH);
      const bhuktiDuration = secondDuration / 12;
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
    
    startJd += secondDuration * YEAR_DURATION;
    totalDuration += secondDuration;
    
    if (totalDuration >= HUMAN_LIFE_SPAN) break;
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
