/**
 * Geolocation utilities
 * Browser Geolocation API wrapper and timezone helpers
 */

import type { Place } from '../types';

// ============================================================================
// BROWSER GEOLOCATION
// ============================================================================

/**
 * Get current location from browser Geolocation API
 * @returns Promise with coordinates or error
 */
export async function getCurrentPosition(): Promise<{
  latitude: number;
  longitude: number;
  accuracy: number;
}> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
      },
      (error) => {
        let message: string;
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = 'Location permission denied';
            break;
          case error.POSITION_UNAVAILABLE:
            message = 'Location information unavailable';
            break;
          case error.TIMEOUT:
            message = 'Location request timed out';
            break;
          default:
            message = 'Unknown geolocation error';
        }
        reject(new Error(message));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  });
}

// ============================================================================
// TIMEZONE UTILITIES
// ============================================================================

/**
 * Get timezone offset in hours for a given location
 * Uses Intl API to determine timezone
 * @param latitude - Latitude
 * @param longitude - Longitude
 * @param date - Date for which to get timezone (accounts for DST)
 * @returns Timezone offset in hours
 */
export function getTimezoneOffset(latitude: number, longitude: number, date: Date = new Date()): number {
  // For browser, we use the local timezone offset as fallback
  // In production, you would use a timezone database or API
  const offsetMinutes = -date.getTimezoneOffset();
  return offsetMinutes / 60;
}

/**
 * Get timezone name for display
 * @returns Timezone name like "Asia/Kolkata"
 */
export function getLocalTimezoneName(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Convert timezone offset hours to formatted string
 * @param offset - Offset in hours
 * @returns Formatted string like "+5:30" or "-8:00"
 */
export function formatTimezoneOffset(offset: number): string {
  const sign = offset >= 0 ? '+' : '-';
  const absOffset = Math.abs(offset);
  const hours = Math.floor(absOffset);
  const minutes = Math.round((absOffset - hours) * 60);
  
  return `${sign}${hours}:${minutes.toString().padStart(2, '0')}`;
}

// ============================================================================
// PLACE UTILITIES
// ============================================================================

/**
 * Create a Place object
 * @param name - Place name
 * @param latitude - Latitude in degrees
 * @param longitude - Longitude in degrees
 * @param timezone - Timezone offset in hours
 * @returns Place object
 */
export function createPlace(
  name: string,
  latitude: number,
  longitude: number,
  timezone: number
): Place {
  return { name, latitude, longitude, timezone };
}

/**
 * Validate latitude value
 * @param latitude - Latitude to validate
 * @returns True if valid (-90 to +90)
 */
export function isValidLatitude(latitude: number): boolean {
  return latitude >= -90 && latitude <= 90;
}

/**
 * Validate longitude value
 * @param longitude - Longitude to validate
 * @returns True if valid (-180 to +180)
 */
export function isValidLongitude(longitude: number): boolean {
  return longitude >= -180 && longitude <= 180;
}

/**
 * Format place as string
 * @param place - Place object
 * @returns Formatted string
 */
export function formatPlace(place: Place): string {
  const latDir = place.latitude >= 0 ? 'N' : 'S';
  const longDir = place.longitude >= 0 ? 'E' : 'W';
  const lat = Math.abs(place.latitude).toFixed(4);
  const long = Math.abs(place.longitude).toFixed(4);
  const tz = formatTimezoneOffset(place.timezone);
  
  return `${place.name} (${lat}°${latDir}, ${long}°${longDir}, UTC${tz})`;
}

// ============================================================================
// DISTANCE CALCULATIONS
// ============================================================================

/**
 * Calculate distance between two coordinates using Haversine formula
 * @param lat1 - Latitude of first point
 * @param lon1 - Longitude of first point
 * @param lat2 - Latitude of second point
 * @param lon2 - Longitude of second point
 * @returns Distance in kilometers
 */
export function haversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in kilometers
  
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

// ============================================================================
// COMMON PLACES (for quick reference)
// ============================================================================

export const COMMON_PLACES: Record<string, Place> = {
  // India
  DELHI: { name: 'Delhi', latitude: 28.6139, longitude: 77.2090, timezone: 5.5 },
  MUMBAI: { name: 'Mumbai', latitude: 19.0760, longitude: 72.8777, timezone: 5.5 },
  BANGALORE: { name: 'Bangalore', latitude: 12.9716, longitude: 77.5946, timezone: 5.5 },
  CHENNAI: { name: 'Chennai', latitude: 13.0827, longitude: 80.2707, timezone: 5.5 },
  KOLKATA: { name: 'Kolkata', latitude: 22.5726, longitude: 88.3639, timezone: 5.5 },
  HYDERABAD: { name: 'Hyderabad', latitude: 17.3850, longitude: 78.4867, timezone: 5.5 },
  UJJAIN: { name: 'Ujjain', latitude: 23.1765, longitude: 75.7885, timezone: 5.5 },
  
  // International
  NEW_YORK: { name: 'New York', latitude: 40.7128, longitude: -74.0060, timezone: -5 },
  LOS_ANGELES: { name: 'Los Angeles', latitude: 34.0522, longitude: -118.2437, timezone: -8 },
  LONDON: { name: 'London', latitude: 51.5074, longitude: -0.1278, timezone: 0 },
  SYDNEY: { name: 'Sydney', latitude: -33.8688, longitude: 151.2093, timezone: 11 },
  SINGAPORE: { name: 'Singapore', latitude: 1.3521, longitude: 103.8198, timezone: 8 }
};
