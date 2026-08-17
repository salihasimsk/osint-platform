import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getAdvisory } from "../api/advisories";
import type { Advisory } from "../types";
import { formatDateTime } from "../utils/date";

function AdvisoryDetailsPage() {
  const { advisoryId } =
    useParams<{ advisoryId: string }>();

  const numericAdvisoryId = Number(advisoryId);

  const isAdvisoryIdValid =
    Number.isInteger(numericAdvisoryId) &&
    numericAdvisoryId > 0;

  const [advisory, setAdvisory] =
    useState<Advisory | null>(null);

  const [isLoading, setIsLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    if (!isAdvisoryIdValid) {
      return;
    }

    let isActive = true;

    getAdvisory(numericAdvisoryId)
      .then((data) => {
        if (isActive) {
          setAdvisory(data);
          setError(null);
        }
      })
      .catch((requestError: unknown) => {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load the advisory.");
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
  }, [numericAdvisoryId, isAdvisoryIdValid]);

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Advisory Details</h1>

          <p>
            {advisory?.cve ?? `ID: ${advisoryId}`}
          </p>
        </div>
      </header>

      {!isAdvisoryIdValid && (
        <p className="error-message" role="alert">
          Invalid advisory ID.
        </p>
      )}

      {isAdvisoryIdValid && isLoading && (
        <p>Loading advisory...</p>
      )}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {advisory && (
        <article className="advisory-details">
          <div className="advisory-title-row">
            <div>
              <span className="eyebrow">
                {advisory.organization}
              </span>

              <h2>{advisory.title}</h2>
            </div>

            <span
              className={`severity-badge ${
                advisory.severity ?? "unknown"
              }`}
            >
              {advisory.severity ?? "unknown"}
            </span>
          </div>

          <dl className="metadata-grid">
            <div>
              <dt>CVE</dt>
              <dd>{advisory.cve ?? "—"}</dd>
            </div>

            <div>
              <dt>Product</dt>
              <dd>{advisory.product ?? "—"}</dd>
            </div>

            <div>
              <dt>Source domain</dt>
              <dd>{advisory.source_domain}</dd>
            </div>

            <div>
              <dt>Published</dt>
              <dd>
                {formatDateTime(
                  advisory.publication_date,
                )}
              </dd>
            </div>

            <div>
              <dt>Collected</dt>
              <dd>
                {formatDateTime(
                  advisory.collection_date,
                )}
              </dd>
            </div>

            <div>
              <dt>Crawl job</dt>
              <dd>{advisory.crawl_job_id ?? "—"}</dd>
            </div>
          </dl>

          <section className="summary-section">
            <h3>Summary</h3>

            <p>
              {advisory.summary ??
                "No summary is available."}
            </p>
          </section>

          <a
            className="primary-button external-link"
            href={advisory.url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open original advisory
          </a>
        </article>
      )}
    </section>
  );
}

export default AdvisoryDetailsPage;
