/**
 * Sudharsana Chakra Dhasa System
 * Ported from PyJHora sudharsana_chakra.py
 *
 * Sign-based dhasa system with Lagna, Moon, and Sun progressions.
 * Each mahadasha is one sign for one sidereal year, with 12 antardhasas.
 */

import { SIDEREAL_YEAR, RASI_NAMES_EN } from '../constants';
import type { PlanetPosition } from '../horoscope/charts';
import { planetsInRetrograde, getHousePlanetListFromPositions } from '../horoscope/charts';
import { julianDayToGregorian } from '../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface SudharsanaAntardasha {
  sign: number;
  signName: string;
  startJd: number;
  startDate: string;
  durationDays: number;
}

export interface SudharsanaDashaPeriod {
  sign: number;
  signName: string;
  endJd: number;
  endDate: string;
  durationDays: number;
  antardhasas: SudharsanaAntardasha[];
}

export interface SudharsanaPratyantardasha {
  sign: number;
  signName: string;
  endJd: number;
  endDate: string;
  durationDays: number;
}

export interface SudharsanaChakraChart {
  lagnaChart: Array<[number, string]>;
  moonChart: Array<[number, string]>;
  sunChart: Array<[number, string]>;
  retrogradePlanets: number[];
}

export interface SudharsanaChakraDhasaResult {
  lagnaPeriods: SudharsanaDashaPeriod[];
  moonPeriods: SudharsanaDashaPeriod[];
  sunPeriods: SudharsanaDashaPeriod[];
}

// ============================================================================
// HELPERS
// ============================================================================

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  return `${date.year}-${pad(date.month)}-${pad(date.day)} ${pad(time.hour)}:${pad(time.minute)}:${pad(time.second)}`;
}

// ============================================================================
// SUDHARSANA CHAKRA CHART
// ============================================================================

/**
 * Create Sudharsana Chakra charts (Lagna, Moon, Sun rotations).
 * @param positions - D1 (or divisional) planet positions
 * @returns Charts rotated from Lagna, Moon, and Sun houses + retrograde planets
 */
export function sudharsanaChakraChart(
  positions: PlanetPosition[],
): SudharsanaChakraChart {
  const retrograde = planetsInRetrograde(positions);
  const natalChart = getHousePlanetListFromPositions(positions);

  const lagnaHouse = positions[0]!.rasi;
  const moonHouse = positions[2]!.rasi;
  const sunHouse = positions[1]!.rasi;

  const lagnaChart: Array<[number, string]> = [];
  const moonChart: Array<[number, string]> = [];
  const sunChart: Array<[number, string]> = [];

  for (let p = 0; p < 12; p++) {
    const lIdx = (p + lagnaHouse) % 12;
    lagnaChart.push([lIdx, natalChart[lIdx]!]);

    const mIdx = (p + moonHouse) % 12;
    moonChart.push([mIdx, natalChart[mIdx]!]);

    const sIdx = (p + sunHouse) % 12;
    sunChart.push([sIdx, natalChart[sIdx]!]);
  }

  return { lagnaChart, moonChart, sunChart, retrogradePlanets: retrograde };
}

// ============================================================================
// DHASA CALCULATION
// ============================================================================

/**
 * Calculate Sudharsana dhasa periods from a seed sign.
 * 12 periods of 1 sidereal year each, progressing through signs.
 * Each period has 12 antardhasas.
 */
function sudharsanaDhasaCalculation(
  jdStart: number,
  seedSign: number,
): SudharsanaDashaPeriod[] {
  const periods: SudharsanaDashaPeriod[] = [];
  let dhasaStart = jdStart;
  const dhasaDuration = SIDEREAL_YEAR;
  const antardasaDuration = Math.round((SIDEREAL_YEAR / 12.0) * 100) / 100;

  for (let h = 0; h < 12; h++) {
    const sign = (seedSign + h) % 12;
    const dhasaEnd = dhasaStart + dhasaDuration;

    const antardhasas: SudharsanaAntardasha[] = [];
    for (let a = 0; a < 12; a++) {
      const antSign = (sign + a) % 12;
      const antStart = dhasaStart + a * antardasaDuration;
      antardhasas.push({
        sign: antSign,
        signName: RASI_NAMES_EN[antSign] ?? `Sign${antSign}`,
        startJd: antStart,
        startDate: formatJdAsDate(antStart),
        durationDays: antardasaDuration,
      });
    }

    periods.push({
      sign,
      signName: RASI_NAMES_EN[sign] ?? `Sign${sign}`,
      endJd: dhasaEnd,
      endDate: formatJdAsDate(dhasaEnd),
      durationDays: dhasaDuration,
      antardhasas,
    });

    dhasaStart = dhasaEnd;
  }

  return periods;
}

/**
 * Main entry: Calculate Sudharsana Chakra dhasas for Lagna, Moon, and Sun.
 * @param positions - Planet positions (D1 or divisional chart)
 * @param jd - Julian Day to start from
 * @param yearsFromDob - Number of years from birth (for annual charts)
 * @returns Lagna, Moon, and Sun dhasa periods
 */
export function getSudharsanaChakraDhasa(
  positions: PlanetPosition[],
  jd: number,
  yearsFromDob: number = 0,
): SudharsanaChakraDhasaResult {
  const lagnaHouse = positions[0]!.rasi;
  const moonHouse = positions[2]!.rasi;
  const sunHouse = positions[1]!.rasi;

  // Seed sign progresses by yearsFromDob
  const lagnaSign = (lagnaHouse + yearsFromDob - 1 + 12) % 12;
  const moonSign = (moonHouse + yearsFromDob - 1 + 12) % 12;
  const sunSign = (sunHouse + yearsFromDob - 1 + 12) % 12;

  const jdAtYears = jd + yearsFromDob * SIDEREAL_YEAR;

  const lagnaPeriods = sudharsanaDhasaCalculation(jdAtYears, lagnaSign);
  const moonPeriods = sudharsanaDhasaCalculation(jdAtYears, moonSign);
  const sunPeriods = sudharsanaDhasaCalculation(jdAtYears, sunSign);

  return { lagnaPeriods, moonPeriods, sunPeriods };
}

/**
 * Calculate pratyantardasas (sub-sub-periods) for a given antardhasa.
 * @param antardhasaStartJd - Start JD of the antardhasa
 * @param antardhasaSeedSign - Seed sign of the antardhasa
 * @returns 12 pratyantardasas
 */
export function sudharsanaPratyantardasas(
  antardhasaStartJd: number,
  antardhasaSeedSign: number,
): SudharsanaPratyantardasha[] {
  const periods: SudharsanaPratyantardasha[] = [];
  let start = antardhasaStartJd;
  const duration = Math.round((SIDEREAL_YEAR / 144.0) * 100) / 100;

  for (let h = 0; h < 12; h++) {
    const sign = (antardhasaSeedSign + h) % 12;
    const end = start + duration;

    periods.push({
      sign,
      signName: RASI_NAMES_EN[sign] ?? `Sign${sign}`,
      endJd: end,
      endDate: formatJdAsDate(end),
      durationDays: duration,
    });

    start = end;
  }

  return periods;
}
