import React, { useEffect, useMemo, useState } from "react";
import "./styles/app.css";
import Layout from "./components/Layout";
import { navigate, useRoute } from "./router";
import { api } from "./api/client";
import Dashboard from "./pages/Dashboard";
import MyTests from "./pages/MyTests";
import Scorecard from "./pages/Scorecard";
import Resume from "./pages/Resume";
import VideoInterview from "./pages/VideoInterview";
import TestRunner from "./pages/TestRunner";
import Login from "./pages/Login";

const DEMO_STUDENT = { student_id: "STU001", name: "Ravi Kumar", email: "ravi@example.com", cgpa: 8.1 };

function parseTestId(path) {
  const m = path.match(/^\/test\/([^/]+)(?:\/([^/]+))?$/);
  if (!m) return null;
  return { testId: decodeURIComponent(m[1]), variant: m[2] ? decodeURIComponent(m[2]) : null };
}

export default function App() {
  const { path } = useRoute();
  const [authed, setAuthed] = useState(() => localStorage.getItem("demo_authed") === "1");
  const [student, setStudent] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("demo_student") || "null") || DEMO_STUDENT;
    } catch {
      return DEMO_STUDENT;
    }
  });

  useEffect(() => {
    localStorage.setItem("demo_student", JSON.stringify(student));
    if (authed) api.post("/api/student/upsert", student).catch(() => {});
  }, [student, authed]);

  useEffect(() => {
    if (!authed && path !== "/login") navigate("/login");
  }, [authed, path]);

  const onLogin = (profile) => {
    setStudent(profile);
    localStorage.setItem("demo_authed", "1");
    setAuthed(true);
    localStorage.removeItem("demo_role");
    navigate("/");
  };

  const testRoute = useMemo(() => parseTestId(path), [path]);

  const onLogout = () => {
    localStorage.removeItem("demo_student");
    localStorage.removeItem("demo_authed");
    localStorage.removeItem("demo_role");
    setAuthed(false);
    setStudent(DEMO_STUDENT);
    navigate("/login");
  };

  if (!authed) {
    return <Login onLogin={onLogin} />;
  }

  const content = (() => {
    if (testRoute) return <TestRunner studentId={student.student_id} testId={testRoute.testId} variant={testRoute.variant} />;
    if (path === "/" || path === "/dashboard") return <Dashboard studentId={student.student_id} />;
    if (path === "/my-tests") return <MyTests studentId={student.student_id} />;
    if (path === "/scorecard") return <Scorecard studentId={student.student_id} />;
    if (path === "/resume") return <Resume studentId={student.student_id} />;
    if (path === "/video-interview") return <VideoInterview studentId={student.student_id} />;
    return (
      <div className="card" style={{ padding: 16 }}>
        <div className="h1">Not Found</div>
        <p className="sub">Page does not exist.</p>
      </div>
    );
  })();

  return (
    <Layout routePath={path} student={student} onLogout={onLogout}>
      {content}
    </Layout>
  );
}
