import { useEffect, useRef, useState } from "react";
import { api, describeError } from "../api.js";
import Sources from "./Sources.jsx";
import RawJson from "./RawJson.jsx";

const examples = ["İade süresi kaç gün?", "E20 hata kodu ne anlama geliyor?", "Bulaşık makinesi satıyor musunuz?"];

export default function Ask() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const threadRef = useRef(null);

  useEffect(() => {
    const thread = threadRef.current;
    const questions = thread.querySelectorAll(".question");
    const lastQuestion = questions[questions.length - 1];

    if (!lastQuestion) {
      return;
    }

    if (thread.scrollHeight > thread.clientHeight) {
      thread.scrollTo({ top: lastQuestion.offsetTop - 8, behavior: "smooth" });
    } else {
      lastQuestion.scrollIntoView({ block: "start", behavior: "smooth" });
    }
  }, [messages, loading]);

  async function ask(event) {
    event.preventDefault();
    const question = text.trim();
    if (!question || loading) {
      return;
    }

    setText("");
    setError(null);
    setLoading(true);
    setMessages((current) => [...current, { role: "user", text: question }]);

    try {
      const response = await api.answer(question, conversationId);
      setConversationId(response.conversation_id);
      setMessages((current) => [...current, { role: "assistant", text: response.answer, response }]);
    } catch (problem) {
      setError(describeError(problem));
    }

    setLoading(false);
  }

  function startNewConversation() {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <p className="hint">
          {conversationId
            ? "The most recent messages of this conversation are sent with each question."
            : "Ask in Turkish. The answer names the document, the section and the version it came from."}
        </p>
        <button className="quiet" disabled={messages.length === 0} onClick={startNewConversation}>
          New conversation
        </button>
      </div>

      <div className="thread" ref={threadRef}>
        {messages.length === 0 && !error && (
          <div className="empty">
            <div className="version-demo" aria-hidden="true">
              <div className="demo-card demo-old">
                <span className="stamp">Version 1, replaced</span>
                <p>İade süresi 14 gündür.</p>
              </div>
              <div className="demo-card demo-new">
                <span className="stamp">Version 2</span>
                <p>İade süresi 30 gündür.</p>
              </div>
            </div>

            <h3>Ask about your documents</h3>
            <p>
              When two versions of a document disagree, the answer comes from the newest one and the older one is
              shown as replaced.
            </p>

            <div className="suggestions">
              {examples.map((example) => (
                <button key={example} className="chip" onClick={() => setText(example)}>
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) =>
          message.role === "user" ? (
            <p key={index} className="question">
              {message.text}
            </p>
          ) : (
            <article key={index} className={`answer ${message.response.answerable ? "" : "answer-refused"}`}>
              {!message.response.answerable && <p className="refused-note">Not in the documents</p>}
              <p className="answer-text">{message.text}</p>
              <Sources sources={message.response.sources} superseded={message.response.superseded_sources} />
              <RawJson data={message.response} />
            </article>
          )
        )}

        {loading && <p className="thinking">Looking through the documents</p>}
        {error && <p className="problem">{error}</p>}
      </div>

      <form className="composer" onSubmit={ask}>
        <input
          type="text"
          value={text}
          placeholder="İade süresi kaç gün?"
          aria-label="Your question"
          onChange={(event) => setText(event.target.value)}
        />
        <button className="primary" disabled={loading || !text.trim()}>
          Ask
        </button>
      </form>
    </div>
  );
}
