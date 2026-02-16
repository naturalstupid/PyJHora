/**
 * Structural tests for Brahma and Kalachakra raasi dhasas.
 * Birth data: 1996/12/7, 10:34, Hyderabad (17.385, 78.487, +5.5)
 * JD = 2450424.940278
 */
import { describe, expect, it } from 'vitest';
import type { Place } from '../../../../src/core/types';
import { getBrahmaDashaBhukti } from '../../../../src/core/dhasa/raasi/brahma';
import { getKalachakraDashaBhukti } from '../../../../src/core/dhasa/raasi/kalachakra';

const place: Place = {
    name: 'Hyderabad',
    latitude: 17.3850,
    longitude: 78.4867,
    timezone: 5.5
};
const jd = 2450424.940278;

describe('Brahma Dasha (Raasi)', () => {
    it('should produce 12 maha dasha periods', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: false });
        expect(result.mahadashas.length).toBe(12);
    });

    it('should have valid rasi values (0-11)', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: false });
        for (const d of result.mahadashas) {
            expect(d.rasi).toBeGreaterThanOrEqual(0);
            expect(d.rasi).toBeLessThanOrEqual(11);
        }
    });

    it('should cover all 12 rasis exactly once', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: false });
        const rasis = result.mahadashas.map(d => d.rasi).sort((a, b) => a - b);
        expect(rasis).toEqual([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
    });

    it('should have durations in valid range (-1 to 12)', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: false });
        for (const d of result.mahadashas) {
            // Brahma dasha durations can be -1 (debilitated lord in own sign edge case)
            // through 12 based on the 6th lord calculation
            expect(d.durationYears).toBeGreaterThanOrEqual(-1);
            expect(d.durationYears).toBeLessThanOrEqual(12);
        }
    });

    it('should produce bhuktis when requested', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: true });
        expect(result.bhuktis).toBeDefined();
        expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have 12 bhuktis per non-zero maha dasha', () => {
        const result = getBrahmaDashaBhukti(jd, place, { includeBhuktis: true });
        const nonZeroDashas = result.mahadashas.filter(d => d.durationYears > 0);
        // Each maha dasha with non-zero duration should have 12 bhuktis
        for (const dasha of nonZeroDashas) {
            const dashaBhuktis = result.bhuktis!.filter(b => b.dashaRasi === dasha.rasi);
            expect(dashaBhuktis.length).toBe(12);
        }
    });
});

describe('Kalachakra Dasha', () => {
    it('should produce 9 maha dasha periods', () => {
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: false });
        expect(result.mahadashas.length).toBe(9);
    });

    it('should have valid rasi values (0-11)', () => {
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: false });
        for (const d of result.mahadashas) {
            expect(d.rasi).toBeGreaterThanOrEqual(0);
            expect(d.rasi).toBeLessThanOrEqual(11);
        }
    });

    it('should have durations from the Kalachakra duration table', () => {
        const validDurations = [7, 16, 9, 21, 5, 9, 16, 7, 10, 4, 4, 10];
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: false });
        // First period may be partial (remaining at birth), but rest should match
        for (let i = 1; i < result.mahadashas.length; i++) {
            expect(validDurations).toContain(result.mahadashas[i]!.durationYears);
        }
    });

    it('should have first period <= max duration for its rasi', () => {
        const durationTable = [7, 16, 9, 21, 5, 9, 16, 7, 10, 4, 4, 10];
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: false });
        const firstPeriod = result.mahadashas[0]!;
        const maxDuration = durationTable[firstPeriod.rasi]!;
        expect(firstPeriod.durationYears).toBeLessThanOrEqual(maxDuration);
        expect(firstPeriod.durationYears).toBeGreaterThan(0);
    });

    it('should produce bhuktis when requested', () => {
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: true });
        expect(result.bhuktis).toBeDefined();
        expect(result.bhuktis!.length).toBeGreaterThan(0);
    });

    it('should have rasi names set', () => {
        const result = getKalachakraDashaBhukti(jd, place, { includeBhuktis: false });
        for (const d of result.mahadashas) {
            expect(d.rasiName).toBeTruthy();
            expect(d.rasiName).not.toBe('');
        }
    });
});
