
import React from 'react';
import { DIVISIONAL_CHART_FACTORS, VARGA_NAMES } from '../../core/constants';

interface DivisionalChartSelectorProps {
  selectedVarga: number;
  onSelect: (varga: number) => void;
}

export const DivisionalChartSelector: React.FC<DivisionalChartSelectorProps> = ({
  selectedVarga,
  onSelect
}) => {
  return (
    <div className="varga-selector mb-sm flex gap-2 items-center">
      <label htmlFor="varga-select" className="text-sm font-medium">Chart:</label>
      <select
        id="varga-select"
        className="form-select text-sm p-1 border rounded"
        value={selectedVarga}
        onChange={(e) => onSelect(Number(e.target.value))}
      >
        {DIVISIONAL_CHART_FACTORS.map(factor => (
          <option key={factor} value={factor}>
            {VARGA_NAMES[factor] || `D-${factor}`}
          </option>
        ))}
      </select>
    </div>
  );
};
