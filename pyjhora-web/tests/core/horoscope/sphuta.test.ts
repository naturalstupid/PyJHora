/**
 * Tests for Sphuta (Sensitive Point) calculations
 * Test data generated from PyJHora Python implementation
 *
 * Test case: Chennai 1996-12-07 10:34 IST
 * Python D-1 positions:
 *   [['L', (9, 22.45)], [0, (7, 21.57)], [1, (6, 6.96)], [2, (4, 25.54)],
 *    [3, (8, 9.94)], [4, (8, 25.83)], [5, (6, 23.72)], [6, (11, 6.81)],
 *    [7, (5, 10.55)], [8, (11, 10.55)]]
 */

import { describe, expect, it } from 'vitest';
import { PlanetPosition } from '../../../src/core/types';
import {
  beejaSphuta,
  kshetraSphuta,
  tithiSphuta,
  yogaSphuta,
  yogiSphuta,
  avayogiSphuta,
  rahuTithiSphuta,
} from '../../../src/core/horoscope/sphuta';

// D-1 planet positions for Chennai, 1996-12-07, 10:34:00 IST
// Constructed from Python output with full precision
const testPositions: PlanetPosition[] = [
  { planet: -1, rasi: 9, longitude: 22.445758844045656, longitudeInSign: 22.445758844045656, isRetrograde: false, nakshatra: 21, nakshatraPada: 2 },  // Lagna
  { planet: 0, rasi: 7, longitude: 21.565282199774686, longitudeInSign: 21.565282199774686, isRetrograde: false, nakshatra: 17, nakshatraPada: 3 },   // Sun
  { planet: 1, rasi: 6, longitude: 6.959489439173353, longitudeInSign: 6.959489439173353, isRetrograde: false, nakshatra: 14, nakshatraPada: 2 },     // Moon
  { planet: 2, rasi: 4, longitude: 25.53974731723366, longitudeInSign: 25.53974731723366, isRetrograde: false, nakshatra: 10, nakshatraPada: 4 },     // Mars
  { planet: 3, rasi: 8, longitude: 9.936449033727513, longitudeInSign: 9.936449033727513, isRetrograde: false, nakshatra: 19, nakshatraPada: 3 },     // Mercury
  { planet: 4, rasi: 8, longitude: 25.82805158487281, longitudeInSign: 25.82805158487281, isRetrograde: false, nakshatra: 20, nakshatraPada: 4 },     // Jupiter
  { planet: 5, rasi: 6, longitude: 23.71713310477864, longitudeInSign: 23.71713310477864, isRetrograde: false, nakshatra: 15, nakshatraPada: 3 },     // Venus
  { planet: 6, rasi: 11, longitude: 6.8072763533850775, longitudeInSign: 6.8072763533850775, isRetrograde: false, nakshatra: 25, nakshatraPada: 2 },  // Saturn
  { planet: 7, rasi: 5, longitude: 10.553787374475831, longitudeInSign: 10.553787374475831, isRetrograde: false, nakshatra: 12, nakshatraPada: 4 },   // Rahu
  { planet: 8, rasi: 11, longitude: 10.55378737447586, longitudeInSign: 10.55378737447586, isRetrograde: false, nakshatra: 25, nakshatraPada: 3 },    // Ketu
];

// Python expected results (rasi, longitude)
const expectedResults = {
  beeja:      { rasi: 11, longitude: 11.11 },
  kshetra:    { rasi: 7,  longitude: 28.33 },
  tithi:      { rasi: 10, longitude: 15.39 },
  yoga:       { rasi: 1,  longitude: 28.52 },
  yogi:       { rasi: 5,  longitude: 1.86 },
  avayogi:    { rasi: 11, longitude: 8.52 },
  rahuTithi:  { rasi: 9,  longitude: 18.99 },
};

describe('Sphuta (Sensitive Point) Calculations', () => {

  describe('beejaSphuta', () => {
    it('should calculate Beeja Sphuta = (Sun + Jupiter + Venus) % 360', () => {
      const result = beejaSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.beeja.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.beeja.longitude, 0);
    });
  });

  describe('kshetraSphuta', () => {
    it('should calculate Kshetra Sphuta = (Moon + Jupiter + Mars) % 360', () => {
      const result = kshetraSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.kshetra.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.kshetra.longitude, 0);
    });
  });

  describe('tithiSphuta', () => {
    it('should calculate Tithi Sphuta = (Moon - Sun) % 360', () => {
      const result = tithiSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.tithi.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.tithi.longitude, 0);
    });
  });

  describe('yogaSphuta', () => {
    it('should calculate Yoga Sphuta = (Moon + Sun) % 360 without yogi offset', () => {
      const result = yogaSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.yoga.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.yoga.longitude, 0);
    });

    it('should calculate Yoga Sphuta with yogi offset when addYogiLongitude=true', () => {
      const result = yogaSphuta(testPositions, true);
      expect(result.rasi).toBe(expectedResults.yogi.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.yogi.longitude, 0);
    });
  });

  describe('yogiSphuta', () => {
    it('should calculate Yogi Sphuta = (Moon + Sun + 93d20m) % 360', () => {
      const result = yogiSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.yogi.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.yogi.longitude, 0);
    });

    it('should equal yogaSphuta with addYogiLongitude=true', () => {
      const yogiResult = yogiSphuta(testPositions);
      const yogaResult = yogaSphuta(testPositions, true);
      expect(yogiResult.rasi).toBe(yogaResult.rasi);
      expect(yogiResult.longitude).toBeCloseTo(yogaResult.longitude, 10);
    });
  });

  describe('avayogiSphuta', () => {
    it('should calculate Avayogi Sphuta = (yogiSphuta + 186d40m) % 360', () => {
      const result = avayogiSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.avayogi.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.avayogi.longitude, 0);
    });
  });

  describe('rahuTithiSphuta', () => {
    it('should calculate Rahu Tithi Sphuta = (Rahu - Sun) % 360', () => {
      const result = rahuTithiSphuta(testPositions);
      expect(result.rasi).toBe(expectedResults.rahuTithi.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.rahuTithi.longitude, 0);
    });
  });

  describe('Error handling', () => {
    it('should throw when a required planet is missing', () => {
      const incompletePositions = testPositions.filter(p => p.planet !== 0); // Remove Sun
      expect(() => beejaSphuta(incompletePositions)).toThrow('Planet 0 not found');
      expect(() => tithiSphuta(incompletePositions)).toThrow('Planet 0 not found');
      expect(() => rahuTithiSphuta(incompletePositions)).toThrow('Planet 0 not found');
    });

    it('should throw when Moon is missing for kshetraSphuta', () => {
      const noMoon = testPositions.filter(p => p.planet !== 1);
      expect(() => kshetraSphuta(noMoon)).toThrow('Planet 1 not found');
    });

    it('should throw when Rahu is missing for rahuTithiSphuta', () => {
      const noRahu = testPositions.filter(p => p.planet !== 7);
      expect(() => rahuTithiSphuta(noRahu)).toThrow('Planet 7 not found');
    });
  });
});
