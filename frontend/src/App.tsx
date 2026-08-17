import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import SourcesPage from "./pages/SourcesPage";
import NewCrawlPage from "./pages/NewCrawlPage";
import CrawlJobsPage from "./pages/CrawlJobsPage";
import CrawlDetailsPage from "./pages/CrawlDetailsPage";
import AdvisoriesPage from "./pages/AdvisoriesPage";
import AdvisoryDetailsPage from "./pages/AdvisoryDetailsPage";
import LogsPage from "./pages/LogsPage";

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="sources" element={<SourcesPage />} />
        <Route path="crawls/new" element={<NewCrawlPage />} />
        <Route path="crawls" element={<CrawlJobsPage />} />
        <Route path="crawls/:jobId" element={<CrawlDetailsPage />}/>
        <Route path="advisories" element={<AdvisoriesPage />}/>
        <Route path="advisories/:advisoryId" element={<AdvisoryDetailsPage />}/>
        <Route path="logs" element={<LogsPage />} />
      </Route>

      <Route
        path="*"
        element={<Navigate to="/" replace />}
      />
    </Routes>
  );
}

export default App;
