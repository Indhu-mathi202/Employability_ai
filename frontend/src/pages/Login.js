import React, { useMemo, useState } from "react";

function hashToStudentId(email) {
  const s = String(email || "").trim().toLowerCase();
  if (s === "ravi@example.com") return "STU001";
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  const code = h.toString(36).toUpperCase().padStart(6, "0").slice(0, 6);
  return `STU${code}`;
}

export default function Login({ onLogin }) {
  const [name, setName] = useState("Ravi Kumar");
  const [email, setEmail] = useState("ravi@example.com");
  const [cgpa, setCgpa] = useState("8.1");

  const canSubmit = useMemo(() => name.trim().length >= 2 && email.trim().includes("@"), [name, email]);

  const submit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    const profile = {
      student_id: hashToStudentId(email),
      name: name.trim(),
      email: email.trim(),
      cgpa: Math.max(0, Math.min(10, Number(cgpa) || 0)),
    };
    onLogin(profile);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div className="card" style={{ padding: 18, width: "100%", maxWidth: 520 }}>
        <div className="h1">Student Login</div>
        <p className="sub">Demo mode login (no password).</p>
        <div style={{ height: 12 }} />

        <form onSubmit={submit} className="grid" style={{ gap: 10 }}>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input className="input" value={cgpa} onChange={(e) => setCgpa(e.target.value)} placeholder="CGPA (0-10)" />

          <div className="form" style={{ justifyContent: "space-between" }}>
            <div className="note">After logout, you’ll return here.</div>
            <button className="btn" type="submit" disabled={!canSubmit}>
              Login
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
