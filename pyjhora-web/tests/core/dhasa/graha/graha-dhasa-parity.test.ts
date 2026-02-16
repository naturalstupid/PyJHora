/**
 * Python parity tests for 11 untested graha dhasa modules.
 * Birth data: 1996/12/7, 10:34, Hyderabad (17.385, 78.487, +5.5)
 * JD = 2450424.940278
 *
 * Note: Some dasha systems depend on Moon nakshatra which differs slightly
 * between Python (Swiss Ephemeris) and TS (sync approximation). For these,
 * we verify structural correctness (lord-duration mappings, cycle totals,
 * sequential order) rather than exact starting lord.
 */
import { describe, expect, it } from 'vitest';
import type { Place } from '../../../../src/core/types';
import {
    SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU
} from '../../../../src/core/constants';

import { getChaturaseethiDashaBhukti } from '../../../../src/core/dhasa/graha/chaturaseethi';
import { getDwadasottariDashaBhukti } from '../../../../src/core/dhasa/graha/dwadasottari';
import { getDwisatpathiDashaBhukti } from '../../../../src/core/dhasa/graha/dwisatpathi';
import { getNaisargikaDashaBhukti } from '../../../../src/core/dhasa/graha/naisargika';
import { getPanchottariDashaBhukti } from '../../../../src/core/dhasa/graha/panchottari';
import { getSaptharishiDashaBhukti } from '../../../../src/core/dhasa/graha/saptharishi';
import { getSataabdikaDashaBhukti } from '../../../../src/core/dhasa/graha/sataabdika';
import { getShastihayaniDashaBhukti } from '../../../../src/core/dhasa/graha/shastihayani';
import { getShattrimsaDashaBhukti } from '../../../../src/core/dhasa/graha/shattrimsa';
import { getShodasottariDashaBhukti } from '../../../../src/core/dhasa/graha/shodasottari';
import { getTaraDashaBhukti } from '../../../../src/core/dhasa/graha/tara';

const place: Place = {
    name: 'Hyderabad',
    latitude: 17.3850,
    longitude: 78.4867,
    timezone: 5.5
};
const jd = 2450424.940278;

/** Verify lord-duration cycle: lords appear in correct order with correct durations */
function verifyCycle(
    mahadashas: Array<{ lord: number; durationYears: number }>,
    expectedCycle: Array<{ lord: number; dur: number }>
) {
    // Find the starting position in the cycle
    const firstLord = mahadashas[0]!.lord;
    const startIdx = expectedCycle.findIndex(e => e.lord === firstLord);
    expect(startIdx).toBeGreaterThanOrEqual(0); // First lord must be in the cycle

    // Verify all entries match the cycle from that starting point
    for (let i = 0; i < mahadashas.length; i++) {
        const cycleIdx = (startIdx + i) % expectedCycle.length;
        expect(mahadashas[i]!.lord).toBe(expectedCycle[cycleIdx]!.lord);
        expect(mahadashas[i]!.durationYears).toBe(expectedCycle[cycleIdx]!.dur);
    }
}

describe('Graha Dhasa Structural Tests', () => {

    describe('Chaturaseethi Sama Dasha (84-year cycle)', () => {
        it('should produce 7 periods of 12 years each', () => {
            const result = getChaturaseethiDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(7);
            // Python: all 12-year periods, order: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
            const cycle = [
                { lord: SUN, dur: 12 }, { lord: MOON, dur: 12 }, { lord: MARS, dur: 12 },
                { lord: MERCURY, dur: 12 }, { lord: JUPITER, dur: 12 }, { lord: VENUS, dur: 12 },
                { lord: SATURN, dur: 12 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });

        it('should total 84 years', () => {
            const result = getChaturaseethiDashaBhukti(jd, place, { includeBhuktis: false });
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(84);
        });

        it('should produce bhuktis when requested', () => {
            const result = getChaturaseethiDashaBhukti(jd, place, { includeBhuktis: true });
            expect(result.bhuktis).toBeDefined();
            expect(result.bhuktis!.length).toBeGreaterThan(0);
        });
    });

    describe('Dwadasottari Dasha (112-year cycle)', () => {
        it('should produce 8 periods totaling 112 years', () => {
            const result = getDwadasottariDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(8);
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(112);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getDwadasottariDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Sun=7, Jupiter=9, Ketu=11, Mercury=13, Rahu=15, Mars=17, Saturn=19, Moon=21
            const cycle = [
                { lord: SUN, dur: 7 }, { lord: JUPITER, dur: 9 }, { lord: KETU, dur: 11 },
                { lord: MERCURY, dur: 13 }, { lord: RAHU, dur: 15 }, { lord: MARS, dur: 17 },
                { lord: SATURN, dur: 19 }, { lord: MOON, dur: 21 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });
    });

    describe('Dwisatpathi Dasha (190-year cycle)', () => {
        it('should produce equal 9-year periods', () => {
            const result = getDwisatpathiDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBeGreaterThanOrEqual(8);
            for (const d of result.mahadashas) {
                expect(d.durationYears).toBe(9);
            }
        });

        it('should use correct planet cycle', () => {
            const result = getDwisatpathiDashaBhukti(jd, place, { includeBhuktis: false });
            const cycle = [
                { lord: RAHU, dur: 9 }, { lord: SUN, dur: 9 }, { lord: MOON, dur: 9 },
                { lord: MARS, dur: 9 }, { lord: MERCURY, dur: 9 }, { lord: JUPITER, dur: 9 },
                { lord: VENUS, dur: 9 }, { lord: SATURN, dur: 9 },
            ];
            verifyCycle(result.mahadashas.slice(0, 8), cycle);
        });
    });

    describe('Naisargika Dasha (fixed sequence)', () => {
        it('should produce correct fixed sequence', () => {
            const result = getNaisargikaDashaBhukti(jd, place, { includeBhuktis: false });
            // Naisargika is always in natural order: Moon, Mars, Mercury, Venus, Jupiter, Sun, Saturn
            const expected = [
                { lord: MOON, dur: 1 }, { lord: MARS, dur: 2 },
                { lord: MERCURY, dur: 9 }, { lord: VENUS, dur: 20 },
                { lord: JUPITER, dur: 18 }, { lord: SUN, dur: 20 },
                { lord: SATURN, dur: 50 },
            ];
            expect(result.mahadashas.length).toBeGreaterThanOrEqual(7);
            for (let i = 0; i < Math.min(7, result.mahadashas.length); i++) {
                expect(result.mahadashas[i]!.lord).toBe(expected[i]!.lord);
                expect(result.mahadashas[i]!.durationYears).toBe(expected[i]!.dur);
            }
        });

        it('should total 120 years for first 7 periods', () => {
            const result = getNaisargikaDashaBhukti(jd, place, { includeBhuktis: false });
            const total = result.mahadashas.slice(0, 7).reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(120);
        });
    });

    describe('Panchottari Dasha (105-year cycle)', () => {
        it('should produce 7 periods totaling 105 years', () => {
            const result = getPanchottariDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(7);
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(105);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getPanchottariDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Sun=12, Mercury=13, Saturn=14, Mars=15, Venus=16, Moon=17, Jupiter=18
            const cycle = [
                { lord: SUN, dur: 12 }, { lord: MERCURY, dur: 13 }, { lord: SATURN, dur: 14 },
                { lord: MARS, dur: 15 }, { lord: VENUS, dur: 16 }, { lord: MOON, dur: 17 },
                { lord: JUPITER, dur: 18 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });
    });

    describe('Saptharishi Nakshatra Dasha', () => {
        it('should produce periods with 10-year durations', () => {
            const result = getSaptharishiDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBeGreaterThanOrEqual(9);
            for (const d of result.mahadashas) {
                expect(d.durationYears).toBe(10);
            }
        });

        it('should have valid starting lord', () => {
            const result = getSaptharishiDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas[0]!.lord).toBeGreaterThanOrEqual(0);
        });

        it('should have decreasing lord sequence (nakshatras count down)', () => {
            const result = getSaptharishiDashaBhukti(jd, place, { includeBhuktis: false });
            // In Saptharishi, lords count down in nakshatra order
            if (result.mahadashas.length >= 2) {
                const first = result.mahadashas[0]!.lord;
                const second = result.mahadashas[1]!.lord;
                // Lords decrease by 1 (wrapping around 27)
                expect(second).toBe(first === 0 ? 26 : first - 1);
            }
        });
    });

    describe('Sataabdika Dasha (100-year cycle)', () => {
        it('should produce 7 periods totaling 100 years', () => {
            const result = getSataabdikaDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(7);
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(100);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getSataabdikaDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Sun=5, Moon=5, Venus=10, Mercury=10, Jupiter=20, Mars=20, Saturn=30
            const cycle = [
                { lord: SUN, dur: 5 }, { lord: MOON, dur: 5 }, { lord: VENUS, dur: 10 },
                { lord: MERCURY, dur: 10 }, { lord: JUPITER, dur: 20 }, { lord: MARS, dur: 20 },
                { lord: SATURN, dur: 30 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });
    });

    describe('Shastihayani Dasha (60-year cycle)', () => {
        it('should produce 8 periods totaling 60 years', () => {
            const result = getShastihayaniDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(8);
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(60);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getShastihayaniDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Jupiter=10, Sun=10, Mars=10, Moon=6, Mercury=6, Venus=6, Saturn=6, Rahu=6
            const cycle = [
                { lord: JUPITER, dur: 10 }, { lord: SUN, dur: 10 }, { lord: MARS, dur: 10 },
                { lord: MOON, dur: 6 }, { lord: MERCURY, dur: 6 }, { lord: VENUS, dur: 6 },
                { lord: SATURN, dur: 6 }, { lord: RAHU, dur: 6 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });
    });

    describe('Shattrimsa Sama Dasha (36-year cycle)', () => {
        it('should produce at least 8 periods', () => {
            const result = getShattrimsaDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBeGreaterThanOrEqual(8);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getShattrimsaDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Moon=1, Sun=2, Jupiter=3, Mars=4, Mercury=5, Saturn=6, Venus=7, Rahu=8
            const cycle = [
                { lord: MOON, dur: 1 }, { lord: SUN, dur: 2 }, { lord: JUPITER, dur: 3 },
                { lord: MARS, dur: 4 }, { lord: MERCURY, dur: 5 }, { lord: SATURN, dur: 6 },
                { lord: VENUS, dur: 7 }, { lord: RAHU, dur: 8 },
            ];
            verifyCycle(result.mahadashas.slice(0, 8), cycle);
        });

        it('should have first cycle totaling 36 years', () => {
            const result = getShattrimsaDashaBhukti(jd, place, { includeBhuktis: false });
            const total = result.mahadashas.slice(0, 8).reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(36);
        });
    });

    describe('Shodasottari Dasha (116-year cycle)', () => {
        it('should produce 8 periods totaling 116 years', () => {
            const result = getShodasottariDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(8);
            const total = result.mahadashas.reduce((sum, d) => sum + d.durationYears, 0);
            expect(total).toBe(116);
        });

        it('should have correct lord-duration cycle', () => {
            const result = getShodasottariDashaBhukti(jd, place, { includeBhuktis: false });
            // TS order: Sun=11, Mars=12, Jupiter=13, Saturn=14, Ketu=15, Moon=16, Mercury=17, Venus=18
            const cycle = [
                { lord: SUN, dur: 11 }, { lord: MARS, dur: 12 }, { lord: JUPITER, dur: 13 },
                { lord: SATURN, dur: 14 }, { lord: KETU, dur: 15 }, { lord: MOON, dur: 16 },
                { lord: MERCURY, dur: 17 }, { lord: VENUS, dur: 18 },
            ];
            verifyCycle(result.mahadashas, cycle);
        });
    });

    describe('Tara Dasha', () => {
        it('should produce 9 maha dasha periods', () => {
            const result = getTaraDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas.length).toBe(9);
        });

        it('should start with Venus as default starting lord', () => {
            const result = getTaraDashaBhukti(jd, place, { includeBhuktis: false });
            expect(result.mahadashas[0]!.lord).toBe(VENUS);
        });

        it('should have positive durations', () => {
            const result = getTaraDashaBhukti(jd, place, { includeBhuktis: false });
            for (const d of result.mahadashas) {
                expect(d.durationYears).toBeGreaterThan(0);
            }
        });

        it('should produce bhuktis for each maha dasha', () => {
            const result = getTaraDashaBhukti(jd, place, { includeBhuktis: true });
            expect(result.bhuktis).toBeDefined();
            expect(result.bhuktis!.length).toBeGreaterThan(0);
        });
    });
});
