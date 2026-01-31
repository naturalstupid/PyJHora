/**
 * Tara Lagna Dasha System
 * Ported from PyJHora tara_lagna.py
 *
 * Uses Moon's nakshatra fraction and Atmakaraka house for calculations.
 * Fixed 9-year duration per dasha.
 */

import { RASI_NAMES_EN, SIDEREAL_YEAR, EVEN_SIGNS } from '../../constants';
import { PlanetPosition, getDivisionalChart } from '../../horoscope/charts';
import { getCharaKarakas } from '../../horoscope/house';
import { getPlanetLongitude, nakshatraPada } from '../../panchanga/drik';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface TaraLagnaDashaPeriod {
  rasi: number;
  rasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TaraLagnaBhuktiPeriod {
  dashaRasi: number;
  bhuktiRasi: number;
  bhuktiRasiName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface TaraLagnaResult {
  mahadashas: TaraLagnaDashaPeriod[];
  bhuktis?: TaraLagnaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;
const DHASA_DURATION = 9; // Fixed 9 years per sign

// Even-footed signs for bhukti direction: Taurus(1), Leo(4), Scorpio(7), Aquarius(10)
const EVEN_FOOTED_FOR_BHUKTI = [1, 4, 7, 10];

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

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Tara Lagna Dasha periods
 * Uses Moon's nakshatra fraction for seed calculation
 * Fixed 9-year duration per dasha
 *
 * @param jd - Julian day number
 * @param place - Birth place
 * @param options - Configuration options
 * @param options.divisionalChartFactor - Divisional chart factor (default 1 for D-1)
 * @param options.includeBhuktis - Whether to include sub-periods (default true)
 */
export function getTaraLagnaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): TaraLagnaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;

  const planetPositions = getPlanetPositionsArray(jd, place, divisionalChartFactor);

  // Get ascendant house
  const ascHouse = planetPositions[0]?.rasi ?? 0;

  // Get Moon's full longitude (rasi * 30 + degrees in rasi)
  const moonPosition = planetPositions[1]; // Moon is planet 1
  const moonLongitude = (moonPosition?.rasi ?? 0) * 30 + (moonPosition?.longitude ?? 0);

  // Calculate nakshatra fraction
  const ONE_STAR = 360 / 27;
  const NAK_FRAC = ONE_STAR / 12.0;

  const [nak, , ] = nakshatraPada(moonLongitude);

  // Calculate dhasa seed based on ascendant + moon's nakshatra fraction
  const moonNakFraction = Math.floor((moonLongitude - (nak - 1) * ONE_STAR) / NAK_FRAC);
  const dhasaSeed = (ascHouse + moonNakFraction) % 12;

  // Build progression based on even/odd sign of seed
  let dhasaLords: number[];
  if (EVEN_SIGNS.includes(dhasaSeed)) {
    // For even signs: reverse direction
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed - h + 12) % 12);
  } else {
    // For odd signs: forward direction
    dhasaLords = Array.from({ length: 12 }, (_, h) => (dhasaSeed + h) % 12);
  }

  // Get Atmakaraka (first chara karaka) and its house
  const charaKarakas = getCharaKarakas(planetPositions);
  const atmakaraka = charaKarakas[0] ?? 0;
  const atmakarakaHouse = planetPositions.find(p => p.planet === atmakaraka)?.rasi ?? 0;

  // Determine bhukti direction based on atmakaraka house
  const bhuktiDirection = EVEN_FOOTED_FOR_BHUKTI.includes(atmakarakaHouse) ? -1 : 1;

  const mahadashas: TaraLagnaDashaPeriod[] = [];
  const bhuktis: TaraLagnaBhuktiPeriod[] = [];
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

    if (includeBhuktis) {
      const bhuktiDuration = DHASA_DURATION / 12;
      let bhuktiStartJd = startJd;

      // Bhuktis are based on atmakaraka house, not dhasa lord
      for (let h = 0; h < 12; h++) {
        const bhuktiLord = ((atmakarakaHouse + bhuktiDirection * h) % 12 + 12) % 12;
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

    startJd += DHASA_DURATION * YEAR_DURATION;
  }

  return includeBhuktis ? { mahadashas, bhuktis } : { mahadashas };
}
