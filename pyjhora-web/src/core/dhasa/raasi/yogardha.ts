/**
 * Yogardha Dasha System
 * Ported from PyJHora yogardha.py
 * 
 * Duration = Average of Chara (movable) and Sthira (fixed) durations
 * Chara: 7/8/9 based on lord placement
 * Sthira: 7/8/9 based on sign type
 */

import { EVEN_FOOTED_SIGNS, HOUSE_STRENGTHS_OF_PLANETS, RASI_NAMES_EN, SIDEREAL_YEAR, STRENGTH_DEBILITATED, STRENGTH_EXALTED } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface YogardhaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface YogardhaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface YogardhaResult {
  mahadashas: YogardhaDashaPeriod[];
  bhuktis?: YogardhaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const EVEN_SIGNS = [1, 3, 5, 7, 9, 11];
const MOVABLE_SIGNS = [0, 3, 6, 9];
const FIXED_SIGNS = [1, 4, 7, 10];

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
 * Chara duration: based on lord's position relative to sign
 */
function getCharaDuration(planetPositions: PlanetPosition[], sign: number): number {
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

  // Exalted lord: +1 year; Debilitated lord: -1 year
  const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
  if (strength === STRENGTH_EXALTED) {
    dhasaPeriod += 1;
  } else if (strength === STRENGTH_DEBILITATED) {
    dhasaPeriod -= 1;
  }

  return dhasaPeriod;
}

/**
 * Sthira duration: fixed based on sign type
 */
function getSthiraDuration(sign: number): number {
  if (MOVABLE_SIGNS.includes(sign)) return 7;
  if (FIXED_SIGNS.includes(sign)) return 8;
  return 9; // Dual signs
}

/**
 * Yogardha duration = average of Chara and Sthira
 */
function getYogardhaDuration(planetPositions: PlanetPosition[], sign: number): number {
  const chara = getCharaDuration(planetPositions, sign);
  const sthira = getSthiraDuration(sign);
  return (chara + sthira) / 2;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Yogardha Dasha periods
 */
export function getYogardhaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): YogardhaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  
  const ascHouse = planetPositions[0]?.rasi ?? 0;
  const seventhHouse = (ascHouse + 6) % 12;
  
  const dhasaSeed = getStrongerRasi(planetPositions, ascHouse, seventhHouse);
  
  // Build progression based on even/odd
  let dhasaLords: number[];
  if (EVEN_SIGNS.includes(dhasaSeed)) {
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed - h + 12) % 12);
  } else {
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  }
  
  const mahadashas: YogardhaDashaPeriod[] = [];
  const bhuktis: YogardhaBhuktiPeriod[] = [];
  let startJd = jd;
  
  for (const dhasaLord of dhasaLords) {
    const duration = getYogardhaDuration(planetPositions, dhasaLord);
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });
    
    if (includeBhuktis) {
      // Bhuktis follow chara antardhasa pattern
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
