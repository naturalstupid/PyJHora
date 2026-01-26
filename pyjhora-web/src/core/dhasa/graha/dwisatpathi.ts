/**
 * Dwisatpathi Dasha System
 * Ported from PyJHora dwisatpathi.py
 * 
 * 72-year dasha cycle with 8 lords (9 years each), run for 2 cycles = 144 years
 * Applicability: Lagna lord in 7th or 7th lord in lagna
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
import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { normalizeDegrees } from '../../utils/angle';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface DwisatpathiDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DwisatpathiBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface DwisatpathiResult {
  mahadashas: DwisatpathiDashaPeriod[];
  bhuktis?: DwisatpathiBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

/** 
 * Dwisatpathi lords - all 8 lords have 9 years each
 * Order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu
 * Total per cycle: 72 years, 2 cycles = 144 years
 */
const DWISATPATHI_LORDS = [SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU];

const DWISATPATHI_YEARS = 9; // All lords have 9 years

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function buildNakshatraDict(seedStar = 19): Map<number, number> {
  const nakToLord = new Map<number, number>();
  let nak = seedStar;
  let lordIndex = 0;
  
  for (let i = 0; i < 27; i++) {
    nakToLord.set(nak, DWISATPATHI_LORDS[lordIndex]!);
    nak = (nak % 27) + 1;
    lordIndex = (lordIndex + 1) % 8;
  }
  
  return nakToLord;
}

export function getDwisatpathiDhasaLord(nakshatra: number, seedStar = 19): [number, number] {
  const nakToLord = buildNakshatraDict(seedStar);
  const lord = nakToLord.get(nakshatra) ?? SUN;
  return [lord, DWISATPATHI_YEARS];
}

export function getNextDwisatpathiLord(lord: number, direction = 1): number {
  const currentIndex = DWISATPATHI_LORDS.indexOf(lord);
  if (currentIndex === -1) return DWISATPATHI_LORDS[0]!;
  const nextIndex = ((currentIndex + direction) % 8 + 8) % 8;
  return DWISATPATHI_LORDS[nextIndex]!;
}

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

export function dwisatpathiDashaStart(
  jd: number,
  place: Place,
  starPositionFromMoon = 1,
  seedStar = 19,
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
  
  const [lord] = getDwisatpathiDhasaLord(nakNumber, seedStar);
  const periodElapsedDays = (remainder / oneStar) * DWISATPATHI_YEARS * YEAR_DURATION;
  const startDate = jd - periodElapsedDays;
  
  return [lord, startDate, DWISATPATHI_YEARS];
}

export function getDwisatpathiDashaBhukti(
  jd: number,
  place: Place,
  options: {
    starPositionFromMoon?: number;
    seedStar?: number;
    startingPlanet?: number;
    includeBhuktis?: boolean;
    antardashaOption?: number;
    cycles?: number;
    divisionalChartFactor?: number;
  } = {}
): DwisatpathiResult {
  const {
    starPositionFromMoon = 1,
    seedStar = 19,
    startingPlanet = MOON,
    includeBhuktis = true,
    antardashaOption = 1,
    cycles = 2,
    divisionalChartFactor = 1
  } = options;
  
  let [currentLord, startJd] = dwisatpathiDashaStart(jd, place, starPositionFromMoon, seedStar, startingPlanet, divisionalChartFactor);
  
  const mahadashas: DwisatpathiDashaPeriod[] = [];
  const bhuktis: DwisatpathiBhuktiPeriod[] = [];
  
  for (let cycle = 0; cycle < cycles; cycle++) {
    for (let i = 0; i < 8; i++) {
      const durationYears = DWISATPATHI_YEARS;
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
          bhuktiLord = getNextDwisatpathiLord(bhuktiLord, 1);
        } else if (antardashaOption === 5 || antardashaOption === 6) {
          bhuktiLord = getNextDwisatpathiLord(bhuktiLord, -1);
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
          bhuktiLord = getNextDwisatpathiLord(bhuktiLord, direction);
        }
      }
      
      startJd += durationYears * YEAR_DURATION;
      currentLord = getNextDwisatpathiLord(currentLord);
    }
  }
  
  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
