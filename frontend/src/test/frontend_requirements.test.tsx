import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import userEvent from "@testing-library/user-event";

import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";

import DashboardPage from "../pages/DashboardPage";
import NewCrawlPage from "../pages/NewCrawlPage";
import AdvisoriesPage from "../pages/AdvisoriesPage";
import CrawlDetailsPage from "../pages/CrawlDetailsPage";

import * as healthApi from "../api/health";
import * as statisticsApi from "../api/statistics";
import * as advisoriesApi from "../api/advisories";
import * as crawlsApi from "../api/crawls";
import * as sourcesApi from "../api/sources";
import * as logsApi from "../api/logs";


vi.mock("../components/SeverityChart", () => ({
  default: () => <div>Severity Chart</div>,
}));

vi.mock("../components/OrganizationChart", () => ({
  default: () => <div>Organization Chart</div>,
}));


const testSource = {
  id: 1,
  name: "Ubuntu Security Notices",
  base_url:
    "https://ubuntu.com/security/notices",
  enabled_status: true,
  request_delay: 2,
  created_date: "2026-08-01T10:00:00",
  updated_date: null,
  last_crawl_date: null,
};


const testAdvisory = {
  id: 1,
  title: "Kernel Security Update",
  organization: "Ubuntu",
  publication_date:
    "2026-08-18T10:00:00",
  url:
    "https://ubuntu.com/security/notices/USN-9999-1",
  source_domain: "ubuntu.com",
  cve: "CVE-2026-9999",
  product: "Linux Kernel",
  severity: "high" as const,
  summary: "Kernel vulnerability.",
  crawl_job_id: 1,
  collection_date:
    "2026-08-18T11:00:00",
};


const runningJob = {
  job_id: "crawl_20260818_001",
  status: "running" as const,
  progress: 45,
  pages_visited: 4,
  records_extracted: 12,
  error_count: 1,
  started_date:
    "2026-08-18T10:00:00",
  completed_date: null,
};


beforeEach(() => {
  vi.restoreAllMocks();
});


describe(
  "Frontend requirement tests",
  () => {
    it(
      "renders the dashboard",
      async () => {
        vi.spyOn(
          healthApi,
          "getHealth",
        ).mockResolvedValue({
          status: "healthy",
          database: "connected",
          crawler: "available",
        });

        vi.spyOn(
          statisticsApi,
          "getStatisticsSummary",
        ).mockResolvedValue({
          total_advisories: 25,
          critical: 2,
          high: 8,
          medium: 10,
          low: 5,
          active_sources: 5,
          completed_crawls: 7,
          unknown_severity: 0,
          by_organization: {
            Ubuntu: 10,
            NVD: 15,
          },
        });

        vi.spyOn(
          advisoriesApi,
          "getAdvisories",
        ).mockResolvedValue([
          testAdvisory,
        ]);

        vi.spyOn(
          crawlsApi,
          "getCrawlJobs",
        ).mockResolvedValue([
          runningJob,
        ]);

        render(
          <MemoryRouter>
            <DashboardPage />
          </MemoryRouter>,
        );

        expect(
          screen.getByRole(
            "heading",
            {
              name: "Dashboard",
            },
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Loading dashboard...",
          ),
        ).toBeInTheDocument();

        expect(
          await screen.findByText(
            "Total advisories",
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText("25"),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "API: healthy",
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Kernel Security Update",
          ),
        ).toBeInTheDocument();
      },
    );


    it(
      "shows loading state",
      async () => {
        let resolveHealth:
          | ((
              value: {
                status: string;
                database: string;
                crawler: string;
              },
            ) => void)
          | undefined;

        vi.spyOn(
          healthApi,
          "getHealth",
        ).mockImplementation(
          () =>
            new Promise((resolve) => {
              resolveHealth = resolve;
            }),
        );

        vi.spyOn(
          statisticsApi,
          "getStatisticsSummary",
        ).mockResolvedValue({
          total_advisories: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          active_sources: 0,
          completed_crawls: 0,
          unknown_severity: 0,
          by_organization: {},
        });

        vi.spyOn(
          advisoriesApi,
          "getAdvisories",
        ).mockResolvedValue([]);

        vi.spyOn(
          crawlsApi,
          "getCrawlJobs",
        ).mockResolvedValue([]);

        render(
          <MemoryRouter>
            <DashboardPage />
          </MemoryRouter>,
        );

        expect(
          screen.getByText(
            "Loading dashboard...",
          ),
        ).toBeInTheDocument();

        resolveHealth?.({
          status: "healthy",
          database: "connected",
          crawler: "available",
        });

        await waitFor(() => {
          expect(
            screen.queryByText(
              "Loading dashboard...",
            ),
          ).not.toBeInTheDocument();
        });
      },
    );


    it(
      "handles API errors",
      async () => {
        vi.spyOn(
          healthApi,
          "getHealth",
        ).mockRejectedValue(
          new Error(
            "Dashboard API failed",
          ),
        );

        vi.spyOn(
          statisticsApi,
          "getStatisticsSummary",
        ).mockResolvedValue({
          total_advisories: 0,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          active_sources: 0,
          completed_crawls: 0,
          unknown_severity: 0,
          by_organization: {},
        });

        vi.spyOn(
          advisoriesApi,
          "getAdvisories",
        ).mockResolvedValue([]);

        vi.spyOn(
          crawlsApi,
          "getCrawlJobs",
        ).mockResolvedValue([]);

        render(
          <MemoryRouter>
            <DashboardPage />
          </MemoryRouter>,
        );

        expect(
          await screen.findByRole(
            "alert",
          ),
        ).toHaveTextContent(
          "Dashboard API failed",
        );
      },
    );


    it(
      "validates the crawl form",
      async () => {
        const user =
          userEvent.setup();

        vi.spyOn(
          sourcesApi,
          "getSources",
        ).mockResolvedValue([
          testSource,
        ]);

        const startCrawlSpy =
          vi.spyOn(
            crawlsApi,
            "startCrawl",
          ).mockResolvedValue({
            job_id:
              "crawl_20260818_100",
            status: "queued",
            progress: 0,
            pages_visited: 0,
            records_extracted: 0,
            error_count: 0,
            started_date: null,
            completed_date: null,
          });

        render(
          <MemoryRouter>
            <NewCrawlPage />
          </MemoryRouter>,
        );

        await user.click(
          await screen.findByRole(
            "checkbox",
          ),
        );

        const maximumPagesInput =
          screen.getByRole(
            "spinbutton",
          );

        await user.clear(
          maximumPagesInput,
        );

        await user.type(
          maximumPagesInput,
          "101",
        );

        expect(
          maximumPagesInput,
        ).toBeInvalid();

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Start Crawl",
            },
          ),
        );

        expect(
          startCrawlSpy,
        ).not.toHaveBeenCalled();
      },
    );


    it(
      "submits crawl keywords and starting date",
      async () => {
        const user =
          userEvent.setup();

        vi.spyOn(
          sourcesApi,
          "getSources",
        ).mockResolvedValue([
          testSource,
        ]);

        const startCrawlSpy =
          vi.spyOn(
            crawlsApi,
            "startCrawl",
          ).mockResolvedValue({
            job_id:
              "crawl_20260818_101",
            status: "queued",
            progress: 0,
            pages_visited: 0,
            records_extracted: 0,
            error_count: 0,
            started_date: null,
            completed_date: null,
          });

        render(
          <MemoryRouter>
            <NewCrawlPage />
          </MemoryRouter>,
        );

        await user.click(
          await screen.findByRole(
            "checkbox",
          ),
        );

        const dateInput =
          screen.getByLabelText(
            /Starting date/i,
          );

        await user.type(
          dateInput,
          "2026-08-01",
        );

        const keywordInput =
          screen.getByPlaceholderText(
            "critical, kernel, remote code execution",
          );

        await user.type(
          keywordInput,
          "kernel, CVE",
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name: "Start Crawl",
            },
          ),
        );

        await waitFor(() => {
          expect(
            startCrawlSpy,
          ).toHaveBeenCalledWith({
            source_ids: [1],
            maximum_pages: 1,
            date_from:
              "2026-08-01",
            keywords: [
              "kernel",
              "CVE",
            ],
          });
        });
      },
    );


    it(
      "applies advisory table filters",
      async () => {
        const user =
          userEvent.setup();

        const getAdvisoriesSpy =
          vi.spyOn(
            advisoriesApi,
            "getAdvisories",
          );

        getAdvisoriesSpy
          .mockResolvedValueOnce([
            testAdvisory,
          ])
          .mockResolvedValueOnce([
            testAdvisory,
          ]);

        render(
          <MemoryRouter>
            <AdvisoriesPage />
          </MemoryRouter>,
        );

        await screen.findByText(
          "Kernel Security Update",
        );

        await user.type(
          screen.getByLabelText(
            "Search",
          ),
          "kernel",
        );

        await user.selectOptions(
          screen.getByLabelText(
            "Organization",
          ),
          "Ubuntu",
        );

        await user.selectOptions(
          screen.getByLabelText(
            "Severity",
          ),
          "high",
        );

        await user.click(
          screen.getByRole(
            "button",
            {
              name:
                "Apply Filters",
            },
          ),
        );

        await waitFor(() => {
          expect(
            getAdvisoriesSpy,
          ).toHaveBeenLastCalledWith(
            expect.objectContaining({
              keyword: "kernel",
              organization:
                "Ubuntu",
              severity: "high",
              page: 1,
              page_size: 25,
            }),
          );
        });
      },
    );


    it(
      "displays crawl progress",
      async () => {
        vi.spyOn(
          crawlsApi,
          "getCrawlJob",
        ).mockResolvedValue(
          runningJob,
        );

        vi.spyOn(
          logsApi,
          "getCrawlLogs",
        ).mockResolvedValue([
          {
            id: 1,
            crawl_job_id: 1,
            log_level: "info",
            message:
              "Crawl started",
            source: "Ubuntu",
            timestamp:
              "2026-08-18T10:00:00",
          },
        ]);

        render(
          <MemoryRouter
            initialEntries={[
              "/crawls/crawl_20260818_001",
            ]}
          >
            <Routes>
              <Route
                path="/crawls/:jobId"
                element={
                  <CrawlDetailsPage />
                }
              />
            </Routes>
          </MemoryRouter>,
        );

        const progressBar =
          await screen.findByRole(
            "progressbar",
          );

        expect(
          progressBar,
        ).toHaveAttribute(
          "aria-valuenow",
          "45",
        );

        expect(
          screen.getByText(
            "45%",
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            "Crawl started",
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByRole(
            "button",
            {
              name: "Stop Crawl",
            },
          ),
        ).toBeInTheDocument();
      },
    );
  },
);