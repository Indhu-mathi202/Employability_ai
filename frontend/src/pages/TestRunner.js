import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { navigate } from "../router";

function Likert({ value, onChange }) {
  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <label key={n} className="pill" style={{ cursor: "pointer" }}>
          <input
            type="radio"
            checked={Number(value) === n}
            onChange={() => onChange(n)}
            style={{ marginRight: 6 }}
          />
          {n}
        </label>
      ))}
    </div>
  );
}

export default function TestRunner({ studentId, testId, variant }) {
  const [loading, setLoading] = useState(true);
  const [format, setFormat] = useState("mcq");
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [variantLabel, setVariantLabel] = useState(null);

  useEffect(() => {
    setLoading(true);
    setSubmitted(null);
    setAnswers({});
    setError(null);
    setVariantLabel(null);
    api
      .get(`/api/tests/${testId}/questions${variant ? `?variant=${encodeURIComponent(variant)}` : ""}`)
      .then((res) => {
        setFormat(res.data.format);
        setQuestions(res.data.questions || []);
        setVariantLabel(res.data.variant_label || null);
      })
      .finally(() => setLoading(false));
  }, [testId, variant]);

  const canSubmit = useMemo(() => Object.keys(answers).length > 0, [answers]);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.post("/api/tests/submit", {
        student_id: studentId,
        test_id: testId,
        responses: answers,
        variant,
      });
      setSubmitted(res.data);
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Submit failed. Please try again.";
      setError(String(msg));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="card" style={{ padding: 16 }}>Loading…</div>;

  if (submitted) {
    return (
      <div className="card" style={{ padding: 16 }}>
        <div className="h1">Result</div>
        <p className="sub">
          Score: <b>{submitted.score}</b>/100
        </p>
        <div style={{ height: 10 }} />
        <button className="btn" onClick={() => navigate("/my-tests")}>
          Back to My Tests
        </button>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: 16 }}>
      <div className="h1">
        {testId.toUpperCase()} Test{variantLabel ? ` — ${variantLabel}` : ""}
      </div>
      <p className="sub">Answer all questions and submit.</p>
      <div style={{ height: 10 }} />

      {error && (
        <>
          <div className="card" style={{ padding: 12, borderColor: "#fecaca", background: "#fff1f2" }}>
            <div style={{ fontWeight: 900, color: "#be123c" }}>Error</div>
            <div className="sub" style={{ color: "#9f1239" }}>{error}</div>
          </div>
          <div style={{ height: 10 }} />
        </>
      )}

      <div className="grid">
        {questions.map((q, idx) => (
          <div key={q.id} className="card" style={{ padding: 14 }}>
            <div style={{ fontWeight: 900, marginBottom: 8 }}>
              {idx + 1}. {q.text || q.question}
            </div>

            {format === "mcq" && (
              <div className="grid" style={{ gap: 8 }}>
                {(q.options || []).map((opt, i) => (
                  <label key={i} className="pill" style={{ cursor: "pointer", justifyContent: "flex-start" }}>
                    <input
                      type="radio"
                      checked={String(answers[q.id]) === String(i)}
                      onChange={() => setAnswers((a) => ({ ...a, [q.id]: i }))}
                      style={{ marginRight: 8 }}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            )}

            {format === "likert" && (
              <Likert value={answers[q.id]} onChange={(n) => setAnswers((a) => ({ ...a, [q.id]: n }))} />
            )}
          </div>
        ))}
      </div>

      <div style={{ height: 12 }} />
      <div className="form">
        <button className="btn secondary" onClick={() => navigate("/my-tests")}>
          Cancel
        </button>
        <button className="btn" disabled={!canSubmit || submitting} onClick={submit}>
          {submitting ? "Submitting…" : "Submit"}
        </button>
      </div>
    </div>
  );
}
