/**
 * Sataabdika (Shatabdika) Dasha System
 * Ported from PyJHora sataatbika.py
 * 
 * 100-year dasha cycle with 7 lords
 * Applicability: Lagna in the same sign in rasi & navamsa
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

export interface SataabdikaDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SataabdikaBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SataabdikaResult {
  mahadashas: SataabdikaDashaPeriod[];
  bhuktis?: SataabdikaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Sataabdika lords and their durations
 * Order: Sun(5), Moon(5), Venus(10), Mercury(10), Jupiter(20), Mars(20), Saturn(30)
 * Total: 100 years
 */
const SATAABDIKA_LORDS = [SUN, MOON, VENUS, MERCURY, JUPITER, MARS, SATURN];

const SATAABDIKA_YEARS: Record<number, number> = {
  [SUN]: 5,
  [MOON]: 5,
  [VENUS]: 10,
  [MERCURY]: 10,
  [JUPITER]: 20,
  [MARS]: 20,
  [SATURN]: 30
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildNakshatraDict(seedStar = 27): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, SATAABDIKA_LORDS[lordIndex]!);
    nak = (nak % 27) + 1;
    lordIndex = (lordIndex + 1) % 7;
  }
  
  return nakToLord;
}

export function getSataabdikaDhasaLord(nakshatra: number, seedStar = 27): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? SUN;
  const duration = SATAABDIKA_YEARS[lord] ?? 5;
  return [lord, duration];
}

export function getNextSataabdikaLord(lord: number, direction = 1): number {
  const currentIndex = SATAABDIKA_LORDS.indexOf(lord);
  if (currentIndex === -1) return SATAABDIKA_LORDS[0]!;
  const nextIndex = ((currentIndex + direction) % 7 + 7) % 7;
  return SATAABDIKA_LORDS[nextIndex]!;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function sataabdikaDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 27,
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
  
  const [lord, duration] = getSataabdikaDhasaLord(nakNumber, seedStar);
  const periodElapsedDays = (remainder / oneStar) * duration * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, duration];
}

export function getSataabdikaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
  } = {}
): SataabdikaResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 27,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1
  } = options;
  
  let [currentLord, startJd] = sataabdikaDashaStart(jd, place, starPositionFromMoon, seedStar, startingPlanet);
  
  const mahadashas: SataabdikaDashaPeriod[] = [];
  const bhuktis: SataabdikaBhuktiPeriod[] = [];
  
  for (let i = 0; i < 7; i++) {
    const durationYears = SATAABDIKA_YEARS[currentLord] ?? 5;
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
        bhuktiLord = getNextSataabdikaLord(bhuktiLord, 1);
      } else if (antardashaOption === 5 || antardashaOption === 6) {
        bhuktiLord = getNextSataabdikaLord(bhuktiLord, -1);
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
        bhuktiLord = getNextSataabdikaLord(bhuktiLord, direction);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextSataabdikaLord(currentLord);
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
