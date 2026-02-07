/**
 * Kaala Dasha System
 * Ported from PyJHora kaala.py
 *
 * Time-based dasha system that divides the day into 4 kaala periods:
 * Dawn, Day, Dusk, Night
 * Total: 120 years split into two cycles based on birth kaala
 */

import {
  PLANET_NAMES_EN,
  SIDEREAL_YEAR,
  TROPICAL_YEAR
} from '../../constants';
import { sunrise, sunset } from '../../ephemeris/swe-adapter';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface KaalaDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KaalaBhuktiPeriod {
  dashaLord: number;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KaalaResult {
  kaalaType: number; // 0=Dawn, 1=Day, 2=Dusk, 3=Night
  kaalaTypeName: string;
  kaalaFraction: number;
  mahadashas: KaalaDashaPeriod[];
  bhuktis?: KaalaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const KAALA_LIFE_SPAN = 120; // years
const YEAR_DURATION = SIDEREAL_YEAR;

const KAALA_TYPE_NAMES = ['Dawn', 'Day', 'Dusk', 'Night'];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatJdAsDate(jd: number): string {
  const { date, time } = julianDayToGregorian(jd);
  const pad = (n: number) => Math.abs(n).toString().padStart(2, '0');
  const hour12 = time.hour % 12 || 12;
  const ampm = time.hour < 12 ? 'AM' : 'PM';
  const yearStr = date.year < 0 ? `${Math.abs(date.year)} BC` : date.year.toString();
  return `${yearStr}-${pad(date.month)}-${pad(date.day)} ${pad(hour12)}:${pad(time.minute)}:${pad(time.second)} ${ampm}`;
}

/**
 * Approximate next_solar_date from Python drik.py.
 * Python uses inverse_lagrange + iterative solar longitude search for precision;
 * here we approximate by advancing JD by the tropical year fraction.
 * When years=1, months=1, sixtyHours=1 (defaults), returns jd unchanged (matching Python).
 * TODO: Implement full next_solar_date with solar longitude search once drik.ts has
 * solarLongitude + inverse_lagrange support.
 */
function nextSolarDateApprox(
  jd: number,
  _place: Place,
  years: number = 1,
  months: number = 1,
  sixtyHours: number = 1
): number {
  if (years === 1 && months === 1 && sixtyHours === 1) return jd;
  // Approximate: advance by the tropical year fraction (matches Python's jd_extra logic)
  const jdExtra = Math.floor(
    ((years - 1) + (months - 1) / 12 + (sixtyHours - 1) / 144) * TROPICAL_YEAR
  );
  return jd + jdExtra;
}

/**
 * Calculate kaala type and fraction based on birth time
 * Divides the day into 4 periods: Dawn, Day, Dusk, Night
 * Each period is further divided into 6 parts
 */
function calculateKaalaProgression(jd: number, place: Place): {
  kaalaType: number;
  kaalaFraction: number;
  firstCyclePeriods: number[];
  secondCyclePeriods: number[];
} {
  // Get sunrise/sunset times
  const previousDaySunset = sunset(jd - 1, place).localTime;
  const todaySunset = sunset(jd, place).localTime;
  const todaySunrise = sunrise(jd, place).localTime;
  const tomorrowSunrise = 24.0 + sunrise(jd + 1, place).localTime;

  // Calculate day and night fractions (1/6 of each period)
  const dayFraction = Math.abs(todaySunset - todaySunrise) / 6.0;
  const nightFraction1 = Math.abs(todaySunrise - previousDaySunset) / 6.0;
  const nightFraction2 = Math.abs(tomorrowSunrise - todaySunset) / 6.0;

  // Define period boundaries
  const dawnStart = todaySunrise - nightFraction1;
  const dawnEnd = todaySunrise + nightFraction1;
  const dayStart = dawnEnd;
  const dayEnd = todaySunset - nightFraction1;
  const duskStart = dayEnd;
  const duskEnd = todaySunset + nightFraction2;
  const yesterdayNightStart = -(previousDaySunset + nightFraction1);
  const yesterdayNightEnd = todaySunrise - nightFraction1;
  const tonightStart = todaySunset + nightFraction2;
  const tonightEnd = tomorrowSunrise - nightFraction2;

  // Get birth time from JD
  const { time } = julianDayToGregorian(jd);
  const birthTime = time.hour + time.minute / 60 + time.second / 3600;

  // Determine kaala type and fraction
  let kaalaType: number;
  let kaalaFraction: number;

  if (birthTime > dawnStart && birthTime < dawnEnd) {
    // Dawn
    kaalaType = 0;
    kaalaFraction = (birthTime - dawnStart) / (dawnEnd - dawnStart);
  } else if (birthTime > duskStart && birthTime < duskEnd) {
    // Dusk
    kaalaType = 2;
    kaalaFraction = (birthTime - duskStart) / (duskEnd - duskStart);
  } else if (birthTime > dayStart && birthTime < dayEnd) {
    // Day
    kaalaType = 1;
    kaalaFraction = (birthTime - dayStart) / (dayEnd - dayStart);
  } else if (birthTime > yesterdayNightStart && birthTime < yesterdayNightEnd) {
    // Yesterday's night (early morning before dawn)
    kaalaType = 3;
    kaalaFraction = (birthTime - yesterdayNightStart) / (yesterdayNightEnd - yesterdayNightStart);
  } else if (birthTime > tonightStart && birthTime < tonightEnd) {
    // Tonight
    kaalaType = 3;
    kaalaFraction = (birthTime - tonightStart) / (tonightEnd - tonightStart);
  } else {
    // Default to day if unable to determine
    kaalaType = 1;
    kaalaFraction = 0.5;
  }

  // Calculate dasha periods based on kaala fraction
  // First cycle: 9 periods, each duration = (lord_index + 1) * total_duration / 45
  const firstCycleLifeSpan = KAALA_LIFE_SPAN * kaalaFraction;
  const firstCyclePeriods = Array.from({ length: 9 }, (_, i) =>
    (i + 1) * firstCycleLifeSpan / 45.0
  );

  // Second cycle
  const secondCycleLifeSpan = KAALA_LIFE_SPAN - firstCycleLifeSpan;
  const secondCyclePeriods = Array.from({ length: 9 }, (_, i) =>
    (i + 1) * secondCycleLifeSpan / 45.0
  );

  return {
    kaalaType,
    kaalaFraction,
    firstCyclePeriods,
    secondCyclePeriods
  };
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Kaala Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data
 * @param options - Calculation options
 * @returns Kaala dasha result with mahadashas and optional bhuktis
 */
export function getKaalaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    includeBhuktis?: boolean;
    years?: number;
    months?: number;
    sixtyHours?: number;
  } = {}
): KaalaResult {
  const { includeBhuktis = true, years = 1, months = 1, sixtyHours = 1 } = options;

  // Apply solar date adjustment (Python: drik.next_solar_date)
  const jdAdjusted = nextSolarDateApprox(jd, place, years, months, sixtyHours);

  const {
    kaalaType,
    kaalaFraction,
    firstCyclePeriods,
    secondCyclePeriods
  } = calculateKaalaProgression(jdAdjusted, place);

  const mahadashas: KaalaDashaPeriod[] = [];
  const bhuktis: KaalaBhuktiPeriod[] = [];

  let startJd = jdAdjusted;

  // Process both cycles
  const cycles = [
    { periods: firstCyclePeriods, fraction: kaalaFraction },
    { periods: secondCyclePeriods, fraction: 1 - kaalaFraction }
  ];

  for (const cycle of cycles) {
    for (let dashaLord = 0; dashaLord < 9; dashaLord++) {
      const durationYears = cycle.periods[dashaLord]!;

      if (includeBhuktis) {
        // Two sub-cycles for bhuktis within each dasha
        const bhuktiCycles = [cycle.fraction, 1 - cycle.fraction];

        for (const bhuktiCycleFraction of bhuktiCycles) {
          const cycleDuration = bhuktiCycleFraction * durationYears;

          for (let bhuktiLord = 0; bhuktiLord < 9; bhuktiLord++) {
            const bhuktiDuration = (bhuktiLord + 1) * cycleDuration / 45.0;
            const bhuktiLordName = PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`;

            bhuktis.push({
              dashaLord,
              bhuktiLord,
              bhuktiLordName,
              startJd,
              startDate: formatJdAsDate(startJd),
              durationYears: bhuktiDuration
            });

            startJd += bhuktiDuration * YEAR_DURATION;
          }
        }
      } else {
        const lordName = PLANET_NAMES_EN[dashaLord] ?? `Planet ${dashaLord}`;

        mahadashas.push({
          lord: dashaLord,
          lordName,
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears
        });

        startJd += durationYears * YEAR_DURATION;
      }
    }
  }

  // If bhuktis were generated, create mahadashas from them
  if (includeBhuktis && bhuktis.length > 0) {
    // Group bhuktis by dasha lord to create mahadashas
    let currentDashaLord = -1;
    let currentDashaStart = jdAdjusted;

    for (let i = 0; i < bhuktis.length; i++) {
      const bhukti = bhuktis[i]!;
      if (bhukti.dashaLord !== currentDashaLord) {
        if (currentDashaLord !== -1 && i > 0) {
          // Calculate duration for previous dasha
          const prevBhuktis = bhuktis.filter(b => b.dashaLord === currentDashaLord);
          const totalDuration = prevBhuktis.reduce((sum, b) => sum + b.durationYears, 0);

          mahadashas.push({
            lord: currentDashaLord,
            lordName: PLANET_NAMES_EN[currentDashaLord] ?? `Planet ${currentDashaLord}`,
            startJd: currentDashaStart,
            startDate: formatJdAsDate(currentDashaStart),
            durationYears: totalDuration
          });
        }
        currentDashaLord = bhukti.dashaLord;
        currentDashaStart = bhukti.startJd;
      }
    }

    // Add the last dasha
    if (currentDashaLord !== -1) {
      const lastBhuktis = bhuktis.filter(b => b.dashaLord === currentDashaLord);
      const totalDuration = lastBhuktis.reduce((sum, b) => sum + b.durationYears, 0);

      mahadashas.push({
        lord: currentDashaLord,
        lordName: PLANET_NAMES_EN[currentDashaLord] ?? `Planet ${currentDashaLord}`,
        startJd: currentDashaStart,
        startDate: formatJdAsDate(currentDashaStart),
        durationYears: totalDuration
      });
    }
  }

  return {
    kaalaType,
    kaalaTypeName: KAALA_TYPE_NAMES[kaalaType] ?? 'Unknown',
    kaalaFraction,
    mahadashas,
    bhuktis: includeBhuktis ? bhuktis : undefined
  };
}
