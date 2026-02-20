import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api.service';

export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: apiService.getHealth,
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useIndicators = () => {
  return useQuery({
    queryKey: ['indicators'],
    queryFn: apiService.getIndicators,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useSeriesData = (
  indicatorCode: string,
  startDate?: string,
  endDate?: string,
  limit?: number
) => {
  return useQuery({
    queryKey: ['series', indicatorCode, startDate, endDate, limit],
    queryFn: () => apiService.getSeriesData(indicatorCode, startDate, endDate, limit),
    enabled: !!indicatorCode,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: apiService.getDashboardOverview,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};
