/**
 * Navamsa Dasha System
 * Ported from PyJHora navamsa.py
 * 
 * Fixed 9-year duration per sign.
 * Seed determined by mapping from Lagna.
 */

import { EVEN_SIGNS, RASI_NAMES_EN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface NavamsaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NavamsaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NavamsaResult {
  mahadashas: NavamsaDashaPeriod[];
  bhuktis?: NavamsaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/**
 * Mapping from Lagna to Start Seed
 * Aries(0)->Aries(0), Taurus(1)->Leo(4), Gemini(2)->Libra(6), Cancer(3)->Aquarius(10)
 * Pattern repeats every 4 signs?
 * 0, 4, 6, 10
 */
const DHASA_ADHIPATI_LIST = [0, 4, 6, 10, 0, 4, 6, 10, 0, 4, 6, 10];

/**
 * Mapping from Dasha Lord to Antardasha Seed
 */
const ANTARDHASA_LIST = [6, 0, 8, 10, 4, 8, 6, 0, 8, 10, 4, 8];

const DHASA_DURATION = 9; // Fixed 9 years

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

// ============================================================================
// MAIN FUNCTION
// ============================================================================

export function getNavamsaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): NavamsaResult {
  const {
    divisionalChartFactor = 9, 
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  
  const lagna = planetPositions.find(p => p.planet === 0)?.rasi ?? 0; // Using Sun as proxy
  const dhasaSeed = DHASA_ADHIPATI_LIST[lagna]!;
  
  // Build Progression
  let dhasaLords: number[];
  
  if (EVEN_SIGNS.includes(dhasaSeed)) {
    // Start from 7th (seed+6), go backwards (-h)
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + 6 - h + 12) % 12);
  } else {
    // Start from seed, go forward (+h)
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  }
  
  const mahadashas: NavamsaDashaPeriod[] = [];
  const bhuktis: NavamsaBhuktiPeriod[] = [];
  let startJd = jd;
  
  for (const dhasaLord of dhasaLords) {
    const duration = DHASA_DURATION;
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });
    
    if (includeBhuktis) {
      const bhuktiSeed = ANTARDHASA_LIST[dhasaLord]!;
      // Bhuktis are forward from bhuktiSeed
      const bhuktiLords = Array.from({ length: 12 }, (_, h) => (bhuktiSeed + h) % 12);
      
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
