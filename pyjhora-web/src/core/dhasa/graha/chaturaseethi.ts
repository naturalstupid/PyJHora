/**
 * Chaturaseethi Sama Dasha System
 * Ported from PyJHora chathuraaseethi_sama.py
 * 
 * 84-year dasha cycle with 7 lords (12 years each)
 * Applicability: The 10th lord in 10th house
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
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ChaturaseethiDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ChaturaseethiBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ChaturaseethiResult {
  mahadashas: ChaturaseethiDashaPeriod[];
  bhuktis?: ChaturaseethiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Chaturaseethi lords - all 7 lords have 12 years each
 * Order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
 * Total: 84 years (7 × 12)
 */
const CHATURASEETHI_LORDS = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN];

const CHATURASEETHI_YEARS = 12; // All lords have 12 years

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildNakshatraDict(seedStar = 15): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, CHATURASEETHI_LORDS[lordIndex]!);
    nak = (nak % 27) + 1;
    lordIndex = (lordIndex + 1) % 7;
  }
  
  return nakToLord;
}

export function getChaturaseethiDhasaLord(nakshatra: number, seedStar = 15): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? SUN;
  return [lord, CHATURASEETHI_YEARS];
}

export function getNextChaturaseethiLord(lord: number, direction = 1): number {
  const currentIndex = CHATURASEETHI_LORDS.indexOf(lord);
  if (currentIndex === -1) return CHATURASEETHI_LORDS[0]!;
  const nextIndex = ((currentIndex + direction) % 7 + 7) % 7;
  return CHATURASEETHI_LORDS[nextIndex]!;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function chaturaseethiDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 15,
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
  
  const [lord] = getChaturaseethiDhasaLord(nakNumber, seedStar);
  const periodElapsedDays = (remainder / oneStar) * CHATURASEETHI_YEARS * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, CHATURASEETHI_YEARS];
}

export function getChaturaseethiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
  } = {}
): ChaturaseethiResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 15,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1
  } = options;
  
  let [currentLord, startJd] = chaturaseethiDashaStart(jd, place, starPositionFromMoon, seedStar, startingPlanet);
  
  const mahadashas: ChaturaseethiDashaPeriod[] = [];
  const bhuktis: ChaturaseethiBhuktiPeriod[] = [];
  
  for (let i = 0; i < 7; i++) {
    const durationYears = CHATURASEETHI_YEARS;
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
        bhuktiLord = getNextChaturaseethiLord(bhuktiLord, 1);
      } else if (antardashaOption === 5 || antardashaOption === 6) {
        bhuktiLord = getNextChaturaseethiLord(bhuktiLord, -1);
      }
      
      const direction = (antardashaOption === 1 || antardashaOption === 3 || antardashaOption === 5) ? 1 : -1;
      const bhuktiDuration = durationYears / 7;
      let bhuktiStartJd = startJd;
      
      for (let j = 0; j < 7; j++) {
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
        bhuktiLord = getNextChaturaseethiLord(bhuktiLord, direction);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextChaturaseethiLord(currentLord);
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
