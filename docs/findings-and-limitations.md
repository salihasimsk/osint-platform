# Findings and Limitations Report

## Findings

The OSINT Web Crawler Platform was successfully developed as a modular full-stack application for collecting publicly available cybersecurity advisories from approved sources.

The final system integrates a React/TypeScript web interface, FastAPI REST API, Python crawler engine, SQLAlchemy data-access layer, SQLite database, and Docker-based local deployment.

Five cybersecurity sources are configured:

- Ubuntu Security Notices
- CERT/CC Vulnerability Notes
- CISA Known Exploited Vulnerabilities
- NVD CVE Database
- Red Hat Security Data

The crawler applies responsible crawling controls including robots.txt validation, configurable request delays, rate limiting, timeout handling, retry logic, URL safety checks, and blocking/access-denied handling.

Source-specific parsers convert HTML or JSON data into a common advisory structure. This separation allows different sources to be supported without changing the complete crawler architecture.

The system also implements crawl jobs that run in the background. Users can start a crawl from the web interface, monitor its status and progress, review logs, and stop a running crawl when necessary.

Collected advisory data is stored in SQLite and can be searched, filtered, sorted, paginated, inspected in detail, and exported through the web application.

A key implementation finding was the importance of duplicate handling. Before inserting an advisory, the application checks whether the same advisory URL already exists in the database. New records are counted as `Saved`, while existing records are counted as `Skipped` and are not inserted again. `Skipped` therefore does not represent an error.

For example, a CISA crawl processed 1670 records, where 4 were new and 1666 already existed in the development database. This behavior confirmed that repeated crawls do not create unnecessary duplicate database rows.

The development database is not empty because it contains data collected during earlier implementation and test runs. As a result, repeated crawls can naturally produce high skipped counts.

The database stores timestamps in UTC, while the frontend converts them to the user's local timezone for display.

The final validation process included backend, frontend, integration, lint, build, Docker, database persistence, and live crawl checks. The backend test suite completed with 58 passing tests and the frontend test suite completed with 9 passing tests.

## Limitations

The current implementation is designed primarily as a local internship project rather than a large-scale production system.

SQLite is appropriate for local development and demonstration, but it is not ideal for high-volume or distributed environments. A production deployment would benefit from a database such as PostgreSQL.

Background crawler execution currently uses FastAPI background processing. This is suitable for the current scope, but a distributed job queue such as Celery with Redis would provide better scalability, retry management, and worker isolation in a larger production environment.

Source parsers depend on external HTML and API structures. If a source changes its page structure, field names, endpoint format, or access policy, the related parser may need to be updated.

Not every source provides all advisory fields. For example, severity, product, or summary information may be missing for some records.

Authentication and role-based authorization are not implemented in the current version. The project specification defines authentication as optional for the initial version, but it would be recommended for a multi-user production deployment.

The current project does not use Alembic for database schema migrations. Tables are created from SQLAlchemy model definitions during application startup.

Live crawl behavior also depends on external source availability, robots.txt rules, rate limits, network conditions, and temporary access restrictions.

Finally, the frontend production build may display a non-blocking bundle-size warning. This does not prevent the application from building or running, but code splitting could be considered as a future optimization.

Overall, the project demonstrates the complete end-to-end workflow of a responsible OSINT crawler platform, while leaving clear opportunities for production-oriented improvements in scalability, authentication, database management, and distributed background processing.
