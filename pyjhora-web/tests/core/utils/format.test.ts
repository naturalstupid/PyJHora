/**
 * Tests for format utility functions
 */
import { describe, expect, it } from 'vitest';
import {
    formatTime,
    formatTime12Hour,
    parseTime,
    formatDate,
    formatDateLocalized,
    getMonthName,
    formatPlanetLongitude,
    toDmsString,
    formatDuration,
    formatDurationFull,
    formatPlanet,
    formatHouseContent,
    formatDateTime,
} from '../../../src/core/utils/format';

describe('Format Utilities', () => {

    describe('formatTime', () => {
        it('should format time as HH:MM:SS', () => {
            expect(formatTime({ hour: 10, minute: 34, second: 0 })).toBe('10:34:00');
        });
        it('should pad single digits', () => {
            expect(formatTime({ hour: 5, minute: 3, second: 9 })).toBe('05:03:09');
        });
        it('should handle midnight', () => {
            expect(formatTime({ hour: 0, minute: 0, second: 0 })).toBe('00:00:00');
        });
    });

    describe('formatTime12Hour', () => {
        it('should format morning time with AM', () => {
            expect(formatTime12Hour({ hour: 10, minute: 34, second: 0 })).toBe('10:34:00 AM');
        });
        it('should format afternoon time with PM', () => {
            expect(formatTime12Hour({ hour: 14, minute: 30, second: 0 })).toBe('02:30:00 PM');
        });
        it('should handle noon', () => {
            expect(formatTime12Hour({ hour: 12, minute: 0, second: 0 })).toBe('12:00:00 PM');
        });
        it('should handle midnight', () => {
            expect(formatTime12Hour({ hour: 0, minute: 0, second: 0 })).toBe('12:00:00 AM');
        });
    });

    describe('parseTime', () => {
        it('should parse 24-hour time', () => {
            expect(parseTime('10:34:00')).toEqual({ hour: 10, minute: 34, second: 0 });
        });
        it('should parse 12-hour AM time', () => {
            expect(parseTime('10:34:00 AM')).toEqual({ hour: 10, minute: 34, second: 0 });
        });
        it('should parse 12-hour PM time', () => {
            expect(parseTime('02:30:00 PM')).toEqual({ hour: 14, minute: 30, second: 0 });
        });
        it('should handle 12 PM as noon', () => {
            expect(parseTime('12:00:00 PM')).toEqual({ hour: 12, minute: 0, second: 0 });
        });
        it('should handle 12 AM as midnight', () => {
            expect(parseTime('12:00:00 AM')).toEqual({ hour: 0, minute: 0, second: 0 });
        });
        it('should return null for invalid strings', () => {
            expect(parseTime('invalid')).toBeNull();
            expect(parseTime('25:00:00')).toBeNull();
            expect(parseTime('10:60:00')).toBeNull();
        });
    });

    describe('formatDate', () => {
        it('should format normal date', () => {
            expect(formatDate({ year: 1996, month: 12, day: 7 })).toBe('1996-12-07');
        });
        it('should format BC date', () => {
            expect(formatDate({ year: -500, month: 3, day: 15 })).toBe('500 BC-03-15');
        });
    });

    describe('formatDateLocalized', () => {
        it('should format BC dates', () => {
            const result = formatDateLocalized({ year: 0, month: 1, day: 1 });
            expect(result).toContain('BC');
        });
    });

    describe('getMonthName', () => {
        it('should return correct month names', () => {
            expect(getMonthName(1)).toBe('January');
            expect(getMonthName(6)).toBe('June');
            expect(getMonthName(12)).toBe('December');
        });
        it('should return Unknown for invalid months', () => {
            expect(getMonthName(0)).toBe('Unknown');
            expect(getMonthName(13)).toBe('Unknown');
        });
    });

    describe('formatPlanetLongitude', () => {
        it('should format longitude as DMS', () => {
            const result = formatPlanetLongitude(15.5);
            expect(result).toContain('15');
            expect(result).toContain('30');
        });
    });

    describe('toDmsString', () => {
        it('should format latitude with N/S', () => {
            expect(toDmsString(17.385, 'lat')).toContain('N');
            expect(toDmsString(-33.87, 'lat')).toContain('S');
        });
        it('should format longitude with E/W', () => {
            expect(toDmsString(78.487, 'long')).toContain('E');
            expect(toDmsString(-74.006, 'long')).toContain('W');
        });
        it('should format planet longitude without direction', () => {
            const result = toDmsString(186.96, 'plong');
            expect(result).not.toContain('N');
            expect(result).not.toContain('E');
        });
    });

    describe('formatDuration', () => {
        it('should format full duration', () => {
            expect(formatDuration(2, 3, 15)).toBe('2y 3m 15d');
        });
        it('should skip zero parts', () => {
            expect(formatDuration(5, 0, 0)).toBe('5y');
            expect(formatDuration(0, 6, 0)).toBe('6m');
        });
        it('should show 0d when all zeros', () => {
            expect(formatDuration(0, 0, 0)).toBe('0d');
        });
    });

    describe('formatDurationFull', () => {
        it('should format with full words', () => {
            expect(formatDurationFull(2, 3, 15)).toBe('2 years, 3 months and 15 days');
        });
        it('should use singular for 1', () => {
            expect(formatDurationFull(1, 1, 1)).toBe('1 year, 1 month and 1 day');
        });
        it('should return 0 days for all zeros', () => {
            expect(formatDurationFull(0, 0, 0)).toBe('0 days');
        });
    });

    describe('formatPlanet', () => {
        const names = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'];
        it('should format planet name', () => {
            expect(formatPlanet(0, names)).toBe('Sun');
            expect(formatPlanet(4, names)).toBe('Jupiter');
        });
        it('should include longitude when provided', () => {
            const result = formatPlanet(0, names, 15.5);
            expect(result).toContain('Sun');
            expect(result).toContain('15');
        });
        it('should handle unknown planet index', () => {
            expect(formatPlanet(99, names)).toBe('Planet99');
        });
    });

    describe('formatHouseContent', () => {
        const symbols = ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke'];
        it('should format planets in house', () => {
            expect(formatHouseContent([0, 1], symbols)).toBe('Su/Mo');
        });
        it('should add L for ascendant', () => {
            expect(formatHouseContent([0], symbols, true)).toBe('L/Su');
        });
        it('should handle empty house', () => {
            expect(formatHouseContent([], symbols)).toBe('');
        });
    });

    describe('formatDateTime', () => {
        it('should format date and time', () => {
            const result = formatDateTime(
                { year: 1996, month: 12, day: 7 },
                { hour: 10, minute: 34, second: 0 }
            );
            expect(result).toBe('1996-12-07 10:34:00');
        });
    });
});
