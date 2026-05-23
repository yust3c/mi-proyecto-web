import { useState } from "react";

const EXAMPLE_PROMPT =
  "Explica brevemente qué aporta Docker Compose en una práctica de despliegue.";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!prompt.trim()) {
      setError("Introduce un prompt antes de enviar la petición.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse("");

    try {
      const apiResponse = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
      });

      const data = await apiResponse.json();

      if (!apiResponse.ok) {
        throw new Error(data.detail || "No se pudo obtener respuesta del backend.");
      }

      setResponse(data.response || "El modelo no devolvió texto.");
    } catch (requestError) {
      setError(requestError.message || "Se produjo un error inesperado.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <span className="eyebrow">Docker + FastAPI + Ollama + Nginx</span>
          <h1>Chat IA local desplegado con contenedores</h1>
          <p>
            Demostración sencilla para una práctica académica de despliegue con
            Docker Compose y CI/CD sobre una VM Linux.
          </p>
        </div>

        <div className="info-panel">
          <h2>Arquitectura</h2>
          <ul>
            <li>Frontend React con formulario simple.</li>
            <li>Backend FastAPI en `/api/chat`.</li>
            <li>Modelo local servido por Ollama.</li>
            <li>Nginx como punto de entrada único.</li>
          </ul>
        </div>
      </section>

      <section className="chat-layout">
        <form className="chat-form" onSubmit={handleSubmit}>
          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            name="prompt"
            rows="8"
            placeholder={EXAMPLE_PROMPT}
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />

          <div className="actions">
            <button type="submit" disabled={loading}>
              {loading ? "Consultando..." : "Enviar al modelo"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => setPrompt(EXAMPLE_PROMPT)}
              disabled={loading}
            >
              Cargar ejemplo
            </button>
          </div>
        </form>

        <article className="response-card">
          <div className="response-header">
            <h2>Respuesta</h2>
            <span className={loading ? "status pending" : "status ready"}>
              {loading ? "Procesando" : "Listo"}
            </span>
          </div>

          {error ? <p className="message error">{error}</p> : null}
          {!error && !response ? (
            <p className="message empty">
              La respuesta del modelo aparecerá aquí en cuanto envíes un prompt.
            </p>
          ) : null}
          {response ? <pre className="response-text">{response}</pre> : null}
        </article>
      </section>
    </main>
  );
}
