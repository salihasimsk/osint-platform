import { useEffect, useState } from "react";

import { getCrawlJobs } from "../api/crawls";
import type { CrawlJob } from "../types";
import { formatDateTime } from "../utils/date";
import { Link } from "react-router-dom";

function CrawlJobsPage() {
  const [jobs, setJobs] = useState<CrawlJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadJobs() {
      try {
        const data = await getCrawlJobs();

        if (isActive) {
          const sortedJobs = [...data].sort((firstJob, secondJob) =>
            secondJob.job_id.localeCompare(firstJob.job_id),
          );

          setJobs(sortedJobs);
          setError(null);
        }
      } catch (requestError: unknown) {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load crawl jobs.");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadJobs();

    const intervalId = window.setInterval(
      loadJobs,
      5000,
    );

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, []);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Crawl Jobs</h1>
          <p>
            Monitor crawl status, progress and results.
          </p>
        </div>
      </header>

      {isLoading && <p>Loading crawl jobs...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!isLoading && !error && jobs.length === 0 && (
        <p>No crawl jobs were found.</p>
      )}

      {jobs.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th scope="col">Job ID</th>
                <th scope="col">Status</th>
                <th scope="col">Progress</th>
                <th scope="col">Pages</th>
                <th scope="col">Records</th>
                <th scope="col">Errors</th>
                <th scope="col">Started</th>
              </tr>
            </thead>

            <tbody>
              {jobs.map((job) => (
                <tr key={job.job_id}>
                  <td>
                    <Link
                        className="job-link"
                        to={`/crawls/${job.job_id}`}
                    >
                        {job.job_id}
                     </Link>
                   </td>

                  <td>
                    <span
                      className={`status-badge ${job.status}`}
                    >
                      {job.status}
                    </span>
                  </td>

                  <td>
                    <div className="progress-cell">
                      <progress
                        value={job.progress}
                        max="100"
                      />
                      <span>{job.progress}%</span>
                    </div>
                  </td>

                  <td>{job.pages_visited}</td>
                  <td>{job.records_extracted}</td>
                  <td>{job.error_count}</td>

                  <td>
                    {formatDateTime(job.started_date)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default CrawlJobsPage;
