/**
 * South Indian Chart Component
 * Renders a traditional South Indian style horoscope chart
 */

import { useMemo } from 'react';
import './SouthIndianChart.css';

// Planet symbols
const PLANET_SYMBOLS: Record<number, string> = {
  0: 'Su',
  1: 'Mo',
  2: 'Ma',
  3: 'Me',
  4: 'Ju',
  5: 'Ve',
  6: 'Sa',
  7: 'Ra',
  8: 'Ke'
};

// Rasi names
const RASI_NAMES = [
  'Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
  'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis'
];

interface PlanetData {
  planet: number;
  rasi: number;
  longitude: number;
  isRetrograde?: boolean;
}

interface SouthIndianChartProps {
  planets: PlanetData[];
  ascendantRasi: number;
  title?: string;
  showDegrees?: boolean;
}

/**
 * South Indian Chart layout (fixed positions):
 * 
 *   [Pis] [Ari] [Tau] [Gem]
 *   [Aqu]             [Can]
 *   [Cap]             [Leo]
 *   [Sag] [Sco] [Lib] [Vir]
 * 
 * Rasi positions are fixed, planets move through them
 */
const HOUSE_POSITIONS: Record<number, { row: number; col: number }> = {
  0: { row: 0, col: 1 },   // Aries
  1: { row: 0, col: 2 },   // Taurus
  2: { row: 0, col: 3 },   // Gemini
  3: { row: 1, col: 3 },   // Cancer
  4: { row: 2, col: 3 },   // Leo
  5: { row: 3, col: 3 },   // Virgo
  6: { row: 3, col: 2 },   // Libra
  7: { row: 3, col: 1 },   // Scorpio
  8: { row: 3, col: 0 },   // Sagittarius
  9: { row: 2, col: 0 },   // Capricorn
  10: { row: 1, col: 0 },  // Aquarius
  11: { row: 0, col: 0 }   // Pisces
};

export function SouthIndianChart({ 
  planets, 
  ascendantRasi, 
  title = 'Rasi Chart',
  showDegrees = false 
}: SouthIndianChartProps) {
  // Group planets by rasi
  const planetsByRasi = useMemo(() => {
    const grouped: Record<number, PlanetData[]> = {};
    for (let i = 0; i < 12; i++) {
      grouped[i] = [];
    }
    
    for (const planet of planets) {
      if (grouped[planet.rasi]) {
        grouped[planet.rasi].push(planet);
      }
    }
    
    return grouped;
  }, [planets]);

  // Create grid cells
  const gridCells = useMemo(() => {
    const cells: Array<{
      rasi: number;
      name: string;
      isAscendant: boolean;
      planets: PlanetData[];
      row: number;
      col: number;
    } | null> = [];

    // Create 4x4 grid
    for (let row = 0; row < 4; row++) {
      for (let col = 0; col < 4; col++) {
        // Find which rasi is at this position
        const rasiEntry = Object.entries(HOUSE_POSITIONS).find(
          ([_, pos]) => pos.row === row && pos.col === col
        );

        if (rasiEntry) {
          const rasiNum = parseInt(rasiEntry[0]);
          cells.push({
            rasi: rasiNum,
            name: RASI_NAMES[rasiNum] ?? '',
            isAscendant: rasiNum === ascendantRasi,
            planets: planetsByRasi[rasiNum] ?? [],
            row,
            col
          });
        } else {
          // Center cells (empty in South Indian chart)
          cells.push(null);
        }
      }
    }

    return cells;
  }, [ascendantRasi, planetsByRasi]);

  return (
    <div className="south-indian-chart">
      <div className="chart-title">{title}</div>
      <div className="chart-grid">
        {gridCells.map((cell, index) => (
          <div
            key={index}
            className={`chart-cell ${cell ? '' : 'chart-cell-empty'} ${cell?.isAscendant ? 'chart-cell-ascendant' : ''}`}
          >
            {cell && (
              <>
                <div className="cell-rasi">{cell.name}</div>
                {cell.isAscendant && <div className="cell-asc">Asc</div>}
                <div className="cell-planets">
                  {cell.planets.map((p, i) => (
                    <span
                      key={i}
                      className={`planet planet-${p.planet} ${p.isRetrograde ? 'retrograde' : ''}`}
                      title={showDegrees ? `${p.longitude.toFixed(2)}°` : undefined}
                    >
                      {PLANET_SYMBOLS[p.planet] ?? '?'}
                      {p.isRetrograde && <sup>R</sup>}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default SouthIndianChart;
