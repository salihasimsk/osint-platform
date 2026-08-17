import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getCrawlJob } from "../api/crawls";
import type { CrawlJob } from "../types";
import { formatDateTime } from "../utils/date";

function CrawlDetailsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const isJobIdMissing = !jobId;

  const [job, setJob] = useState<CrawlJob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
        return;
    }

    let isActive = true;

    async function loadJob() {
      try {
        const data = await getCrawlJob(jobId!);

        if (isActive) {
          setJob(data);
          setError(null);
        }
      } catch (requestError: unknown) {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load the crawl job.");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadJob();

    const intervalId = window.setInterval(
      loadJob,
      3000,
    );

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, [jobId]);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Crawl Details</h1>
          <p>{jobId}</p>
        </div>
      </header>

      {isJobIdMissing && (
        <p className="error-message" role="alert">
             Crawl job ID is missing.
        </p>
      )}

      {!isJobIdMissing && isLoading && (
        <p>Loading crawl details...</p>
      )}


      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {job && (
        <div className="details-card">
          <div>
            <span>Status</span>
            <strong>
              <span
                className={`status-badge ${job.status}`}
              >
                {job.status}
              </span>
            </strong>
          </div>

          <div>
            <span>Progress</span>
            <strong>{job.progress}%</strong>
          </div>

          <div>
            <span>Pages visited</span>
            <strong>{job.pages_visited}</strong>
          </div>

          <div>
            <span>Records extracted</span>
            <strong>{job.records_extracted}</strong>
          </div>

          <div>
            <span>Error count</span>
            <strong>{job.error_count}</strong>
          </div>

          <div>
            <span>Started</span>
            <strong>
              {formatDateTime(job.started_date)}
            </strong>
          </div>

          <div>
            <span>Completed</span>
            <strong>
              {formatDateTime(job.completed_date)}
            </strong>
          </div>
        </div>
      )}
    </section>
  );
}

export default CrawlDetailsPage;
