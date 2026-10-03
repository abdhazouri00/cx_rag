import { useEffect, useState } from "react";
import { api, describeError } from "../api.js";
import RawJson from "./RawJson.jsx";

function count(number, word) {
  return `${number} ${word}${number === 1 ? "" : "s"}`;
}

function useAction() {
  const [state, setState] = useState({ loading: false, data: null, error: null });

  async function run(action) {
    setState({ loading: true, data: null, error: null });
    try {
      const data = await action();
      setState({ loading: false, data, error: null });
      return data;
    } catch (error) {
      setState({ loading: false, data: null, error: describeError(error) });
      return null;
    }
  }

  return [state, run];
}

function Step({ title, hint, action, children }) {
  return (
    <li className={action.data ? "step step-done" : "step"}>
      <h3>{title}</h3>
      <p className="hint">{hint}</p>
      {children}
      {action.error && <p className="problem">{action.error}</p>}
      <RawJson data={action.data} />
    </li>
  );
}

export default function Pipeline() {
  const [files, setFiles] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [resetChunks, setResetChunks] = useState(true);
  const [resetIndex, setResetIndex] = useState(true);

  const [upload, runUpload] = useAction();
  const [split, runSplit] = useAction();
  const [index, runIndex] = useAction();
  const [status, runStatus] = useAction();

  function refreshStatus() {
    return runStatus(() => api.indexInfo());
  }

  useEffect(() => {
    refreshStatus();
  }, []);

  function dropFiles(event) {
    event.preventDefault();
    setDragging(false);
    setFiles(Array.from(event.dataTransfer.files));
  }

  function uploadFiles() {
    return runUpload(async () => {
      const results = [];
      for (const file of files) {
        results.push({ name: file.name, ...(await api.upload(file)) });
      }
      return results;
    });
  }

  async function indexChunks() {
    const result = await runIndex(() => api.push(resetIndex));
    if (result) {
      refreshStatus();
    }
  }

  const collection = status.data?.collection_info;

  return (
    <aside className="pipeline">
      <h2>Prepare the documents</h2>

      <ol className="steps">
        <Step title="Upload" hint="Text or PDF files. Uploading a file with the same name again adds a newer version of that document." action={upload}>
          <label
            className={dragging ? "dropzone dropzone-over" : "dropzone"}
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={dropFiles}
          >
            <input
              type="file"
              multiple
              accept=".txt,.pdf"
              onChange={(event) => setFiles(Array.from(event.target.files))}
            />
            <span className="dropzone-title">
              {files.length > 0 ? `${count(files.length, "file")} selected` : "Choose files or drop them here"}
            </span>
            {files.length > 0 && <span className="dropzone-files">{files.map((file) => file.name).join(", ")}</span>}
          </label>

          <button disabled={files.length === 0 || upload.loading} onClick={uploadFiles}>
            {upload.loading && <span className="spinner" />}
            {upload.loading ? "Uploading" : "Upload files"}
          </button>
          {upload.data && <p className="result">{count(upload.data.length, "file")} uploaded.</p>}
        </Step>

        <Step
          title="Split into sections"
          hint="Each section becomes one chunk that keeps its title, version and date."
          action={split}
        >
          <label className="check">
            <input type="checkbox" checked={resetChunks} onChange={(event) => setResetChunks(event.target.checked)} />
            Replace existing chunks
          </label>
          <button disabled={split.loading} onClick={() => runSplit(() => api.process(resetChunks))}>
            {split.loading && <span className="spinner" />}
            {split.loading ? "Splitting" : "Split documents"}
          </button>
          {split.data && (
            <p className="result">
              {count(split.data.inserted_records, "chunk")} from {count(split.data.processed_files, "file")}.
            </p>
          )}
        </Step>

        <Step
          title="Add to the search index"
          hint="Every chunk is embedded and stored in Qdrant. This can take a moment."
          action={index}
        >
          <label className="check">
            <input type="checkbox" checked={resetIndex} onChange={(event) => setResetIndex(event.target.checked)} />
            Rebuild the index
          </label>
          <button disabled={index.loading} onClick={indexChunks}>
            {index.loading && <span className="spinner" />}
            {index.loading ? "Indexing" : "Index chunks"}
          </button>
          {index.data && <p className="result">{count(index.data.inserted_items_count, "chunk")} indexed.</p>}
        </Step>
      </ol>

      <div className="index-status">
        <div className="index-status-head">
          <h3>Search index</h3>
          <button className="quiet" disabled={status.loading} onClick={refreshStatus}>
            Refresh
          </button>
        </div>

        {collection && (
          <dl>
            <div>
              <dt>Chunks</dt>
              <dd>{collection.points_count}</dd>
            </div>
            <div>
              <dt>Vector size</dt>
              <dd>{collection.config.params.vectors.size}</dd>
            </div>
            <div>
              <dt>Distance</dt>
              <dd>{collection.config.params.vectors.distance}</dd>
            </div>
          </dl>
        )}
        {status.error && <p className="hint">Nothing is indexed yet.</p>}
        <RawJson data={status.data} />
      </div>
    </aside>
  );
}
