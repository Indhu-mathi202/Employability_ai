import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { navigate } from "../router";

const TECH_VARIANTS = [
  { value: "python", label: "Python / General" },
  { value: "web", label: "Web Developer" },
  { value: "data", label: "Data Analyst" },
  { value: "java", label: "Java Developer" },
  { value: "devops", label: "DevOps / Cloud" },
];

export default function MyTests({ studentId }) {
  const [tests, setTests] = useState([]);
  const [history, setHistory] = useState([]);
  const [techVariant, setTechVariant] = useState("python");

  useEffect(() => {
    api.get("/api/tests").then((res) => setTests(res.data.tests || [])).catch(() => {});
    api.get(`/api/tests/history/${studentId}`).then((res) => setHistory(res.data.history || [])).catch(() => {});
  }, [studentId]);

  return (
    <div>
      <div className="sectionTitle">Available Tests</div>
      <div className="grid cols-3">
        {tests.map((t) => (
          <div key={t.id} className="card testCard">
            <div className="top">
              <div className="tag">{t.type}</div>
              <div className="pill">
                {t.questions} questions • {t.marks} marks
              </div>
            </div>
            <div className="name">{t.name}</div>
            <div className="sub">{t.description}</div>
            <div className="meta">
              <span />
              <span />
            </div>
            <div className="cta">
              {t.id === "technical" && (
                <select className="input" value={techVariant} onChange={(e) => setTechVariant(e.target.value)} style={{ marginBottom: 10 }}>
                  {TECH_VARIANTS.map((v) => (
                    <option key={v.value} value={v.value}>
                      Target: {v.label}
                    </option>
                  ))}
                </select>
              )}
              <button
                className="btn"
                onClick={() => navigate(t.id === "technical" ? `/test/technical/${encodeURIComponent(techVariant)}` : `/test/${t.id}`)}
              >
                Start Test
              </button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ height: 18 }} />
      <div className="sectionTitle">My Test History</div>
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <table>
          <thead>
            <tr>
              <th>Test</th>
              <th>Type</th>
              <th>Score</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 && (
              <tr>
                <td colSpan={5} style={{ color: "#64748b" }}>
                  No attempts yet.
                </td>
              </tr>
            )}
            {history.map((h, idx) => (
              <tr key={idx}>
                <td>{h.test_name}</td>
                <td style={{ color: "#64748b" }}>{h.type}</td>
                <td style={{ fontWeight: 900 }}>{h.score}/100</td>
                <td>
                  <span className={`status ${h.status === "Passed" ? "pass" : "warn"}`}>{h.status}</span>
                </td>
                <td style={{ color: "#64748b" }}>{h.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
