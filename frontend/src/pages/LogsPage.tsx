import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { getLogs } from "../api/logs";
import type { CrawlLog } from "../types";
import { formatDateTime } from "../utils/date";

function LogsPage() {
  const [logs, setLogs] = useState<CrawlLog[]>([]);
  const [level, setLevel] = useState("");
  const [keyword, setKeyword] = useState("");

  const [isLoading, setIsLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    async function loadLogs() {
      try {
        const data = await getLogs();

        if (isActive) {
          const sortedLogs = [...data].sort(
            (firstLog, secondLog) =>
              secondLog.id - firstLog.id,
          );

          setLogs(sortedLogs);
          setError(null);
        }
      } catch (requestError: unknown) {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load logs.");
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    loadLogs();

    const intervalId = window.setInterval(
      loadLogs,
      5000,
    );

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const filteredLogs = useMemo(() => {
    const normalizedKeyword =
      keyword.trim().toLowerCase();

    return logs.filter((log) => {
      const matchesLevel =
        !level ||
        log.log_level.toLowerCase() ===
          level.toLowerCase();

      const matchesKeyword =
        !normalizedKeyword ||
        log.message
          .toLowerCase()
          .includes(normalizedKeyword) ||
        (log.source ?? "")
          .toLowerCase()
          .includes(normalizedKeyword);

      return matchesLevel && matchesKeyword;
    });
  }, [logs, level, keyword]);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Logs</h1>
          <p>
            Review crawler activity and operational
            messages.
          </p>
        </div>
      </header>

      <div className="filter-bar log-filters">
        <label>
          <span>Search</span>

          <input
            type="search"
            value={keyword}
            placeholder="Message or source"
            onChange={(event) => {
              setKeyword(event.target.value);
            }}
          />
        </label>

        <label>
          <span>Log level</span>

          <select
            value={level}
            onChange={(event) => {
              setLevel(event.target.value);
            }}
          >
            <option value="">All levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
        </label>
      </div>

      {isLoading && <p>Loading logs...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!isLoading &&
        !error &&
        filteredLogs.length === 0 && (
          <p>No logs were found.</p>
        )}

      {!error && filteredLogs.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th scope="col">Timestamp</th>
                <th scope="col">Level</th>
                <th scope="col">Source</th>
                <th scope="col">Crawl job</th>
                <th scope="col">Message</th>
              </tr>
            </thead>

            <tbody>
              {filteredLogs.map((log) => (
                <tr key={log.id}>
                  <td>
                    {formatDateTime(log.timestamp)}
                  </td>

                  <td>
                    <span
                      className={`log-level ${log.log_level.toLowerCase()}`}
                    >
                      {log.log_level}
                    </span>
                  </td>

                  <td>{log.source ?? "—"}</td>
                  <td>{log.crawl_job_id}</td>
                  <td>{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default LogsPage;
