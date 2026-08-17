import {
  useEffect,
  useState,
  type SyntheticEvent,
} from "react";
import { Link } from "react-router-dom";

import {
  getAdvisories,
  type AdvisoryFilters,
} from "../api/advisories";
import type { Advisory } from "../types";
import { formatDateTime } from "../utils/date";

const PAGE_SIZE = 25;

function AdvisoriesPage() {
  const [advisories, setAdvisories] =
    useState<Advisory[]>([]);

  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [keyword, setKeyword] = useState("");
  const [organization, setOrganization] = useState("");
  const [severity, setSeverity] = useState("");

  const [appliedFilters, setAppliedFilters] =
    useState<AdvisoryFilters>({});

  useEffect(() => {
    let isActive = true;

    getAdvisories({
      ...appliedFilters,
      page,
      page_size: PAGE_SIZE,
      sort_by: "publication_date",
      sort_order: "desc",
    })
      .then((data) => {
        if (isActive) {
          setAdvisories(data);
        }
      })
      .catch((requestError: unknown) => {
        if (!isActive) {
          return;
        }

        if (requestError instanceof Error) {
          setError(requestError.message);
        } else {
          setError("Could not load advisories.");
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
  }, [page, appliedFilters]);

  function handleFilterSubmit(
    event: SyntheticEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setIsLoading(true);
    setError(null);
    setPage(1);

    setAppliedFilters({
      keyword: keyword.trim(),
      organization,
      severity,
    });
  }

  function clearFilters() {
    setIsLoading(true);
    setError(null);
    setKeyword("");
    setOrganization("");
    setSeverity("");
    setPage(1);
    setAppliedFilters({});
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <h1>Advisories</h1>

          <p>
            Browse collected public cybersecurity
            advisories.
          </p>
        </div>
      </header>

      <form
        className="filter-bar"
        onSubmit={handleFilterSubmit}
      >
        <label>
          <span>Search</span>

          <input
            type="search"
            value={keyword}
            placeholder="Title, CVE or summary"
            onChange={(event) => {
              setKeyword(event.target.value);
            }}
          />
        </label>

        <label>
          <span>Organization</span>

          <select
            value={organization}
            onChange={(event) => {
              setOrganization(event.target.value);
            }}
          >
            <option value="">All organizations</option>
            <option value="Ubuntu">Ubuntu</option>
            <option value="CERT/CC">CERT/CC</option>
            <option value="CISA">CISA</option>
            <option value="NVD">NVD</option>
            <option value="Red Hat">Red Hat</option>
          </select>
        </label>

        <label>
          <span>Severity</span>

          <select
            value={severity}
            onChange={(event) => {
              setSeverity(event.target.value);
            }}
          >
            <option value="">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="moderate">Moderate</option>
            <option value="low">Low</option>
          </select>
        </label>

        <button
          className="primary-button"
          type="submit"
        >
          Apply Filters
        </button>

        <button
          className="secondary-button"
          type="button"
          onClick={clearFilters}
        >
          Clear
        </button>
      </form>

      {isLoading && <p>Loading advisories...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!isLoading &&
        !error &&
        advisories.length === 0 && (
          <p>No advisories were found.</p>
        )}

      {!error && advisories.length > 0 && (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th scope="col">Title</th>
                  <th scope="col">Organization</th>
                  <th scope="col">Severity</th>
                  <th scope="col">CVE</th>
                  <th scope="col">Product</th>
                  <th scope="col">Published</th>
                </tr>
              </thead>

              <tbody>
                {advisories.map((advisory) => (
                  <tr key={advisory.id}>
                    <td>
                      <Link
                        className="job-link"
                        to={`/advisories/${advisory.id}`}
                      >
                        {advisory.title}
                      </Link>
                    </td>

                    <td>{advisory.organization}</td>

                    <td>
                      <span
                        className={`severity-badge ${
                          advisory.severity ?? "unknown"
                        }`}
                      >
                        {advisory.severity ?? "unknown"}
                      </span>
                    </td>

                    <td>{advisory.cve ?? "—"}</td>
                    <td>{advisory.product ?? "—"}</td>

                    <td>
                      {formatDateTime(
                        advisory.publication_date,
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              type="button"
              disabled={page === 1 || isLoading}
              onClick={() => {
                setPage((currentPage) =>
                  Math.max(1, currentPage - 1),
                );
              }}
            >
              Previous
            </button>

            <span>Page {page}</span>

            <button
              type="button"
              disabled={
                isLoading ||
                advisories.length < PAGE_SIZE
              }
              onClick={() => {
                setPage((currentPage) => currentPage + 1);
              }}
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  );
}

export default AdvisoriesPage;
