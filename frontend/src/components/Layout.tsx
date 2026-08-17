import { NavLink, Outlet } from "react-router-dom";

function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">OS</span>

          <div>
            <strong>OSINT Crawler</strong>
            <small>Security Intelligence</small>
          </div>
        </div>

        <nav
          className="sidebar-nav"
          aria-label="Main navigation"
        >
          <NavLink to="/" end>
            Dashboard
          </NavLink>

          <NavLink to="/sources">
            Sources
          </NavLink>

          <NavLink to="/crawls/new">
            New Crawl
          </NavLink>
          <NavLink to="/crawls">
            Crawl Jobs
          </NavLink>
          <NavLink to="/advisories">
            Advisories
          </NavLink>
          <NavLink to="/logs">
            Logs
          </NavLink>
        </nav>
      </aside>

      <main className="page-content">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
