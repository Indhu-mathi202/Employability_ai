import React from "react";
import { Link } from "../router";

function isActive(path, to) {
  if (to === "/") return path === "/";
  return path === to || path.startsWith(to + "/");
}

export default function Layout({ routePath, student, onLogout, children }) {
  return (
    <>
      <div className="nav">
        <div className="inner">
          <div className="brand">
            AI<span>Employ</span>
          </div>

          <div className="navlinks">
            <Link to="/" className={isActive(routePath, "/") ? "active" : ""}>
              Dashboard
            </Link>
            <Link to="/my-tests" className={isActive(routePath, "/my-tests") ? "active" : ""}>
              My Tests
            </Link>
            <Link to="/scorecard" className={isActive(routePath, "/scorecard") ? "active" : ""}>
              Scorecard
            </Link>
            <Link to="/resume" className={isActive(routePath, "/resume") ? "active" : ""}>
              Resume
            </Link>
            <Link to="/video-interview" className={isActive(routePath, "/video-interview") ? "active" : ""}>
              Video Interview
            </Link>
          </div>

          <div className="navright">
            <div className="navuser">{student?.name || "Student"}</div>
            <button className="btn secondary" onClick={onLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="container">{children}</div>
    </>
  );
}
