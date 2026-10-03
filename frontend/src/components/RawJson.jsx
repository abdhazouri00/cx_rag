export default function RawJson({ data }) {
  if (!data) {
    return null;
  }

  return (
    <details className="raw">
      <summary>API response</summary>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </details>
  );
}
