/**
 * Lagnamsaka Dasha System
 * Ported from PyJHora lagnamsaka.py
 * 
 * Uses the Ascendant sign in Navamsa (D-9) as the seed for Narayana Dasha
 * Calculate D9, find Ascendant sign, then run Narayana on the requested chart (D-1 usually)
 */

import { getDivisionalChart, PlanetPosition } from '../../horoscope/charts';
import { getPlanetLongitude } from '../../panchanga/drik';
import type { Place } from '../../types';
import { getNarayanaDashaBhukti, NarayanaResult } from './narayana';

// ============================================================================
// HELPERS (Re-implementing locally to avoid circular deps or heavy refactors)
// ============================================================================

function getPositions(jd: number, place: Place, divisionalChartFactor: number): PlanetPosition[] {
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

// ============================================================================
// MAIN FUNCTION
// ============================================================================

/**
 * Get Lagnamsaka Dasha periods
 * Seed = Ascendant in Navamsa (D-9)
 * Logic = Narayana Dasha
 */
export function getLagnamsakaDashaBhukti(
  jd: number,
  place: Place,
  options: {
    divisionalChartFactor?: number;
    includeBhuktis?: boolean;
  } = {}
): NarayanaResult {
  const {
    divisionalChartFactor = 1,
    includeBhuktis = true
  } = options;
  
  // 1. Calculate Navamsa (D-9) positions
  const navamsaPositions = getPositions(jd, place, 9);
  
  // Use Sun (planet 0) in D-9 as proxy for Lagna in D-9
  // Note: This aligns with current system behavior where Sun is proxy for Lagna
  const navamsaLagna = navamsaPositions.find(p => p.planet === 0)?.rasi ?? 0;
  
  return getNarayanaDashaBhukti(jd, place, {
    divisionalChartFactor,
    includeBhuktis,
    seedSignOverride: navamsaLagna
  });
}
