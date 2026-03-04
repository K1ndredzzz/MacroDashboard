/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useMemo } from 'react';
import { useDashboardOverview } from '../hooks/useApi';
import type { DashboardOverview, LatestSnapshot } from '../types/api';

interface MarketDataContextType {
  overview: DashboardOverview | undefined;
  isLoading: boolean;
  error: unknown;
  snapshotsByCode: Record<string, LatestSnapshot>;
}

const MarketDataContext = createContext<MarketDataContextType | undefined>(undefined);

export const MarketDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { data: overview, isLoading, error } = useDashboardOverview();

  const snapshotsByCode = useMemo(() => {
    const byCode: Record<string, LatestSnapshot> = {};
    (overview?.indicators || []).forEach((snapshot) => {
      byCode[snapshot.indicator_code] = snapshot;
    });
    return byCode;
  }, [overview?.indicators]);

  const value = useMemo(
    () => ({
      overview,
      isLoading,
      error,
      snapshotsByCode
    }),
    [overview, isLoading, error, snapshotsByCode]
  );

  return <MarketDataContext.Provider value={value}>{children}</MarketDataContext.Provider>;
};

export const useMarketData = (): MarketDataContextType => {
  const context = useContext(MarketDataContext);
  if (context === undefined) {
    throw new Error('useMarketData must be used within a MarketDataProvider');
  }
  return context;
};

