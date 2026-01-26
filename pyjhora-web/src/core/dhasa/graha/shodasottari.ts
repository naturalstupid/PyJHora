/**
 * Shodasottari Dasha System
 * Ported from PyJHora shodasottari.py
 * 
 * 116-year dasha cycle with 8 lords
 * Applicability: Lagna in Sun's hora in Sukla paksha or Lagna in Moon's hora in Krishna paksha
 */

import {
    JUPITER,
    KETU,
    MARS, MERCURY,
    MOON,
    PLANET_NAMES_EN,
    SATURN,
    SIDEREAL_YEAR,
    SUN,
    VENUS
} from '../../constants';
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface ShodasottariDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShodasottariBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface ShodasottariResult {
  mahadashas: ShodasottariDashaPeriod[];
  bhuktis?: ShodasottariBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

/** Year duration in days */
const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Shodasottari lords and their durations
 * Order: Sun(11), Mars(12), Jupiter(13), Saturn(14), Ketu(15), Moon(16), Mercury(17), Venus(18)
 * Total: 116 years
 */
const SHODASOTTARI_LORDS = [SUN, MARS, JUPITER, SATURN, KETU, MOON, MERCURY, VENUS];

/** Dasha period for each lord in years */
const SHODASOTTARI_YEARS: Record<number, number> = {
  [SUN]: 11,
  [MARS]: 12,
  [JUPITER]: 13,
  [SATURN]: 14,
  [KETU]: 15,
  [MOON]: 16,
  [MERCURY]: 17,
  [VENUS]: 18
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Build nakshatra to lord mapping based on seed star
 * Lords cycle through nakshatras starting from seed star
 */
function buildNakshatraDict(seedStar = 8): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, SHODASOTTARI_LORDS[lordIndex]!);
    nak = ((nak) % 27) + 1;
    lordIndex = (lordIndex + 1) % 8;
  }
  
  return nakToLord;
}

/**
 * Get the Shodasottari lord for a nakshatra
 */
export function getShodasottariDhasaLord(nakshatra: number, seedStar = 8): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? SUN;
  const duration = SHODASOTTARI_YEARS[lord] ?? 11;
  
  return [lord, duration];
}

/**
 * Get the next lord in the Shodasottari sequence
 */
export function getNextShodasottariLord(lord: number, direction = 1): number {
  const currentIndex = SHODASOTTARI_LORDS.indexOf(lord);
  if (currentIndex === -1) {
    return SHODASOTTARI_LORDS[0]!;
  }
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return SHODASOTTARI_LORDS[nextIndex]!;
}

/**
 * Format Julian Day as date string
 */
function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

// ============================================================================
// DASHA START DATE CALCULATION
// ============================================================================

/**
 * Calculate the start date of the Shodasottari mahadasha at birth
 */
export function shodasottariDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 8,
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
  
  const [lord, duration] = getShodasottariDhasaLord(nakNumber, seedStar);
  
  const periodElapsedFraction = remainder / oneStar;
  const periodElapsedDays = periodElapsedFraction * duration * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, duration];
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get complete Shodasottari dasha-bhukti data
 */
export function getShodasottariDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    divisionalChartFactor?: number;
  } = {}
): ShodasottariResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 8,
    startingPlanet = MOON,
    includeBhuktis = true,
    divisionalChartFactor = 1
  } = options;
  
  let [currentLord, startJd] = shodasottariDashaStart(
    jd, place, starPositionFromMoon, seedStar, startingPlanet, divisionalChartFactor
  );
  
  const mahadashas: ShodasottariDashaPeriod[] = [];
  const bhuktis: ShodasottariBhuktiPeriod[] = [];
  
  for (let i = 0; i < 8; i++) {
    const durationYears = SHODASOTTARI_YEARS[currentLord] ?? 11;
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
        bhuktiLord = getNextShodasottariLord(bhuktiLord);
      }
    }
    
    startJd += durationYears * YEAR_DURATION;
    currentLord = getNextShodasottariLord(currentLord);
  }
  
  if (!includeBhuktis) {
    return { mahadashas };
  }
  
  return {
    mahadashas,
    bhuktis
  };
}
