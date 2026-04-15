import { useState } from "react";

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const d = data.detail;
        const msg = Array.isArray(d)
          ? d.map((x) => x.msg || JSON.stringify(x)).join("; ")
          : d || res.statusText || "Request failed";
        throw new Error(msg);
      }
      setResult(data);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>Nexus HR Assist</h1>
      <p className="muted">
        Uses the FastAPI backend (proxy in dev). Run:{" "}
        <code>uvicorn fastapi_app:app --reload</code>
      </p>

      <form onSubmit={onSubmit}>
        <label htmlFor="q">Your question</label>
        <textarea
          id="q"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "What are the standard office hours?"'
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? "Working…" : "Ask HR"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <>
          <div className="section">
            <h2>Answer</h2>
            <div className="answer">{result.answer}</div>
          </div>

          {result.thoughts?.length > 0 && (
            <details className="thoughts">
              <summary>Search / intent</summary>
              <ul>
                {result.thoughts.map((t, i) => (
                  <li key={i}>
                    <strong>{t.title || "—"}</strong>
                    {t.description ? `: ${t.description}` : null}
                  </li>
                ))}
              </ul>
            </details>
          )}

          <div className="section">
            <h2>Documents used for grounding ({result.documents?.length || 0})</h2>
            {(result.documents || []).map((doc, i) => (
              <article className="doc" key={doc.id || i}>
                <h3>{doc.title || doc.filepath || doc.id || `Document ${i + 1}`}</h3>
                <div className="doc-meta">
                  {doc.url && (
                    <a href={doc.url} target="_blank" rel="noreferrer">
                      Open link
                    </a>
                  )}
                  {doc.filepath && <span>{doc.url ? " · " : ""}{doc.filepath}</span>}
                </div>
                <pre>{doc.content}</pre>
              </article>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
