import {
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { startCrawl } from "../api/crawls";
import { getSources } from "../api/sources";
import NewCrawlPage from "./NewCrawlPage";

vi.mock("../api/sources", () => ({
  getSources: vi.fn(),
}));

vi.mock("../api/crawls", () => ({
  startCrawl: vi.fn(),
}));

const mockedGetSources = vi.mocked(getSources);
const mockedStartCrawl = vi.mocked(startCrawl);

describe("NewCrawlPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockedGetSources.mockResolvedValue([
      {
        id: 1,
        name: "Ubuntu Security Notices",
        base_url:
          "https://ubuntu.com/security/notices",
        enabled_status: true,
        request_delay: 2,
        created_date: "2026-08-12T12:05:58",
        updated_date: null,
        last_crawl_date: null,
      },
    ]);

    mockedStartCrawl.mockResolvedValue({
      job_id: "crawl_20260817_010",
      status: "queued",
      progress: 0,
      pages_visited: 0,
      records_extracted: 0,
      error_count: 0,
      started_date: null,
      completed_date: null,
    });
  });

  it("selects a source and starts a crawl", async () => {
    const user = userEvent.setup();

    render(<NewCrawlPage />);

    const sourceCheckbox =
      await screen.findByRole("checkbox", {
        name: /Ubuntu Security Notices/i,
      });

    await user.click(sourceCheckbox);

    await user.click(
      screen.getByRole("button", {
        name: "Start Crawl",
      }),
    );

    await waitFor(() => {
      expect(mockedStartCrawl).toHaveBeenCalledWith({
        source_ids: [1],
        maximum_pages: 1,
      });
    });

    expect(
      await screen.findByText("Crawl created"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /crawl_20260817_010/i,
      ),
    ).toBeInTheDocument();
  });
});
