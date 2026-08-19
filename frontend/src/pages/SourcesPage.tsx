import {
  useEffect,
  useState,
} from "react";

import {
  createSource,
  getSources,
  getSourceRobotsStatus,
  updateSource,
  updateSourceStatus,
} from "../api/sources";

import type {
  Source,
  SourceCreateRequest,
} from "../types";

import {
  formatDateTime,
} from "../utils/date";


type RobotsStatuses = Record<
  number,
  boolean | null
>;


const EMPTY_SOURCE_FORM: SourceCreateRequest = {
  name: "",
  base_url: "",
  enabled_status: false,
  request_delay: 2,
};


function SourcesPage() {
  const [sources, setSources] =
    useState<Source[]>([]);

  const [
    robotsStatuses,
    setRobotsStatuses,
  ] = useState<RobotsStatuses>({});

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [
    savingSourceId,
    setSavingSourceId,
  ] = useState<number | null>(null);

  const [
    isAddSourceOpen,
    setIsAddSourceOpen,
  ] = useState(false);

  const [
    isCreatingSource,
    setIsCreatingSource,
  ] = useState(false);

  const [
    newSource,
    setNewSource,
  ] = useState<SourceCreateRequest>(
    EMPTY_SOURCE_FORM,
  );


  useEffect(() => {
    let isActive = true;

    async function loadSources() {
      try {
        setIsLoading(true);
        setError(null);

        const data = await getSources();

        if (!isActive) {
          return;
        }

        setSources(data);

        const initialStatuses:
          RobotsStatuses = {};

        data.forEach((source) => {
          initialStatuses[source.id] =
            null;
        });

        setRobotsStatuses(
          initialStatuses,
        );

        const results =
          await Promise.allSettled(
            data.map(
              async (source) => {
                const robotsStatus =
                  await getSourceRobotsStatus(
                    source.id,
                  );

                return {
                  sourceId: source.id,
                  allowed:
                    robotsStatus.allowed,
                };
              },
            ),
          );

        if (!isActive) {
          return;
        }

        setRobotsStatuses(
          (current) => {
            const updated = {
              ...current,
            };

            results.forEach(
              (result) => {
                if (
                  result.status ===
                  "fulfilled"
                ) {
                  updated[
                    result.value.sourceId
                  ] =
                    result.value.allowed;
                }
              },
            );

            return updated;
          },
        );
      } catch (
        requestError: unknown
      ) {
        if (!isActive) {
          return;
        }

        if (
          requestError instanceof Error
        ) {
          setError(
            requestError.message,
          );
        } else {
          setError(
            "Could not load sources.",
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void loadSources();

    return () => {
      isActive = false;
    };
  }, []);


  async function loadRobotsStatus(
    sourceId: number,
  ) {
    try {
      const status =
        await getSourceRobotsStatus(
          sourceId,
        );

      setRobotsStatuses(
        (current) => ({
          ...current,
          [sourceId]:
            status.allowed,
        }),
      );
    } catch {
      setRobotsStatuses(
        (current) => ({
          ...current,
          [sourceId]: null,
        }),
      );
    }
  }


  async function handleCreateSource(
    event:
      React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const name =
      newSource.name.trim();

    const baseUrl =
      newSource.base_url.trim();

    if (!name) {
      setError(
        "Source name is required.",
      );
      return;
    }

    if (!baseUrl) {
      setError(
        "Base URL is required.",
      );
      return;
    }

    if (
      !baseUrl.startsWith(
        "http://",
      ) &&
      !baseUrl.startsWith(
        "https://",
      )
    ) {
      setError(
        "Base URL must start with http:// or https://.",
      );
      return;
    }

    if (
      newSource.request_delay < 1
    ) {
      setError(
        "Request delay must be at least 1 second.",
      );
      return;
    }

    try {
      setIsCreatingSource(true);
      setError(null);

      const createdSource =
        await createSource({
          ...newSource,
          name,
          base_url: baseUrl,
        });

      setSources(
        (currentSources) => [
          ...currentSources,
          createdSource,
        ],
      );

      setRobotsStatuses(
        (current) => ({
          ...current,
          [createdSource.id]: null,
        }),
      );

      setNewSource(
        EMPTY_SOURCE_FORM,
      );

      setIsAddSourceOpen(false);

      await loadRobotsStatus(
        createdSource.id,
      );
    } catch (
      requestError: unknown
    ) {
      if (
        requestError instanceof Error
      ) {
        setError(
          requestError.message,
        );
      } else {
        setError(
          "Could not create source.",
        );
      }
    } finally {
      setIsCreatingSource(false);
    }
  }


  async function handleStatusChange(
    source: Source,
  ) {
    try {
      setError(null);

      const updatedSource =
        await updateSourceStatus(
          source.id,
          !source.enabled_status,
        );

      setSources(
        (currentSources) =>
          currentSources.map(
            (currentSource) =>
              currentSource.id ===
              updatedSource.id
                ? updatedSource
                : currentSource,
          ),
      );
    } catch (
      requestError: unknown
    ) {
      if (
        requestError instanceof Error
      ) {
        setError(
          requestError.message,
        );
      } else {
        setError(
          "Could not update source status.",
        );
      }
    }
  }


  function handleDelayChange(
    sourceId: number,
    value: number,
  ) {
    setSources(
      (currentSources) =>
        currentSources.map(
          (source) =>
            source.id === sourceId
              ? {
                  ...source,
                  request_delay:
                    value,
                }
              : source,
        ),
    );
  }


  async function handleSave(
    source: Source,
  ) {
    if (
      source.request_delay < 1
    ) {
      setError(
        "Request delay must be at least 1 second.",
      );
      return;
    }

    try {
      setSavingSourceId(
        source.id,
      );

      setError(null);

      const updatedSource =
        await updateSource(
          source.id,
          {
            name: source.name,
            base_url:
              source.base_url,
            enabled_status:
              source.enabled_status,
            request_delay:
              source.request_delay,
          },
        );

      setSources(
        (currentSources) =>
          currentSources.map(
            (currentSource) =>
              currentSource.id ===
              updatedSource.id
                ? updatedSource
                : currentSource,
          ),
      );
    } catch (
      requestError: unknown
    ) {
      if (
        requestError instanceof Error
      ) {
        setError(
          requestError.message,
        );
      } else {
        setError(
          "Could not update source.",
        );
      }
    } finally {
      setSavingSourceId(null);
    }
  }


  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Sources</h1>

          <p>
            Manage approved public
            cybersecurity sources and
            crawl settings.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setIsAddSourceOpen(
              (current) =>
                !current,
            );

            setError(null);
          }}
        >
          {isAddSourceOpen
            ? "Cancel"
            : "+ Add Source"}
        </button>
      </header>


      {isAddSourceOpen && (
        <form
          className="add-source-card"
          onSubmit={
            handleCreateSource
          }
        >
          <div className="add-source-header">
            <div>
              <h2>
                Add Source
              </h2>

              <p>
                Add an approved source
                supported by the current
                crawler parsers.
              </p>
            </div>
          </div>

          <div className="add-source-grid">
            <label className="form-field">
              <span>
                Source name
              </span>

              <input
                type="text"
                value={
                  newSource.name
                }
                placeholder="Ubuntu Security Notices"
                disabled={
                  isCreatingSource
                }
                onChange={(
                  event,
                ) => {
                  setNewSource(
                    (current) => ({
                      ...current,
                      name:
                        event.target
                          .value,
                    }),
                  );
                }}
              />
            </label>


            <label className="form-field">
              <span>
                Base URL
              </span>

              <input
                type="url"
                value={
                  newSource.base_url
                }
                placeholder="https://ubuntu.com/security/notices"
                disabled={
                  isCreatingSource
                }
                onChange={(
                  event,
                ) => {
                  setNewSource(
                    (current) => ({
                      ...current,
                      base_url:
                        event.target
                          .value,
                    }),
                  );
                }}
              />
            </label>


            <label className="form-field">
              <span>
                Request delay
                (seconds)
              </span>

              <input
                type="number"
                min="1"
                max="60"
                value={
                  newSource.request_delay
                }
                disabled={
                  isCreatingSource
                }
                onChange={(
                  event,
                ) => {
                  setNewSource(
                    (current) => ({
                      ...current,
                      request_delay:
                        Number(
                          event.target
                            .value,
                        ),
                    }),
                  );
                }}
              />
            </label>


            <label className="source-checkbox">
              <input
                type="checkbox"
                checked={
                  newSource.enabled_status
                }
                disabled={
                  isCreatingSource
                }
                onChange={(
                  event,
                ) => {
                  setNewSource(
                    (current) => ({
                      ...current,
                      enabled_status:
                        event.target
                          .checked,
                    }),
                  );
                }}
              />

              <span>
                Enable source
                immediately
              </span>
            </label>
          </div>


          <div className="add-source-help">
            Supported sources:
            Ubuntu, CERT/CC,
            CISA KEV, NVD and
            Red Hat.
          </div>


          <div className="add-source-actions">
            <button
              type="button"
              className="secondary-button"
              disabled={
                isCreatingSource
              }
              onClick={() => {
                setNewSource(
                  EMPTY_SOURCE_FORM,
                );

                setIsAddSourceOpen(
                  false,
                );

                setError(null);
              }}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={
                isCreatingSource
              }
            >
              {isCreatingSource
                ? "Adding..."
                : "Add Source"}
            </button>
          </div>
        </form>
      )}


      {isLoading && (
        <p>
          Loading sources...
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


      {!isLoading &&
        !error &&
        sources.length === 0 && (
          <p>
            No sources were found.
          </p>
        )}


      {sources.length > 0 && (
        <div className="table-container sources-table-container">
          <table className="sources-table">
            <thead>
              <tr>
                <th scope="col">
                  Name
                </th>

                <th scope="col">
                  Status
                </th>

                <th scope="col">
                  Request Delay
                </th>

                <th scope="col">
                  Base URL
                </th>

                <th scope="col">
                  Last Crawl
                </th>

                <th scope="col">
                  Robots
                </th>

                <th scope="col">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody>
              {sources.map(
                (source) => {
                  const robotsStatus =
                    robotsStatuses[
                      source.id
                    ];

                  return (
                    <tr
                      key={
                        source.id
                      }
                    >
                      <td>
                        {
                          source.name
                        }
                      </td>

                      <td>
                        <button
                          type="button"
                          className={
                            source
                              .enabled_status
                              ? "status-badge completed"
                              : "status-badge stopped"
                          }
                          onClick={() => {
                            void handleStatusChange(
                              source,
                            );
                          }}
                        >
                          {source
                            .enabled_status
                            ? "Enabled"
                            : "Disabled"}
                        </button>
                      </td>

                      <td>
                        <input
                          type="number"
                          min="1"
                          max="60"
                          value={
                            source
                              .request_delay
                          }
                          onChange={(
                            event,
                          ) => {
                            handleDelayChange(
                              source.id,
                              Number(
                                event
                                  .target
                                  .value,
                              ),
                            );
                          }}
                        />
                      </td>

                      <td>
                        <a
                          href={
                            source.base_url
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          {
                            source.base_url
                          }
                        </a>
                      </td>

                      <td>
                        {source
                          .last_crawl_date
                          ? formatDateTime(
                              source
                                .last_crawl_date,
                            )
                          : "Never"}
                      </td>

                      <td>
                        {robotsStatus ===
                          undefined ||
                        robotsStatus ===
                          null ? (
                          <span>
                            Checking...
                          </span>
                        ) : robotsStatus ? (
                          <span>
                            Allowed
                          </span>
                        ) : (
                          <span>
                            Blocked
                          </span>
                        )}
                      </td>

                      <td>
                        <button
                          type="button"
                          className="secondary-button"
                          disabled={
                            savingSourceId ===
                            source.id
                          }
                          onClick={() => {
                            void handleSave(
                              source,
                            );
                          }}
                        >
                          {savingSourceId ===
                          source.id
                            ? "Saving..."
                            : "Save"}
                        </button>
                      </td>
                    </tr>
                  );
                },
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}


export default SourcesPage;