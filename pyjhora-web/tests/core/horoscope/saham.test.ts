import { describe, expect, it } from 'vitest';
import {
    SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU
} from '../../../src/core/constants';
import {
    punyaSaham, vidyaSaham, yasasSaham, mitraSaham,
    mahatmyaSaham, ashaSaham, bhratriSaham,
    gauravaSaham, pithriSaham, rajyaSaham,
    maathriSaham, puthraSaham, jeevaSaham, karmaSaham,
    rogaSaham, rogaSaham1, kaliSaham, sastraSaham,
    bandhuSaham, mrithyuSaham, paradesaSaham, arthaSaham,
    paradaraSaham, vanikaSaham, karyasiddhiSaham,
    vivahaSaham, santapaSaham, sraddhaSaham,
    preethiSaham, jadyaSaham, vyaapaaraSaham,
    sathruSaham, jalapatnaSaham, bandhanaSaham,
    apamrithyuSaham, laabhaSaham,
    isCBetweenBToA
} from '../../../src/core/horoscope/saham';

/**
 * Test data from Python: 1996/12/7, 10:34, Hyderabad
 * Planet positions from drik.dhasavarga(jd, place, 1):
 *   Lagna: (7, 21.565282) → 231.565282
 *   Sun:   (6, 6.959489)  → 186.959489
 *   Moon:  (4, 25.539747) → 145.539747
 *   Mars:  (8, 9.936449)  → 249.936449
 *   Merc:  (8, 25.828052) → 265.828052
 *   Jup:   (6, 23.717133) → 203.717133
 *   Venus: (11, 6.807276) → 336.807276
 *   Sat:   (5, 10.553787) → 160.553787
 *   Ketu:  (11, 10.553787)→ 340.553787
 */
const LAGNA_LONG = 7 * 30 + 21.565282;  // 231.565282
const LAGNA_RASI = 7; // Scorpio

const positions = [
    { planet: SUN,     rasi: 6,  longitude: 6 * 30 + 6.959489 },   // 186.959489
    { planet: MOON,    rasi: 4,  longitude: 4 * 30 + 25.539747 },  // 145.539747
    { planet: MARS,    rasi: 8,  longitude: 8 * 30 + 9.936449 },   // 249.936449
    { planet: MERCURY, rasi: 8,  longitude: 8 * 30 + 25.828052 },  // 265.828052
    { planet: JUPITER, rasi: 6,  longitude: 6 * 30 + 23.717133 },  // 203.717133
    { planet: VENUS,   rasi: 11, longitude: 11 * 30 + 6.807276 },  // 336.807276
    { planet: SATURN,  rasi: 5,  longitude: 5 * 30 + 10.553787 },  // 160.553787
    { planet: RAHU,    rasi: 5,  longitude: 5 * 30 + 10.553787 },  // placeholder
    { planet: KETU,    rasi: 11, longitude: 11 * 30 + 10.553787 }, // 340.553787
];

const TOL = 0.01; // tolerance for floating point comparisons

describe('Saham (Arabic Parts) calculations', () => {
    describe('isCBetweenBToA helper', () => {
        it('should return true when C is between B and A', () => {
            // B=Aries(0-30), A=Gemini(60-90), C=Taurus(30-60) → true
            expect(isCBetweenBToA(75, 15, 45)).toBe(true);
        });
        it('should return false when C is not between B and A', () => {
            // B=Aries, A=Taurus, C=Leo → false (C not between B→A)
            expect(isCBetweenBToA(45, 15, 135)).toBe(false);
        });
    });

    describe('Day-time birth parity with Python', () => {
        it('punya_saham (day)', () => {
            expect(punyaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(190.145540, 1);
        });
        it('vidya_saham (day)', () => {
            expect(vidyaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(302.985024, 1);
        });
        it('yasas_saham (day)', () => {
            expect(yasasSaham(positions, LAGNA_LONG, false)).toBeCloseTo(245.136875, 1);
        });
        it('mitra_saham (day)', () => {
            expect(mitraSaham(positions, LAGNA_LONG, false)).toBeCloseTo(350.378869, 1);
        });
        it('mahatmya_saham (day)', () => {
            expect(mahatmyaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(201.774373, 1);
        });
        it('asha_saham (day)', () => {
            expect(ashaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(172.182621, 1);
        });
        it('bhratri_saham', () => {
            expect(bhratriSaham(positions, LAGNA_LONG)).toBeCloseTo(304.728628, 1);
        });
        it('gaurava_saham (day)', () => {
            expect(gauravaSaham(positions, false)).toBeCloseTo(245.136875, 1);
        });
        it('pithri_saham (day)', () => {
            expect(pithriSaham(positions, LAGNA_LONG, false)).toBeCloseTo(205.159580, 1);
        });
        it('rajya_saham (day) = pithri', () => {
            expect(rajyaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(205.159580, 1);
        });
        it('maathri_saham (day)', () => {
            expect(maathriSaham(positions, LAGNA_LONG, false)).toBeCloseTo(70.297753, 1);
        });
        it('puthra_saham (day)', () => {
            expect(puthraSaham(positions, LAGNA_LONG, false)).toBeCloseTo(319.742668, 1);
        });
        it('jeeva_saham (day)', () => {
            expect(jeevaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(188.401936, 1);
        });
        it('karma_saham (day)', () => {
            expect(karmaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(215.673680, 1);
        });
        it('roga_saham', () => {
            expect(rogaSaham(positions, LAGNA_LONG)).toBeCloseTo(317.590817, 1);
        });
        it('roga_saham_1 (day)', () => {
            expect(rogaSaham1(positions, LAGNA_LONG, false)).toBeCloseTo(276.579322, 1);
        });
        it('kali_saham (day)', () => {
            expect(kaliSaham(positions, LAGNA_LONG, false)).toBeCloseTo(215.345966, 1);
        });
        it('sastra_saham (day)', () => {
            expect(sastraSaham(positions, false)).toBeCloseTo(338.991397, 1);
        });
        it('bandhu_saham (day)', () => {
            expect(bandhuSaham(positions, LAGNA_LONG, false)).toBeCloseTo(351.853586, 1);
        });
        it('mrithyu_saham', () => {
            expect(mrithyuSaham(positions, LAGNA_LONG)).toBeCloseTo(167.590817, 1);
        });
        it('paradesa_saham', () => {
            expect(paradesaSaham(positions, LAGNA_LONG, LAGNA_RASI)).toBeCloseTo(197.590817, 1);
        });
        it('artha_saham', () => {
            expect(arthaSaham(positions, LAGNA_LONG, LAGNA_RASI)).toBeCloseTo(289.413431, 1);
        });
        it('paradara_saham (day)', () => {
            expect(paradaraSaham(positions, LAGNA_LONG, false)).toBeCloseTo(21.413069, 1);
        });
        it('vanika_saham (day)', () => {
            expect(vanikaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(141.276978, 1);
        });
        it('karyasiddhi_saham (day)', () => {
            expect(karyasiddhiSaham(positions, LAGNA_LONG, false)).toBeCloseTo(310.401574, 1);
        });
        it('vivaha_saham (day)', () => {
            expect(vivahaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(47.818771, 1);
        });
        it('santapa_saham (day)', () => {
            expect(santapaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(66.579322, 1);
        });
        it('sraddha_saham (day)', () => {
            expect(sraddhaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(348.436110, 1);
        });
        it('preethi_saham (day)', () => {
            expect(preethiSaham(positions, LAGNA_LONG, false)).toBeCloseTo(20.411139, 1);
        });
        it('jadya_saham (day)', () => {
            expect(jadyaSaham(positions, false)).toBeCloseTo(355.210713, 1);
        });
        it('vyaapaara_saham', () => {
            expect(vyaapaaraSaham(positions, LAGNA_LONG)).toBeCloseTo(320.947944, 1);
        });
        it('sathru_saham (day)', () => {
            expect(sathruSaham(positions, LAGNA_LONG, false)).toBeCloseTo(320.947944, 1);
        });
        it('jalapatna_saham (day)', () => {
            expect(jalapatnaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(176.011495, 1);
        });
        it('bandhana_saham (day)', () => {
            expect(bandhanaSaham(positions, LAGNA_LONG, false)).toBeCloseTo(291.157035, 1);
        });
        it('apamrithyu_saham (day)', () => {
            expect(apamrithyuSaham(positions, LAGNA_LONG, false)).toBeCloseTo(63.194115, 1);
        });
        it('laabha_saham (day)', () => {
            expect(laabhaSaham(positions, LAGNA_LONG, LAGNA_RASI, false)).toBeCloseTo(137.302513, 1);
        });
    });

    describe('Night-time birth parity with Python', () => {
        it('punya_saham (night)', () => {
            expect(punyaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(302.985024, 1);
        });
        it('vidya_saham (night)', () => {
            expect(vidyaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(190.145540, 1);
        });
        it('yasas_saham (night)', () => {
            expect(yasasSaham(positions, LAGNA_LONG, true)).toBeCloseTo(330.833173, 1);
        });
        it('mitra_saham (night)', () => {
            expect(mitraSaham(positions, LAGNA_LONG, true)).toBeCloseTo(106.075168, 1);
        });
        it('mahatmya_saham (night)', () => {
            expect(mahatmyaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(178.516707, 1);
        });
        it('asha_saham (night)', () => {
            expect(ashaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(320.947944, 1);
        });
        it('gaurava_saham (night)', () => {
            expect(gauravaSaham(positions, true)).toBeCloseTo(158.782104, 1);
        });
        it('pithri_saham (night)', () => {
            expect(pithriSaham(positions, LAGNA_LONG, true)).toBeCloseTo(287.970984, 1);
        });
        it('rajya_saham (night) = pithri', () => {
            expect(rajyaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(287.970984, 1);
        });
        it('maathri_saham (night)', () => {
            expect(maathriSaham(positions, LAGNA_LONG, true)).toBeCloseTo(62.832811, 1);
        });
        it('puthra_saham (night)', () => {
            expect(puthraSaham(positions, LAGNA_LONG, true)).toBeCloseTo(173.387896, 1);
        });
        it('jeeva_saham (night)', () => {
            expect(jeevaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(304.728628, 1);
        });
        it('karma_saham (night)', () => {
            expect(karmaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(247.456885, 1);
        });
        it('roga_saham_1 (night)', () => {
            expect(rogaSaham1(positions, LAGNA_LONG, true)).toBeCloseTo(216.551242, 1);
        });
        it('kali_saham (night)', () => {
            expect(kaliSaham(positions, LAGNA_LONG, true)).toBeCloseTo(277.784598, 1);
        });
        it('sastra_saham (night)', () => {
            expect(sastraSaham(positions, true)).toBeCloseTo(222.664706, 1);
        });
        it('bandhu_saham (night)', () => {
            expect(bandhuSaham(positions, LAGNA_LONG, true)).toBeCloseTo(141.276978, 1);
        });
        it('paradara_saham (night)', () => {
            expect(paradaraSaham(positions, LAGNA_LONG, true)).toBeCloseTo(111.717495, 1);
        });
        it('vanika_saham (night)', () => {
            expect(vanikaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(351.853586, 1);
        });
        it('karyasiddhi_saham (night)', () => {
            expect(karyasiddhiSaham(positions, LAGNA_LONG, true)).toBeCloseTo(231.973529, 1);
        });
        it('vivaha_saham (night)', () => {
            expect(vivahaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(85.311793, 1);
        });
        it('santapa_saham (night)', () => {
            expect(santapaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(36.551242, 1);
        });
        it('sraddha_saham (night)', () => {
            expect(sraddhaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(144.694455, 1);
        });
        it('preethi_saham (night)', () => {
            expect(preethiSaham(positions, LAGNA_LONG, true)).toBeCloseTo(341.885601, 1);
        });
        it('jadya_saham (night)', () => {
            expect(jadyaSaham(positions, true)).toBeCloseTo(206.445390, 1);
        });
        it('sathru_saham (night)', () => {
            expect(sathruSaham(positions, LAGNA_LONG, true)).toBeCloseTo(172.182621, 1);
        });
        it('jalapatna_saham (night)', () => {
            expect(jalapatnaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(317.119070, 1);
        });
        it('bandhana_saham (night)', () => {
            expect(bandhanaSaham(positions, LAGNA_LONG, true)).toBeCloseTo(119.134045, 1);
        });
        it('apamrithyu_saham (night)', () => {
            expect(apamrithyuSaham(positions, LAGNA_LONG, true)).toBeCloseTo(39.936449, 1);
        });
        it('laabha_saham (night)', () => {
            expect(laabhaSaham(positions, LAGNA_LONG, LAGNA_RASI, true)).toBeCloseTo(325.828052, 1);
        });
    });
});
