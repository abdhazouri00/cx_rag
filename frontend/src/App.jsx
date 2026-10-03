import { useEffect, useState } from "react";
import { api } from "./api.js";
import Pipeline from "./components/Pipeline.jsx";
import Ask from "./components/Ask.jsx";
import Search from "./components/Search.jsx";

export default function App() {
  const [info, setInfo] = useState(null);
  const [online, setOnline] = useState(null);
  const [view, setView] = useState("ask");

  useEffect(() => {
    api.info().then(setInfo).catch(() => setInfo(null));
    api.ping().then(() => setOnline(true)).catch(() => setOnline(false));
  }, []);

  return (
    <>
      <header className="masthead">
        <div className="masthead-inner">
          <div>
            <h1 className="wordmark">{info ? info["App Name"] : "cx_rag"}</h1>
            <p className="tagline">Support answers taken only from your documents, always from the current version.</p>
          </div>

          <div className="masthead-side">
            <p className={`status status-${online === null ? "wait" : online ? "on" : "off"}`}>
              {online === null && "Checking the API"}
              {online === true && `API online, version ${info ? info["App Version"] : ""}`}
              {online === false && "API offline. Start it with docker compose up."}
            </p>
          </div>
        </div>
      </header>

      <main className="layout">
        <Pipeline />

        <section className="desk">
          <div className="tabs" role="tablist">
            <button role="tab" aria-selected={view === "ask"} onClick={() => setView("ask")}>
              Ask
            </button>
            <button role="tab" aria-selected={view === "search"} onClick={() => setView("search")}>
              Search
            </button>
          </div>

          {view === "ask" ? <Ask /> : <Search />}
        </section>
      </main>
    </>
  );
}
