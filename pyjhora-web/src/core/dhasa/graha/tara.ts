/**
 * Tara Dasha System
 * Ported from PyJHora tara.py
 * 
 * 120-year cycle based on planets in kendras
 * Applicability: All four quadrants are occupied
 */

import {
    JUPITER,
    KETU,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
    RAHU,
    SATURN,
    SIDEREAL_YEAR,
    SUN,
    VENUS
} from '../../constants';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface TaraDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TaraBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TaraResult {
  mahadashas: TaraDashaPeriod[];
  bhuktis?: TaraBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Tara dasha periods - Sanjay Rath method
 * Order: Venus(20), Moon(10), Ketu(7), Saturn(19), Jupiter(16), Mercury(17), Rahu(18), Mars(7), Sun(6)
 * Total: 120 years
 */
const TARA_LORDS_SANJAY = [VENUS, MOON, KETU, SATURN, JUPITER, MERCURY, RAHU, MARS, SUN];

const TARA_YEARS_SANJAY: Record<number, number> = {
  [VENUS]: 20,
  [MOON]: 10,
  [KETU]: 7,
  [SATURN]: 19,
  [JUPITER]: 16,
  [MERCURY]: 17,
  [RAHU]: 18,
  [MARS]: 7,
  [SUN]: 6
};

/** Parasara method order */
const TARA_LORDS_PARASARA = [VENUS, SUN, MOON, MARS, RAHU, JUPITER, SATURN, MERCURY, KETU];

const TARA_YEARS_PARASARA: Record<number, number> = {
  [VENUS]: 20,
  [SUN]: 6,
  [MOON]: 10,
  [MARS]: 7,
  [RAHU]: 18,
  [JUPITER]: 16,
  [SATURN]: 19,
  [MERCURY]: 17,
  [KETU]: 7
};

const HUMAN_LIFE_SPAN = 120; // Sum of all periods

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function getNextTaraLord(lord: number, method: 1 | 2 = 1, direction = 1): number {
  const lords = method === 1 ? TARA_LORDS_SANJAY : TARA_LORDS_PARASARA;
  const currentIndex = lords.indexOf(lord);
  if (currentIndex === -1) return lords[0]!;
  const nextIndex = ((currentIndex + direction) % 9 + 9) % 9;
  return lords[nextIndex]!;
}

/**
 * Get complete Tara dasha data
 */
export function getTaraDashaBhukti(
  jd: number,
  _place: Place,
  options: {
    includeBhuktis?: boolean;
    method?: 1 | 2;  // 1 = Sanjay Rath, 2 = Parasara
    startingLord?: number;
  } = {}
): TaraResult {
  const {
    includeBhuktis = true,
    method = 1,
    startingLord = VENUS
  } = options;
  
  const lords = method === 1 ? TARA_LORDS_SANJAY : TARA_LORDS_PARASARA;
  const years = method === 1 ? TARA_YEARS_SANJAY : TARA_YEARS_PARASARA;
  
  // Find starting index
  let currentLord = startingLord;
  let startJd = jd;
  
  const mahadashas: TaraDashaPeriod[] = [];
  const bhuktis: TaraBhuktiPeriod[] = [];
  
  for (let i = 0; i < 9; i++) {
    const durationYears = years[currentLord] ?? 10;
    const lordName = PLANET_NAMES_EN[currentLord] ?? `Planet ${currentLord}`;
    
    mahadashas.push({
      lord: currentLord,
      lordName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears
    });
    
    if (includeBhuktis) {
      let bhuktiLord = currentLord;
      let bhuktiStartJd = startJd;
      
      for (let j = 0; j < 9; j++) {
        const bhuktiYears = years[bhuktiLord] ?? 10;
        const bhuktiDuration = (bhuktiYears * durationYears) / HUMAN_LIFE_SPAN;
        const bhuktiLordName = PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`;
        
        bhuktis.push({
          dashaLord: currentLord,
          bhuktiLord,
          bhuktiLordName,
          startJd: bhuktiStartJd,
          startDate: formatJdAsDate(bhuktiStartJd),
          durationYears: bhuktiDuration
        });
        bhuktiStartJd += bhuktiDuration * YEAR_DURATION;
        bhuktiLord = getNextTaraLord(bhuktiLord, method);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextTaraLord(currentLord, method);
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
