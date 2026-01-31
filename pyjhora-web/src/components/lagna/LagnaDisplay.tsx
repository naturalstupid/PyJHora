/**
 * Lagna (Ascendant) Display Component
 * Shows ascendant sign, longitude, nakshatra, and characteristics
 */

import './LagnaDisplay.css';
import {
  RASI_NAMES_EN,
  RASI_NAMES_SA,
  NAKSHATRA_NAMES_EN,
  NAKSHATRA_SPAN,
  PLANET_NAMES_EN,
  SIGN_LORDS,
  FIRE_SIGNS,
  EARTH_SIGNS,
  AIR_SIGNS,
  WATER_SIGNS,
  MOVABLE_SIGNS,
  FIXED_SIGNS,
  DUAL_SIGNS
} from '../../core/constants';

interface LagnaDisplayProps {
  ascendantRasi: number;
  ascendantLongitude: number; // Full longitude 0-360
}

function formatDegrees(longitude: number): string {
  const totalDegrees = longitude % 30;
  const degrees = Math.floor(totalDegrees);
  const minutes = Math.floor((totalDegrees - degrees) * 60);
  return `${degrees}° ${minutes}'`;
}

function getNakshatra(longitude: number): { name: string; pada: number } {
  const nakshatraIndex = Math.floor(longitude / NAKSHATRA_SPAN);
  const positionInNakshatra = longitude % NAKSHATRA_SPAN;
  const pada = Math.floor(positionInNakshatra / (NAKSHATRA_SPAN / 4)) + 1;
  return {
    name: NAKSHATRA_NAMES_EN[nakshatraIndex] || 'Unknown',
    pada
  };
}

function getElement(rasi: number): string {
  if (FIRE_SIGNS.includes(rasi)) return 'Fire';
  if (EARTH_SIGNS.includes(rasi)) return 'Earth';
  if (AIR_SIGNS.includes(rasi)) return 'Air';
  if (WATER_SIGNS.includes(rasi)) return 'Water';
  return 'Unknown';
}

function getQuality(rasi: number): string {
  if (MOVABLE_SIGNS.includes(rasi)) return 'Movable';
  if (FIXED_SIGNS.includes(rasi)) return 'Fixed';
  if (DUAL_SIGNS.includes(rasi)) return 'Dual';
  return 'Unknown';
}

function getElementClass(rasi: number): string {
  if (FIRE_SIGNS.includes(rasi)) return 'element-fire';
  if (EARTH_SIGNS.includes(rasi)) return 'element-earth';
  if (AIR_SIGNS.includes(rasi)) return 'element-air';
  if (WATER_SIGNS.includes(rasi)) return 'element-water';
  return '';
}

export function LagnaDisplay({ ascendantRasi, ascendantLongitude }: LagnaDisplayProps) {
  const rasiNameEn = RASI_NAMES_EN[ascendantRasi] || 'Unknown';
  const rasiNameSa = RASI_NAMES_SA[ascendantRasi] || '';
  const nakshatra = getNakshatra(ascendantLongitude);
  const lordIndex = SIGN_LORDS[ascendantRasi] ?? 0;
  const lordName = PLANET_NAMES_EN[lordIndex] ?? 'Unknown';
  const element = getElement(ascendantRasi);
  const quality = getQuality(ascendantRasi);
  const elementClass = getElementClass(ascendantRasi);

  return (
    <div className="lagna-display card">
      <h3 className="lagna-title">Lagna (Ascendant)</h3>

      <div className="lagna-main">
        <span className={`lagna-rasi ${elementClass}`}>{rasiNameEn}</span>
        <span className="lagna-rasi-sa">{rasiNameSa}</span>
        <span className="lagna-degrees">{formatDegrees(ascendantLongitude)}</span>
      </div>

      <div className="lagna-grid">
        <div className="lagna-item">
          <span className="lagna-label">Nakshatra</span>
          <span className="lagna-value">
            {nakshatra.name}
            <span className="lagna-detail">(Pada {nakshatra.pada})</span>
          </span>
        </div>

        <div className="lagna-item">
          <span className="lagna-label">Lord</span>
          <span className="lagna-value">{lordName}</span>
        </div>

        <div className="lagna-item">
          <span className="lagna-label">Element</span>
          <span className={`lagna-value ${elementClass}`}>{element}</span>
        </div>

        <div className="lagna-item">
          <span className="lagna-label">Quality</span>
          <span className="lagna-value">{quality}</span>
        </div>
      </div>
    </div>
  );
}

export default LagnaDisplay;
