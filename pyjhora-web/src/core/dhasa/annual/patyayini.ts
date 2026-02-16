/**
 * Patyayini Annual Dhasa System
 * Ported from PyJHora patyayini.py
 *
 * Used for Tajaka Annual charts. Planets sorted by longitude,
 * differences (patyamsas) determine proportional dasa durations.
 */

import { AVERAGE_GREGORIAN_YEAR, PLANET_NAMES_EN, KETU, RAHU } from '../../constants';
import type { PlanetPosition } from '../../horoscope/charts';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface PatyayiniDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationDays: number;
}

export interface PatyayiniBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
}

export interface PatyayiniResult {
  mahadashas: PatyayiniDashaPeriod[];
  bhuktis: PatyayiniBhuktiPeriod[];
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
// MAIN FUNCTION
// ============================================================================

/**
 * Compute Patyayini Dhasa for a Tajaka Annual chart.
 * @param jdYear - Julian Day for Tajaka annual return
 * @param d1Positions - Planet positions (from divisional chart)
 * @returns PatyayiniResult with mahadashas and bhuktis
 */
export function getPatyayiniDhasa(
  jdYear: number,
  d1Positions: PlanetPosition[],
): PatyayiniResult {
  // Exclude Rahu (7) and Ketu (8) — use Sun-Saturn only
  const planets = d1Positions.filter(p => p.planet !== RAHU && p.planet !== KETU);

  // Sort by longitude within sign (ascending)
  const sorted = [...planets].sort((a, b) => a.longitude - b.longitude);

  // Calculate patyamsas: differences between consecutive longitudes
  const patyamsas: Array<{ planet: number; value: number }> = [];
  patyamsas.push({ planet: sorted[0]!.planet, value: sorted[0]!.longitude });
  for (let i = 1; i < sorted.length; i++) {
    patyamsas.push({
      planet: sorted[i]!.planet,
      value: sorted[i]!.longitude - sorted[i - 1]!.longitude,
    });
  }

  const totalSum = patyamsas.reduce((acc, p) => acc + p.value, 0);

  // Compute period factors (fraction of year)
  const factors: Record<number, number> = {};
  for (const p of patyamsas) {
    factors[p.planet] = p.value / totalSum;
  }

  const lordOrder = patyamsas.map(p => p.planet);

  // Build mahadashas
  const mahadashas: PatyayiniDashaPeriod[] = [];
  let jdStart = jdYear;

  for (const pa of patyamsas) {
    const durationDays = AVERAGE_GREGORIAN_YEAR * factors[pa.planet]!;
    mahadashas.push({
      lord: pa.planet,
      lordName: PLANET_NAMES_EN[pa.planet] ?? `Planet${pa.planet}`,
      startJd: jdStart,
      startDate: formatJdAsDate(jdStart),
      durationDays,
    });
    jdStart += durationDays;
  }

  // Build bhuktis for each mahadasha
  const bhuktis: PatyayiniBhuktiPeriod[] = [];
  for (let d = 0; d < mahadashas.length; d++) {
    const dasha = mahadashas[d]!;
    let bn = d;
    let bhuktiJd = dasha.startJd;

    for (let _b = 0; _b < lordOrder.length; _b++) {
      const bhuktiLord = lordOrder[bn]!;
      bhuktis.push({
        dashaLord: dasha.lord,
        bhuktiLord,
        bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet${bhuktiLord}`,
        startJd: bhuktiJd,
        startDate: formatJdAsDate(bhuktiJd),
      });
      bhuktiJd += factors[bhuktiLord]! * dasha.durationDays;
      bn = (bn + 1) % lordOrder.length;
    }
  }

  return { mahadashas, bhuktis };
}
