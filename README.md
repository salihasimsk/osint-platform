# OSINT Web Crawler Platform

A full-stack OSINT platform for collecting, processing, storing, and viewing publicly available cybersecurity advisories from approved sources.

The system consists of a Python crawler engine, FastAPI REST API, SQLite database, and React/TypeScript web interface. It is designed according to responsible crawling principles and does not target private, leaked, authentication-protected, or restricted content.

## 1. Project Purpose

The project aims to:

- Crawl approved public cybersecurity sources
- Extract structured advisory and vulnerability data
- Store collected records in a database
- Prevent duplicate records
- Track crawl jobs, progress, and logs
- Expose crawler functionality through a REST API
- Provide a web interface for source management, crawling, filtering, monitoring, and analysis

Supported sources:

- Ubuntu Security Notices
- CERT/CC Vulnerability Notes
- CISA Known Exploited Vulnerabilities
- NVD CVE Database
- Red Hat Security Data

## 2. Architecture Overview

The application follows a layered structure:

```text
React Web UI
    |
    | HTTP / JSON
    v
   Nginx
    |
    v
FastAPI REST API
    |
    v
Service Layer
   /        \
  v          v
Crawler    Repository
Engine        |
  |           v
Parsers    SQLite DB
```

The frontend communicates only with the REST API. Backend request processing generally follows:

```text
Route -> Service -> Crawler / Repository -> Database
```

During a crawl:

```text
Source Selection
-> URL Safety Validation
-> robots.txt Check
-> Rate Limiting
-> HTTP Request
-> Source-Specific Parser
-> Duplicate Check
-> Database Storage
-> Progress and Log Update
```

More detailed architecture information is provided in `docs/architecture.md`.

## 3. Technology Choices

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- httpx
- BeautifulSoup
- Pydantic
- Pytest

### Frontend
- React
- TypeScript
- Vite
- React Router
- Recharts
- Vitest
- React Testing Library

### Infrastructure
- Docker
- Docker Compose
- Nginx
- Git / GitHub

## 4. Installation Instructions

Clone the repository:

```bash
git clone <repository-url>
cd osint-web-crawler
```

Docker Compose is the recommended method for local demonstration and testing. The backend and frontend can also be started separately for development.

## 5. Environment Variable Configuration

Backend database connection:

```text
DATABASE_URL=sqlite:////app/data/osint.db
```

Frontend API base path used during the Docker build:

```text
VITE_API_BASE_URL=/api
```

Nginx forwards frontend `/api` requests to the FastAPI backend.

## 6. Docker Setup

From the project root:

```bash
docker compose up --build -d
```

Services:

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000`
- Swagger / OpenAPI: `http://localhost:8000/docs`

Stop the application:

```bash
docker compose down
```

The backend SQLite database path inside the container is `/app/data/osint.db`, bind-mounted to `backend/data/osint.db` on the host. Therefore, the backend and DB Browser can access the same live database file.

## 7. Backend Setup

Without Docker:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend API: `http://localhost:8000`  
Swagger: `http://localhost:8000/docs`

## 8. Frontend Setup

Without Docker:

```bash
cd frontend
npm install
npm run dev
```

Validation commands:

```bash
npm run lint
npm run build
npm test
```

## 9. Database Migration Instructions

The current version does not use Alembic or another dedicated migration tool.

Database tables are created from SQLAlchemy model definitions during application startup using:

```python
Base.metadata.create_all(bind=engine)
```

Main tables:

- `sources`
- `crawl_jobs`
- `advisories`
- `crawl_logs`

The current development database may already contain records collected during previous development and testing crawls.

### Duplicate and Skipped Records

Before inserting an advisory, the system checks whether the same advisory URL already exists.

- New URL -> inserted and counted as `Saved`
- Existing URL -> duplicate row is not inserted and counted as `Skipped`
- Existing records may still be updated with newly parsed information

`Skipped` does not indicate an error.

Example:

```text
Records Extracted: 1670
Saved: 4
Skipped: 1666
```

This means 1670 records were processed, 1666 already existed, and 4 were newly inserted. Repeated crawls can therefore produce high `Skipped` counts when the development database already contains previous results.

Database timestamps are stored in UTC and displayed by the frontend in the user's local timezone.

## 10. How to Start a Crawl

1. Open `http://localhost:8080`
2. Go to **New Crawl**
3. Select one or more enabled sources
4. Configure options such as maximum pages, starting date, or keywords where supported
5. Click **Start Crawl**
6. Monitor the job from **Crawl Jobs** or **Crawl Details**

The interface displays status, progress, pages visited, records extracted, error count, timestamps, and crawl logs. Running crawl jobs can also be stopped from the UI.

## 11. API Endpoint Overview

### Health
`GET /api/health`

### Sources
- `GET /api/sources`
- `POST /api/sources`
- `PUT /api/sources/{source_id}`
- `PATCH /api/sources/{source_id}/status`

### Crawls
- `POST /api/crawls`
- `GET /api/crawls`
- `GET /api/crawls/{job_id}`
- `POST /api/crawls/{job_id}/stop`

### Advisories
- `GET /api/advisories`
- `GET /api/advisories/{advisory_id}`

### Logs and Statistics
- `GET /api/logs`
- `GET /api/statistics/summary`

Detailed API documentation and sample requests/responses are provided in `docs/api.md`.

## 12. Testing Instructions

### Backend

```bash
cd backend
python -m pytest -v
```

Final backend validation: **58 passed**

### Frontend

```bash
cd frontend
npm test
```

Final frontend validation: **9 passed**

Backend tests cover health, source validation, crawl jobs, filtering, pagination, errors, duplicate handling, URL safety, parsers, and integration flow.

Frontend tests cover dashboard rendering, loading states, API errors, crawl form validation, advisory filtering, and crawl progress.

Automated integration testing uses local fixture data instead of repeatedly crawling live websites.

## 13. Security Controls

Implemented controls include:

- URL safety validation
- Blocking private and internal network addresses
- robots.txt validation
- Configurable request delays
- Rate limiting
- HTTP timeout and retry handling
- Input validation
- Duplicate prevention
- Stop functionality
- Approved-source management
- Repeated blocking and access-denied handling

The crawler does not attempt to bypass access restrictions.

## 14. Ethical Safeguards

The application:

- Collects only intentionally public cybersecurity information
- Uses approved public sources
- Respects robots.txt
- Uses conservative request rates
- Avoids unnecessary personal information
- Does not collect credentials
- Does not collect leaked or stolen datasets
- Does not bypass authentication, CAPTCHA, or paywalls
- Does not exploit vulnerabilities
- Does not perform account enumeration

Every source should be reviewed before being enabled.

## 15. Known Limitations

- SQLite is appropriate for the current local internship project but not for high-volume distributed production workloads.
- Background crawling uses FastAPI background processing instead of a distributed task queue such as Celery.
- Parsers may require maintenance if external HTML or API structures change.
- Some sources do not provide every advisory field, such as severity or product.
- Repeated crawls can produce many skipped records because earlier records already exist in the development database.
- Authentication and user-role management are not implemented in the current version.
- Alembic-based migrations are not implemented.
- External source availability, rate limits, or access restrictions can affect live crawl behavior.
- The frontend production build may show a non-blocking bundle-size warning.

## Additional Documentation

Additional deliverables are stored under `docs/`:

- `architecture.md` - detailed architecture and architecture diagram
- `database.md` - database structure and database diagram
- `api.md` - detailed API documentation and sample requests/responses
- `findings-and-limitations.md` - findings and technical limitations
- `screenshots/` - example application screenshots

## Author

Saliha Şimşek  
Computer Engineering Internship Project
