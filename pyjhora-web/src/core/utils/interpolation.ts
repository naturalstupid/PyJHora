/**
 * Interpolation utilities for panchanga calculations
 * Ported from Python utils.py (inverse_lagrange, unwrap_angles, extend_angle_range)
 */

/**
 * Inverse Lagrange interpolation.
 * Given paired data points (x, y), find the value x = xa when y = ya.
 * Constructs a Lagrange polynomial through the points (y_i, x_i) and evaluates at y = ya.
 *
 * Used extensively in panchanga calculations: tithi end time, nakshatra end time,
 * yogam end time, karana end time, new/full moon, planet entry dates, etc.
 *
 * Python: utils.inverse_lagrange(x, y, ya)
 *
 * @param x - Array of x values (e.g., Julian day offsets)
 * @param y - Array of y values (e.g., longitudes/phases at those times)
 * @param ya - Target y value to find x for
 * @returns Interpolated x value
 */
export function inverseLagrange(x: number[], y: number[], ya: number): number {
  let total = 0;
  for (let i = 0; i < x.length; i++) {
    let numer = 1;
    let denom = 1;
    for (let j = 0; j < x.length; j++) {
      if (j !== i) {
        numer *= (ya - y[j]);
        denom *= (y[i] - y[j]);
      }
    }
    total += numer * x[i] / denom;
  }
  return total;
}

/**
 * Unwrap angles for circular continuity.
 * Ensures angles are monotonically increasing by adding 360 at wrap-around points.
 * For example: [350, 355, 2, 8, 15] → [350, 355, 362, 368, 375]
 *
 * Critical for nakshatra calculations near the Ashwini/Revati boundary (0°/360°).
 *
 * Python: utils.unwrap_angles(angles)
 *
 * @param angles - Array of angles in degrees
 * @returns Unwrapped angles (monotonically increasing)
 */
export function unwrapAngles(angles: number[]): number[] {
  if (angles.length === 0) return [];
  const result = [angles[0]];
  for (let i = 1; i < angles.length; i++) {
    let angle = angles[i];
    if (angle < result[i - 1]) {
      angle += 360;
    }
    result.push(angle);
  }
  return result;
}

/**
 * Extend angle range for interpolation.
 * Adds 360 to all angles until the range covers at least `target` degrees.
 *
 * Python: utils.extend_angle_range(angles, target)
 *
 * @param angles - Array of angles in degrees
 * @param target - Minimum range to cover
 * @returns Extended array of angles
 */
export function extendAngleRange(angles: number[], target: number): number[] {
  let extended = [...angles];
  while (Math.max(...extended) - Math.min(...extended) < target) {
    extended = [...extended, ...angles.map(a => a + 360)];
  }
  return extended;
}
