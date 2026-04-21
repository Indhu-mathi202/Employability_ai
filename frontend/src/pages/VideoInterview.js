import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api/client";

function clamp01(x) {
  const n = Number(x);
  if (Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

export default function VideoInterview({ studentId }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [questions, setQuestions] = useState([]);
  const [step, setStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [startTs, setStartTs] = useState(null);
  const [elapsed, setElapsed] = useState(0);
  const [faceSupported, setFaceSupported] = useState(false);
  const [frames, setFrames] = useState({ total: 0, good: 0 });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(null);
  const [ttsSupported, setTtsSupported] = useState(false);
  const [speakEnabled, setSpeakEnabled] = useState(true);
  const [voices, setVoices] = useState([]);
  const [voiceUri, setVoiceUri] = useState("");
  const [autoNext, setAutoNext] = useState(true);
  const [answerSeconds, setAnswerSeconds] = useState(30);

  useEffect(() => {
    setFaceSupported(Boolean(window.FaceDetector));
    setTtsSupported(Boolean(window.speechSynthesis && window.SpeechSynthesisUtterance));
  }, []);

  useEffect(() => {
    api
      .post("/api/interview/start", { student_id: studentId, count: 5 })
      .then((res) => setQuestions(res.data.questions || []))
      .catch(() =>
        setQuestions([
          "Tell me about yourself in 60 seconds.",
          "Walk me through one project you are proud of.",
          "Why should we hire you?",
          "Tell me about a challenge you faced and how you solved it.",
          "Where do you see yourself in 2 years?",
        ])
      );
  }, [studentId]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setElapsed(Math.round((Date.now() - startTs) / 1000));
    }, 250);
    return () => clearInterval(id);
  }, [running, startTs]);

  const eyeRatio = useMemo(() => {
    if (!frames.total) return 0;
    return frames.good / frames.total;
  }, [frames]);

  // Load TTS voices
  useEffect(() => {
    if (!ttsSupported) return;
    const synth = window.speechSynthesis;
    const load = () => {
      const vs = synth.getVoices ? synth.getVoices() : [];
      if (vs && vs.length) {
        setVoices(vs);
        if (!voiceUri) setVoiceUri(vs[0].voiceURI);
      }
    };
    load();
    synth.addEventListener?.("voiceschanged", load);
    return () => synth.removeEventListener?.("voiceschanged", load);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ttsSupported]);

  const speak = (text) => {
    if (!ttsSupported || !speakEnabled) return;
    const synth = window.speechSynthesis;
    try {
      synth.cancel();
      const u = new window.SpeechSynthesisUtterance(String(text || ""));
      const v = (voices || []).find((x) => x.voiceURI === voiceUri) || (voices || [])[0];
      if (v) u.voice = v;
      u.rate = 1.0;
      u.pitch = 1.0;
      synth.speak(u);
    } catch {
      // ignore
    }
  };

  // Speak current question when session is running and question changes
  useEffect(() => {
    if (!running) return;
    const q = questions[step];
    if (q) speak(q);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, step, questions, speakEnabled, voiceUri]);

  // Auto-advance to next question after answerSeconds (demo)
  useEffect(() => {
    if (!running || !autoNext) return;
    if (!questions.length) return;
    if (step >= questions.length - 1) return;

    const id = setTimeout(() => {
      const nextIdx = Math.min(step + 1, questions.length - 1);
      setStep(nextIdx);
      const q = questions[nextIdx];
      if (q) speak(q);
    }, Math.max(5, Number(answerSeconds) || 30) * 1000);

    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, autoNext, answerSeconds, step, questions.length]);

  const start = async () => {
    setErr(null);
    setResult(null);
    setFrames({ total: 0, good: 0 });
    setStep(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setRunning(true);
      setStartTs(Date.now());
      if (questions[0]) speak(questions[0]);
    } catch (e) {
      setErr("Camera permission denied or not available.");
    }
  };

  const stop = async () => {
    setRunning(false);
    try {
      if (ttsSupported) window.speechSynthesis.cancel();
    } catch {}
    const v = videoRef.current;
    const stream = v?.srcObject;
    if (stream && stream.getTracks) stream.getTracks().forEach((t) => t.stop());
    if (v) v.srcObject = null;
  };

  // Demo "eye contact": face centered in frame using FaceDetector (if available)
  useEffect(() => {
    if (!running) return;
    let cancelled = false;
    const detector = window.FaceDetector ? new window.FaceDetector({ fastMode: true, maxDetectedFaces: 1 }) : null;
    const tick = async () => {
      if (cancelled || !running) return;
      const v = videoRef.current;
      const c = canvasRef.current;
      if (!v || !c || !detector) return;

      const w = v.videoWidth || 640;
      const h = v.videoHeight || 480;
      c.width = w;
      c.height = h;
      const ctx = c.getContext("2d");
      ctx.drawImage(v, 0, 0, w, h);

      try {
        const faces = await detector.detect(c);
        let good = 0;
        if (faces && faces[0]?.boundingBox) {
          const b = faces[0].boundingBox;
          const cx = b.x + b.width / 2;
          const cy = b.y + b.height / 2;
          const inCenter = cx > w * 0.3 && cx < w * 0.7 && cy > h * 0.25 && cy < h * 0.75;
          good = inCenter ? 1 : 0;
        }
        setFrames((f) => ({ total: f.total + 1, good: f.good + good }));
      } catch {
        // ignore
      }
    };

    const id = setInterval(tick, 700);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [running]);

  const next = () => {
    const nextIdx = Math.min(step + 1, questions.length - 1);
    setStep(nextIdx);
    const q = questions[nextIdx];
    if (running && q) speak(q);
  };

  const finish = async () => {
    const durationSeconds = elapsed;
    const payload = {
      student_id: studentId,
      eye_contact_ratio: clamp01(eyeRatio),
      duration_seconds: durationSeconds,
      answered_count: questions.length,
      total_questions: questions.length,
    };
    const res = await api.post("/api/interview/submit", payload);
    setResult(res.data.result);
    await stop();
  };

  return (
    <div className="grid cols-2">
      <div className="card" style={{ padding: 16 }}>
        <div className="h1">Video Interview</div>
        <p className="sub">
          AI questions + demo eye-contact score (face centered).{" "}
          {faceSupported ? "" : "FaceDetector not supported in this browser."}{" "}
          {ttsSupported ? "" : "TTS not supported in this browser."}
        </p>
        <div style={{ height: 10 }} />

        {err && <div className="card" style={{ padding: 12, borderColor: "#fecaca", background: "#fff1f2" }}>{err}</div>}

        <div className="card" style={{ padding: 12, marginTop: 10 }}>
          <div className="sectionTitle" style={{ marginBottom: 6 }}>
            Question {questions.length ? step + 1 : 0}/{questions.length || 0}
          </div>
          <div style={{ fontWeight: 900 }}>{questions[step] || "Loading questions…"}</div>
          <div style={{ height: 10 }} />
          <div className="form">
            <button
              className="btn secondary"
              disabled={!running || step === 0}
              onClick={() => {
                const prevIdx = Math.max(0, step - 1);
                setStep(prevIdx);
                const q = questions[prevIdx];
                if (running && q) speak(q);
              }}
            >
              Prev
            </button>
            <button className="btn secondary" disabled={!running || step >= questions.length - 1} onClick={next}>
              Next
            </button>
            <button className="btn secondary" disabled={!ttsSupported} onClick={() => speak(questions[step])}>
              Speak
            </button>
            <button className="btn secondary" disabled={!ttsSupported} onClick={() => setSpeakEnabled((v) => !v)}>
              {speakEnabled ? "Mute" : "Unmute"}
            </button>
            <button className="btn" disabled={!running} onClick={finish}>
              Finish
            </button>
          </div>
          <div style={{ height: 10 }} />
          <div className="form">
            <label className="pill" style={{ cursor: "pointer" }}>
              <input type="checkbox" checked={autoNext} onChange={(e) => setAutoNext(e.target.checked)} style={{ marginRight: 8 }} />
              Auto Next
            </label>
            <div className="pill">
              Answer time
              <select
                value={answerSeconds}
                onChange={(e) => setAnswerSeconds(Number(e.target.value))}
                style={{ marginLeft: 8, border: "none", background: "transparent", fontWeight: 800 }}
              >
                {[15, 30, 45, 60].map((s) => (
                  <option key={s} value={s}>
                    {s}s
                  </option>
                ))}
              </select>
            </div>
          </div>
          {ttsSupported && voices.length > 0 && (
            <>
              <div style={{ height: 10 }} />
              <div className="form">
                <div className="note" style={{ minWidth: 110 }}>
                  Voice
                </div>
                <select
                  className="input"
                  style={{ minWidth: 260 }}
                  value={voiceUri}
                  onChange={(e) => setVoiceUri(e.target.value)}
                >
                  {voices.map((v) => (
                    <option key={v.voiceURI} value={v.voiceURI}>
                      {v.name} ({v.lang})
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>

        <div style={{ height: 12 }} />
        <div className="grid cols-2">
          <div className="card statCard">
            <div className="label">Timer</div>
            <div className="val">{running ? `${elapsed}s` : "—"}</div>
          </div>
          <div className="card statCard">
            <div className="label">Eye Contact (Demo)</div>
            <div className="val">{running ? `${Math.round(eyeRatio * 100)}%` : "—"}</div>
          </div>
        </div>

        <div style={{ height: 12 }} />
        <div className="form">
          {!running ? (
            <button className="btn" onClick={start}>
              Start Camera
            </button>
          ) : (
            <button className="btn secondary" onClick={stop}>
              Stop
            </button>
          )}
        </div>

        {result && (
          <>
            <div style={{ height: 14 }} />
            <div className="card" style={{ padding: 14 }}>
              <div className="h1">Feedback</div>
              <p className="sub">
                Video AI Score: <b>{result.video_ai_score}</b>/100 • Eye ratio: <b>{Math.round(result.eye_contact_ratio * 100)}%</b>
              </p>
              <div style={{ height: 8 }} />
              <div className="sectionTitle">Strengths</div>
              <div className="chips">{(result.strengths || []).map((s) => <span key={s} className="chip">{s}</span>)}</div>
              <div style={{ height: 8 }} />
              <div className="sectionTitle">Improvements</div>
              <div className="chips">{(result.improvements || []).map((s) => <span key={s} className="chip gap">{s}</span>)}</div>
            </div>
          </>
        )}
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div className="sectionTitle">Camera Preview</div>
        <video ref={videoRef} muted playsInline style={{ width: "100%", borderRadius: 14, background: "#0b0f19" }} />
        <canvas ref={canvasRef} style={{ display: "none" }} />
        <div style={{ height: 10 }} />
        <div className="note">
          This is a demo implementation. Real eye-contact detection needs gaze estimation (MediaPipe / OpenCV / ML model).
        </div>
      </div>
    </div>
  );
}
