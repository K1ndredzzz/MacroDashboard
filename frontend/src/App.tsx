import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TimeRangeProvider } from './contexts/TimeRangeContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { MarketDataProvider } from './contexts/MarketDataContext';
import Dashboard from './pages/Dashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TimeRangeProvider>
        <AnalyticsProvider>
          <MarketDataProvider>
            <Dashboard />
          </MarketDataProvider>
        </AnalyticsProvider>
      </TimeRangeProvider>
    </QueryClientProvider>
  );
}

export default App;
