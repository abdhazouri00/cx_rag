function SourceCard({ doc, replacedBy, plain }) {
  const meta = doc.metadata || {};
  const replaced = replacedBy !== undefined;
  const body = meta.section && doc.text.startsWith(meta.section) ? doc.text.slice(meta.section.length).trim() : doc.text;

  return (
    <li className={`source ${plain ? "source-plain" : replaced ? "source-replaced" : "source-current"}`}>
      <div className="source-head">
        <p className="source-title">
          {meta.title || "Untitled document"}
          {meta.section && <span className="source-section">{meta.section}</span>}
        </p>
        {meta.version !== undefined && (
          <span className="stamp">
            {replaced ? `Version ${meta.version}, replaced` : `Version ${meta.version}`}
          </span>
        )}
      </div>

      <p className="source-text">{body}</p>

      <p className="source-foot">
        {meta.effective_date && <span>Effective {meta.effective_date}</span>}
        <span>Match {Math.round(doc.score * 100)}%</span>
        {replaced && replacedBy && <span>Version {replacedBy} is used instead</span>}
      </p>
    </li>
  );
}

export default function Sources({ sources = [], superseded = [], title = "Sources used", plain = false }) {
  if (sources.length === 0 && superseded.length === 0) {
    return null;
  }

  const currentVersions = {};
  sources.forEach((doc) => {
    if (doc.metadata?.title) {
      currentVersions[doc.metadata.title] = doc.metadata.version;
    }
  });

  return (
    <div className="sources">
      {sources.length > 0 && (
        <>
          <h3>{title}</h3>
          <ul>
            {sources.map((doc, index) => (
              <SourceCard key={index} doc={doc} plain={plain} />
            ))}
          </ul>
        </>
      )}

      {superseded.length > 0 && (
        <>
          <h3>Older versions left out</h3>
          <ul>
            {superseded.map((doc, index) => (
              <SourceCard key={index} doc={doc} replacedBy={currentVersions[doc.metadata?.title] || null} />
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
