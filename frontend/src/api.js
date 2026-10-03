const base = "/api/v1";

async function request(path, options = {}) {
  const response = await fetch(base + path, options);
  const text = await response.text();

  let data = null;
  try {
    data = JSON.parse(text);
  } catch {
    data = null;
  }

  if (!response.ok) {
    const error = new Error(data?.message || data?.detail || text || "Request failed");
    error.status = response.status;
    throw error;
  }

  return data;
}

function postJson(path, body) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  info: () => request("/"),

  ping: () => request("/ping"),

  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/data/upload", { method: "POST", body: form });
  },

  process: (doReset) => postJson("/data/process", { do_reset: doReset ? 1 : 0 }),

  push: (doReset) => postJson("/nlp/index/push", { do_reset: doReset ? 1 : 0 }),

  indexInfo: () => request("/nlp/index/info"),

  search: (text, limit) => postJson("/nlp/index/search", { text, limit }),

  answer: (text, conversationId) => postJson("/nlp/index/answer", { text, conversation_id: conversationId }),
};

export function describeError(error) {
  if (error.status === 500) {
    return "The server returned an error (500). If the documents are not indexed yet, run steps 1 to 3 first.";
  }
  return error.message;
}
