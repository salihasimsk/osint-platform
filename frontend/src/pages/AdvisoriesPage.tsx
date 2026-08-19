import {
  useEffect,
  useState,
  type SyntheticEvent,
} from "react";
import { Link } from "react-router-dom";

import {
  getAdvisories,
  getAdvisoriesCsvUrl,
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
  const [sourceDomain, setSourceDomain] = useState("");

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [sortBy, setSortBy] =
    useState("publication_date");

  const [sortOrder, setSortOrder] =
    useState<"asc" | "desc">("desc");

  const [appliedFilters, setAppliedFilters] =
    useState<AdvisoryFilters>({});

  useEffect(() => {
    let isActive = true;

    getAdvisories({
      ...appliedFilters,
      page,
      page_size: PAGE_SIZE,
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

    setError(null);
    setPage(1);

    if (dateFrom && dateTo && dateFrom > dateTo) {
      setError(
        "Date from cannot be later than Date to.",
      );
      return;
    }

    setIsLoading(true);

    setAppliedFilters({
      keyword: keyword.trim(),
      organization,
      severity,
      source_domain: sourceDomain,
      date_from: dateFrom,
      date_to: dateTo,
      sort_by: sortBy,
      sort_order: sortOrder,
    });
  }

  function clearFilters() {
    setIsLoading(true);
    setError(null);

    setKeyword("");
    setOrganization("");
    setSeverity("");
    setSourceDomain("");

    setDateFrom("");
    setDateTo("");

    setSortBy("publication_date");
    setSortOrder("desc");

    setPage(1);
    setAppliedFilters({});
  }

  function exportCsv() {
    window.location.href =
      getAdvisoriesCsvUrl(appliedFilters);
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
            <option value="">
              All organizations
            </option>

            <option value="Ubuntu">
              Ubuntu
            </option>

            <option value="CERT/CC">
              CERT/CC
            </option>

            <option value="CISA">
              CISA
            </option>

            <option value="NVD">
              NVD
            </option>

            <option value="Red Hat">
              Red Hat
            </option>
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
            <option value="">
              All severities
            </option>

            <option value="critical">
              Critical
            </option>

            <option value="high">
              High
            </option>

            <option value="medium">
              Medium
            </option>

            <option value="moderate">
              Moderate
            </option>

            <option value="low">
              Low
            </option>
          </select>
        </label>

        <label>
          <span>Source</span>

          <select
            value={sourceDomain}
            onChange={(event) => {
              setSourceDomain(event.target.value);
            }}
          >
            <option value="">
              All sources
            </option>

            <option value="ubuntu.com">
              Ubuntu
            </option>

            <option value="kb.cert.org">
              CERT/CC
            </option>

            <option value="cisa.gov">
              CISA
            </option>

            <option value="nvd.nist.gov">
              NVD
            </option>

            <option value="access.redhat.com">
              Red Hat
            </option>
          </select>
        </label>

        <label>
          <span>Date from</span>

          <input
            type="date"
            value={dateFrom}
            onChange={(event) => {
              setDateFrom(event.target.value);
            }}
          />
        </label>

        <label>
          <span>Date to</span>

          <input
            type="date"
            value={dateTo}
            onChange={(event) => {
              setDateTo(event.target.value);
            }}
          />
        </label>

        <label>
          <span>Sort by</span>

          <select
            value={sortBy}
            onChange={(event) => {
              setSortBy(event.target.value);
            }}
          >
            <option value="publication_date">
              Publication date
            </option>

            <option value="collection_date">
              Collection date
            </option>

            <option value="title">
              Title
            </option>

            <option value="organization">
              Organization
            </option>

            <option value="severity">
              Severity
            </option>
          </select>
        </label>

        <label>
          <span>Sort order</span>

          <select
            value={sortOrder}
            onChange={(event) => {
              setSortOrder(
                event.target.value as
                  | "asc"
                  | "desc",
              );
            }}
          >
            <option value="desc">
              Descending
            </option>

            <option value="asc">
              Ascending
            </option>
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

        <button
          className="secondary-button"
          type="button"
          onClick={exportCsv}
        >
          Export CSV
        </button>
      </form>

      {isLoading && (
        <p>Loading advisories...</p>
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
        advisories.length === 0 && (
          <p>No advisories were found.</p>
        )}

      {!error && advisories.length > 0 && (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th scope="col">
                    Title
                  </th>

                  <th scope="col">
                    Organization
                  </th>

                  <th scope="col">
                    Severity
                  </th>

                  <th scope="col">
                    CVE
                  </th>

                  <th scope="col">
                    Product
                  </th>

                  <th scope="col">
                    Published
                  </th>

                  <th scope="col">
                    Collected
                  </th>
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

                    <td>
                      {advisory.organization}
                    </td>

                    <td>
                      <span
                        className={`severity-badge ${
                          advisory.severity ??
                          "unknown"
                        }`}
                      >
                        {advisory.severity ??
                          "unknown"}
                      </span>
                    </td>

                    <td>
                      {advisory.cve ?? "—"}
                    </td>

                    <td>
                      {advisory.product ?? "—"}
                    </td>

                    <td>
                      {formatDateTime(
                        advisory.publication_date,
                      )}
                    </td>

                    <td>
                      {formatDateTime(
                        advisory.collection_date,
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
              disabled={
                page === 1 || isLoading
              }
              onClick={() => {
                setPage((currentPage) =>
                  Math.max(
                    1,
                    currentPage - 1,
                  ),
                );
              }}
            >
              Previous
            </button>

            <span>
              Page {page}
            </span>

            <button
              type="button"
              disabled={
                isLoading ||
                advisories.length < PAGE_SIZE
              }
              onClick={() => {
                setPage(
                  (currentPage) =>
                    currentPage + 1,
                );
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