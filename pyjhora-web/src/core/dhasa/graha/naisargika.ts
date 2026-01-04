/**
 * Naisargika Dasha System
 * Ported from PyJHora naisargika.py
 * 
 * Fixed age-based dasha system (132 years total)
 * Periods: Moon(1), Mars(2), Mercury(9), Venus(20), Jupiter(18), Sun(20), Saturn(50), Lagna(12)
 */

import {
    JUPITER,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
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

export interface NaisargikaDashaPeriod {
  lord: number | 'L';  // 'L' for Lagna
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NaisargikaBhuktiPeriod {
  dashaLord: number | 'L';
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NaisargikaResult {
  mahadashas: NaisargikaDashaPeriod[];
  bhuktis?: NaisargikaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Naisargika lords and their durations (age-based sequence)
 * Moon(1), Mars(2), Mercury(9), Venus(20), Jupiter(18), Sun(20), Saturn(50), Lagna(12)
 * Total: 132 years
 */
const NAISARGIKA_SEQUENCE: Array<{ lord: number | 'L'; years: number }> = [
  { lord: MOON, years: 1 },
  { lord: MARS, years: 2 },
  { lord: MERCURY, years: 9 },
  { lord: VENUS, years: 20 },
  { lord: JUPITER, years: 18 },
  { lord: SUN, years: 20 },
  { lord: SATURN, years: 50 },
  { lord: 'L', years: 12 }  // Lagna
];

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Get complete Naisargika dasha data
 * This is age-based: starts from birth and runs through fixed periods
 */
export function getNaisargikaDashaBhukti(
  jd: number,
  _place: Place,
  options: {
    includeBhuktis?: boolean;
  } = {}
): NaisargikaResult {
  const { includeBhuktis = false } = options;
  
  let startJd = jd; // Starts from birth
  
  const mahadashas: NaisargikaDashaPeriod[] = [];
  const bhuktis: NaisargikaBhuktiPeriod[] = [];
  
  for (const entry of NAISARGIKA_SEQUENCE) {
    const lordName = entry.lord === 'L' ? 'Lagna' : (PLANET_NAMES_EN[entry.lord] ?? `Planet ${entry.lord}`);
    
    mahadashas.push({
      lord: entry.lord,
      lordName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: entry.years
    });
    
    if (includeBhuktis) {
      // Bhuktis are based on planets in kendras from dasha lord
      // Simplified: divide equally among 7 planets
      const bhuktiDuration = entry.years / 7;
      let bhuktiStartJd = startJd;
      
      for (let j = 0; j < 7; j++) {
        const bhuktiLord = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN][j]!;
        const bhuktiLordName = PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`;
        
        bhuktis.push({
          dashaLord: entry.lord,
          bhuktiLord,
          bhuktiLordName,
          startJd: bhuktiStartJd,
          startDate: formatJdAsDate(bhuktiStartJd),
          durationYears: bhuktiDuration
        });
        bhuktiStartJd += bhuktiDuration * YEAR_DURATION;
      }
    }
    
    startJd += entry.years * YEAR_DURATION;
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
