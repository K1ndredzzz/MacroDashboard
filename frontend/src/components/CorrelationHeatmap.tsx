import React, { useEffect, useState } from 'react';
import { useDateRange } from '../hooks/useDateRange';
import { useAnalytics } from '../contexts/AnalyticsContext';

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

export const CorrelationHeatmap: React.FC = () => {
  const [data, setData] = useState<CorrelationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const { formattedRange } = useDateRange();
  const { correlationIndicators, correlationWindowDays, setCorrelationWindowDays } = useAnalytics();

  useEffect(() => {
    const fetchCorrelation = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          indicator_codes: correlationIndicators.join(','),
          window_days: correlationWindowDays.toString()
        });

        if (formattedRange.startDateStr) {
          params.append('start_date', formattedRange.startDateStr);
        }
        if (formattedRange.endDateStr) {
          params.append('end_date', formattedRange.endDateStr);
        }

        const response = await fetch(`/api/v1/analytics/correlation?${params}`);
        if (!response.ok) {
          let detail = 'Failed to fetch correlation data';
          try {
            const payload = await response.json();
            if (payload?.detail) {
              detail = String(payload.detail);
            } else {
              detail = `HTTP ${response.status}`;
            }
          } catch {
            detail = `HTTP ${response.status}`;
          }
          throw new Error(detail);
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
  }, [formattedRange.startDateStr, formattedRange.endDateStr, correlationIndicators, correlationWindowDays, retryCount]);

  const handleRetry = () => {
    setRetryCount((prev) => prev + 1);
  };

  if (loading && !data) {
    return (
      <div className="correlation-heatmap card">
        <div className="heatmap-header">
          <h3>相关性分析</h3>
          <div className="heatmap-controls">
            <span className="observation-count">加载中...</span>
          </div>
        </div>
        <div className="skeleton-grid" aria-hidden="true">
          {Array.from({ length: 25 }).map((_, idx) => (
            <div key={idx} className="skeleton-cell" />
          ))}
        </div>
        <style>{`
          .correlation-heatmap {
            display: flex;
            flex-direction: column;
            height: 100%;
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
            color: var(--text-primary);
          }

          .skeleton-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.5rem;
            margin-top: 0.5rem;
          }

          .skeleton-cell {
            height: 34px;
            border-radius: 6px;
            background: linear-gradient(90deg, rgba(148, 163, 184, 0.12) 25%, rgba(148, 163, 184, 0.24) 50%, rgba(148, 163, 184, 0.12) 75%);
            background-size: 200% 100%;
            animation: heatmap-shimmer 1.4s infinite;
          }

          @keyframes heatmap-shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
          }
        `}</style>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="correlation-heatmap card">
        <div className="heatmap-header">
          <h3>相关性分析</h3>
          <div className="heatmap-controls">
            <button className="retry-btn" onClick={handleRetry}>重试</button>
          </div>
        </div>

        <div className="fallback-panel">
          <p className="fallback-title">相关性数据暂时不可用</p>
          <p className="fallback-detail">{error}</p>
          <p className="fallback-hint">请稍后重试，或调整窗口期后重新加载。</p>
        </div>

        <style>{`
          .correlation-heatmap {
            display: flex;
            flex-direction: column;
            height: 100%;
          }

          .heatmap-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
          }

          .heatmap-header h3 {
            margin: 0;
            font-size: 1.25rem;
            color: var(--text-primary);
          }

          .retry-btn {
            border: 1px solid var(--border-color);
            background: var(--bg-main);
            color: var(--text-primary);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
          }

          .retry-btn:hover {
            border-color: var(--accent-blue);
          }

          .fallback-panel {
            border: 1px solid rgba(245, 158, 11, 0.35);
            background: rgba(245, 158, 11, 0.08);
            border-radius: 10px;
            padding: 1rem;
          }

          .fallback-title {
            margin: 0 0 0.5rem 0;
            color: var(--text-primary);
            font-weight: 600;
          }

          .fallback-detail {
            margin: 0 0 0.4rem 0;
            color: var(--text-secondary);
            word-break: break-word;
          }

          .fallback-hint {
            margin: 0;
            color: var(--text-secondary);
            opacity: 0.85;
            font-size: 0.85rem;
          }
        `}</style>
      </div>
    );
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
    <div className="correlation-heatmap card">
      <div className="heatmap-header">
        <h3>相关性分析</h3>
        <div className="heatmap-controls">
          <label>
            窗口期:
            <select value={correlationWindowDays} onChange={(e) => setCorrelationWindowDays(Number(e.target.value))}>
              <option value={30}>30天</option>
              <option value={60}>60天</option>
              <option value={90}>90天</option>
              <option value={180}>180天</option>
            </select>
          </label>
          <span className="observation-count">
            样本数: {data.observation_count}
          </span>
          {error && <button className="retry-inline-btn" onClick={handleRetry}>重试</button>}
        </div>
      </div>

      {error && (
        <div className="heatmap-warning">
          最新请求失败，当前展示上次成功结果：{error}
        </div>
      )}

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
          display: flex;
          flex-direction: column;
          height: 100%;
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
          color: var(--text-primary);
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
          color: var(--text-secondary);
        }

        .heatmap-controls select {
          padding: 0.25rem 0.5rem;
          border: 1px solid var(--border-color);
          border-radius: 4px;
          font-size: 0.875rem;
          background: var(--bg-main);
          color: var(--text-primary);
        }

        .observation-count {
          color: var(--text-secondary);
        }

        .retry-inline-btn {
          border: 1px solid var(--border-color);
          background: var(--bg-main);
          color: var(--text-primary);
          padding: 0.25rem 0.6rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.8rem;
        }

        .retry-inline-btn:hover {
          border-color: var(--accent-blue);
        }

        .heatmap-warning {
          margin-bottom: 1rem;
          padding: 0.6rem 0.75rem;
          border: 1px solid rgba(245, 158, 11, 0.35);
          background: rgba(245, 158, 11, 0.08);
          border-radius: 6px;
          color: var(--text-primary);
          font-size: 0.85rem;
          word-break: break-word;
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
          color: var(--text-primary);
          background: var(--bg-main);
          border: 1px solid var(--border-color);
        }

        .heatmap-table td {
          padding: 0.75rem;
          text-align: center;
          border: 1px solid var(--border-color);
          cursor: pointer;
          transition: transform 0.2s;
          color: white;
          text-shadow: 0 1px 2px rgba(0,0,0,0.8);
          font-weight: 600;
        }

        .heatmap-table td:hover {
          transform: scale(1.1);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
          z-index: 10;
        }

        .strong-correlations {
          padding-top: 1rem;
          border-top: 1px solid var(--border-color);
        }

        .strong-correlations h4 {
          margin: 0 0 0.75rem 0;
          font-size: 1rem;
          color: var(--text-primary);
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
          background: var(--bg-main);
          border-radius: 4px;
          border: 1px solid var(--border-color);
        }

        .indicator-pair {
          font-weight: 500;
          color: var(--text-primary);
        }

        .correlation-value {
          font-weight: 600;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
        }

        .correlation-value.positive {
          color: var(--accent-green);
          background: rgba(0, 200, 5, 0.1);
        }

        .correlation-value.negative {
          color: var(--accent-red);
          background: rgba(255, 59, 48, 0.1);
        }

        .correlation-heatmap.loading,
        .correlation-heatmap.error {
          padding: 2rem;
          text-align: center;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
};
