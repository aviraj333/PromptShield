
import { useState } from "react";
import "./App.css";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [source, setSource] = useState("user");
  const [result, setResult] = useState(null);

  function scanPrompt() {
    if (!prompt.trim()) {
      setResult({
        decision: "ESCALATE",
        reasons: ["Please enter a prompt first."]
      });
      return;
    }

    // Temporary UI preview only.
    // Real security decisions will come from FastAPI.
    setResult({
      decision: "PENDING",
      reasons: [
        "Frontend is ready.",
        "Connect the FastAPI backend to perform real detection."
      ]
    });
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>🛡️ Prompt<span>Shield</span></h2>
        <p className="muted">Secure AI. Safer Tomorrow.</p>

        <nav>
          <div className="nav-active">▦ Dashboard</div>
          <div>⌕ Scan Prompt</div>
          <div>♢ Policy Manager</div>
          <div>▤ Audit Logs</div>
          <div>▥ Analytics</div>
        </nav>

        <div className="sidebar-footer">
          <h3>VORTEXA 3.0</h3>
          <p>C-03 · Prompt Injection Defense</p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>Security Dashboard</h1>
            <p className="muted">
              Monitor and protect AI prompts.
            </p>
          </div>
          <span className="local-badge">● Local Mode</span>
        </header>

        <section className="stats">
          <article className="card">
            <p className="muted">Security outcomes</p>
            <h2>04</h2>
            <p>Allow · Block · Sanitize · Escalate</p>
          </article>
          <article className="card">
            <p className="muted">Detection engine</p>
            <h2>Policy-first</h2>
            <p>Rules + explainable decisions</p>
          </article>
          <article className="card">
            <p className="muted">AI integration</p>
            <h2>Local-first</h2>
            <p>No paid API required for core rules</p>
          </article>
        </section>

        <section className="workspace">
          <article className="card scanner">
            <h2>⚡ Scan a Prompt</h2>
            <p className="muted">
              Inspect prompt content and its source.
            </p>

            <label htmlFor="source">Input source</label>
            <select
              id="source"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            >
              <option value="user">Direct user prompt</option>
              <option value="retrieved_document">
                Retrieved document
              </option>
              <option value="tool_output">Tool output</option>
            </select>

            <label htmlFor="prompt">Prompt content</label>
            <textarea
              id="prompt"
              value={prompt}
              maxLength={5000}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter a prompt to inspect..."
              rows={8}
            />

            <p className="muted counter">
              {prompt.length}/5000 characters
            </p>

            <button onClick={scanPrompt}>
              🛡️ Preview Scanner
            </button>

            <p className="muted note">
              Preview only — real detection will be enabled
              after connecting the backend.
            </p>
          </article>

          <article className="card result-panel">
            <h2>Detection Result</h2>

            {!result ? (
              <div className="empty-state">
                <span className="shield-icon">◇</span>
                <h3>Ready to inspect</h3>
                <p className="muted">
                  Enter a prompt to preview the interface.
                </p>
              </div>
            ) : (
              <div>
                <h2 className={`decision ${result.decision}`}>
                  {result.decision}
                </h2>
                <h3>Detection reasons</h3>
                <ul>
                  {result.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="outcomes">
              <span className="allow">ALLOW</span>
              <span className="block">BLOCK</span>
              <span className="sanitize">SANITIZE</span>
              <span className="escalate">ESCALATE</span>
            </div>
          </article>
        </section>

        <footer>
          PromptShield · VORTEXA 3.0 · C-03
        </footer>
      </main>
    </div>
  );
}
