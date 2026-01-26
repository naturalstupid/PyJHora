/**
 * Chakra Dasha System
 * Ported from PyJHora chakra.py
 * 
 * Fixed 10-year duration cycles
 * Seed based on time of birth (dawn/day/dusk/night)
 */

import { RASI_NAMES_EN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ChakraDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ChakraBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ChakraResult {
  mahadashas: ChakraDashaPeriod[];
  bhuktis?: ChakraBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const DHASA_DURATION = 10; // Fixed 10 years per sign

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
 * Simplified seed determination
 * Uses lagna house as seed (full implementation would check dawn/day/dusk/night)
 */
function getDhasaSeed(planetPositions: PlanetPosition[]): number {
  // Use lagna house (first planet's rasi as proxy)
  const lagnaHouse = planetPositions[0]?.rasi ?? 0;
  return lagnaHouse;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Chakra Dasha periods
 * Fixed 10-year duration per sign
 */
export function getChakraDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): ChakraResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  
  const dhasaSeed = getDhasaSeed(planetPositions);
  
  // Build progression from seed
  const dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  
  const mahadashas: ChakraDashaPeriod[] = [];
  const bhuktis: ChakraBhuktiPeriod[] = [];
  let startJd = jd;
  
  for (const dhasaLord of dhasaLords) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;
    
    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: DHASA_DURATION
    });
    
    if (includeBhuktis) {
      const bhuktiDuration = DHASA_DURATION / 12;
      let bhuktiStartJd = startJd;
      
      for (let h = 0; h < 12; h++) {
        const bhuktiLord = (dhasaLord + h) % 12;
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
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
