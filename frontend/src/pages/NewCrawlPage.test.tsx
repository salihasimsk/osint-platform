import {
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
import { MemoryRouter } from "react-router-dom";

import NewCrawlPage from "./NewCrawlPage";

import * as crawlsApi from "../api/crawls";
import * as sourcesApi from "../api/sources";


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


describe(
  "NewCrawlPage",
  () => {
    it(
      "selects a source and starts a crawl",
      async () => {
        const user =
          userEvent.setup();

        vi.spyOn(
          sourcesApi,
          "getSources",
        ).mockResolvedValue([
          testSource,
        ]);

        const mockedStartCrawl =
          vi.spyOn(
            crawlsApi,
            "startCrawl",
          ).mockResolvedValue({
            job_id:
              "crawl_20260817_010",
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

        const checkbox =
          await screen.findByRole(
            "checkbox",
          );

        await user.click(
          checkbox,
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
            mockedStartCrawl,
          ).toHaveBeenCalledWith({
            source_ids: [1],
            maximum_pages: 1,
            date_from: null,
            keywords: null,
          });
        });

        expect(
          await screen.findByText(
            "Crawl created",
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            /crawl_20260817_010/i,
          ),
        ).toBeInTheDocument();

        expect(
          screen.getByText(
            /Status: queued/i,
          ),
        ).toBeInTheDocument();
      },
    );
  },
);