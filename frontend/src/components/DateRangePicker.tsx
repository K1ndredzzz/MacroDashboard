import React, { useState } from 'react';
import { useTimeRange, type TimeRangePreset } from '../contexts/TimeRangeContext';
import { format } from 'date-fns';

const PRESETS: { label: string; value: TimeRangePreset }[] = [
  { label: '1个月', value: '1M' },
  { label: '3个月', value: '3M' },
  { label: '6个月', value: '6M' },
  { label: '1年', value: '1Y' },
  { label: '今年至今', value: 'YTD' },
  { label: '全部', value: 'ALL' },
];

export const DateRangePicker: React.FC = () => {
  const { timeRange, setPreset, setCustomRange } = useTimeRange();
  const [showCustom, setShowCustom] = useState(false);
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  const handlePresetClick = (preset: TimeRangePreset) => {
    setPreset(preset);
    setShowCustom(false);
  };

  const handleCustomSubmit = () => {
    if (customStart && customEnd) {
      setCustomRange(new Date(customStart), new Date(customEnd));
      setShowCustom(false);
    }
  };

  return (
    <div className="date-range-picker">
      <div className="preset-buttons">
        {PRESETS.map((preset) => (
          <button
            key={preset.value}
            className={`preset-btn ${timeRange.preset === preset.value ? 'active' : ''}`}
            onClick={() => handlePresetClick(preset.value)}
          >
            {preset.label}
          </button>
        ))}
        <button
          className={`preset-btn ${timeRange.preset === 'CUSTOM' ? 'active' : ''}`}
          onClick={() => setShowCustom(!showCustom)}
        >
          自定义
        </button>
      </div>

      {showCustom && (
        <div className="custom-range">
          <input
            type="date"
            value={customStart}
            onChange={(e) => setCustomStart(e.target.value)}
            placeholder="开始日期"
          />
          <span>至</span>
          <input
            type="date"
            value={customEnd}
            onChange={(e) => setCustomEnd(e.target.value)}
            placeholder="结束日期"
          />
          <button onClick={handleCustomSubmit}>确定</button>
        </div>
      )}

      <div className="current-range">
        {timeRange.startDate && timeRange.endDate && (
          <span>
            {format(timeRange.startDate, 'yyyy-MM-dd')} 至 {format(timeRange.endDate, 'yyyy-MM-dd')}
          </span>
        )}
        {!timeRange.startDate && <span>全部数据</span>}
      </div>

      <style>{`
        .date-range-picker {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem 1.5rem;
          background: rgba(15, 23, 42, 0.45);
          backdrop-filter: var(--glass-blur);
          -webkit-backdrop-filter: var(--glass-blur);
          border: 1px solid var(--border-color);
          border-radius: 12px;
          box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.5);
        }

        .preset-buttons {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .preset-btn {
          padding: 0.5rem 1rem;
          border: 1px solid var(--border-color);
          background: var(--bg-main);
          color: var(--text-primary);
          border-radius: 6px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.2s;
        }

        .preset-btn:hover {
          background: var(--border-color);
          border-color: var(--accent-blue);
        }

        .preset-btn.active {
          background: var(--accent-blue);
          color: white;
          border-color: var(--accent-blue);
        }

        .custom-range {
          display: flex;
          gap: 0.5rem;
          align-items: center;
          padding: 1rem;
          background: var(--bg-main);
          border-radius: 6px;
          margin-bottom: 1rem;
        }

        .custom-range input[type="date"] {
          padding: 0.5rem;
          border: 1px solid var(--border-color);
          background: var(--bg-card);
          color: var(--text-primary);
          border-radius: 4px;
          font-size: 0.875rem;
        }

        .custom-range button {
          padding: 0.5rem 1rem;
          background: var(--accent-blue);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.875rem;
        }

        .custom-range button:hover {
          background: #2563eb;
        }

        .current-range {
          font-size: 0.875rem;
          color: var(--text-secondary);
          text-align: center;
        }
      `}</style>
    </div>
  );
};
