/**
 * Mudda (Varsha Vimsottari) Annual Dhasa System
 * Ported from PyJHora mudda.py
 *
 * Calculates Varsha Vimsottari Dasha-Bhukti for annual charts.
 * Total cycle = 360 days, proportioned like Vimsottari but for annual use.
 */

import {
  HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI,
  PLANET_NAMES_EN,
  TROPICAL_YEAR,
  VARSHA_VIMSOTTARI_ADHIPATI_LIST,
  VARSHA_VIMSOTTARI_DAYS,
} from '../../constants';
import type { PlanetPosition } from '../../horoscope/charts';
import { getVimsottariAdhipati } from '../graha/vimsottari';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface MuddaDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationDays: number;
}

export interface MuddaBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationDays: number;
}

export interface MuddaResult {
  mahadashas: MuddaDashaPeriod[];
  bhuktis: MuddaBhuktiPeriod[];
}

// ============================================================================
// HELPERS
// ============================================================================

const CYCLE = HUMAN_LIFE_SPAN_VARSHA_VIMSOTTARI; // 360

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  return `${date.year}-${pad(date.month)}-${pad(date.day)} ${pad(time.hour)}:${pad(time.minute)}:${pad(time.second)}`;
}

/** Get next adhipati in Varsha Vimsottari sequence */
function getNextVarshaAdhipati(lord: number): number {
  const idx = VARSHA_VIMSOTTARI_ADHIPATI_LIST.indexOf(lord);
  return VARSHA_VIMSOTTARI_ADHIPATI_LIST[(idx + 1) % VARSHA_VIMSOTTARI_ADHIPATI_LIST.length]!;
}

// ============================================================================
// DASHA START DATE
// ============================================================================

/**
 * Calculate the starting dasha lord and start date for Varsha Vimsottari.
 * @param jd - Julian Day of birth
 * @param d1Positions - Planet positions
 * @param years - Number of years from birth
 * @returns [lord, startDateJd]
 */
function varshaVimsottariDashaStartDate(
  jd: number,
  d1Positions: PlanetPosition[],
  years: number,
): [number, number] {
  const oneStar = 360 / 27;
  const moonPos = d1Positions[2]!;
  const moonLong = moonPos.rasi * 30 + moonPos.longitude;

  const nak = Math.floor(moonLong / oneStar);
  const rem = moonLong - nak * oneStar;

  // Get vimsottari lord index, then offset by years
  let lord = getVimsottariAdhipati(nak);
  const lordIdx = VARSHA_VIMSOTTARI_ADHIPATI_LIST.indexOf(lord);
  lord = VARSHA_VIMSOTTARI_ADHIPATI_LIST[((lordIdx + years) % 9 + 9) % 9]!;

  const period = VARSHA_VIMSOTTARI_DAYS[lord]!;
  const periodElapsed = (rem / oneStar) * period;
  const startDate = jd + years * TROPICAL_YEAR - periodElapsed;

  return [lord, startDate];
}

// ============================================================================
// MAHADASHA
// ============================================================================

function varshaVimsottariMahadasha(
  jd: number,
  d1Positions: PlanetPosition[],
  years: number,
): Array<[number, number, number]> {
  let [lord, startDate] = varshaVimsottariDashaStartDate(jd, d1Positions, years);

  const result: Array<[number, number, number]> = [];
  for (let i = 0; i < 9; i++) {
    const duration = (VARSHA_VIMSOTTARI_DAYS[lord]! * TROPICAL_YEAR) / CYCLE;
    result.push([lord, startDate, duration]);
    startDate += duration;
    lord = getNextVarshaAdhipati(lord);
  }
  return result;
}

// ============================================================================
// BHUKTI
// ============================================================================

function varshaVimsottariBhukti(
  mahaLord: number,
  startDate: number,
): Array<[number, number, number]> {
  let lord = mahaLord;
  const result: Array<[number, number, number]> = [];

  for (let i = 0; i < 9; i++) {
    const factor = (VARSHA_VIMSOTTARI_DAYS[lord]! * VARSHA_VIMSOTTARI_DAYS[mahaLord]!) / CYCLE;
    const duration = (factor * TROPICAL_YEAR) / CYCLE;
    result.push([lord, startDate, duration]);
    startDate += duration;
    lord = getNextVarshaAdhipati(lord);
  }
  return result;
}

// ============================================================================
// PUBLIC API
// ============================================================================

/**
 * Compute Mudda (Varsha Vimsottari) Dasha-Bhukti.
 * @param jd - Julian Day of birth
 * @param d1Positions - D1 planet positions
 * @param years - Number of years from birth for annual chart
 * @param includeBhuktis - Whether to include bhukti sub-periods
 * @returns MuddaResult
 */
export function getMuddaDhasa(
  jd: number,
  d1Positions: PlanetPosition[],
  years: number,
  includeBhuktis: boolean = true,
): MuddaResult {
  const dashas = varshaVimsottariMahadasha(jd, d1Positions, years);

  const mahadashas: MuddaDashaPeriod[] = [];
  const bhuktis: MuddaBhuktiPeriod[] = [];

  for (const [lord, dashaStart, durn] of dashas) {
    mahadashas.push({
      lord,
      lordName: PLANET_NAMES_EN[lord] ?? `Planet${lord}`,
      startJd: dashaStart,
      startDate: formatJdAsDate(dashaStart),
      durationDays: durn,
    });

    if (includeBhuktis) {
      const bhuktiList = varshaVimsottariBhukti(lord, dashaStart);
      for (const [bhuktiLord, bhuktiStart, bhuktiDurn] of bhuktiList) {
        bhuktis.push({
          dashaLord: lord,
          bhuktiLord,
          bhuktiLordName: PLANET_NAMES_EN[bhuktiLord] ?? `Planet${bhuktiLord}`,
          startJd: bhuktiStart,
          startDate: formatJdAsDate(bhuktiStart),
          durationDays: bhuktiDurn,
        });
      }
    }
  }

  return { mahadashas, bhuktis };
}
