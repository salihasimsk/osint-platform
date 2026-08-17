import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAdvisories } from "../api/advisories";
import { getCrawlJobs } from "../api/crawls";
import { getHealth } from "../api/health";
import { getStatisticsSummary } from "../api/statistics";
import type {
  Advisory,
  CrawlJob,
  HealthResponse,
  StatisticsSummary,
} from "../types";
import { formatDateTime } from "../utils/date";
import SeverityChart from "../components/SeverityChart";
import OrganizationChart from "../components/OrganizationChart";

function DashboardPage() {
  const [health, setHealth] =
    useState<HealthResponse | null>(null);

  const [statistics, setStatistics] =
    useState<StatisticsSummary | null>(null);

  const [recentAdvisories, setRecentAdvisories] =
    useState<Advisory[]>([]);

  const [recentJobs, setRecentJobs] =
    useState<CrawlJob[]>([]);

  const [lastRefreshed, setLastRefreshed] =
    useState<Date | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    Promise.all([
      getHealth(),
      getStatisticsSummary(),
      getAdvisories({
        page: 1,
        page_size: 5,
        sort_by: "publication_date",
        sort_order: "desc",
      }),
      getCrawlJobs(),
    ])
      .then(
        ([
          healthData,
          statisticsData,
          advisoryData,
          crawlData,
        ]) => {
          if (!isActive) {
            return;
          }

          const sortedJobs = [...crawlData]
            .sort((firstJob, secondJob) =>
              secondJob.job_id.localeCompare(
                firstJob.job_id,
              ),
            )
            .slice(0, 5);

          setHealth(healthData);
          setStatistics(statisticsData);
          setRecentAdvisories(advisoryData);
          setRecentJobs(sortedJobs);
          setLastRefreshed(new Date());
          setError(null);
        },
      )
      .catch((requestError: unknown) => {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load dashboard data.");
        }
      })
      .finally(() => {
        if (isActive) {
          setIsLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, []);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Security advisory collection overview.
          </p>
        </div>

        {lastRefreshed && (
          <span className="last-refreshed">
            Last refreshed:{" "}
            {lastRefreshed.toLocaleTimeString(
              "en-GB",
            )}
          </span>
        )}
      </header>

      {isLoading && <p>Loading dashboard...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {statistics && (
        <>
          <div className="stats-grid">
            <article className="stat-card">
              <span>Total advisories</span>
              <strong>
                {statistics.total_advisories}
              </strong>
            </article>

            <article className="stat-card">
              <span>Active sources</span>
              <strong>
                {statistics.active_sources}
              </strong>
            </article>

            <article className="stat-card">
              <span>Completed crawls</span>
              <strong>
                {statistics.completed_crawls}
              </strong>
            </article>

            <article className="stat-card">
              <span>High severity</span>
              <strong>{statistics.high}</strong>
            </article>
          </div>

          <div className="dashboard-grid">
            <article className="dashboard-panel">
            <h2>Severity Overview</h2>

            <SeverityChart
                critical={statistics.critical}
                high={statistics.high}
                medium={statistics.medium}
                low={statistics.low}
                unknown={statistics.unknown_severity}
            />
            </article>

            <article className="dashboard-panel">
              <h2>Advisories by Organization</h2>

              <OrganizationChart
                organizations={statistics.by_organization}
              />

            </article>
          </div>
        </>
      )}

      {health && (
        <article className="dashboard-panel health-panel">
          <h2>System Status</h2>

          <div className="health-items">
            <span>API: {health.status}</span>
            <span>Database: {health.database}</span>
            <span>Crawler: {health.crawler}</span>
          </div>
        </article>
      )}

      <div className="dashboard-grid">
        <article className="dashboard-panel">
          <div className="panel-header">
            <h2>Recent Advisories</h2>
            <Link to="/advisories">View all</Link>
          </div>

          <div className="compact-list">
            {recentAdvisories.map((advisory) => (
              <Link
                key={advisory.id}
                to={`/advisories/${advisory.id}`}
              >
                <strong>{advisory.title}</strong>

                <span>
                  {advisory.organization} ·{" "}
                  {formatDateTime(
                    advisory.publication_date,
                  )}
                </span>
              </Link>
            ))}
          </div>
        </article>

        <article className="dashboard-panel">
          <div className="panel-header">
            <h2>Recent Crawl Jobs</h2>
            <Link to="/crawls">View all</Link>
          </div>

          <div className="compact-list">
            {recentJobs.map((job) => (
              <Link
                key={job.job_id}
                to={`/crawls/${job.job_id}`}
              >
                <strong>{job.job_id}</strong>

                <span>
                  {job.status} · {job.progress}% ·{" "}
                  {job.records_extracted} records
                </span>
              </Link>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

export default DashboardPage;
