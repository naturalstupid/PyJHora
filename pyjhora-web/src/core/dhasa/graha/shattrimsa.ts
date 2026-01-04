/**
 * Shattrimsa Sama Dasha System
 * Ported from PyJHora shattrimsa_sama.py
 * 
 * 36-year dasha cycle with 8 lords, run for 3 cycles = 108 years
 * Applicability: Lagna in Sun's hora in daytime or Moon's hora in nighttime
 */

import {
    JUPITER,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
    RAHU,
    SATURN,
    SIDEREAL_YEAR,
    SUN,
    VENUS
} from '../../constants';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ShattrimsaDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShattrimsaBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShattrimsaResult {
  mahadashas: ShattrimsaDashaPeriod[];
  bhuktis?: ShattrimsaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Shattrimsa lords and their durations
 * Order: Moon(1), Sun(2), Jupiter(3), Mars(4), Mercury(5), Saturn(6), Venus(7), Rahu(8)
 * Total per cycle: 36 years, 3 cycles = 108 years
 */
const SHATTRIMSA_LORDS = [MOON, SUN, JUPITER, MARS, MERCURY, SATURN, VENUS, RAHU];

const SHATTRIMSA_YEARS: Record<number, number> = {
  [MOON]: 1,
  [SUN]: 2,
  [JUPITER]: 3,
  [MARS]: 4,
  [MERCURY]: 5,
  [SATURN]: 6,
  [VENUS]: 7,
  [RAHU]: 8
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildNakshatraDict(seedStar = 22): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, SHATTRIMSA_LORDS[lordIndex]!);
    nak = (nak % 27) + 1;
    lordIndex = (lordIndex + 1) % 8;
  }
  
  return nakToLord;
}

export function getShattrimsaDhasaLord(nakshatra: number, seedStar = 22): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? MOON;
  const duration = SHATTRIMSA_YEARS[lord] ?? 1;
  return [lord, duration];
}

export function getNextShattrimsaLord(lord: number, direction = 1): number {
  const currentIndex = SHATTRIMSA_LORDS.indexOf(lord);
  if (currentIndex === -1) return SHATTRIMSA_LORDS[0]!;
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return SHATTRIMSA_LORDS[nextIndex]!;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function shattrimsaDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 22,
  startingPlanet = MOON
): [number, number, number] {
  const oneStar = 360 / 27;
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);
  
  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }
  
  const nakIndex = Math.floor(planetLong / oneStar);
  const nakNumber = nakIndex + 1;
  const remainder = planetLong % oneStar;
  
  const [lord, duration] = getShattrimsaDhasaLord(nakNumber, seedStar);
  const periodElapsedDays = (remainder / oneStar) * duration * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, duration];
}

export function getShattrimsaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
    cycles?: number;
  } = {}
): ShattrimsaResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 22,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1,
    cycles = 3  // Default 3 cycles = 108 years
  } = options;
  
  let [currentLord, startJd] = shattrimsaDashaStart(jd, place, starPositionFromMoon, seedStar, startingPlanet);
  
  const mahadashas: ShattrimsaDashaPeriod[] = [];
  const bhuktis: ShattrimsaBhuktiPeriod[] = [];
  
  for (let cycle = 0; cycle < cycles; cycle++) {
    for (let i = 0; i < 8; i++) {
      const durationYears = SHATTRIMSA_YEARS[currentLord] ?? 1;
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
        if (antardashaOption === 3 || antardashaOption === 4) {
          bhuktiLord = getNextShattrimsaLord(bhuktiLord, 1);
        } else if (antardashaOption === 5 || antardashaOption === 6) {
          bhuktiLord = getNextShattrimsaLord(bhuktiLord, -1);
        }
        
        const direction = (antardashaOption === 1 || antardashaOption === 3 || antardashaOption === 5) ? 1 : -1;
        const bhuktiDuration = durationYears / 8;
        let bhuktiStartJd = startJd;
        
        for (let j = 0; j < 8; j++) {
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
          bhuktiLord = getNextShattrimsaLord(bhuktiLord, direction);
        }
      }
      
      startJd += durationYears * YEAR_DURATION;
      currentLord = getNextShattrimsaLord(currentLord);
    }
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
