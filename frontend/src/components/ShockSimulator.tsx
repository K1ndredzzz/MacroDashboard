import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';
import { useDateRange } from '../hooks/useDateRange';
import { useAnalytics } from '../contexts/AnalyticsContext';

interface ImpactPrediction {
  indicator_code: string;
  indicator_name: string;
  correlation: number;
  predicted_change: number;
  confidence_lower: number;
  confidence_upper: number;
  impact_level: string;
}

interface SimulationResult {
  shock_type: string;
  target_indicator: string;
  shock_magnitude: number;
  impacts: ImpactPrediction[];
  correlation_window_days: number;
  observation_count: number;
}

type ShockType = 'interest_rate' | 'exchange_rate' | 'oil_price';

const SHOCK_TYPES = [
  { value: 'interest_rate' as ShockType, label: '利率冲击', unit: 'bps', min: -200, max: 200, step: 25 },
  { value: 'exchange_rate' as ShockType, label: '汇率冲击', unit: '%', min: -20, max: 20, step: 1 },
  { value: 'oil_price' as ShockType, label: '油价冲击', unit: '%', min: -50, max: 100, step: 5 }
];

const TARGET_INDICATORS: Record<ShockType, Array<{ value: string; label: string }>> = {
  interest_rate: [
    { value: 'US10Y', label: '美债10年期' },
    { value: 'US2Y', label: '美债2年期' }
  ],
  exchange_rate: [
    { value: 'EURUSD', label: '欧元/美元' },
    { value: 'USDJPY', label: '美元/日元' }
  ],
  oil_price: [
    { value: 'WTI', label: 'WTI原油' }
  ]
};

export const ShockSimulator: React.FC = () => {
  const [shockType, setShockType] = useState<ShockType>('interest_rate');
  const [shockMagnitude, setShockMagnitude] = useState<number>(50);
  const [targetIndicator, setTargetIndicator] = useState<string>('US10Y');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { formattedRange } = useDateRange();
  const { correlationIndicators, correlationWindowDays } = useAnalytics();

  const currentShockConfig = SHOCK_TYPES.find(s => s.value === shockType)!;

  const handleShockTypeChange = (newType: ShockType) => {
    setShockType(newType);
    setTargetIndicator(TARGET_INDICATORS[newType][0].value);
    const config = SHOCK_TYPES.find(s => s.value === newType)!;
    setShockMagnitude(config.step);
    setResult(null);
  };

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/simulation/shock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          shock_type: shockType,
          shock_magnitude: shockMagnitude / (shockType === 'interest_rate' ? 100 : 1), // Convert bps to percentage
          target_indicator: targetIndicator,
          affected_indicators: correlationIndicators,
          window_days: correlationWindowDays,
          start_date: formattedRange.startDateStr,
          end_date: formattedRange.endDateStr
        })
      });

      if (!response.ok) {
        throw new Error('模拟失败');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  const getImpactColor = (level: string) => {
    const colors: Record<string, string> = {
      'direct': '#3b82f6',
      'strong': '#10b981',
      'moderate': '#f59e0b',
      'weak': '#6b7280'
    };
    return colors[level] || '#6b7280';
  };

  const formatChange = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  return (
    <div className="shock-simulator card">
      <div className="simulator-header">
        <h3>情景冲击模拟器</h3>
        <p className="subtitle">模拟经济冲击对各指标的影响</p>
      </div>

      <div className="simulator-controls">
        <div className="control-group">
          <label>冲击类型</label>
          <div className="shock-type-buttons">
            {SHOCK_TYPES.map(type => (
              <button
                key={type.value}
                className={`type-button ${shockType === type.value ? 'active' : ''}`}
                onClick={() => handleShockTypeChange(type.value)}
              >
                {type.label}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group">
          <label>目标指标</label>
          <select
            value={targetIndicator}
            onChange={(e) => setTargetIndicator(e.target.value)}
            className="indicator-select"
          >
            {TARGET_INDICATORS[shockType].map(ind => (
              <option key={ind.value} value={ind.value}>{ind.label}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>
            冲击幅度: {shockMagnitude} {currentShockConfig.unit}
          </label>
          <input
            type="range"
            min={currentShockConfig.min}
            max={currentShockConfig.max}
            step={currentShockConfig.step}
            value={shockMagnitude}
            onChange={(e) => setShockMagnitude(Number(e.target.value))}
            className="magnitude-slider"
          />
          <div className="slider-labels">
            <span>{currentShockConfig.min}</span>
            <span>0</span>
            <span>{currentShockConfig.max}</span>
          </div>
        </div>

        <button
          onClick={handleSimulate}
          disabled={loading}
          className="simulate-button"
        >
          {loading ? '模拟中...' : '开始模拟'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          模拟失败: {error}
        </div>
      )}

      {result && (
        <div className="simulation-results">
          <div className="results-header">
            <h4>影响预测</h4>
            <p className="results-meta">
              基于最近 {result.correlation_window_days} 天的 {result.observation_count} 个观测数据
            </p>
          </div>

          <div className="impact-chart">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={result.impacts}
                layout="vertical"
                margin={{ top: 20, right: 30, left: 120, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                <XAxis type="number" label={{ value: '预测变化 (%)', position: 'insideBottom', offset: -10, fill: 'var(--text-secondary)' }} stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} />
                <YAxis type="category" dataKey="indicator_name" width={110} stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                  formatter={(value: number | undefined) => value !== undefined ? formatChange(value) : '-'}
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  labelFormatter={(label: any) => `指标: ${label}`}
                />
                <Legend wrapperStyle={{ color: 'var(--text-primary)' }} />
                <ReferenceLine x={0} stroke="var(--border-color)" />
                <Bar dataKey="predicted_change" name="预测变化" radius={[0, 4, 4, 0]}>
                  {result.impacts.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={getImpactColor(entry.impact_level)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="impact-details">
            <h5>详细影响</h5>
            <div className="impact-table">
              <table>
                <thead>
                  <tr>
                    <th>指标</th>
                    <th>相关系数</th>
                    <th>预测变化</th>
                    <th>置信区间</th>
                    <th>影响程度</th>
                  </tr>
                </thead>
                <tbody>
                  {result.impacts.map((impact) => (
                    <tr key={impact.indicator_code}>
                      <td className="indicator-name">{impact.indicator_name}</td>
                      <td className="correlation">{impact.correlation.toFixed(3)}</td>
                      <td className={`change ${impact.predicted_change >= 0 ? 'positive' : 'negative'}`}>
                        {formatChange(impact.predicted_change)}
                      </td>
                      <td className="confidence">
                        [{formatChange(impact.confidence_lower)}, {formatChange(impact.confidence_upper)}]
                      </td>
                      <td>
                        <span className={`impact-badge ${impact.impact_level}`}>
                          {impact.impact_level === 'direct' && '直接'}
                          {impact.impact_level === 'strong' && '强'}
                          {impact.impact_level === 'moderate' && '中等'}
                          {impact.impact_level === 'weak' && '弱'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="simulation-notes">
            <h5>说明</h5>
            <ul>
              <li>预测基于历史相关性和敏感度系数计算</li>
              <li>置信区间反映预测的不确定性</li>
              <li>实际影响可能因市场环境而异</li>
              <li>仅供参考，不构成投资建议</li>
            </ul>
          </div>
        </div>
      )}

      <style>{`
        .shock-simulator {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .simulator-header {
          margin-bottom: 1.5rem;
        }

        .simulator-header h3 {
          margin: 0 0 0.25rem 0;
          font-size: 1.25rem;
          color: var(--text-primary);
        }

        .simulator-header .subtitle {
          margin: 0;
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .simulator-controls {
          background: var(--bg-main);
          border-radius: 6px;
          padding: 1.5rem;
          margin-bottom: 1.5rem;
          border: 1px solid var(--border-color);
        }

        .control-group {
          margin-bottom: 1.5rem;
        }

        .control-group:last-child {
          margin-bottom: 0;
        }

        .control-group label {
          display: block;
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .shock-type-buttons {
          display: flex;
          gap: 0.5rem;
        }

        .type-button {
          flex: 1;
          padding: 0.75rem 1rem;
          border: 1px solid var(--border-color);
          background: var(--bg-card);
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          color: var(--text-secondary) !important;
          transition: all 0.2s;
        }

        .type-button:hover {
          border-color: var(--accent-blue);
          color: var(--accent-blue) !important;
          background: var(--bg-main);
        }

        .type-button.active {
          border-color: var(--accent-blue);
          background: var(--accent-blue);
          color: white !important;
        }

        .indicator-select {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          font-size: 0.875rem;
          background: var(--bg-card);
          color: var(--text-primary);
        }

        .magnitude-slider {
          width: 100%;
          height: 6px;
          border-radius: 3px;
          background: var(--border-color);
          outline: none;
          -webkit-appearance: none;
        }

        .magnitude-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: var(--accent-blue);
          cursor: pointer;
        }

        .magnitude-slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: var(--accent-blue);
          cursor: pointer;
          border: none;
        }

        .slider-labels {
          display: flex;
          justify-content: space-between;
          margin-top: 0.5rem;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        .simulate-button {
          width: 100%;
          padding: 0.875rem;
          background: var(--accent-blue);
          color: white;
          border: none;
          border-radius: 6px;
          font-weight: 600;
          font-size: 0.875rem;
          cursor: pointer;
          transition: background 0.2s;
          margin-top: 1rem;
        }

        .simulate-button:hover:not(:disabled) {
          background: #2563eb;
        }

        .simulate-button:disabled {
          background: var(--border-color);
          color: var(--text-secondary);
          cursor: not-allowed;
        }

        .error-message {
          padding: 1rem;
          background: rgba(255, 59, 48, 0.15);
          border: 1px solid var(--accent-red);
          border-radius: 6px;
          color: var(--text-primary);
          margin-bottom: 1.5rem;
        }

        .simulation-results {
          margin-top: 1.5rem;
          border-top: 1px solid var(--border-color);
          padding-top: 1.5rem;
        }

        .results-header {
          margin-bottom: 1.5rem;
        }

        .results-header h4 {
          margin: 0 0 0.25rem 0;
          font-size: 1.125rem;
          color: var(--text-primary);
        }

        .results-meta {
          margin: 0;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        .impact-chart {
          margin-bottom: 1.5rem;
          background: var(--bg-main);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 1rem;
        }

        .impact-details {
          margin-bottom: 1.5rem;
        }

        .impact-details h5 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .impact-table {
          overflow-x: auto;
        }

        .impact-table table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .impact-table th {
          background: var(--bg-main);
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          color: var(--text-primary);
          border-bottom: 2px solid var(--border-color);
          border-top: 1px solid var(--border-color);
        }

        .impact-table td {
          padding: 0.75rem;
          border-bottom: 1px solid var(--border-color);
        }

        .impact-table .indicator-name {
          font-weight: 500;
          color: var(--text-primary);
        }

        .impact-table .correlation {
          font-family: monospace;
          color: var(--text-secondary);
        }

        .impact-table .change {
          font-weight: 600;
          font-family: monospace;
        }

        .impact-table .change.positive {
          color: var(--accent-green);
        }

        .impact-table .change.negative {
          color: var(--accent-red);
        }

        .impact-table .confidence {
          font-size: 0.75rem;
          color: var(--text-secondary);
          font-family: monospace;
        }

        .impact-badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .impact-badge.direct {
          background: rgba(59, 130, 246, 0.2);
          color: #60a5fa;
        }

        .impact-badge.strong {
          background: rgba(0, 200, 5, 0.15);
          color: var(--accent-green);
        }

        .impact-badge.moderate {
          background: rgba(245, 158, 11, 0.15);
          color: #fbbf24;
        }

        .impact-badge.weak {
          background: var(--border-color);
          color: var(--text-secondary);
        }

        .simulation-notes {
          background: var(--bg-main);
          border: 1px solid var(--border-color);
          border-radius: 6px;
          padding: 1rem;
        }

        .simulation-notes h5 {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: var(--text-primary);
        }

        .simulation-notes ul {
          margin: 0;
          padding-left: 1.25rem;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        .simulation-notes li {
          margin-bottom: 0.25rem;
        }
      `}</style>
    </div>
  );
};
