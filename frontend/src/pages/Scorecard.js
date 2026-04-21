import React, { useEffect, useMemo, useState } from "react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import { api } from "../api/client";

function toRadarData(breakdown) {
  const labels = [
    ["technical", "Technical"],
    ["cognitive", "Cognitive"],
    ["resume", "Resume NLP"],
    ["video_ai", "Video AI"],
    ["behavioral", "Behavioral"],
  ];
  return labels.map(([k, label]) => ({ subject: label, score: Number(breakdown?.[k] || 0) }));
}

export default function Scorecard({ studentId }) {
  const [data, setData] = useState(null);

  const fetchIt = () => api.get(`/api/scorecard/${studentId}`).then((res) => setData(res.data));

  useEffect(() => {
    fetchIt().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [studentId]);

  const sc = data?.scorecard;
  const breakdown = sc?.score_breakdown;
  const radar = useMemo(() => toRadarData(breakdown), [breakdown]);
  const bars = useMemo(
    () => [
      { name: "Technical", value: Number(breakdown?.technical || 0) },
      { name: "Cognitive", value: Number(breakdown?.cognitive || 0) },
      { name: "NLP/Resume", value: Number(breakdown?.resume || 0) },
      { name: "Video AI", value: Number(breakdown?.video_ai || 0) },
      { name: "Behavioral", value: Number(breakdown?.behavioral || 0) },
    ],
    [breakdown]
  );

  return (
    <div className="grid" style={{ gap: 14 }}>
      <div className="scoreHero">
        <div className="row">
          <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
            <div className="ring">
              <div style={{ textAlign: "center" }}>
                {sc ? Math.round(sc.employability_score) : "—"}
                <small>/100</small>
              </div>
            </div>

            <div>
              <div style={{ fontWeight: 900, fontSize: 16 }}>{data?.student?.name || "Student"}</div>
              <div className="sub" style={{ color: "#cbd5e1" }}>
                Complete your assessments to see your prediction.
              </div>
              <div style={{ height: 8 }} />
              <div className="sectionTitle" style={{ margin: 0, color: "#94a3b8" }}>
                Top Matching Roles
              </div>
              <div className="chips">
                {(sc?.top_roles || []).map((r) => (
                  <span key={r} className="chip">
                    {r}
                  </span>
                ))}
              </div>
              <div style={{ height: 8 }} />
              <div className="sectionTitle" style={{ margin: 0, color: "#94a3b8" }}>
                Skill Gaps
              </div>
              <div className="chips">
                {(sc?.skill_gaps || []).map((g) => (
                  <span key={g} className="chip gap">
                    {g}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ fontWeight: 900, fontSize: 12, color: "#94a3b8" }}>PLACEMENT PROBABILITY</div>
            <div style={{ fontWeight: 900, fontSize: 34, color: "#fbbf24" }}>{sc ? `${sc.placement_probability}%` : "—"}</div>
            <button className="btn" onClick={fetchIt}>
              Recompute
            </button>
          </div>
        </div>
      </div>

      <div className="grid cols-3">
        {[
          ["TECHNICAL", breakdown?.technical, sc?.weights?.technical],
          ["COGNITIVE", breakdown?.cognitive, sc?.weights?.cognitive],
          ["NLP/RESUME", breakdown?.resume, sc?.weights?.resume],
          ["VIDEO AI", breakdown?.video_ai, sc?.weights?.video_ai],
          ["BEHAVIORAL", breakdown?.behavioral, sc?.weights?.behavioral],
        ].map(([label, val, wt]) => (
          <div key={label} className="card statCard">
            <div className="label">
              {label} <span style={{ fontWeight: 700 }}>• Weight {wt || 0}%</span>
            </div>
            <div className="val">{val != null ? Math.round(Number(val)) : "—"}</div>
          </div>
        ))}
      </div>

      <div className="grid cols-2">
        <div className="card" style={{ padding: 14 }}>
          <div className="sectionTitle">Skill Radar</div>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <RadarChart data={radar}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <Radar name="Score" dataKey="score" stroke="#0f6b4a" fill="#0f6b4a" fillOpacity={0.25} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card" style={{ padding: 14 }}>
          <div className="sectionTitle">Score Breakdown</div>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={bars}>
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="value" fill="#0f6b4a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

