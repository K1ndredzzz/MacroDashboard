import React, { useEffect, useState } from 'react';
import { useDateRange } from '../hooks/useDateRange';

interface CorrelationRow {
  indicator: string;
  correlations: Record<string, number | null>;
}

interface StrongCorrelation {
  indicator1: string;
  indicator2: string;
  correlation: number;
}

interface CorrelationData {
  matrix: CorrelationRow[];
  strong_correlations: StrongCorrelation[];
  start_date: string;
  end_date: string;
  window_days: number;
  observation_count: number;
}

const DEFAULT_INDICATORS = ['US10Y', 'US2Y', 'EURUSD', 'WTI', 'USDJPY'];

export const CorrelationHeatmap: React.FC = () => {
  const [data, setData] = useState<CorrelationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [windowDays, setWindowDays] = useState(90);
  const { formattedRange } = useDateRange();

  useEffect(() => {
    const fetchCorrelation = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          indicator_codes: DEFAULT_INDICATORS.join(','),
          window_days: windowDays.toString()
        });

        if (formattedRange.startDateStr) {
          params.append('start_date', formattedRange.startDateStr);
        }
        if (formattedRange.endDateStr) {
          params.append('end_date', formattedRange.endDateStr);
        }

        const response = await fetch(`/api/v1/analytics/correlation?${params}`);
        if (!response.ok) {
          throw new Error('Failed to fetch correlation data');
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchCorrelation();
  }, [formattedRange.startDateStr, formattedRange.endDateStr, windowDays]);

  if (loading) {
    return <div className="correlation-heatmap loading">加载中...</div>;
  }

  if (error) {
    return <div className="correlation-heatmap error">加载失败: {error}</div>;
  }

  if (!data) {
    return null;
  }

  const getColorForCorrelation = (value: number | null): string => {
    if (value === null) return '#f3f4f6';
    if (value === 1) return '#1f2937';

    const absValue = Math.abs(value);
    if (value > 0) {
      // Positive correlation: white to blue
      const intensity = Math.floor(absValue * 255);
      return `rgb(${255 - intensity}, ${255 - intensity}, 255)`;
    } else {
      // Negative correlation: white to red
      const intensity = Math.floor(absValue * 255);
      return `rgb(255, ${255 - intensity}, ${255 - intensity})`;
    }
  };

  const indicators = data.matrix.map(row => row.indicator);

  return (
    <div className="correlation-heatmap">
      <div className="heatmap-header">
        <h3>相关性分析</h3>
        <div className="heatmap-controls">
          <label>
            窗口期:
            <select value={windowDays} onChange={(e) => setWindowDays(Number(e.target.value))}>
              <option value={30}>30天</option>
              <option value={60}>60天</option>
              <option value={90}>90天</option>
              <option value={180}>180天</option>
            </select>
          </label>
          <span className="observation-count">
            样本数: {data.observation_count}
          </span>
        </div>
      </div>

      <div className="heatmap-container">
        <table className="heatmap-table">
          <thead>
            <tr>
              <th></th>
              {indicators.map(indicator => (
                <th key={indicator}>{indicator}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.matrix.map((row) => (
              <tr key={row.indicator}>
                <th>{row.indicator}</th>
                {indicators.map((indicator) => {
                  const value = row.correlations[indicator];
                  return (
                    <td
                      key={indicator}
                      style={{ backgroundColor: getColorForCorrelation(value) }}
                      title={value !== null ? value.toFixed(3) : 'N/A'}
                    >
                      {value !== null ? value.toFixed(2) : '-'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.strong_correlations.length > 0 && (
        <div className="strong-correlations">
          <h4>强相关性 (|r| &gt; 0.7)</h4>
          <ul>
            {data.strong_correlations.map((corr, idx) => (
              <li key={idx}>
                <span className="indicator-pair">
                  {corr.indicator1} ↔ {corr.indicator2}
                </span>
                <span className={`correlation-value ${corr.correlation > 0 ? 'positive' : 'negative'}`}>
                  {corr.correlation.toFixed(3)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <style>{`
        .correlation-heatmap {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          margin-bottom: 1.5rem;
        }

        .heatmap-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .heatmap-header h3 {
          margin: 0;
          font-size: 1.25rem;
          color: #1f2937;
        }

        .heatmap-controls {
          display: flex;
          gap: 1rem;
          align-items: center;
          font-size: 0.875rem;
        }

        .heatmap-controls label {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .heatmap-controls select {
          padding: 0.25rem 0.5rem;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .observation-count {
          color: #6b7280;
        }

        .heatmap-container {
          overflow-x: auto;
          margin-bottom: 1.5rem;
        }

        .heatmap-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .heatmap-table th {
          padding: 0.75rem;
          text-align: center;
          font-weight: 600;
          color: #1f2937;
          background: #f9fafb;
        }

        .heatmap-table td {
          padding: 0.75rem;
          text-align: center;
          border: 1px solid #e5e7eb;
          cursor: pointer;
          transition: transform 0.2s;
        }

        .heatmap-table td:hover {
          transform: scale(1.1);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
          z-index: 10;
        }

        .strong-correlations {
          padding-top: 1rem;
          border-top: 1px solid #e5e7eb;
        }

        .strong-correlations h4 {
          margin: 0 0 0.75rem 0;
          font-size: 1rem;
          color: #1f2937;
        }

        .strong-correlations ul {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .strong-correlations li {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem;
          background: #f9fafb;
          border-radius: 4px;
        }

        .indicator-pair {
          font-weight: 500;
          color: #1f2937;
        }

        .correlation-value {
          font-weight: 600;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .correlation-value.positive {
          color: #059669;
          background: #d1fae5;
        }

        .correlation-value.negative {
          color: #dc2626;
          background: #fee2e2;
        }

        .correlation-heatmap.loading,
        .correlation-heatmap.error {
          padding: 2rem;
          text-align: center;
          color: #6b7280;
        }

        .correlation-heatmap.error {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
};
