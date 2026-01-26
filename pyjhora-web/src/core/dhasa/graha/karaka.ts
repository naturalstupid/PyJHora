/**
 * Karaka Dasha System
 * Ported from PyJHora karaka.py
 *
 * A Jaimini dasha system based on Chara Karakas (significators).
 * The dasha lords are ordered by the Atmakaraka (highest degree),
 * Amatyakaraka, Bhratrikaraka, etc.
 * Duration for each dasha is the house count from ascendant to the planet's house.
 */

import {
  PLANET_NAMES_EN,
  SIDEREAL_YEAR
} from '../../constants';
import { getCharaKarakas } from '../../horoscope/house';
import type { Place } from '../../types';
import { julianDayToGregorian } from '../../utils/julian';

// ============================================================================
// TYPES
// ============================================================================

export interface KarakaDashaPeriod {
  lord: number;
  lordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KarakaBhuktiPeriod {
  dashaLord: number;
  dashaLordName: string;
  bhuktiLord: number;
  bhuktiLordName: string;
  startJd: number;
  startDate: string;
  durationYears: number;
}

export interface KarakaResult {
  karakas: number[]; // Ordered karakas (Atma, Amatya, etc.)
  humanLifeSpan: number; // Total years calculated
  mahadashas: KarakaDashaPeriod[];
  bhuktis?: KarakaBhuktiPeriod[];
}

// ============================================================================
// CONSTANTS
// ============================================================================

const YEAR_DURATION = SIDEREAL_YEAR;

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
 * Calculate house distance from ascendant
 * Returns 0-11 (house count - 1)
 */
function getHouseDistance(planetRasi: number, ascRasi: number): number {
  return (planetRasi - ascRasi + 12) % 12;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Karaka Dasha data
 * @param jd - Julian Day Number (birth time)
 * @param place - Place data (not used directly but kept for API consistency)
 * @param planetPositions - Array of planet positions with planet ID, rasi, and longitude
 * @param options - Calculation options
 * @returns Karaka dasha result with mahadashas and optional bhuktis
 */
export function getKarakaDashaBhukti(
  jd: number,
  place: Place,
  planetPositions: Array<{ planet: number; rasi: number; longitude: number }>,
  options: {
    includeBhuktis?: boolean;
  } = {}
): KarakaResult {
  const { includeBhuktis = true } = options;

  // Get ascendant house (planet 0 in the array typically represents ascendant position)
  // In PyJHora, planet_positions[0][1][0] is the ascendant rasi
  // We need to find the ascendant from the positions
  // Ascendant is typically passed as a special entry or the first element
  const ascEntry = planetPositions.find(p => p.planet === -1); // -1 for ascendant
  const ascRasi = ascEntry?.rasi ?? planetPositions[0]?.rasi ?? 0;

  // Get chara karakas ordering
  const karakas = getCharaKarakas(planetPositions);

  // Calculate human lifespan as sum of all house distances
  let humanLifeSpan = 0;
  for (const karaka of karakas) {
    const pos = planetPositions.find(p => p.planet === karaka);
    if (pos) {
      humanLifeSpan += getHouseDistance(pos.rasi, ascRasi);
    }
  }

  // Prevent division by zero
  if (humanLifeSpan === 0) {
    humanLifeSpan = 120; // Default fallback
  }

  const mahadashas: KarakaDashaPeriod[] = [];
  const bhuktis: KarakaBhuktiPeriod[] = [];

  let startJd = jd;
  const karakaCount = karakas.length;

  for (let ki = 0; ki < karakaCount; ki++) {
    const dashaLord = karakas[ki]!;
    const dashaPos = planetPositions.find(p => p.planet === dashaLord);
    const dashaHouse = dashaPos ? getHouseDistance(dashaPos.rasi, ascRasi) : 0;
    const dashaDuration = dashaHouse;

    if (includeBhuktis) {
      // Bhuktis rotate through karakas starting from the next one
      const bhuktiOrder = [
        ...karakas.slice(ki + 1),
        ...karakas.slice(0, ki + 1)
      ];

      for (const bhuktiLord of bhuktiOrder) {
        const bhuktiPos = planetPositions.find(p => p.planet === bhuktiLord);
        const bhuktiHouse = bhuktiPos ? getHouseDistance(bhuktiPos.rasi, ascRasi) : 0;

        // Bhukti duration is proportional: (bhukti_house * dasha_duration) / human_life_span
        const bhuktiDuration = (bhuktiHouse * dashaDuration) / humanLifeSpan;

        const dashaLordName = PLANET_NAMES_EN[dashaLord] ?? `Planet ${dashaLord}`;
        const bhuktiLordName = PLANET_NAMES_EN[bhuktiLord] ?? `Planet ${bhuktiLord}`;

        bhuktis.push({
          dashaLord,
          dashaLordName,
          bhuktiLord,
          bhuktiLordName,
          startJd,
          startDate: formatJdAsDate(startJd),
          durationYears: bhuktiDuration
        });

        startJd += bhuktiDuration * YEAR_DURATION;
      }
    } else {
      const lordName = PLANET_NAMES_EN[dashaLord] ?? `Planet ${dashaLord}`;

      mahadashas.push({
        lord: dashaLord,
        lordName,
        startJd,
        startDate: formatJdAsDate(startJd),
        durationYears: dashaDuration
      });

      startJd += dashaDuration * YEAR_DURATION;
    }
  }

  // If bhuktis were generated, create mahadashas from them
  if (includeBhuktis && bhuktis.length > 0) {
    let currentDashaLord = -1;
    let currentDashaStart = jd;

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
    karakas,
    humanLifeSpan,
    mahadashas,
    bhuktis: includeBhuktis ? bhuktis : undefined
  };
}
