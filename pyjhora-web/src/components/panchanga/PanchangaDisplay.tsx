/**
 * Panchanga Display Component
 * Shows tithi, nakshatra, yoga, karana, vara
 */

import './PanchangaDisplay.css';

interface PanchangaData {
  tithi: {
    number: number;
    name: string;
    paksha: 'shukla' | 'krishna';
  };
  nakshatra: {
    number: number;
    name: string;
    pada: number;
  };
  yoga: {
    number: number;
    name: string;
  };
  karana: {
    number: number;
    name: string;
  };
  vara: {
    number: number;
    name: string;
  };
}

interface PanchangaDisplayProps {
  panchanga: PanchangaData;
}

export function PanchangaDisplay({ panchanga }: PanchangaDisplayProps) {
  return (
    <div className="panchanga-display card">
      <h3 className="panchanga-title">Panchanga</h3>
      
      <div className="panchanga-grid">
        <div className="panchanga-item">
          <span className="panchanga-label">Tithi</span>
          <span className="panchanga-value">
            {panchanga.tithi.name}
            <span className="panchanga-detail">
              ({panchanga.tithi.paksha === 'shukla' ? 'Bright' : 'Dark'} {panchanga.tithi.number})
            </span>
          </span>
        </div>
        
        <div className="panchanga-item">
          <span className="panchanga-label">Nakshatra</span>
          <span className="panchanga-value">
            {panchanga.nakshatra.name}
            <span className="panchanga-detail">
              (Pada {panchanga.nakshatra.pada})
            </span>
          </span>
        </div>
        
        <div className="panchanga-item">
          <span className="panchanga-label">Yoga</span>
          <span className="panchanga-value">{panchanga.yoga.name}</span>
        </div>
        
        <div className="panchanga-item">
          <span className="panchanga-label">Karana</span>
          <span className="panchanga-value">{panchanga.karana.name}</span>
        </div>
        
        <div className="panchanga-item">
          <span className="panchanga-label">Vara</span>
          <span className="panchanga-value">{panchanga.vara.name}</span>
        </div>
      </div>
    </div>
  );
}

export default PanchangaDisplay;
