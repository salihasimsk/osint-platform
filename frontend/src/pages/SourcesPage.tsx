import { useEffect, useState } from "react";

import { getSources } from "../api/sources";
import type { Source } from "../types";

function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    getSources()
      .then((data) => {
        if (isActive) {
          setSources(data);
        }
      })
      .catch((requestError: unknown) => {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load sources.");
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
          <h1>Sources</h1>
          <p>
            Approved public cybersecurity data sources.
          </p>
        </div>
      </header>

      {isLoading && <p>Loading sources...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!isLoading && !error && sources.length === 0 && (
        <p>No sources have been configured.</p>
      )}

      {sources.length > 0 && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Status</th>
                <th scope="col">Request delay</th>
                <th scope="col">Base URL</th>
              </tr>
            </thead>

            <tbody>
              {sources.map((source) => (
                <tr key={source.id}>
                  <td>{source.name}</td>

                  <td>
                    <span
                      className={
                        source.enabled_status
                          ? "status-badge active"
                          : "status-badge disabled"
                      }
                    >
                      {source.enabled_status
                        ? "Active"
                        : "Disabled"}
                    </span>
                  </td>

                  <td>{source.request_delay} seconds</td>

                  <td>
                    <a
                      href={source.base_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {source.base_url}
                    </a>
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

export default SourcesPage;
