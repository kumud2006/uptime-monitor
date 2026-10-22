import { useState } from "react";

function AddTargetForm({ onAdd, mockMode = false }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event) {
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

    setBusy(true);
    try {
      await onAdd({
        name: trimmedName || parsedUrl.hostname,
        url: parsedUrl.href,
        email: trimmedEmail,
      });

      setName("");
      setUrl("");
      setEmail("");
      setMessage(
        mockMode
          ? "Website added to the demo data!"
          : "Website added. The first check has run."
      );
    } catch (err) {
      setError(err.message || "Could not add the website.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="add-target-container">
      <div className="form-heading">
        <div>
          <h3>Add a website</h3>
          <p>Enter a website to include in your monitoring dashboard.</p>
        </div>

        {mockMode && <span className="mock-label">Demo mode</span>}
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

        <button type="submit" className="primary-button" disabled={busy}>
          {busy ? "Adding…" : "Add website"}
        </button>
      </form>

      <p className="form-note">
        {mockMode
          ? "Demo mode: websites are added locally and no real email alerts are sent."
          : "Websites are saved to the cloud database and checked every 5 minutes. Alerts go to the email above."}
      </p>
    </div>
  );
}

export default AddTargetForm;
