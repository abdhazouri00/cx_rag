import { useState } from "react";
import { api, describeError } from "../api.js";
import Sources from "./Sources.jsx";
import RawJson from "./RawJson.jsx";

export default function Search() {
  const [text, setText] = useState("");
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  async function search(event) {
    event.preventDefault();
    if (!text.trim() || loading) {
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      setResponse(await api.search(text.trim(), limit));
    } catch (problem) {
      setError(describeError(problem));
    }

    setLoading(false);
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <p className="hint">
          The closest chunks exactly as the index returns them, before old versions and weak matches are removed.
        </p>
      </div>

      <form className="composer" onSubmit={search}>
        <input
          type="text"
          value={text}
          placeholder="kargo ücreti"
          aria-label="Search text"
          onChange={(event) => setText(event.target.value)}
        />
        <label className="limit-field">
          Results
          <input
            type="number"
            min="1"
            max="20"
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value) || 1)}
          />
        </label>
        <button className="primary" disabled={loading || !text.trim()}>
          {loading ? "Searching" : "Search"}
        </button>
      </form>

      <div className="thread">
        {error && <p className="problem">{error}</p>}
        {response && (
          <article className="answer">
            <Sources sources={response.results} title="Closest chunks" plain />
            <RawJson data={response} />
          </article>
        )}
      </div>
    </div>
  );
}
