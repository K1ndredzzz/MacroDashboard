import React, { createContext, useContext, useState, useCallback } from 'react';
import { subMonths, subYears, startOfYear } from 'date-fns';

export type TimeRangePreset = '1M' | '3M' | '6M' | '1Y' | 'YTD' | 'ALL' | 'CUSTOM';

export interface TimeRange {
  startDate: Date | null;
  endDate: Date | null;
  preset: TimeRangePreset;
}

interface TimeRangeContextType {
  timeRange: TimeRange;
  setTimeRange: (range: TimeRange) => void;
  setPreset: (preset: TimeRangePreset) => void;
  setCustomRange: (startDate: Date, endDate: Date) => void;
}

const TimeRangeContext = createContext<TimeRangeContextType | undefined>(undefined);

export const TimeRangeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [timeRange, setTimeRangeState] = useState<TimeRange>({
    startDate: subYears(new Date(), 1),
    endDate: new Date(),
    preset: '1Y',
  });

  const setTimeRange = useCallback((range: TimeRange) => {
    setTimeRangeState(range);
  }, []);

  const setPreset = useCallback((preset: TimeRangePreset) => {
    const endDate = new Date();
    let startDate: Date | null = null;

    switch (preset) {
      case '1M':
        startDate = subMonths(endDate, 1);
        break;
      case '3M':
        startDate = subMonths(endDate, 3);
        break;
      case '6M':
        startDate = subMonths(endDate, 6);
        break;
      case '1Y':
        startDate = subYears(endDate, 1);
        break;
      case 'YTD':
        startDate = startOfYear(endDate);
        break;
      case 'ALL':
        startDate = null;
        break;
      case 'CUSTOM':
        // Keep current dates for custom
        return;
    }

    setTimeRangeState({
      startDate,
      endDate,
      preset,
    });
  }, []);

  const setCustomRange = useCallback((startDate: Date, endDate: Date) => {
    setTimeRangeState({
      startDate,
      endDate,
      preset: 'CUSTOM',
    });
  }, []);

  return (
    <TimeRangeContext.Provider value={{ timeRange, setTimeRange, setPreset, setCustomRange }}>
      {children}
    </TimeRangeContext.Provider>
  );
};

export const useTimeRange = () => {
  const context = useContext(TimeRangeContext);
  if (context === undefined) {
    throw new Error('useTimeRange must be used within a TimeRangeProvider');
  }
  return context;
};
