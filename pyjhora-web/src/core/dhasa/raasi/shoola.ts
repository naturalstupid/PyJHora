/**
 * Shoola Dasha System
 * Ported from PyJHora shoola.py
 * 
 * Raasi-based dasha with fixed 9-year duration
 * Direction always forward, uses stronger of Asc vs 7th
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

export interface ShoolaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShoolaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShoolaResult {
  mahadashas: ShoolaDashaPeriod[];
  bhuktis?: ShoolaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const DHASA_DURATION = 9;
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
 * Get Shoola Dasha periods
 */
export function getShoolaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): ShoolaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseMap(planetPositions);
  
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  const seventhHouse = (ascHouse + 6) % 12;
  
  const dhasaSeedSign = getStrongerRasi(planetPositions, ascHouse, seventhHouse);
  
  const direction = 1;
  const dhasaProgression = Array.from({ length: 12 }, (_, k) => 
    (dhasaSeedSign + direction * k) % 12
  );
  
  const mahadashas: ShoolaDashaPeriod[] = [];
  const bhuktis: ShoolaBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  
  // First cycle
  for (const dhasaLord of dhasaProgression) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: DHASA_DURATION
    });
    
    if (includeBhuktis) {
      const bhuktiLords = getAntardhasa(dhasaLord, pToH);
      const bhuktiDuration = DHASA_DURATION / 12;
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
    
    startJd += DHASA_DURATION * YEAR_DURATION;
    totalDuration += DHASA_DURATION;
  }
  
  // Second cycle
  for (let c = 0; c < dhasaProgression.length && totalDuration < HUMAN_LIFE_SPAN; c++) {
    const dhasaLord = dhasaProgression[c]!;
    const dhasaDuration = 12 - DHASA_DURATION;
    
    if (dhasaDuration <= 0) continue;
    
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: dhasaDuration
    });
    
    if (includeBhuktis) {
      const bhuktiLords = getAntardhasa(dhasaLord, pToH);
      const bhuktiDuration = dhasaDuration / 12;
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
    
    startJd += dhasaDuration * YEAR_DURATION;
    totalDuration += dhasaDuration;
    
    if (totalDuration >= HUMAN_LIFE_SPAN) break;
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
