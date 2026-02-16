/**
 * Tests for geo utility functions (pure-calc only, no browser API)
 */
import { describe, expect, it } from 'vitest';
import {
    formatTimezoneOffset,
    createPlace,
    isValidLatitude,
    isValidLongitude,
    formatPlace,
    haversineDistance,
    COMMON_PLACES
} from '../../../src/core/utils/geo';

describe('Geo Utilities', () => {

    describe('formatTimezoneOffset', () => {
        it('should format positive offset', () => {
            expect(formatTimezoneOffset(5.5)).toBe('+5:30');
        });
        it('should format negative offset', () => {
            expect(formatTimezoneOffset(-8)).toBe('-8:00');
        });
        it('should format zero offset', () => {
            expect(formatTimezoneOffset(0)).toBe('+0:00');
        });
        it('should format fractional offset', () => {
            expect(formatTimezoneOffset(5.75)).toBe('+5:45');
        });
    });

    describe('createPlace', () => {
        it('should create a Place object', () => {
            const place = createPlace('Hyderabad', 17.385, 78.487, 5.5);
            expect(place.name).toBe('Hyderabad');
            expect(place.latitude).toBe(17.385);
            expect(place.longitude).toBe(78.487);
            expect(place.timezone).toBe(5.5);
        });
    });

    describe('isValidLatitude', () => {
        it('should accept valid latitudes', () => {
            expect(isValidLatitude(0)).toBe(true);
            expect(isValidLatitude(90)).toBe(true);
            expect(isValidLatitude(-90)).toBe(true);
            expect(isValidLatitude(17.385)).toBe(true);
        });
        it('should reject invalid latitudes', () => {
            expect(isValidLatitude(91)).toBe(false);
            expect(isValidLatitude(-91)).toBe(false);
        });
    });

    describe('isValidLongitude', () => {
        it('should accept valid longitudes', () => {
            expect(isValidLongitude(0)).toBe(true);
            expect(isValidLongitude(180)).toBe(true);
            expect(isValidLongitude(-180)).toBe(true);
            expect(isValidLongitude(78.487)).toBe(true);
        });
        it('should reject invalid longitudes', () => {
            expect(isValidLongitude(181)).toBe(false);
            expect(isValidLongitude(-181)).toBe(false);
        });
    });

    describe('formatPlace', () => {
        it('should format northern/eastern place', () => {
            const place = createPlace('Hyderabad', 17.385, 78.4867, 5.5);
            const result = formatPlace(place);
            expect(result).toContain('Hyderabad');
            expect(result).toContain('N');
            expect(result).toContain('E');
            expect(result).toContain('+5:30');
        });
        it('should format southern/western place', () => {
            const place = createPlace('Sydney', -33.8688, 151.2093, 11);
            const result = formatPlace(place);
            expect(result).toContain('S');
            expect(result).toContain('E');
        });
    });

    describe('haversineDistance', () => {
        it('should calculate distance between known cities', () => {
            // Delhi to Mumbai: ~1153 km
            const dist = haversineDistance(28.6139, 77.2090, 19.0760, 72.8777);
            expect(dist).toBeGreaterThan(1100);
            expect(dist).toBeLessThan(1200);
        });
        it('should return 0 for same point', () => {
            const dist = haversineDistance(17.385, 78.487, 17.385, 78.487);
            expect(dist).toBe(0);
        });
        it('should be symmetric', () => {
            const d1 = haversineDistance(28.61, 77.21, 19.08, 72.88);
            const d2 = haversineDistance(19.08, 72.88, 28.61, 77.21);
            expect(d1).toBeCloseTo(d2, 5);
        });
    });

    describe('COMMON_PLACES', () => {
        it('should have Hyderabad', () => {
            expect(COMMON_PLACES.HYDERABAD).toBeDefined();
            expect(COMMON_PLACES.HYDERABAD!.timezone).toBe(5.5);
        });
        it('should have international cities', () => {
            expect(COMMON_PLACES.NEW_YORK).toBeDefined();
            expect(COMMON_PLACES.LONDON).toBeDefined();
            expect(COMMON_PLACES.SYDNEY).toBeDefined();
        });
        it('should have valid coordinates for all places', () => {
            for (const [, place] of Object.entries(COMMON_PLACES)) {
                expect(place.latitude).toBeGreaterThanOrEqual(-90);
                expect(place.latitude).toBeLessThanOrEqual(90);
                expect(place.longitude).toBeGreaterThanOrEqual(-180);
                expect(place.longitude).toBeLessThanOrEqual(180);
            }
        });
    });
});
