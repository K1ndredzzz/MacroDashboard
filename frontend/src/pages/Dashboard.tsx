import { useDashboardOverview } from '../hooks/useApi';
import { DateRangePicker } from '../components/DateRangePicker';
import { YieldCurve } from '../components/YieldCurve';
import { CorrelationHeatmap } from '../components/CorrelationHeatmap';
import { EventBacktest } from '../components/EventBacktest';
import { ShockSimulator } from '../components/ShockSimulator';
import './Dashboard.css';

export default function Dashboard() {
  const { data, isLoading, error } = useDashboardOverview();

  if (isLoading) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-left">
            <h1>MacroDashboard V2</h1>
            <p className="subtitle">Quantitative Finance Control Room</p>
          </div>
        </header>
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <div className="header-left">
            <h1>MacroDashboard V2</h1>
            <p className="subtitle">Quantitative Finance Control Room</p>
          </div>
        </header>
        <div className="error">
          加载失败: {error instanceof Error ? error.message : '未知错误'}
        </div>
      </div>
    );
  }

  const groupedIndicators = data?.indicators.reduce((acc, indicator) => {
    if (!acc[indicator.category]) {
      acc[indicator.category] = [];
    }
    acc[indicator.category].push(indicator);
    return acc;
  }, {} as Record<string, typeof data.indicators>);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>MacroDashboard V2</h1>
          <p className="subtitle">Quantitative Finance Control Room</p>
        </div>
        <div className="header-right">
          <div className="update-time">
            UPDATED: {data?.as_of ? new Date(data.as_of).toLocaleString('zh-CN') : '-'}
          </div>
          <a href="https://github.com/K1ndredzzz/MacroDashboard" target="_blank" rel="noopener noreferrer" className="github-link" title="View Source on GitHub">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
            </svg>
          </a>
        </div>
      </header>

      <div className="container">
        {/* Top Controls span full width */}
        <div className="col-span-12">
          <DateRangePicker />
        </div>

        {/* Indicators take individual grid placement or wrapped in a wider column */}
        {groupedIndicators && Object.entries(groupedIndicators).map(([category, indicators]) => (
          <section key={category} className="category-section">
            {indicators.map((indicator) => (
              <div key={indicator.indicator_code} className="card indicator-card col-span-4">
                <h3 className="indicator-name">{indicator.indicator_name}</h3>
                <div className="indicator-value">
                  {indicator.latest_value} <span className="unit">{indicator.unit}</span>
                </div>
                {indicator.delta_pct && (
                  <div className="indicator-footer">
                    <span className="indicator-date">{new Date(indicator.as_of_date).toLocaleDateString('zh-CN')}</span>
                    <div className={`indicator-change ${parseFloat(indicator.delta_pct) >= 0 ? 'positive' : 'negative'}`}>
                      {parseFloat(indicator.delta_pct) >= 0 ? '↑' : '↓'} {Math.abs(parseFloat(indicator.delta_pct)).toFixed(2)}%
                    </div>
                  </div>
                )}
              </div>
            ))}
          </section>
        ))}

        <div className="col-span-8">
          <YieldCurve />
        </div>

        <div className="col-span-4">
          <ShockSimulator />
        </div>

        <div className="col-span-6">
          <CorrelationHeatmap />
        </div>

        <div className="col-span-6">
          <EventBacktest />
        </div>
      </div>
    </div>
  );
}
