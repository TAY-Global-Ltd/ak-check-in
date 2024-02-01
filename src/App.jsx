import { Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "./App.css";
import CheckInProvider from "./context/CheckInContext";
import CheckInPage from "./components/CheckInPage";

const App = () => {
  const queryClient = new QueryClient()

  return (
    <Suspense fallback="Loading...">
      <QueryClientProvider client={queryClient}>
        <CheckInProvider>
          <CheckInPage/>
        </CheckInProvider>
      </QueryClientProvider>
    </Suspense>
  );
};

export default App;
