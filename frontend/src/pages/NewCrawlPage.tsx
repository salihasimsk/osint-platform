import {
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { startCrawl } from "../api/crawls";
import { getSources } from "../api/sources";
import type { CrawlJob, Source } from "../types";

function NewCrawlPage() {
  const [sources, setSources] = useState<Source[]>([]);

  const [selectedSourceIds, setSelectedSourceIds] =
    useState<number[]>([]);

  const [maximumPages, setMaximumPages] =
    useState(1);

  const [dateFrom, setDateFrom] =
    useState("");

  const [keywords, setKeywords] =
    useState("");

  const [createdJob, setCreatedJob] =
    useState<CrawlJob | null>(null);

  const [isLoadingSources, setIsLoadingSources] =
    useState(true);

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    getSources()
      .then((data) => {
        setSources(
          data.filter(
            (source) => source.enabled_status,
          ),
        );
      })
      .catch((requestError: unknown) => {
        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError(
            "Could not load sources.",
          );
        }
      })
      .finally(() => {
        setIsLoadingSources(false);
      });
  }, []);

  function toggleSource(
    sourceId: number,
  ) {
    setSelectedSourceIds((currentIds) => {
      if (currentIds.includes(sourceId)) {
        return currentIds.filter(
          (id) => id !== sourceId,
        );
      }

      return [
        ...currentIds,
        sourceId,
      ];
    });
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);
    setCreatedJob(null);

    if (selectedSourceIds.length === 0) {
      setError(
        "Select at least one source.",
      );
      return;
    }

    if (
      maximumPages < 1 ||
      maximumPages > 100
    ) {
      setError(
        "Maximum pages must be between 1 and 100.",
      );
      return;
    }

    const keywordList = keywords
      .split(",")
      .map((keyword) => keyword.trim())
      .filter((keyword) => keyword.length > 0);

    setIsSubmitting(true);

    try {
      const job = await startCrawl({
        source_ids: selectedSourceIds,
        maximum_pages: maximumPages,
        date_from:
          dateFrom || null,
        keywords:
          keywordList.length > 0
            ? keywordList
            : null,
      });

      setCreatedJob(job);
    } catch (requestError: unknown) {
      if (requestError instanceof Error) {
        setError(requestError.message);
      } else {
        setError(
          "Could not start the crawl.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>New Crawl</h1>

          <p>
            Select approved sources and
            configure the crawl.
          </p>
        </div>
      </header>

      <form
        className="crawl-form"
        onSubmit={handleSubmit}
      >
        <fieldset
          disabled={isSubmitting}
        >
          <legend>
            Sources
          </legend>

          {isLoadingSources && (
            <p>
              Loading sources...
            </p>
          )}

          {!isLoadingSources &&
            sources.map((source) => (
              <label
                className="source-option"
                key={source.id}
              >
                <input
                  type="checkbox"
                  checked={
                    selectedSourceIds.includes(
                      source.id,
                    )
                  }
                  onChange={() =>
                    toggleSource(source.id)
                  }
                />

                <span>
                  <strong>
                    {source.name}
                  </strong>

                  <small>
                    Request delay:{" "}
                    {source.request_delay}
                    {" seconds"}
                  </small>
                </span>
              </label>
            ))}
        </fieldset>

        <label className="form-field">
          <span>
            Starting date
          </span>

          <input
            type="date"
            value={dateFrom}
            onChange={(event) => {
              setDateFrom(
                event.target.value,
              );
            }}
            disabled={isSubmitting}
          />
        </label>

        <label className="form-field">
          <span>
            Keywords
          </span>

          <input
            type="text"
            value={keywords}
            placeholder="critical, kernel, remote code execution"
            onChange={(event) => {
              setKeywords(
                event.target.value,
              );
            }}
            disabled={isSubmitting}
          />

          <small>
            Separate multiple keywords
            with commas.
          </small>
        </label>

        <label className="form-field">
          <span>
            Maximum pages per source
          </span>

          <input
            type="number"
            min="1"
            max="100"
            value={maximumPages}
            onChange={(event) => {
              setMaximumPages(
                Number(
                  event.target.value,
                ),
              );
            }}
            disabled={isSubmitting}
          />
        </label>

        {error && (
          <p
            className="error-message"
            role="alert"
          >
            {error}
          </p>
        )}

        <button
          className="primary-button"
          type="submit"
          disabled={
            isSubmitting ||
            isLoadingSources ||
            selectedSourceIds.length === 0
          }
        >
          {isSubmitting
            ? "Starting..."
            : "Start Crawl"}
        </button>
      </form>

      {createdJob && (
        <section className="success-message">
          <h2>
            Crawl created
          </h2>

          <p>
            Job ID: {createdJob.job_id}
          </p>

          <p>
            Status: {createdJob.status}
          </p>
        </section>
      )}
    </section>
  );
}

export default NewCrawlPage;