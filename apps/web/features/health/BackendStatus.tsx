"use client";

import { useEffect, useState } from "react";

import { fetchBackendHealth, type HealthResponse } from "./api";

export function BackendStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchBackendHealth()
      .then(setHealth)
      .catch(() => setError("Backend is unavailable. Start the FastAPI service to connect it."));
  }, []);

  return (
    <aside className="status-card" aria-live="polite">
      <strong>Backend connection</strong>
      {health ? <p className="success">{health.service} is {health.status}.</p> : null}
      {error ? <p className="error">{error}</p> : null}
      {!health && !error ? <p>Checking API health...</p> : null}
    </aside>
  );
}
