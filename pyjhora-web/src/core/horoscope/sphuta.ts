/**
 * Sphuta (Sensitive Point) Calculations
 * Ported from PyJHora sphuta.py
 *
 * Calculates various sensitive points from planet longitudes:
 * - Beeja Sphuta (seed point - male fertility)
 * - Kshetra Sphuta (field point - female fertility)
 * - Tithi Sphuta
 * - Yoga Sphuta
 * - Yogi Sphuta
 * - Avayogi Sphuta
 * - Rahu Tithi Sphuta
 */

import { PlanetPosition } from '../types';
import { SUN, MOON, MARS, JUPITER, VENUS, RAHU } from '../constants';
import { dasavargaFromLong } from './varga-utils';

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Extract absolute longitude (0-360) from a planet in the positions array.
 * @param positions - Array of planet positions
 * @param planetIndex - Planet index (SUN=0, MOON=1, etc.; Lagna=-1)
 * @returns Absolute longitude in degrees (0-360)
 */
const getAbsLong = (positions: PlanetPosition[], planetIndex: number): number => {
  const pos = positions.find(p => p.planet === planetIndex);
  if (!pos) throw new Error(`Planet ${planetIndex} not found in positions`);
  return pos.rasi * 30 + pos.longitude;
};

// ============================================================================
// SPHUTA CALCULATIONS
// ============================================================================

/**
 * Beeja Sphuta (Seed Point) - male fertility indicator.
 * Formula: (Sun + Jupiter + Venus) % 360
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Beeja Sphuta
 */
export const beejaSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  const sunLong = getAbsLong(positions, SUN);
  const jupiterLong = getAbsLong(positions, JUPITER);
  const venusLong = getAbsLong(positions, VENUS);
  const beejaLong = (sunLong + jupiterLong + venusLong) % 360;
  return dasavargaFromLong(beejaLong, 1);
};

/**
 * Kshetra Sphuta (Field Point) - female fertility indicator.
 * Formula: (Moon + Jupiter + Mars) % 360
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Kshetra Sphuta
 */
export const kshetraSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  const moonLong = getAbsLong(positions, MOON);
  const jupiterLong = getAbsLong(positions, JUPITER);
  const marsLong = getAbsLong(positions, MARS);
  const kshetraLong = (moonLong + jupiterLong + marsLong) % 360;
  return dasavargaFromLong(kshetraLong, 1);
};

/**
 * Tithi Sphuta - sensitive point derived from Moon-Sun difference.
 * Formula: (Moon - Sun) % 360
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Tithi Sphuta
 */
export const tithiSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  const moonLong = getAbsLong(positions, MOON);
  const sunLong = getAbsLong(positions, SUN);
  const tithiLong = ((moonLong - sunLong) % 360 + 360) % 360;
  return dasavargaFromLong(tithiLong, 1);
};

/**
 * Yoga Sphuta - sensitive point from Sun+Moon combination.
 * Formula: (Moon + Sun + yogiOffset) % 360
 * Where yogiOffset = 93 + 20/60 = 93.333... if addYogiLongitude is true, else 0.
 *
 * @param positions - D-1 planet positions
 * @param addYogiLongitude - Whether to add the yogi longitude offset (default false)
 * @returns Rasi and longitude of the Yoga Sphuta
 */
export const yogaSphuta = (
  positions: PlanetPosition[],
  addYogiLongitude: boolean = false
): { rasi: number; longitude: number } => {
  const moonLong = getAbsLong(positions, MOON);
  const sunLong = getAbsLong(positions, SUN);
  const yogiLong = addYogiLongitude ? 93 + 20 / 60 : 0;
  const yogaLong = (moonLong + sunLong + yogiLong) % 360;
  return dasavargaFromLong(yogaLong, 1);
};

/**
 * Yogi Sphuta - yoga sphuta with yogi longitude added.
 * Simply calls yogaSphuta with addYogiLongitude=true.
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Yogi Sphuta
 */
export const yogiSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  return yogaSphuta(positions, true);
};

/**
 * Avayogi Sphuta - opposite of yogi point.
 * Formula: (yogiSphuta + 186 + 40/60) % 360
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Avayogi Sphuta
 */
export const avayogiSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  const yogi = yogiSphuta(positions);
  const avayogiLong = (yogi.rasi * 30 + yogi.longitude + 186 + 40 / 60) % 360;
  return dasavargaFromLong(avayogiLong, 1);
};

/**
 * Rahu Tithi Sphuta - tithi sphuta using Rahu instead of Moon.
 * Formula: (Rahu - Sun) % 360
 *
 * @param positions - D-1 planet positions
 * @returns Rasi and longitude of the Rahu Tithi Sphuta
 */
export const rahuTithiSphuta = (positions: PlanetPosition[]): { rasi: number; longitude: number } => {
  const rahuLong = getAbsLong(positions, RAHU);
  const sunLong = getAbsLong(positions, SUN);
  const tithiLong = ((rahuLong - sunLong) % 360 + 360) % 360;
  return dasavargaFromLong(tithiLong, 1);
};
