/**
 * Nirayana Shoola Dasha System
 * Ported from PyJHora nirayana.py
 * 
 * Uses 2nd and 8th houses as seed
 * Fixed durations: Movable=7, Fixed=8, Dual=9
 */

import { KETU, RASI_NAMES_EN, SATURN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface NirayanaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NirayanaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NirayanaShoolaResult {
  mahadashas: NirayanaDashaPeriod[];
  bhuktis?: NirayanaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 120;
const ODD_SIGNS = [0, 2, 4, 6, 8, 10];
const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];
const MOVABLE_SIGNS = [0, 3, 6, 9];
const FIXED_SIGNS = [1, 4, 7, 10];
const DUAL_SIGNS = [2, 5, 8, 11];

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

function getPlanetToHouseMap(planetPositions: PlanetPosition[]): Map<number, number> {
  const map = new Map<number, number>();
  for (const pos of planetPositions) {
    map.set(pos.planet, pos.rasi);
  }
  return map;
}

/**
 * Get fixed duration based on sign type
 */
function getSignDuration(sign: number): number {
  if (MOVABLE_SIGNS.includes(sign)) return 7;
  if (FIXED_SIGNS.includes(sign)) return 8;
  return 9; // Dual signs
}

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
 * Get Nirayana Shoola Dasha periods
 * Uses 2nd and 8th houses as seed
 */
export function getNirayanaShoolaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): NirayanaShoolaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseMap(planetPositions);
  
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  
  // 2nd and 8th houses (0-indexed: +1 and +7)
  const secondHouse = (ascHouse + 1) % 12;
  const eighthHouse = (ascHouse + 7) % 12;
  
  const dhasaSeedSign = getStrongerRasi(planetPositions, secondHouse, eighthHouse);
  
  // Direction based on even/odd
  const direction = EVEN_SIGNS.includes(dhasaSeedSign) ? -1 : 1;
  
  // Build progression
  const dhasaProgression = Array.from({ length: 12 }, (_, k) => 
    (dhasaSeedSign + direction * k + 12) % 12
  );
  
  const mahadashas: NirayanaDashaPeriod[] = [];
  const bhuktis: NirayanaBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  const firstCycleDurations: number[] = [];
  
  // First cycle
  for (const dhasaLord of dhasaProgression) {
    const duration = getSignDuration(dhasaLord);
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
  
  // Second cycle
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
