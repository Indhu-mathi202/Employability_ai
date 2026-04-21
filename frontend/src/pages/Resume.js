import React, { useState } from "react";
import { api } from "../api/client";

const ROLE_OPTIONS = [
  { value: "", label: "Auto (based on resume)" },
  { value: "software_engineer", label: "Software Engineer" },
  { value: "web_developer", label: "Web Developer" },
  { value: "data_analyst", label: "Data Analyst" },
  { value: "data_scientist", label: "Data Scientist" },
  { value: "devops", label: "DevOps / Cloud" },
  { value: "java_developer", label: "Java Developer" },
];

export default function Resume({ studentId }) {
  const [file, setFile] = useState(null);
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  const upload = async () => {
    if (!file) return;
    setLoading(true);
    setAnalysis(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const roleParam = targetRole ? `&target_role=${encodeURIComponent(targetRole)}` : "";
      const res = await api.post(`/api/resume/analyze?student_id=${encodeURIComponent(studentId)}${roleParam}`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAnalysis(res.data.analysis);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid" style={{ gap: 14 }}>
      <div className="card" style={{ padding: 16 }}>
        <div className="h1">Resume Analyzer</div>
        <p className="sub">Upload a text resume (demo). PDF/DOCX parsing can be added later.</p>
        <div style={{ height: 10 }} />
        <div className="form">
          <select className="input" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}>
            {ROLE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                Target: {o.label}
              </option>
            ))}
          </select>
          <input className="input" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <button className="btn" disabled={!file || loading} onClick={upload}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
        <div style={{ height: 10 }} />
        <div className="note">
          Tip: upload a <code>.txt</code> file for best demo results.
        </div>
      </div>

      {analysis && (
        <div className="card" style={{ padding: 16 }}>
          <div className="h1">Result</div>
          <div className="grid cols-3">
            <div className="card statCard">
              <div className="label">Resume Score</div>
              <div className="val">{analysis.resume_score}/100</div>
            </div>
            <div className="card statCard">
              <div className="label">Words</div>
              <div className="val">{analysis.word_count ?? "-"}</div>
            </div>
            <div className="card statCard">
              <div className="label">Skills Found</div>
              <div className="val">{analysis.total_unique_skills ?? "-"}</div>
            </div>
          </div>
          <div style={{ height: 12 }} />
          <div className="sectionTitle">Recommended Roles</div>
          <div className="chips">
            {(analysis.recommended_roles || []).map((r) => (
              <span key={r.role} className="chip">
                {r.role} ({r.match_percentage}%)
              </span>
            ))}
          </div>
          <div style={{ height: 12 }} />
          <div className="sectionTitle">Skill Gaps</div>
          <div className="chips">
            {(analysis.skill_gaps || []).map((g) => (
              <span key={g} className="chip gap">
                {g}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

