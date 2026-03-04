/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useMemo, useState } from 'react';
import { CORRELATION_INDICATORS, DEFAULT_CORRELATION_WINDOW_DAYS } from '../constants/analytics';

interface AnalyticsContextType {
  correlationIndicators: string[];
  correlationWindowDays: number;
  setCorrelationWindowDays: (days: number) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

export const AnalyticsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [correlationWindowDays, setCorrelationWindowDays] = useState<number>(DEFAULT_CORRELATION_WINDOW_DAYS);

  const value = useMemo(
    () => ({
      correlationIndicators: [...CORRELATION_INDICATORS],
      correlationWindowDays,
      setCorrelationWindowDays
    }),
    [correlationWindowDays]
  );

  return <AnalyticsContext.Provider value={value}>{children}</AnalyticsContext.Provider>;
};

export const useAnalytics = (): AnalyticsContextType => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};
