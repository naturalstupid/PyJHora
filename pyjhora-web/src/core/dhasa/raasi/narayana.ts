/**
 * Narayana Dasha System
 * Ported from PyJHora narayana.py
 */

import {
  EVEN_FOOTED_SIGNS,
  HOUSE_STRENGTHS_OF_PLANETS,
  KETU,
  ODD_SIGNS,
  RASI_NAMES_EN,
  SATURN,
  SIDEREAL_YEAR,
  STRENGTH_DEBILITATED,
  STRENGTH_EXALTED
} from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getHouseOwnerFromPlanetPositions, getStrongerRasi } from '../../horoscope/house';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface NarayanaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NarayanaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface NarayanaResult {
  mahadashas: NarayanaDashaPeriod[];
  bhuktis?: NarayanaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

export const NARAYANA_DHASA_NORMAL_PROGRESSION = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  [1, 8, 3, 10, 5, 0, 7, 2, 9, 4, 11, 6],
  [2, 10, 6, 5, 1, 9, 8, 4, 0, 11, 7, 3],
  [3, 2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4],
  [4, 9, 2, 7, 0, 5, 10, 3, 8, 1, 6, 11],
  [5, 9, 1, 2, 6, 10, 11, 3, 7, 8, 0, 4],
  [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
  [7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 0],
  [8, 4, 0, 11, 7, 3, 2, 10, 6, 5, 1, 9],
  [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 11, 10],
  [10, 3, 8, 1, 6, 11, 4, 9, 2, 7, 0, 5],
  [11, 3, 7, 8, 0, 4, 5, 9, 1, 2, 6, 10]
];

export const NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION = [
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0],
  [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1],
  [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2],
  [4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3],
  [5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4],
  [6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5],
  [7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6],
  [8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7],
  [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8],
  [10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
  [11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
];

export const NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION = [
  [0, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
  [1, 6, 11, 4, 9, 2, 7, 0, 5, 10, 3, 8],
  [2, 6, 10, 11, 3, 7, 8, 0, 4, 5, 9, 1],
  [3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2],
  [4, 11, 6, 1, 8, 3, 10, 5, 0, 7, 2, 9],
  [5, 1, 9, 8, 4, 0, 11, 7, 3, 2, 10, 6],
  [6, 5, 4, 3, 2, 1, 0, 11, 10, 9, 8, 7],
  [7, 0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2],
  [8, 0, 4, 5, 9, 1, 2, 6, 10, 11, 3, 7],
  [9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8],
  [10, 5, 0, 7, 2, 9, 4, 11, 6, 1, 8, 3],
  [11, 7, 3, 2, 10, 6, 5, 1, 9, 8, 4, 0]
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function getPlanetPositionsArray(jd: number, place: Place, divisionalChartFactor: number): PlanetPosition[] {
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

function getPlanetToHouseMap(planetPositions: PlanetPosition[]): Map<number, number> {
  const map = new Map<number, number>();
  for (const pos of planetPositions) {
    map.set(pos.planet, pos.rasi);
  }
  return map;
}

function countRasis(start: number, end: number): number {
  return ((end - start) % 12 + 12) % 12 + 1;
}

export function getNarayanaDashaDuration(
  planetPositions: PlanetPosition[],
  sign: number,
  varshaNarayana: boolean = false
): number {
  const lordOfSign = getHouseOwnerFromPlanetPositions(planetPositions, sign, false);

  const lordPosition = planetPositions.find(p => p.planet === lordOfSign);
  if (!lordPosition) {
    return 12; // Fallback
  }
  
  const houseOfLord = lordPosition.rasi;
  
  // Count
  let dhasaPeriod = 0;
  if (EVEN_FOOTED_SIGNS.includes(sign)) {
    dhasaPeriod = countRasis(houseOfLord, sign);
  } else {
    dhasaPeriod = countRasis(sign, houseOfLord);
  }
  
  dhasaPeriod -= 1; // Subtract one

  // Exception 1: if period is 0 (lord in same sign), becomes 12
  if (dhasaPeriod <= 0) {
    dhasaPeriod = 12;
  }
  
  // Exception 2: Exalted lord -> +1
  // Exception 3: Debilitated lord -> -1
  // Need strength matrix from constants
  const strength = HOUSE_STRENGTHS_OF_PLANETS[lordOfSign]?.[houseOfLord];
  
  if (strength === STRENGTH_EXALTED) {
    dhasaPeriod += 1;
  } else if (strength === STRENGTH_DEBILITATED) {
    dhasaPeriod -= 1;
  }
  
  if (varshaNarayana) {
    dhasaPeriod *= 3;
  }
  
  return dhasaPeriod;
}

export function getNarayanaAntardhasa(planetPositions: PlanetPosition[], dhasaRasi: number): number[] {
  // Logic from _narayana_antardhasa in narayana.py

  // 1. Lord of dhasa rasi
  const lordOfDhasaRasi = getHouseOwnerFromPlanetPositions(planetPositions, dhasaRasi, true);
  const houseOfDhasaRasiLord = planetPositions.find(p => p.planet === lordOfDhasaRasi)?.rasi ?? 0;

  // 2. Lord of 7th house from dhasa rasi
  const seventhHouse = (dhasaRasi + 6) % 12;
  const lordOf7th = getHouseOwnerFromPlanetPositions(planetPositions, seventhHouse, true);
  const houseOf7thLord = planetPositions.find(p => p.planet === lordOf7th)?.rasi ?? 0;

  // 3. Stronger of the two is seed
  const antardhasaSeedRasi = getStrongerRasi(planetPositions, houseOfDhasaRasiLord, houseOf7thLord);

  // 4. Calculate sequence
  const pToH = getPlanetToHouseMap(planetPositions);
  let direction = -1;

  if (pToH.get(SATURN) === antardhasaSeedRasi || ODD_SIGNS.includes(antardhasaSeedRasi)) {
    direction = 1;
  }

  if (pToH.get(KETU) === antardhasaSeedRasi) {
    direction *= -1;
  }

  return Array.from({ length: 12 }, (_, i) =>
    ((antardhasaSeedRasi + direction * i) % 12 + 12) % 12
  );
}

// ============================================================================
// MAIN FUNCTIONS
// ============================================================================

export function getNarayanaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
    seedSignOverride?: number;
  } = {}
): NarayanaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true,
    seedSignOverride
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const pToH = getPlanetToHouseMap(planetPositions);

  // Determine Seed Sign
  let dhasaSeedSign: number;

  if (seedSignOverride !== undefined && seedSignOverride >= 0) {
    dhasaSeedSign = seedSignOverride;
  } else {
    // Standard D-1 logic
    const ascHouse = planetPositions[0]?.rasi ?? 0;
    const seventhHouse = (ascHouse + 6) % 12;
    dhasaSeedSign = getStrongerRasi(planetPositions, ascHouse, seventhHouse);
  }

  // Progression
  let dhasaProgression = NARAYANA_DHASA_NORMAL_PROGRESSION[dhasaSeedSign]!;

  if (pToH.get(KETU) === dhasaSeedSign) {
    dhasaProgression = NARAYANA_DHASA_KETU_EXCEPTION_PROGRESSION[dhasaSeedSign]!;
  } else if (pToH.get(SATURN) === dhasaSeedSign) {
    dhasaProgression = NARAYANA_DHASA_SATURN_EXCEPTION_PROGRESSION[dhasaSeedSign]!;
  }

  const mahadashas: NarayanaDashaPeriod[] = [];
  const bhuktis: NarayanaBhuktiPeriod[] = [];
  let startJd = jd;
  let totalDuration = 0;
  const firstCycleDurations: number[] = [];

  // First Cycle
  for (const dhasaLord of dhasaProgression) {
    const duration = getNarayanaDashaDuration(planetPositions, dhasaLord);
    firstCycleDurations.push(duration);
    
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: duration
    });

    if (includeBhuktis) {
      const bhuktiLords = getNarayanaAntardhasa(planetPositions, dhasaLord);
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
    totalDuration += duration;
  }

  // Second Cycle (if needed)
  if (totalDuration < 120) {
    for (let c = 0; c < dhasaProgression.length; c++) {
      if (totalDuration >= 120) break;

      const dhasaLord = dhasaProgression[c]!;
      const secondDuration = 12 - (firstCycleDurations[c] ?? 0);

        if (secondDuration <= 0) continue;

        const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

        mahadashas.push({
          rasi: dhasaLord,
          rasiName,
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears: secondDuration
        });

        if (includeBhuktis) {
          const bhuktiLords = getNarayanaAntardhasa(planetPositions, dhasaLord);
          const bhuktiDuration = secondDuration / 12;
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

        startJd += secondDuration * YEAR_DURATION;
        totalDuration += secondDuration;
    }
  }

  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
