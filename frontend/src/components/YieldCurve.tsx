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
      'normal': '#10b981',
      'inverted': '#ef4444',
      'flat': '#f59e0b'
    };
    return colors[shape] || '#6b7280';
  };

  return (
    <div className="yield-curve">
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
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="maturity" />
          <YAxis
            label={{ value: '收益率 (%)', angle: -90, position: 'insideLeft' }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            formatter={(value: number | undefined) => value ? `${value.toFixed(2)}%` : '-'}
            labelFormatter={(label: any) => `期限: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="rate"
            stroke="#3b82f6"
            strokeWidth={2}
            name="收益率"
            dot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <style>{`
        .yield-curve {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          margin-bottom: 1.5rem;
        }

        .yield-curve-header {
          margin-bottom: 1rem;
        }

        .yield-curve-header h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
          color: #1f2937;
        }

        .yield-curve-info {
          display: flex;
          gap: 1.5rem;
          font-size: 0.875rem;
        }

        .yield-curve-info .date {
          color: #6b7280;
        }

        .yield-curve-info .curve-shape {
          font-weight: 600;
        }

        .yield-curve-info .spread {
          color: #1f2937;
          font-weight: 500;
        }

        .yield-curve.loading,
        .yield-curve.error {
          padding: 2rem;
          text-align: center;
          color: #6b7280;
        }

        .yield-curve.error {
          color: #ef4444;
        }
      `}</style>
    </div>
  );
};
