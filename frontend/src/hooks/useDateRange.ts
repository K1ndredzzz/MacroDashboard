import { useMemo } from 'react';
import { useTimeRange } from '../contexts/TimeRangeContext';
import { format } from 'date-fns';

export const useDateRange = () => {
  const { timeRange, setPreset, setCustomRange } = useTimeRange();

  const formattedRange = useMemo(() => {
    if (!timeRange.startDate || !timeRange.endDate) {
      return {
        startDate: null,
        endDate: null,
        startDateStr: null,
        endDateStr: null,
      };
    }

    return {
      startDate: timeRange.startDate,
      endDate: timeRange.endDate,
      startDateStr: format(timeRange.startDate, 'yyyy-MM-dd'),
      endDateStr: format(timeRange.endDate, 'yyyy-MM-dd'),
    };
  }, [timeRange]);

  const queryParams = useMemo(() => {
    const params: Record<string, string> = {};

    if (formattedRange.startDateStr) {
      params.start_date = formattedRange.startDateStr;
    }

    if (formattedRange.endDateStr) {
      params.end_date = formattedRange.endDateStr;
    }

    return params;
  }, [formattedRange]);

  return {
    timeRange,
    formattedRange,
    queryParams,
    setPreset,
    setCustomRange,
  };
};
