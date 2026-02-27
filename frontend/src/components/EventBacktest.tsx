import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Event {
  event_id: number;
  event_name: string;
  event_date: string;
  event_type: string;
  description: string | null;
  severity: string | null;
}

interface IndicatorImpact {
  indicator_code: string;
  indicator_name: string;
  before_value: number | null;
  after_value: number | null;
  change_pct: number | null;
  observations: Array<{
    observation_date: string;
    value: string;
  }>;
}

interface EventImpact {
  event: Event;
  indicators: IndicatorImpact[];
  analysis_window_days: number;
}

const DEFAULT_INDICATORS = ['US10Y', 'US2Y', 'EURUSD'];

export const EventBacktest: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<number | null>(null);
  const [impact, setImpact] = useState<EventImpact | null>(null);
  const [loading, setLoading] = useState(true);
  const [impactLoading, setImpactLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/api/v1/events');
        if (!response.ok) {
          throw new Error('Failed to fetch events');
        }

        const result = await response.json();
        setEvents(result);

        if (result.length > 0) {
          setSelectedEvent(result[0].event_id);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  useEffect(() => {
    if (!selectedEvent) return;

    const fetchImpact = async () => {
      setImpactLoading(true);

      try {
        const params = new URLSearchParams({
          indicator_codes: DEFAULT_INDICATORS.join(','),
          window_days: '30'
        });

        const response = await fetch(`/api/v1/events/${selectedEvent}/impact?${params}`);
        if (!response.ok) {
          throw new Error('Failed to fetch event impact');
        }

        const result = await response.json();
        setImpact(result);
      } catch (err) {
        console.error('Failed to fetch impact:', err);
      } finally {
        setImpactLoading(false);
      }
    };

    fetchImpact();
  }, [selectedEvent]);

  if (loading) {
    return <div className="event-backtest loading">加载中...</div>;
  }

  if (error) {
    return <div className="event-backtest error">加载失败: {error}</div>;
  }

  const getSeverityColor = (severity: string | null) => {
    const colors: Record<string, string> = {
      'critical': '#dc2626',
      'high': '#f59e0b',
      'medium': '#3b82f6',
      'low': '#10b981'
    };
    return colors[severity || 'medium'] || '#6b7280';
  };

  const getEventTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'financial_crisis': '金融危机',
      'pandemic': '疫情',
      'geopolitical': '地缘政治',
      'market_crash': '市场崩盘',
      'currency': '货币事件'
    };
    return labels[type] || type;
  };

  return (
    <div className="event-backtest card">
      <div className="backtest-header">
        <h3>历史事件回测</h3>
        <p className="subtitle">分析重大事件对宏观指标的影响</p>
      </div>

      <div className="event-timeline">
        <h4>选择事件</h4>
        <div className="timeline-container">
          {events.map((event) => (
            <div
              key={event.event_id}
              className={`timeline-item ${selectedEvent === event.event_id ? 'active' : ''}`}
              onClick={() => setSelectedEvent(event.event_id)}
            >
              <div className="timeline-marker" style={{ backgroundColor: getSeverityColor(event.severity) }} />
              <div className="timeline-content">
                <div className="event-name">{event.event_name}</div>
                <div className="event-meta">
                  <span className="event-date">{new Date(event.event_date).toLocaleDateString('zh-CN')}</span>
                  <span className="event-type">{getEventTypeLabel(event.event_type)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {impactLoading && (
        <div className="impact-loading">分析中...</div>
      )}

      {!impactLoading && impact && (
        <div className="event-impact">
          <div className="impact-header">
            <h4>{impact.event.event_name}</h4>
            <p className="event-description">{impact.event.description}</p>
            <p className="analysis-window">
              分析窗口: 事件前后各 {impact.analysis_window_days} 天
            </p>
          </div>

          <div className="impact-summary">
            <h5>指标变化</h5>
            <div className="impact-cards">
              {impact.indicators.map((indicator) => (
                <div key={indicator.indicator_code} className="impact-card">
                  <div className="indicator-name">{indicator.indicator_name}</div>
                  <div className="values">
                    <div className="value-item">
                      <span className="label">事件前:</span>
                      <span className="value">
                        {indicator.before_value !== null ? indicator.before_value.toFixed(2) : '-'}
                      </span>
                    </div>
                    <div className="value-item">
                      <span className="label">事件后:</span>
                      <span className="value">
                        {indicator.after_value !== null ? indicator.after_value.toFixed(2) : '-'}
                      </span>
                    </div>
                  </div>
                  {indicator.change_pct !== null && (
                    <div className={`change ${indicator.change_pct >= 0 ? 'positive' : 'negative'}`}>
                      {indicator.change_pct >= 0 ? '↑' : '↓'} {Math.abs(indicator.change_pct).toFixed(2)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {impact.indicators.length > 0 && impact.indicators[0].observations.length > 0 && (
            <div className="impact-chart">
              <h5>趋势图</h5>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis
                    dataKey="observation_date"
                    type="category"
                    allowDuplicatedCategory={false}
                    tickFormatter={(date) => new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                    stroke="var(--text-secondary)"
                    tick={{ fill: 'var(--text-secondary)' }}
                  />
                  <YAxis stroke="var(--text-secondary)" tick={{ fill: 'var(--text-secondary)' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-primary)' }}
                    itemStyle={{ color: 'var(--text-primary)' }}
                    labelFormatter={(date) => new Date(date).toLocaleDateString('zh-CN')}
                    formatter={(value: number | undefined) => value ? value.toFixed(2) : '-'}
                  />
                  <Legend wrapperStyle={{ color: 'var(--text-primary)' }} />
                  {impact.indicators.map((indicator, idx) => {
                    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
                    const chartData = indicator.observations.map(obs => ({
                      observation_date: obs.observation_date,
                      [indicator.indicator_code]: parseFloat(obs.value)
                    }));

                    return (
                      <Line
                        key={indicator.indicator_code}
                        data={chartData}
                        type="monotone"
                        dataKey={indicator.indicator_code}
                        stroke={colors[idx % colors.length]}
                        strokeWidth={2}
                        name={indicator.indicator_name}
                        dot={false}
                      />
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      <style>{`
        .event-backtest {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .backtest-header {
          margin-bottom: 1.5rem;
        }

        .backtest-header h3 {
          margin: 0 0 0.25rem 0;
          font-size: 1.25rem;
          color: var(--text-primary);
        }

        .backtest-header .subtitle {
          margin: 0;
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .event-timeline h4 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .timeline-container {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-height: 300px;
          overflow-y: auto;
          padding: 0.5rem;
          background: var(--bg-main);
          border-radius: 6px;
        }

        .timeline-item {
          display: flex;
          gap: 0.75rem;
          padding: 0.75rem;
          background: var(--bg-card);
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
          border: 1px solid var(--border-color);
        }

        .timeline-item:hover {
          background: var(--border-color);
        }

        .timeline-item.active {
          border-color: var(--accent-blue);
          background: rgba(59, 130, 246, 0.1);
        }

        .timeline-marker {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-top: 0.25rem;
          flex-shrink: 0;
        }

        .timeline-content {
          flex: 1;
        }

        .event-name {
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
        }

        .event-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        .impact-loading {
          padding: 2rem;
          text-align: center;
          color: var(--text-secondary);
        }

        .event-impact {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid var(--border-color);
        }

        .impact-header {
          margin-bottom: 1.5rem;
        }

        .impact-header h4 {
          margin: 0 0 0.5rem 0;
          font-size: 1.125rem;
          color: var(--text-primary);
        }

        .event-description {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: var(--text-secondary);
        }

        .analysis-window {
          margin: 0;
          font-size: 0.75rem;
          color: var(--text-secondary);
          opacity: 0.7;
        }

        .impact-summary h5 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .impact-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .impact-card {
          padding: 1rem;
          background: var(--bg-main);
          border-radius: 6px;
          border: 1px solid var(--border-color);
        }

        .impact-card .indicator-name {
          font-weight: 600;
          color: var(--text-primary);
          margin-bottom: 0.75rem;
          font-size: 0.875rem;
        }

        .impact-card .values {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
        }

        .impact-card .value-item {
          display: flex;
          justify-content: space-between;
          font-size: 0.875rem;
        }

        .impact-card .label {
          color: var(--text-secondary);
        }

        .impact-card .value {
          font-weight: 500;
          color: var(--text-primary);
        }

        .impact-card .change {
          font-weight: 600;
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          text-align: center;
        }

        .impact-card .change.positive {
          color: var(--accent-green);
          background: rgba(0, 200, 5, 0.1);
        }

        .impact-card .change.negative {
          color: var(--accent-red);
          background: rgba(255, 59, 48, 0.1);
        }

        .impact-chart {
          margin-top: 1.5rem;
        }

        .impact-chart h5 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .event-backtest.loading,
        .event-backtest.error {
          padding: 2rem;
          text-align: center;
          color: var(--text-secondary);
        }

        .event-backtest.error {
          color: var(--text-primary);
          background: rgba(255, 59, 48, 0.15);
          border: 1px solid var(--accent-red);
        }
      `}</style>
    </div>
  );
};
