import {
  render,
  screen,
} from "@testing-library/react";
import {
  MemoryRouter,
  Route,
  Routes,
} from "react-router-dom";
import {
  describe,
  expect,
  it,
} from "vitest";

import Layout from "./Layout";

describe("Layout", () => {
  it("renders navigation links and page content", () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<Layout />}>
            <Route
              index
              element={<p>Dashboard content</p>}
            />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(
      screen.getByText("OSINT Crawler"),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "Dashboard",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "Sources",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Dashboard content"),
    ).toBeInTheDocument();
  });
});
