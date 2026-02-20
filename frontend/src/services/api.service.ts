import { apiClient } from '../lib/api-client';
import type {
  Indicator,
  SeriesData,
  DashboardOverview,
  HealthStatus,
} from '../types/api';

export const apiService = {
  // Health check
  getHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<HealthStatus>('/health');
    return response.data;
  },

  // Get all indicators
  getIndicators: async (): Promise<Indicator[]> => {
    const response = await apiClient.get<Indicator[]>('/indicators');
    return response.data;
  },

  // Get series data for an indicator
  getSeriesData: async (
    indicatorCode: string,
    startDate?: string,
    endDate?: string,
    limit?: number
  ): Promise<SeriesData> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (limit) params.append('limit', limit.toString());

    const response = await apiClient.get<SeriesData>(
      `/indicators/${indicatorCode}/series?${params.toString()}`
    );
    return response.data;
  },

  // Get dashboard overview
  getDashboardOverview: async (): Promise<DashboardOverview> => {
    const response = await apiClient.get<DashboardOverview>('/dashboard/overview');
    return response.data;
  },
};
