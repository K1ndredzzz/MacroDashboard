import { useDashboardOverview } from '../hooks/useApi';
import './Dashboard.css';

export default function Dashboard() {
  const { data, isLoading, error } = useDashboardOverview();

  if (isLoading) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <h1>宏观经济仪表盘</h1>
          <p>Macro Economic Dashboard</p>
        </header>
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <h1>宏观经济仪表盘</h1>
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
        <h1>宏观经济仪表盘</h1>
        <p className="subtitle">Macro Economic Dashboard</p>
        <p className="update-time">
          更新时间: {data?.as_of ? new Date(data.as_of).toLocaleString('zh-CN') : '-'}
        </p>
      </header>

      <div className="container">
        {groupedIndicators && Object.entries(groupedIndicators).map(([category, indicators]) => (
          <section key={category} className="category-section">
            <h2 className="category-title">{getCategoryName(category)}</h2>
            <div className="grid grid-cols-3">
              {indicators.map((indicator) => (
                <div key={indicator.indicator_code} className="card indicator-card">
                  <h3 className="indicator-name">{indicator.indicator_name}</h3>
                  <div className="indicator-value">
                    {indicator.latest_value} <span className="unit">{indicator.unit}</span>
                  </div>
                  {indicator.delta_pct && (
                    <div className={`indicator-change ${parseFloat(indicator.delta_pct) >= 0 ? 'positive' : 'negative'}`}>
                      {parseFloat(indicator.delta_pct) >= 0 ? '↑' : '↓'} {Math.abs(parseFloat(indicator.delta_pct)).toFixed(2)}%
                    </div>
                  )}
                  <div className="indicator-date">
                    {new Date(indicator.as_of_date).toLocaleDateString('zh-CN')}
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

function getCategoryName(category: string): string {
  const names: Record<string, string> = {
    'rates': '利率',
    'fx': '外汇',
    'commodity': '大宗商品',
    'inflation': '通胀',
    'labor': '就业',
  };
  return names[category] || category;
}
