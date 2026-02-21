import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TimeRangeProvider } from './contexts/TimeRangeContext';
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
        <Dashboard />
      </TimeRangeProvider>
    </QueryClientProvider>
  );
}

export default App;
