import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useDateRange } from '../hooks/useDateRange';

interface YieldCurvePoint {
  maturity: string;
  rate: string;
}

interface YieldCurveData {
  observation_date: string;
  points: YieldCurvePoint[];
  spread_10y_2y: string;
  curve_shape: string;
}

export const YieldCurve: React.FC = () => {
  const [data, setData] = useState<YieldCurveData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { formattedRange } = useDateRange();

  useEffect(() => {
    const fetchYieldCurve = async () => {
      setLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams();
        if (formattedRange.endDateStr) {
          params.append('observation_date', formattedRange.endDateStr);
        }

        const response = await fetch(`/api/v1/indicators/yield-curve?${params}`);
        if (!response.ok) {
          throw new Error('Failed to fetch yield curve data');
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchYieldCurve();
  }, [formattedRange.endDateStr]);

  if (loading) {
    return <div className="yield-curve loading">加载中...</div>;
  }

  if (error) {
    return <div className="yield-curve error">加载失败: {error}</div>;
  }

  if (!data) {
    return null;
  }

  const chartData = data.points.map(point => ({
    maturity: point.maturity,
    rate: parseFloat(point.rate)
  }));

  const getCurveShapeLabel = (shape: string) => {
    const labels: Record<string, string> = {
      'normal': '正常',
      'inverted': '倒挂',
      'flat': '平坦'
    };
    return labels[shape] || shape;
  };

  const getCurveShapeColor = (shape: string) => {
    const colors: Record<string, string> = {
      'normal': 'var(--accent-green)',
      'inverted': 'var(--accent-red)',
      'flat': 'var(--accent-warning)'
    };
    return colors[shape] || 'var(--text-secondary)';
  };

  return (
    <div className="yield-curve card">
      <div className="yield-curve-header">
        <h3>美债收益率曲线</h3>
        <div className="yield-curve-info">
          <span className="date">
            {new Date(data.observation_date).toLocaleDateString('zh-CN')}
          </span>
          <span
            className="curve-shape"
            style={{ color: getCurveShapeColor(data.curve_shape) }}
          >
            {getCurveShapeLabel(data.curve_shape)}
          </span>
          <span className="spread">
            利差: {parseFloat(data.spread_10y_2y).toFixed(2)}%
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
          <XAxis dataKey="maturity" stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} />
          <YAxis
            label={{ value: '收益率 (%)', angle: -90, position: 'insideLeft', fill: 'var(--text-secondary)' }}
            domain={['auto', 'auto']}
            stroke="var(--text-secondary)"
            tick={{ fill: 'var(--text-secondary)' }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
            itemStyle={{ color: 'var(--text-primary)' }}
            formatter={(value: number | undefined) => value ? `${value.toFixed(2)}%` : '-'}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            labelFormatter={(label: any) => `期限: ${label}`}
          />
          <Legend wrapperStyle={{ color: 'var(--text-primary)' }} />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="var(--accent-blue)"
            strokeWidth={2}
            name="收益率"
            dot={{ r: 6, fill: 'var(--bg-card)', stroke: 'var(--accent-blue)', strokeWidth: 2 }}
            activeDot={{ r: 8, fill: 'var(--accent-blue)' }}
          />
        </LineChart>
      </ResponsiveContainer>

      <style>{`
        .yield-curve {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .yield-curve-header {
          margin-bottom: 1rem;
        }

        .yield-curve-header h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
          color: var(--text-primary);
        }

        .yield-curve-info {
          display: flex;
          gap: 1.5rem;
          font-size: 0.875rem;
        }

        .yield-curve-info .date {
          color: var(--text-secondary);
        }

        .yield-curve-info .curve-shape {
          font-weight: 600;
        }

        .yield-curve-info .spread {
          color: var(--text-primary);
          font-weight: 500;
        }

        .yield-curve.loading,
        .yield-curve.error {
          padding: 2rem;
          text-align: center;
          color: var(--text-secondary);
        }

        .yield-curve.error {
          color: var(--text-primary);
          background: rgba(255, 59, 48, 0.15);
          border: 1px solid var(--accent-red);
        }
      `}</style>
    </div>
  );
};
