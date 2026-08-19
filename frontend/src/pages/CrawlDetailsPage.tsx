import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  getCrawlJob,
  stopCrawl,
} from "../api/crawls";

import { getCrawlLogs } from "../api/logs";

import type {
  CrawlJob,
  CrawlLog,
} from "../types";

import { formatDateTime } from "../utils/date";

function CrawlDetailsPage() {
  const { jobId } = useParams<{ jobId: string }>();

  const isJobIdMissing = !jobId;

  const [job, setJob] = useState<CrawlJob | null>(null);

  const [logs, setLogs] = useState<CrawlLog[]>([]);

  const [isLoading, setIsLoading] = useState(!isJobIdMissing);

  const [error, setError] = useState<string | null>(null);

  const [isStopping, setIsStopping] = useState(false);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    const currentJobId = jobId;

    let isActive = true;

    async function loadJob() {
      try {
        const [jobData, logData] =
          await Promise.all([
            getCrawlJob(currentJobId),
            getCrawlLogs(currentJobId),
          ]);

        if (!isActive) {
          return;
        }

        setJob(jobData);
        setLogs(logData);
        setError(null);
      } catch (requestError: unknown) {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError(
            "Could not load the crawl job.",
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadJob();

    const intervalId =
      window.setInterval(
        loadJob,
        3000,
      );

    return () => {
      isActive = false;

      window.clearInterval(
        intervalId,
      );
    };
  }, [jobId]);

  async function handleStopCrawl() {
    if (!jobId) {
      return;
    }

    setIsStopping(true);
    setError(null);

    try {
      const updatedJob =
        await stopCrawl(jobId);

      setJob(updatedJob);
    } catch (requestError: unknown) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError(
          "Could not stop the crawl job.",
        );
      }
    } finally {
      setIsStopping(false);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Crawl Details</h1>
          <p>{jobId}</p>
        </div>

        {job &&
          (job.status === "queued" ||
            job.status === "running") && (
            <button
              className="secondary-button"
              type="button"
              disabled={isStopping}
              onClick={handleStopCrawl}
            >
              {isStopping
                ? "Stopping..."
                : "Stop Crawl"}
            </button>
          )}
      </header>

      {isJobIdMissing && (
        <p
          className="error-message"
          role="alert"
        >
          Crawl job ID is missing.
        </p>
      )}

      {!isJobIdMissing &&
        isLoading && (
          <p>
            Loading crawl details...
          </p>
        )}

      {error && (
        <p
          className="error-message"
          role="alert"
        >
          {error}
        </p>
      )}

      {job && (
        <>
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

            <div className="progress-section">
              <div className="progress-header">
                <span>Progress</span>
                <strong>
                  {job.progress}%
                </strong>
              </div>

              <div
                className="progress-track"
                role="progressbar"
                aria-valuenow={
                  job.progress
                }
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="progress-fill"
                  style={{
                    width: `${Math.min(
                      Math.max(
                        job.progress,
                        0,
                      ),
                      100,
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div>
              <span>
                Pages visited
              </span>

              <strong>
                {job.pages_visited}
              </strong>
            </div>

            <div>
              <span>
                Records extracted
              </span>

              <strong>
                {
                  job.records_extracted
                }
              </strong>
            </div>

            <div>
              <span>
                Error count
              </span>

              <strong>
                {job.error_count}
              </strong>
            </div>

            <div>
              <span>
                Started
              </span>

              <strong>
                {formatDateTime(
                  job.started_date,
                )}
              </strong>
            </div>

            <div>
              <span>
                Completed
              </span>

              <strong>
                {formatDateTime(
                  job.completed_date,
                )}
              </strong>
            </div>
          </div>

          <section className="recent-logs-card">
            <div className="recent-logs-header">
              <div>
                <h2>
                  Recent Logs
                </h2>

                <p>
                  Latest crawler activity
                  for this job.
                </p>
              </div>
            </div>

            {logs.length === 0 ? (
              <p className="empty-message">
                No logs available for
                this crawl.
              </p>
            ) : (
              <div className="recent-logs-list">
                {logs.map((log) => (
                  <div
                    className="recent-log-item"
                    key={log.id}
                  >
                    <span
                      className={`log-level ${log.log_level.toLowerCase()}`}
                    >
                      {log.log_level}
                    </span>

                    <div className="recent-log-content">
                      <strong>
                        {log.message}
                      </strong>

                      <small>
                        {log.source ??
                          "crawler"}
                        {" · "}
                        {formatDateTime(
                          log.timestamp,
                        )}
                      </small>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}

export default CrawlDetailsPage;