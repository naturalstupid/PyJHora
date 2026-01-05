/**
 * Dwadasottari Dasha System
 * Ported from PyJHora dwadasottari.py
 * 
 * 112-year dasha cycle with 8 lords
 * Applicability: Lagna in Taurus/Libra navamsa
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
    SUN
} from '../../constants';
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface DwadasottariDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DwadasottariBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DwadasottariResult {
  mahadashas: DwadasottariDashaPeriod[];
  bhuktis?: DwadasottariBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Dwadasottari lords and their durations
 * Order: Sun(7), Jupiter(9), Ketu(11), Mercury(13), Rahu(15), Mars(17), Saturn(19), Moon(21)
 * Total: 112 years
 */
const DWADASOTTARI_LORDS = [SUN, JUPITER, KETU, MERCURY, RAHU, MARS, SATURN, MOON];

const DWADASOTTARI_YEARS: Record<number, number> = {
  [SUN]: 7,
  [JUPITER]: 9,
  [KETU]: 11,
  [MERCURY]: 13,
  [RAHU]: 15,
  [MARS]: 17,
  [SATURN]: 19,
  [MOON]: 21
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildNakshatraDict(seedStar = 27): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  // Count direction is -1 (anti-zodiac) for this system
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, DWADASOTTARI_LORDS[lordIndex]!);
    nak = ((nak - 2 + 27) % 27) + 1; // Move backwards
    lordIndex = (lordIndex + 1) % 8;
  }
  
  return nakToLord;
}

export function getDwadasottariDhasaLord(nakshatra: number, seedStar = 27): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? SUN;
  const duration = DWADASOTTARI_YEARS[lord] ?? 7;
  return [lord, duration];
}

export function getNextDwadasottariLord(lord: number, direction = 1): number {
  const currentIndex = DWADASOTTARI_LORDS.indexOf(lord);
  if (currentIndex === -1) return DWADASOTTARI_LORDS[0]!;
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return DWADASOTTARI_LORDS[nextIndex]!;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function dwadasottariDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 27,
  startingPlanet = MOON,
  divisionalChartFactor = 1
): [number, number, number] {
  const oneStar = 360 / 27;
  let planetLong = getPlanetLongitude(jd, place, startingPlanet);
  
  if (divisionalChartFactor > 1) {
    const d1Pos: PlanetPosition = { planet: startingPlanet, rasi: Math.floor(planetLong / 30), longitude: planetLong % 30 };
    const vargaPos = getDivisionalChart([d1Pos], divisionalChartFactor)[0];
    if (vargaPos) {
      planetLong = vargaPos.rasi * 30 + vargaPos.longitude;
    }
  }

  if (startingPlanet === MOON) {
    planetLong += (starPositionFromMoon - 1) * oneStar;
    planetLong = normalizeDegrees(planetLong);
  }
  
  const nakIndex = Math.floor(planetLong / oneStar);
  const nakNumber = nakIndex + 1;
  const remainder = planetLong % oneStar;
  
  const [lord, duration] = getDwadasottariDhasaLord(nakNumber, seedStar);
  const periodElapsedDays = (remainder / oneStar) * duration * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, duration];
}

export function getDwadasottariDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
    divisionalChartFactor?: number;
  } = {}
): DwadasottariResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 27,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1,
    divisionalChartFactor = 1
  } = options;
  
  let [currentLord, startJd] = dwadasottariDashaStart(jd, place, starPositionFromMoon, seedStar, startingPlanet, divisionalChartFactor);
  
  const mahadashas: DwadasottariDashaPeriod[] = [];
  const bhuktis: DwadasottariBhuktiPeriod[] = [];
  
  for (let i = 0; i < 8; i++) {
    const durationYears = DWADASOTTARI_YEARS[currentLord] ?? 7;
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
        bhuktiLord = getNextDwadasottariLord(bhuktiLord, 1);
      } else if (antardashaOption === 5 || antardashaOption === 6) {
        bhuktiLord = getNextDwadasottariLord(bhuktiLord, -1);
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
        bhuktiLord = getNextDwadasottariLord(bhuktiLord, direction);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextDwadasottariLord(currentLord);
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
