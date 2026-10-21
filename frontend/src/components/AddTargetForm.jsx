
import { useState } from "react";

function AddTargetForm({ onAdd, mockMode = true }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    const trimmedName = name.trim();
    const trimmedUrl = url.trim();
    const trimmedEmail = email.trim();

    let parsedUrl;

    try {
      parsedUrl = new URL(trimmedUrl);
    } catch {
      setError("Please enter a valid website URL.");
      return;
    }

    if (
      !["http:", "https:"].includes(parsedUrl.protocol) ||
      !parsedUrl.hostname.includes(".")
    ) {
      setError("Enter a public website URL beginning with https://.");
      return;
    }

    if (
      !trimmedEmail ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)
    ) {
      setError("Please enter a valid alert email address.");
      return;
    }

    if (!mockMode) {
      setError(
        "Live website creation is disabled until the backend is confirmed ready."
      );
      return;
    }

    onAdd?.({
      id: `mock-${Date.now()}`,
      name: trimmedName || parsedUrl.hostname,
      url: parsedUrl.href,
      email: trimmedEmail,
      ok: true,
      status_code: 200,
      latency_ms: 120,
      uptime_24h: 100,
      last_checked: new Date().toISOString(),
    });

    setName("");
    setUrl("");
    setEmail("");
    setMessage("Website added to the demo data!");
  }

  return (
    <div className="add-target-container">
      <div className="form-heading">
        <div>
          <h3>Add a website</h3>
          <p>Enter a website to include in your monitoring dashboard.</p>
        </div>

        <span className="mock-label">Demo mode</span>
      </div>

      <form className="add-target-form" onSubmit={handleSubmit}>
        <label>
          Website name
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="My website"
          />
        </label>

        <label>
          Website URL
          <input
            type="url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://example.com"
            required
          />
        </label>

        <label>
          Alert email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>

        {error && <p className="form-error">{error}</p>}
        {message && <p className="form-success">{message}</p>}

        <button type="submit" className="primary-button">
          Add website
        </button>
      </form>

      <p className="form-note">
        Demo mode: websites are added locally and no real email alerts are sent.
      </p>
    </div>
  );
}

export default AddTargetForm;
