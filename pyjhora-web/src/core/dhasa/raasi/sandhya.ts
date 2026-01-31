/**
 * Sandhya Dasha System
 * Ported from PyJHora sandhya.py
 *
 * Sandhya is an Ayurdasa system where the parama-ayush (120 years) is spread
 * among the 12 Rasis, making the dasa span of each Rasi as 1/12th of the Paramaayush.
 * Hence the span of each Sandhya Dasa is 10 years.
 *
 * Also includes Panchaka Dasa Variation - wherein 10 years are divided into 3 compartments:
 * 1 rasi - 60/31, 3 rasis - 30/31, and 8 rasis - 20/31 (each fraction of 10 years)
 */

import { RASI_NAMES_EN, SIDEREAL_YEAR } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface SandhyaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SandhyaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface SandhyaResult {
  mahadashas: SandhyaDashaPeriod[];
  bhuktis?: SandhyaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const DHASA_DURATION = 10; // Fixed 10 years per sign

// Panchaka variation durations (fractions of 10 years)
// 1 rasi: 60/31, 3 rasis: 30/31, 8 rasis: 20/31
const PANCHAKA_DURATION = [
  60/31, 30/31, 30/31, 30/31, 20/31, 20/31,
  20/31, 20/31, 20/31, 20/31, 20/31, 20/31
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getPlanetPositionsArray(jd: number, place: Place, divisionalChartFactor: number): PlanetPosition[] {
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

/**
 * Get the dasha seed - Lagna house (first planet position's rasi)
 */
function getDhasaSeed(planetPositions: PlanetPosition[]): number {
  return planetPositions[0]?.rasi ?? 0;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Sandhya Dasha periods
 * Fixed 10-year duration per sign
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 * @param options.usePanchakaVariation - Use Panchaka duration variation (default false)
 */
export function getSandhyaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
    usePanchakaVariation?: boolean;
  } = {}
): SandhyaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true,
    usePanchakaVariation = false
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);
  const dhasaSeed = getDhasaSeed(planetPositions);

  // Build progression from seed - sequential from Lagna
  const dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);

  const mahadashas: SandhyaDashaPeriod[] = [];
  const bhuktis: SandhyaBhuktiPeriod[] = [];
  let startJd = jd;

  for (const dhasaLord of dhasaLords) {
    const rasiName = RASI_NAMES_EN[dhasaLord] ?? `Rasi ${dhasaLord}`;

    mahadashas.push({
      rasi: dhasaLord,
      rasiName,
      startJd,
      startDate: formatJdAsDate(startJd),
      durationYears: DHASA_DURATION
    });

    if (includeBhuktis || usePanchakaVariation) {
      let bhuktiStartJd = startJd;

      for (let h = 0; h < 12; h++) {
        const bhuktiLord = (dhasaLord + h) % 12;
        const bhuktiRasiName = RASI_NAMES_EN[bhuktiLord] ?? `Rasi ${bhuktiLord}`;

        // Duration depends on variation
        const bhuktiDuration = usePanchakaVariation
          ? PANCHAKA_DURATION[h]
          : DHASA_DURATION / 12;

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

    startJd += DHASA_DURATION * YEAR_DURATION;
  }

  return (includeBhuktis || usePanchakaVariation) ? { mahadashas, bhuktis } : { mahadashas };
}
