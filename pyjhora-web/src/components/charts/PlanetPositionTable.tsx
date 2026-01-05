/**
 * Planet Position Table Component
 * Displays planet positions in Rasi and selected Varga charts
 */

import React from 'react';
import { PLANET_NAMES_EN, RASI_NAMES_EN, VARGA_NAMES } from '../../core/constants';
import { getDivisionalChart, PlanetPosition } from '../../core/horoscope/charts';
import './PlanetPositionTable.css';

interface PlanetPositionTableProps {
  /** D1 (Rasi) positions */
  d1Positions: PlanetPosition[];
  /** Vargas to display (e.g., [1, 9, 10] for D1, D9, D10) */
  vargas?: number[];
  /** Show longitude degrees */
  showDegrees?: boolean;
}

const DEFAULT_VARGAS = [1, 9, 10, 12]; // D1, D9, D10, D12

export const PlanetPositionTable: React.FC<PlanetPositionTableProps> = ({
  d1Positions,
  vargas = DEFAULT_VARGAS,
  showDegrees = true
}) => {
  // Calculate positions for each Varga
  const vargaPositions: Record<number, PlanetPosition[]> = {};
  
  vargas.forEach(v => {
    if (v === 1) {
      vargaPositions[v] = d1Positions;
    } else {
      vargaPositions[v] = getDivisionalChart(d1Positions, v);
    }
  });

  // Get planet IDs (0-8: Sun to Ketu)
  const planetIds = d1Positions.map(p => p.planet).filter(p => p >= 0 && p <= 8);

  const formatDegree = (longitude: number): string => {
    const deg = Math.floor(longitude % 30);
    const min = Math.floor((longitude % 1) * 60);
    return `${deg}°${min.toString().padStart(2, '0')}'`;
  };

  return (
    <div className="planet-position-table">
      <table>
        <thead>
          <tr>
            <th>Planet</th>
            {vargas.map(v => (
              <th key={v}>{VARGA_NAMES[v] || `D-${v}`}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {planetIds.map(planetId => (
            <tr key={planetId}>
              <td className="planet-name">{PLANET_NAMES_EN[planetId] || `P${planetId}`}</td>
              {vargas.map(v => {
                const pos = vargaPositions[v]?.find(p => p.planet === planetId);
                if (!pos) return <td key={v}>-</td>;
                
                return (
                  <td key={v}>
                    <span className="rasi-name">{RASI_NAMES_EN[pos.rasi]}</span>
                    {showDegrees && (
                      <span className="degree">{formatDegree(pos.longitude)}</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PlanetPositionTable;
