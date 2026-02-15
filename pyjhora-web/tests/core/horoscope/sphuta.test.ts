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
  triSphuta,
  chaturSphuta,
  panchaSphuta,
  pranaSphuta,
  dehaSphuta,
  mrityuSphuta,
  sookshmaTriSphuta,
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

// Gulika longitude for Chennai 1996-12-07 10:34 IST (from Python drik.gulika_longitude)
// rasi=7, longitude=21.383659705803353, absolute=231.38365970580335
const gulikaLongitude = 7 * 30 + 21.383659705803353; // 231.38365970580335

// Python expected results (rasi, longitude)
const expectedResults = {
  // Gulika-dependent sphutas (from Python sphuta.py)
  tri:              { rasi: 11, longitude: 20.78890798902239 },
  chatur:           { rasi: 7,  longitude: 12.35419018879702 },
  pancha:           { rasi: 0,  longitude: 22.90797756327288 },
  prana:            { rasi: 8,  longitude: 13.612453926031776 },
  deha:             { rasi: 9,  longitude: 17.059575219190265 },
  mrityu:           { rasi: 1,  longitude: 21.250900140398016 },
  sookshma:         { rasi: 7,  longitude: 21.922929285620057 },
  // Non-Gulika sphutas
  beeja:      { rasi: 11, longitude: 11.11 },
  kshetra:    { rasi: 7,  longitude: 28.33 },
  tithi:      { rasi: 10, longitude: 15.39 },
  yoga:       { rasi: 1,  longitude: 28.52 },
  yogi:       { rasi: 5,  longitude: 1.86 },
  avayogi:    { rasi: 11, longitude: 8.52 },
  rahuTithi:  { rasi: 9,  longitude: 18.99 },
};

describe('Sphuta (Sensitive Point) Calculations', () => {

  // =========================================================================
  // Gulika-dependent sphuta functions
  // =========================================================================

  describe('triSphuta', () => {
    it('should calculate Tri Sphuta = (Moon + Ascendant + Gulika) % 360', () => {
      const result = triSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.tri.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.tri.longitude, 5);
    });
  });

  describe('chaturSphuta', () => {
    it('should calculate Chatur Sphuta = (Sun + triSphuta) % 360', () => {
      const result = chaturSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.chatur.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.chatur.longitude, 5);
    });
  });

  describe('panchaSphuta', () => {
    it('should calculate Pancha Sphuta = (Rahu + chaturSphuta) % 360', () => {
      const result = panchaSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.pancha.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.pancha.longitude, 5);
    });
  });

  describe('pranaSphuta', () => {
    it('should calculate Prana Sphuta = (Ascendant*5 + Gulika) % 360', () => {
      const result = pranaSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.prana.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.prana.longitude, 5);
    });
  });

  describe('dehaSphuta', () => {
    it('should calculate Deha Sphuta = (Moon*8 + Gulika) % 360', () => {
      const result = dehaSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.deha.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.deha.longitude, 5);
    });
  });

  describe('mrityuSphuta', () => {
    it('should calculate Mrityu Sphuta = (Gulika*7 + Sun) % 360', () => {
      const result = mrityuSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.mrityu.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.mrityu.longitude, 5);
    });
  });

  describe('sookshmaTriSphuta', () => {
    it('should calculate Sookshma Tri Sphuta = (prana + deha + mrityu) % 360', () => {
      const result = sookshmaTriSphuta(testPositions, gulikaLongitude);
      expect(result.rasi).toBe(expectedResults.sookshma.rasi);
      expect(result.longitude).toBeCloseTo(expectedResults.sookshma.longitude, 5);
    });

    it('should equal sum of prana, deha, and mrityu sphutas', () => {
      const prana = pranaSphuta(testPositions, gulikaLongitude);
      const deha = dehaSphuta(testPositions, gulikaLongitude);
      const mrityu = mrityuSphuta(testPositions, gulikaLongitude);
      const manualLong = (
        prana.rasi * 30 + prana.longitude +
        deha.rasi * 30 + deha.longitude +
        mrityu.rasi * 30 + mrityu.longitude
      ) % 360;
      const result = sookshmaTriSphuta(testPositions, gulikaLongitude);
      const resultLong = result.rasi * 30 + result.longitude;
      expect(resultLong).toBeCloseTo(manualLong, 10);
    });
  });

  // =========================================================================
  // Non-Gulika sphuta functions
  // =========================================================================

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

    it('should throw when Lagna is missing for triSphuta', () => {
      const noLagna = testPositions.filter(p => p.planet !== -1);
      expect(() => triSphuta(noLagna, gulikaLongitude)).toThrow('Planet -1 not found');
    });

    it('should throw when Moon is missing for dehaSphuta', () => {
      const noMoon = testPositions.filter(p => p.planet !== 1);
      expect(() => dehaSphuta(noMoon, gulikaLongitude)).toThrow('Planet 1 not found');
    });

    it('should throw when Sun is missing for mrityuSphuta', () => {
      const noSun = testPositions.filter(p => p.planet !== 0);
      expect(() => mrityuSphuta(noSun, gulikaLongitude)).toThrow('Planet 0 not found');
    });
  });
});
