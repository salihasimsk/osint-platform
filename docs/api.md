# API Documentation

## 1. Overview

The OSINT Web Crawler Platform exposes its backend functionality through a FastAPI REST API.

The frontend communicates with the backend only through these API endpoints. FastAPI also provides interactive OpenAPI documentation through Swagger.

Base URL:

```text
http://localhost:8000
```

API prefix:

```text
/api
```

Swagger / OpenAPI:

```text
http://localhost:8000/docs
```

## 2. Health

### GET `/api/health`

Checks whether the backend service is available.

Example request:

```http
GET /api/health
```

Example response:

```json
{
  "status": "healthy"
}
```

The exact health response may include additional service information depending on the current implementation.

---

## 3. Sources

Sources represent approved public cybersecurity data providers that can be used by the crawler.

### GET `/api/sources`

Returns the configured sources.

Example request:

```http
GET /api/sources
```

Typical source fields include:

```json
{
  "id": 1,
  "name": "Ubuntu Security Notices",
  "base_url": "https://ubuntu.com/security/notices",
  "enabled_status": true,
  "request_delay": 3,
  "last_crawl_date": "2026-08-18T21:14:47"
}
```

### POST `/api/sources`

Adds a new source configuration.

Example request:

```json
{
  "name": "Example Security Advisories",
  "base_url": "https://example.com/security",
  "enabled_status": true,
  "request_delay": 2
}
```

The source URL is validated before it can be used by the crawler.

### PUT `/api/sources/{source_id}`

Updates an existing source.

Example:

```http
PUT /api/sources/1
```

Example request:

```json
{
  "name": "Ubuntu Security Notices",
  "base_url": "https://ubuntu.com/security/notices",
  "enabled_status": true,
  "request_delay": 3
}
```

### PATCH `/api/sources/{source_id}/status`

Enables or disables a configured source.

Example:

```http
PATCH /api/sources/1/status
```

---

## 4. Crawl Jobs

Crawl jobs allow the frontend to start, monitor, and stop crawler executions without blocking the original REST API request.

### POST `/api/crawls`

Starts a new crawl job.

Example request:

```json
{
  "source_ids": [1, 3, 4],
  "maximum_pages": 1,
  "date_from": "2026-08-01",
  "keywords": ["critical", "remote code execution"]
}
```

`date_from` and `keywords` are optional and are applied where supported by the selected source.

Example response:

```json
{
  "job_id": "crawl_20260819_001",
  "status": "queued"
}
```

The API returns the job information before the complete crawl has finished. The crawler continues as a background task.

### GET `/api/crawls`

Returns crawl jobs.

Example request:

```http
GET /api/crawls
```

Typical fields include:

```json
{
  "job_id": "crawl_20260819_003",
  "status": "completed",
  "progress": 100,
  "pages_visited": 1,
  "records_extracted": 1670,
  "error_count": 0,
  "started_date": "2026-08-19T06:26:10",
  "completed_date": "2026-08-19T06:26:14"
}
```

### GET `/api/crawls/{job_id}`

Returns details for a specific crawl job.

Example:

```http
GET /api/crawls/crawl_20260819_003
```

The frontend uses this endpoint to monitor progress and crawl status.

Typical statuses are:

```text
queued
running
completed
failed
stopping
stopped
```

### POST `/api/crawls/{job_id}/stop`

Requests that a running crawl be stopped.

Example:

```http
POST /api/crawls/crawl_20260819_003/stop
```

The crawler checks the job state during execution and stops further processing when appropriate.

---

## 5. Advisories

Advisories contain the structured cybersecurity information collected by the crawler.

### GET `/api/advisories`

Returns advisory records.

Example:

```http
GET /api/advisories
```

Supported query parameters include:

- `page`
- `page_size`
- `keyword`
- `organization`
- `severity`
- `source_domain`
- `date_from`
- `date_to`
- `sort_by`
- `sort_order`

Example filtered request:

```http
GET /api/advisories?severity=critical&page=1&page_size=25
```

Example source and date filtering:

```http
GET /api/advisories?source_domain=cisa.gov&date_from=2026-08-01&sort_by=collection_date&sort_order=desc
```

Typical advisory response fields include:

```json
{
  "id": 1865,
  "title": "Example Security Vulnerability",
  "organization": "CISA",
  "publication_date": "2026-08-18",
  "url": "https://example.com/advisory",
  "source_domain": "cisa.gov",
  "cve": "CVE-2026-00001",
  "product": "Example Product",
  "severity": "high",
  "summary": "Example advisory summary.",
  "collection_date": "2026-08-19T06:26:13",
  "crawl_job_id": 64
}
```

### GET `/api/advisories/{advisory_id}`

Returns one advisory record.

Example:

```http
GET /api/advisories/1865
```

This endpoint is used by the Advisory Details page.

---

## 6. Logs

### GET `/api/logs`

Returns crawler log records.

Logs are used to show the execution history of crawl jobs.

Typical log information includes:

```json
{
  "crawl_job_id": 64,
  "log_level": "info",
  "message": "Crawl completed. Pages: 1, Saved: 4, Skipped: 1666",
  "source": "CISA Known Exploited Vulnerabilities",
  "timestamp": "2026-08-19T06:26:14"
}
```

Logs can be used to understand:

- When a crawl started
- Which source was processed
- Whether the crawl completed
- How many records were saved
- How many records were skipped
- Whether an error occurred

---

## 7. Statistics

### GET `/api/statistics/summary`

Returns summary information used by the Dashboard.

Example request:

```http
GET /api/statistics/summary
```

Typical information includes:

```json
{
  "total_advisories": 1865,
  "critical": 12,
  "high": 140,
  "medium": 420,
  "low": 90,
  "active_sources": 5,
  "completed_crawls": 50
}
```

Values above are illustrative; actual values depend on the current database contents.

---

## 8. Filtering and Pagination

The advisory API supports filtering and pagination so the frontend does not need to load the entire advisory table at once.

Example:

```http
GET /api/advisories?page=2&page_size=25&organization=CISA&severity=high
```

Sorting can also be requested:

```http
GET /api/advisories?sort_by=publication_date&sort_order=desc
```

This allows the frontend to perform server-side search, filtering, sorting, and pagination through the REST API.

---

## 9. Duplicate Handling

Duplicate handling is part of crawl processing rather than a separate API endpoint.

When the crawler extracts an advisory:

```text
Parsed Advisory
      |
      v
Check advisory URL
   /          \
New          Existing
 |              |
Save          Update
 |              |
Saved++       Skipped++
```

A skipped record is not an error. It means the advisory was successfully found but an advisory with the same URL already existed in the database.

Example crawl log:

```text
Crawl completed. Pages: 1, Saved: 4, Skipped: 1666
```

This behavior prevents repeated crawls from creating duplicate database rows.

---

## 10. Validation and Error Handling

FastAPI and Pydantic are used to validate request data.

The API uses HTTP status codes to distinguish successful and unsuccessful operations.

Typical categories include:

```text
200 - Successful request
201 - Resource created
400 - Invalid request
404 - Resource not found
422 - Request validation error
500 - Internal server error
```

Invalid URLs or unsafe source configurations are rejected by backend validation.

The API does not intentionally expose internal stack traces to frontend users.

---

## 11. Background Job Behavior

A crawl request does not wait for all source processing to complete.

Instead:

```text
POST /api/crawls
       |
       v
Create Crawl Job
       |
       v
Return Job ID
       |
       v
Background Execution
       |
       v
Frontend polls crawl status
```

This prevents long-running crawler operations from blocking normal API communication.

---

## 12. Swagger / OpenAPI

FastAPI automatically publishes interactive API documentation.

Open:

```text
http://localhost:8000/docs
```

Swagger can be used to:

- View available endpoints
- Inspect request parameters
- Inspect schemas
- Send test requests
- View returned status codes and response bodies

For the final demonstration, Swagger provides a direct view of the REST API independently from the React frontend.

---

## 13. Sample End-to-End Request

### Step 1 - Start a crawl

```http
POST /api/crawls
Content-Type: application/json
```

```json
{
  "source_ids": [1],
  "maximum_pages": 1,
  "date_from": null,
  "keywords": null
}
```

Possible response:

```json
{
  "job_id": "crawl_20260819_004",
  "status": "queued"
}
```

### Step 2 - Monitor the crawl

```http
GET /api/crawls/crawl_20260819_004
```

Possible completed response:

```json
{
  "job_id": "crawl_20260819_004",
  "status": "completed",
  "progress": 100,
  "pages_visited": 1,
  "records_extracted": 10,
  "error_count": 0
}
```

### Step 3 - Retrieve advisories

```http
GET /api/advisories?page=1&page_size=10
```

The frontend performs the same REST-based workflow when a user starts and monitors a crawl through the web interface.
