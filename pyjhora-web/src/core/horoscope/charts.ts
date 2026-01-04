/**
 * Divisional Chart (Varga) Calculations
 * Dispatcher for calculating various divisional charts.
 */

import {
    calculateCyclicVarga,
    calculateD10_Dasamsa_Parashara,
    calculateD12_Dwadasamsa_Parashara,
    calculateD16_Shodasamsa_Parashara,
    calculateD1_Rasi,
    calculateD20_Vimsamsa_Parashara,
    calculateD24_Chaturvimsamsa_Parashara,
    calculateD27_Bhamsa_Parashara,
    calculateD2_Hora_Parashara,
    calculateD30_Trimsamsa_Parashara,
    calculateD3_Drekkana_Parashara,
    calculateD40_Khavedamsa_Parashara,
    calculateD45_Akshavedamsa_Parashara,
    calculateD4_Chaturthamsa_Parashara,
    calculateD60_Shashtiamsa_Parashara,
    calculateD7_Saptamsa_Parashara,
    calculateD9_Navamsa_Parashara
} from './varga-utils';

export interface PlanetPosition {
  planet: number;
  rasi: number;
  longitude: number; // In degrees (0-30 within sign)
}

export type VargaMethod = 'PARASHARA' | 'CYCLIC' | 'JAGANNATHA' | 'PARIVRITTI_EVEN_REVERSE'; // Add more as needed

/**
 * Calculate the longitude within the varga sign
 * Formula: (Total Longitude * D) % 30
 * @param totalLongitude - Absolute longitude (0-360)
 * @param divisionFactor - D-Chart factor (e.g. 9 for Navamsa)
 * @returns Longitude in degrees (0-30)
 */
export const getLongitudeInVarga = (totalLongitude: number, divisionFactor: number): number => {
  return (totalLongitude * divisionFactor) % 30;
};

/**
 * Get planetary positions for a specific divisional chart
 * @param d1Positions - Positions in Rasi chart (D1)
 * @param divisionFactor - Chart to calculate (e.g. 9)
 * @param method - Calculation method (default PARASHARA)
 * @returns Array of transformed positions
 */
export const getDivisionalChart = (
  d1Positions: PlanetPosition[],
  divisionFactor: number,
  method: VargaMethod = 'PARASHARA'
): PlanetPosition[] => {
  return d1Positions.map(pos => {
    // Reconstruct absolute longitude from D1 rasi and longitude
    const totalLongitude = pos.rasi * 30 + pos.longitude;
    
    let vargaSign = 0;
    
    // Dispatch to specific calculator based on factor and method
    // Currently implementing standard PARASHARA methods
    switch (divisionFactor) {
      case 1:
        vargaSign = calculateD1_Rasi(totalLongitude);
        break;
      case 2:
        vargaSign = calculateD2_Hora_Parashara(totalLongitude); 
        // Note: Other Hora methods like cyclic/parivritti exist but Parashara is standard
        break;
      case 3:
        vargaSign = calculateD3_Drekkana_Parashara(totalLongitude);
        break;
      case 4:
        vargaSign = calculateD4_Chaturthamsa_Parashara(totalLongitude);
        break;
      case 7:
        vargaSign = calculateD7_Saptamsa_Parashara(totalLongitude);
        break;
      case 9:
        vargaSign = calculateD9_Navamsa_Parashara(totalLongitude);
        break;
      case 10:
        vargaSign = calculateD10_Dasamsa_Parashara(totalLongitude);
        break;
      case 12:
        vargaSign = calculateD12_Dwadasamsa_Parashara(totalLongitude);
        break;
      case 16:
        vargaSign = calculateD16_Shodasamsa_Parashara(totalLongitude);
        break;
      case 20:
        vargaSign = calculateD20_Vimsamsa_Parashara(totalLongitude);
        break;
      case 24:
        vargaSign = calculateD24_Chaturvimsamsa_Parashara(totalLongitude);
        break;
      case 27:
        vargaSign = calculateD27_Bhamsa_Parashara(totalLongitude);
        break;
      case 30:
        vargaSign = calculateD30_Trimsamsa_Parashara(totalLongitude);
        break;
      case 40:
        vargaSign = calculateD40_Khavedamsa_Parashara(totalLongitude);
        break;
      case 45:
        vargaSign = calculateD45_Akshavedamsa_Parashara(totalLongitude);
        break;
      case 60:
        vargaSign = calculateD60_Shashtiamsa_Parashara(totalLongitude);
        break;
      default:
        // Default to Cyclic if no specific logic exists or for custom D-charts
        vargaSign = calculateCyclicVarga(totalLongitude, divisionFactor);
        break;
    }

    // Calculate new longitude in the varga
    const vargaLong = getLongitudeInVarga(totalLongitude, divisionFactor);
    
    return {
      planet: pos.planet,
      rasi: vargaSign,
      longitude: vargaLong
    };
  });
};

/**
 * Get positions for Ascendant and Planets for a specific chart
 * Assumes d1Positions includes Ascendant (usually as special ID or separate)
 * Standardizing input to include everything.
 */
export const calculateDivisionalChart = (
  jd: number, // Not used directly if we have D1 positions, but kept for signature compatibility with future
  d1Positions: PlanetPosition[],
  divisionFactor: number
): PlanetPosition[] => {
  return getDivisionalChart(d1Positions, divisionFactor);
};
