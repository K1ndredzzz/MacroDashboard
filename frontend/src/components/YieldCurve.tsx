import React, { useEffect, useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useDateRange } from '../hooks/useDateRange';
import { useMarketData } from '../contexts/MarketDataContext';

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
  const { snapshotsByCode } = useMarketData();

  const snapshotCurveData = useMemo<YieldCurveData | null>(() => {
    const us2ySnapshot = snapshotsByCode.US2Y;
    const us10ySnapshot = snapshotsByCode.US10Y;

    const rate2y = us2ySnapshot ? Number.parseFloat(us2ySnapshot.latest_value) : Number.NaN;
    const rate10y = us10ySnapshot ? Number.parseFloat(us10ySnapshot.latest_value) : Number.NaN;

    if (!Number.isFinite(rate2y) || !Number.isFinite(rate10y)) {
      return null;
    }

    const spread = rate10y - rate2y;
    const dateCandidates = [us2ySnapshot?.as_of_date, us10ySnapshot?.as_of_date].filter(Boolean) as string[];
    const observationDate = dateCandidates.length > 0
      ? dateCandidates.sort((a, b) => new Date(a).getTime() - new Date(b).getTime())[dateCandidates.length - 1]
      : new Date().toISOString();

    let curveShape = 'flat';
    if (spread > 0.5) {
      curveShape = 'normal';
    } else if (spread < -0.1) {
      curveShape = 'inverted';
    }

    return {
      observation_date: observationDate,
      points: [
        { maturity: '2Y', rate: rate2y.toString() },
        { maturity: '10Y', rate: rate10y.toString() }
      ],
      spread_10y_2y: spread.toString(),
      curve_shape: curveShape
    };
  }, [snapshotsByCode.US2Y, snapshotsByCode.US10Y]);

  useEffect(() => {
    if (snapshotCurveData) {
      setData(snapshotCurveData);
      setError(null);
      setLoading(false);
      return;
    }

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
  }, [formattedRange.endDateStr, snapshotCurveData]);

  if (loading) {
    return <div className="yield-curve loading">加载中...</div>;
  }

  if (error) {
    return <div className="yield-curve error">加载失败: {error}</div>;
  }

  if (!data) {
    return null;
  }

  const maturityToMonths = (maturity: string): number => {
    const label = maturity.trim().toUpperCase();
    if (label.length < 2) return Number.MAX_SAFE_INTEGER;

    const unit = label.slice(-1);
    const value = Number.parseFloat(label.slice(0, -1));
    if (Number.isNaN(value)) return Number.MAX_SAFE_INTEGER;

    if (unit === 'D') return value / 30;
    if (unit === 'W') return (value * 7) / 30;
    if (unit === 'M') return value;
    if (unit === 'Y') return value * 12;
    return Number.MAX_SAFE_INTEGER;
  };

  const chartData = [...data.points]
    .sort((a, b) => maturityToMonths(a.maturity) - maturityToMonths(b.maturity))
    .map(point => ({
      maturity: point.maturity,
      rate: Number.parseFloat(point.rate)
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
