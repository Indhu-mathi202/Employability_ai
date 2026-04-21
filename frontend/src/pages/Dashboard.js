import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { Link } from "../router";

export default function Dashboard({ studentId }) {
  const [scorecard, setScorecard] = useState(null);

  useEffect(() => {
    let active = true;
    api
      .get(`/api/scorecard/${studentId}`)
      .then((res) => {
        if (!active) return;
        setScorecard(res.data);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [studentId]);

  const sc = scorecard?.scorecard;

  return (
    <div className="grid cols-2">
      <div className="card" style={{ padding: 16 }}>
        <div className="h1">Dashboard</div>
        <p className="sub">Complete tests, analyze resume, and practice interviews.</p>
        <div style={{ height: 12 }} />
        <div className="grid cols-2">
          <div className="card statCard">
            <div className="label">Employability Score</div>
            <div className="val">{sc ? `${sc.employability_score}/100` : "—"}</div>
          </div>
          <div className="card statCard">
            <div className="label">Placement Probability</div>
            <div className="val">{sc ? `${sc.placement_probability}%` : "—"}</div>
          </div>
        </div>
        <div style={{ height: 12 }} />
        <div className="form">
          <Link className="btn" to="/my-tests">
            Start Tests
          </Link>
          <Link className="btn secondary" to="/scorecard">
            View Scorecard
          </Link>
        </div>
        <div style={{ height: 10 }} />
        <div className="note">
          Demo mode: scores are saved locally in <code>data/demo_store.json</code>.
        </div>
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div className="h1">What to do next</div>
        <div style={{ height: 8 }} />
        <div className="grid">
          <div className="card" style={{ padding: 14, borderRadius: 14 }}>
            <div style={{ fontWeight: 900 }}>1) Complete assessments</div>
            <div className="sub">Technical, cognitive, communication, and behavioural.</div>
          </div>
          <div className="card" style={{ padding: 14, borderRadius: 14 }}>
            <div style={{ fontWeight: 900 }}>2) Upload resume</div>
            <div className="sub">Get role suggestions and skill gaps.</div>
          </div>
          <div className="card" style={{ padding: 14, borderRadius: 14 }}>
            <div style={{ fontWeight: 900 }}>3) Video interview</div>
            <div className="sub">Practice questions + eye-contact demo score.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

