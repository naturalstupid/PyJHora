/**
 * Kendradhi Rasi Dasha System
 * Ported from PyJHora kendradhi_rasi.py
 * 
 * Also called Lagna Kendradi Raasi Dhasa
 * Uses kendras from stronger of Asc/7th as progression
 */

import { EVEN_FOOTED_SIGNS, KETU, RASI_NAMES_EN, SATURN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface KendradhiDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KendradhiBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KendradhiResult {
  mahadashas: KendradhiDashaPeriod[];
  bhuktis?: KendradhiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const HUMAN_LIFE_SPAN = 120;
const ODD_SIGNS = [0, 2, 4, 6, 8, 10];
const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];

// Kendras: 1,4,7,10 from each sign (we use 3 groups)
const KENDRAS = [1, 4, 7, 10, 2, 5, 8, 11, 3, 6, 9, 12];

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
 * Get Kendradhi Rasi Dasha periods
 * Uses kendras from stronger of Asc/7th
 */
export function getKendradhiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): KendradhiResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseMap(planetPositions);
  
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  const seventhHouse = (ascHouse + 6) % 12;
  
  const dhasaSeedSign = getStrongerRasi(planetPositions, ascHouse, seventhHouse);
  
  // Determine direction based on Saturn/Ketu placement or odd/even
  let direction: number;
  if (pToH.get(SATURN) === dhasaSeedSign) {
    direction = 1;
  } else if (pToH.get(KETU) === dhasaSeedSign) {
    direction = -1;
  } else if (ODD_SIGNS.includes(dhasaSeedSign)) {
    direction = 1;
  } else {
    direction = -1;
  }
  
  // Build kendra progression (1,4,7,10,2,5,8,11,3,6,9,12)
  const dhasaProgression = KENDRAS.map(k => 
    (dhasaSeedSign + direction * (k - 1) + 12) % 12
  );
  
  const mahadashas: KendradhiDashaPeriod[] = [];
  const bhuktis: KendradhiBhuktiPeriod[] = [];
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
