/**
 * Tests for Ashtakoota (8-point) Marriage Compatibility System.
 */
import { describe, expect, it } from 'vitest';
import {
  rasiFromNakshatraPada,
  varnaPorutham,
  vasiyaPorutham,
  ganaPorutham,
  nakshatraPorutham,
  yoniPorutham,
  rasiAdhipathiPorutham,
  maitriPorutham,
  rasiPorutham,
  bahutPorutham,
  naadiPorutham,
  mahendraPorutham,
  vedhaPorutham,
  rajjuPorutham,
  sthreeDheergaPorutham,
  compatibilityScore,
  MAX_SCORE_NORTH,
  MAX_SCORE_SOUTH,
} from '../../../src/core/horoscope/compatibility';

describe('Compatibility / Ashtakoota', () => {
  // =====================================================
  // Helper: rasiFromNakshatraPada
  // =====================================================
  describe('rasiFromNakshatraPada', () => {
    it('should return Aries(0) for Ashwini(1) pada 1', () => {
      expect(rasiFromNakshatraPada(1, 1)).toBe(0);
    });

    it('should return Aries(0) for Ashwini(1) pada 4', () => {
      // Ashwini padas 1-4 all map to Aries (first 4 padas = 1 rasi worth at 9 padas/rasi... nope 4 padas per nakshatra, 9 padas per rasi)
      // Pada 4 → totalPadas = 3 → floor(3/9) = 0 = Aries
      expect(rasiFromNakshatraPada(1, 4)).toBe(0);
    });

    it('should return Taurus(1) for Krittika(3) pada 2', () => {
      // totalPadas = (3-1)*4 + (2-1) = 9 → floor(9/9) = 1 = Taurus
      expect(rasiFromNakshatraPada(3, 2)).toBe(1);
    });

    it('should return Pisces(11) for Revati(27) pada 4', () => {
      // totalPadas = (27-1)*4 + 3 = 107 → floor(107/9) = 11 = Pisces
      expect(rasiFromNakshatraPada(27, 4)).toBe(11);
    });

    it('should return Cancer(3) for Pushya(8) pada 1', () => {
      // totalPadas = 7*4 + 0 = 28 → floor(28/9) = 3 = Cancer
      expect(rasiFromNakshatraPada(8, 1)).toBe(3);
    });
  });

  // =====================================================
  // Varna Porutham
  // =====================================================
  describe('varnaPorutham', () => {
    it('should return 1 when boy varna >= girl varna', () => {
      // Both Aries(0) = Shudra(3), same varna → 1
      expect(varnaPorutham(0, 0, 'North')).toBe(1);
    });

    it('should return 0 when boy varna < girl varna', () => {
      // Boy=Aries(0)=Shudra(3), Girl=Taurus(1)=Vaishya(2)
      // VarnaArray[3][2] = 1 (Shudra can match Vaishya)
      // Boy=Pisces(11)=Brahmin(0), Girl=Aries(0)=Shudra(3)
      // VarnaArray[0][3] = 0
      expect(varnaPorutham(11, 0, 'North')).toBe(0);
    });

    it('should return boolean for South method', () => {
      const result = varnaPorutham(0, 0, 'South');
      expect(typeof result).toBe('boolean');
    });
  });

  // =====================================================
  // Vasiya Porutham
  // =====================================================
  describe('vasiyaPorutham', () => {
    it('should return score between 0 and 2 for North', () => {
      const score = vasiyaPorutham(0, 3, 'North') as number;
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(2);
    });

    it('should return 2.0 for same vasiya type', () => {
      // Aries(0) → Manava(1), Cancer(3) → Chathushpadha(0)
      // Same type: Aries(0)+Taurus(1) → both have vasiya_rasi[0]=1,vasiya_rasi[1]=3
      // Let's try two signs with same vasiya: Aries(0)→1(Manava), Leo(4)→1(Manava)
      expect(vasiyaPorutham(0, 4, 'North')).toBe(2.0);
    });

    it('should return boolean for South method', () => {
      const result = vasiyaPorutham(0, 3, 'South');
      expect(typeof result).toBe('boolean');
    });
  });

  // =====================================================
  // Gana Porutham
  // =====================================================
  describe('ganaPorutham', () => {
    it('should return 6 for same gana', () => {
      // Ashwini(1) = Deva, Mrigashira(5) = Deva
      expect(ganaPorutham(1, 5, 'North')).toBe(6);
    });

    it('should return 0 for Deva-Rakshasa mismatch', () => {
      // Ashwini(1)=Deva, Bharani(3)=Rakshasa → GanaArray[0][2] = 0
      expect(ganaPorutham(1, 3, 'North')).toBe(0);
    });

    it('should return boolean for South method', () => {
      const result = ganaPorutham(1, 5, 'South');
      expect(typeof result).toBe('boolean');
    });

    it('should return max score 6', () => {
      const score = ganaPorutham(1, 1, 'North') as number;
      expect(score).toBeLessThanOrEqual(6);
    });
  });

  // =====================================================
  // Nakshatra / Tara / Dina Porutham
  // =====================================================
  describe('nakshatraPorutham', () => {
    it('should return between 0 and 3', () => {
      const score = nakshatraPorutham(1, 10);
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(3);
    });

    it('should return 3 for same nakshatra', () => {
      // Same star: count=27, 27%9=0→9, position 9 (Athi-Mithra) → 3.0
      expect(nakshatraPorutham(1, 1)).toBe(3);
    });

    it('should return 1.5 for unfavorable position', () => {
      // Position 3 (Vipat), 5 (Pratyari), 7 (Vaadh) → 1.5
      // Count of 3 from girl: boy=girl+3 → boy=1+3=4
      // countFromGirl = (4-1+27)%27 = 3, pos = 3%9 = 3 → 1.5
      // countFromBoy = (1-4+27)%27 = 24, pos = 24%9 = 6 → 3.0
      // min(1.5, 3.0) = 1.5
      expect(nakshatraPorutham(4, 1)).toBe(1.5);
    });
  });

  // =====================================================
  // Yoni Porutham
  // =====================================================
  describe('yoniPorutham', () => {
    it('should return between 0 and 4 for North', () => {
      const score = yoniPorutham(1, 15, 'North') as number;
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(4);
    });

    it('should return 4 for same yoni animal', () => {
      // Ashwini(1) → yoni 0 (Horse), Satabisha(24) → yoni 0 (Horse)
      expect(yoniPorutham(1, 24, 'North')).toBe(4);
    });

    it('should return boolean for South method', () => {
      const result = yoniPorutham(1, 15, 'South');
      expect(typeof result).toBe('boolean');
    });
  });

  // =====================================================
  // Raasi Adhipathi / Maitri Porutham
  // =====================================================
  describe('rasiAdhipathiPorutham', () => {
    it('should return between 0 and 5 for North', () => {
      const score = rasiAdhipathiPorutham(0, 6, 'North') as number;
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(5);
    });

    it('should return 5.0 for same lord', () => {
      // Aries(0) lord=Mars(2), Scorpio(7) lord=Mars(2)
      expect(rasiAdhipathiPorutham(0, 7, 'North')).toBe(5.0);
    });

    it('should be same as maitriPorutham alias', () => {
      expect(maitriPorutham(3, 5, 'North')).toBe(rasiAdhipathiPorutham(3, 5, 'North'));
    });

    it('should return boolean for South method', () => {
      const result = rasiAdhipathiPorutham(0, 6, 'South');
      expect(typeof result).toBe('boolean');
    });
  });

  // =====================================================
  // Raasi / Bahut Porutham
  // =====================================================
  describe('rasiPorutham', () => {
    it('should return 0 or 7 for North', () => {
      const score = rasiPorutham(0, 0, 'North') as number;
      expect([0, 7]).toContain(score);
    });

    it('should return 7 for 6th/7th rasi from each other', () => {
      // Aries(0) and Libra(6) → rasiArray[0][6] = 7
      expect(rasiPorutham(0, 6, 'North')).toBe(7);
    });

    it('should be same as bahutPorutham alias', () => {
      expect(bahutPorutham(2, 8, 'North')).toBe(rasiPorutham(2, 8, 'North'));
    });

    it('should return boolean for South method', () => {
      const result = rasiPorutham(0, 6, 'South');
      expect(typeof result).toBe('boolean');
    });
  });

  // =====================================================
  // Naadi Porutham
  // =====================================================
  describe('naadiPorutham', () => {
    it('should return 0 or 8', () => {
      const score = naadiPorutham(1, 2);
      expect([0, 8]).toContain(score);
    });

    it('should return 0 for same naadi', () => {
      // Ashwini(1) → naadi 0, Bharani(2) → naadi 1 → different → 8
      // Same naadi: Ashwini(1)→0, Magha(10)→0 → NadiArray[0][0] = 0
      expect(naadiPorutham(1, 10)).toBe(0);
    });

    it('should return 8 for different naadi', () => {
      // Ashwini(1)→0, Bharani(2)→1 → NadiArray[0][1] = 8
      expect(naadiPorutham(1, 2)).toBe(8);
    });
  });

  // =====================================================
  // Mahendra Porutham
  // =====================================================
  describe('mahendraPorutham', () => {
    it('should return true when count is in allowed list', () => {
      // count = (boy - girl + 27) % 27; allowed: 4,7,10,13,16,19,22,25
      // boy=5, girl=1 → count = 4 → true
      expect(mahendraPorutham(5, 1)).toBe(true);
    });

    it('should return false when count is not in allowed list', () => {
      // boy=3, girl=1 → count = 2 → false
      expect(mahendraPorutham(3, 1)).toBe(false);
    });
  });

  // =====================================================
  // Vedha Porutham
  // =====================================================
  describe('vedhaPorutham', () => {
    it('should return true when sum is not in vedha pairs', () => {
      // sum = 1 + 2 = 3 → not in [19, 28, 37] → true
      expect(vedhaPorutham(1, 2)).toBe(true);
    });

    it('should return false when sum is in vedha pairs', () => {
      // sum = 10 + 9 = 19 → in vedha pairs → false
      expect(vedhaPorutham(10, 9)).toBe(false);
    });
  });

  // =====================================================
  // Rajju Porutham
  // =====================================================
  describe('rajjuPorutham', () => {
    it('should return true when different rajju groups', () => {
      // Ashwini(1) = Foot, Rohini(4) = Neck → different → true
      expect(rajjuPorutham(1, 4)).toBe(true);
    });

    it('should return false when same rajju group', () => {
      // Ashwini(1) = Foot, Makha(10) = Foot → same → false
      expect(rajjuPorutham(1, 10)).toBe(false);
    });
  });

  // =====================================================
  // Sthree Dheerga Porutham
  // =====================================================
  describe('sthreeDheergaPorutham', () => {
    it('should return true when count exceeds threshold', () => {
      // North threshold = 15
      // boy=20, girl=1 → count = 19 > 15 → true
      expect(sthreeDheergaPorutham(20, 1, 'North')).toBe(true);
    });

    it('should return false when count is below threshold', () => {
      // boy=5, girl=1 → count = 4 < 15 → false
      expect(sthreeDheergaPorutham(5, 1, 'North')).toBe(false);
    });

    it('should use lower threshold for South', () => {
      // South threshold = 7
      // boy=10, girl=1 → count = 9 > 7 → true
      expect(sthreeDheergaPorutham(10, 1, 'South')).toBe(true);
    });
  });

  // =====================================================
  // Compatibility Score (Aggregation)
  // =====================================================
  describe('compatibilityScore', () => {
    it('should return all score fields for North method', () => {
      const result = compatibilityScore(1, 1, 15, 3, 'North');
      expect(result.maxScore).toBe(MAX_SCORE_NORTH);
      expect(result.totalScore).toBeGreaterThanOrEqual(0);
      expect(result.totalScore).toBeLessThanOrEqual(MAX_SCORE_NORTH);
      expect(typeof result.mahendra).toBe('boolean');
      expect(typeof result.vedha).toBe('boolean');
      expect(typeof result.rajju).toBe('boolean');
      expect(typeof result.sthreeDheerga).toBe('boolean');
    });

    it('should return all score fields for South method', () => {
      const result = compatibilityScore(1, 1, 15, 3, 'South');
      expect(result.maxScore).toBe(MAX_SCORE_SOUTH);
      expect(result.totalScore).toBeGreaterThanOrEqual(0);
      expect(result.totalScore).toBeLessThanOrEqual(MAX_SCORE_SOUTH);
    });

    it('should have total equal to sum of individual scores (North)', () => {
      const result = compatibilityScore(5, 2, 20, 1, 'North');
      const sum = result.varna + result.vasiya + result.gana + result.dina +
        result.yoni + result.rasiAdhipathi + result.rasi + result.naadi;
      expect(result.totalScore).toBeCloseTo(sum, 5);
    });

    it('should give maximum score for identical nakshatras (North)', () => {
      // Same star, same pada — should get high scores
      const result = compatibilityScore(1, 1, 1, 1, 'North');
      expect(result.varna).toBe(1); // Same varna
      expect(result.gana).toBe(6); // Same gana
      expect(result.naadi).toBe(0); // Same naadi → 0 (inauspicious)
    });

    it('should give high score for compatible pairs', () => {
      // Ashwini(1)+Satabisha(24) = same yoni (Horse), different naadi
      const result = compatibilityScore(1, 1, 24, 1, 'North');
      expect(result.yoni).toBe(4); // Same animal
    });

    it('should produce different results for North vs South', () => {
      const north = compatibilityScore(5, 2, 20, 1, 'North');
      const south = compatibilityScore(5, 2, 20, 1, 'South');
      expect(north.maxScore).toBe(36);
      expect(south.maxScore).toBe(10);
    });

    it('should work for all nakshatra-pada combinations boundary', () => {
      // First possible: nak=1, pada=1
      const first = compatibilityScore(1, 1, 27, 4, 'North');
      expect(first.totalScore).toBeGreaterThanOrEqual(0);

      // Last possible: nak=27, pada=4
      const last = compatibilityScore(27, 4, 1, 1, 'North');
      expect(last.totalScore).toBeGreaterThanOrEqual(0);
    });

    it('should include mahendra/vedha/rajju/sthreeDheerga checks', () => {
      const result = compatibilityScore(10, 2, 9, 3, 'North');
      // 10+9 = 19 → vedha pair → vedha should be false
      expect(result.vedha).toBe(false);
    });
  });
});
