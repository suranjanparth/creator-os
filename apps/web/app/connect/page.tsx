"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { DEVELOPMENT_CREATOR_ID, useActiveCreatorId } from "@/features/creator/scope";
import { importCreator, type ContentItemOutcome, type CreatorImportResult, type ImportedProfileInput } from "@/features/ingestion/api";

const examplePayload = `{
  "profile": {
    "name": "Maya Chen",
    "handle": "@mayamakes",
    "niche": "Creative systems & solo business",
    "platform": "Instagram",
    "audience": "Ambitious creatives, 24-34",
    "follower_count": 84200
  },
  "content": [
    {
      "id": "imported-post-1",
      "platform": "Instagram",
      "content_type": "Reel",
      "category": "Creative systems",
      "title": "A reel I published",
      "views": 12000,
      "likes": 900,
      "comments": 60,
      "shares": 210,
      "engagement_rate": 9.5,
      "published_at": "2026-08-10"
    }
  ]
}`;

const futureSteps = [
  { number: "01", title: "Sign in to Creator OS", description: "Create or access your Creator OS account." },
  { number: "02", title: "Authorize your Instagram", description: "Connect an authorized Meta/Instagram account you own." },
  { number: "03", title: "Creator OS syncs your content", description: "Your profile and published posts are normalized and persisted for analysis." },
];

const outcomeLabels: Record<ContentItemOutcome["status"], string> = {
  created: "Created",
  updated: "Updated",
  skipped: "Skipped",
  error: "Error",
};

function ImportStatus({ result }: { result: CreatorImportResult }) {
  return <section className="import-summary" role="status" aria-label="Import result">
    <div className="panel-heading"><div><p className="overline">Import report</p><h2>Creator data imported</h2></div><span className="period">creator_id: {result.creator_id}</span></div>
    <div className="import-stats">
      <span><strong>{result.profile_status}</strong><small>profile</small></span>
      <span><strong>{result.created}</strong><small>created</small></span>
      <span><strong>{result.updated}</strong><small>updated</small></span>
      <span><strong>{result.skipped}</strong><small>skipped</small></span>
      <span><strong className={result.errors ? "negative" : ""}>{result.errors}</strong><small>errors</small></span>
    </div>
    {result.content_received === 0 ? <p className="dashboard-empty">This payload contained no content items. Connect published posts to power Dashboard and Content Intelligence.</p> : null}
    {result.items.length ? <ul className="outcome-list">{result.items.map((item) => <li className={`outcome outcome-${item.status}`} key={`${item.id}-${item.status}`}><span><strong>{item.id || "(invalid item)"}</strong>{item.detail ? <small>{item.detail}</small> : null}</span><span className={`outcome-badge ${item.status}`}>{outcomeLabels[item.status]}</span></li>)}</ul> : null}
    <div className="composer-controls">
      <Link className="button button-primary" href="/dashboard">Open dashboard <span>→</span></Link>
      <Link className="text-link" href="/content">View content intelligence</Link>
    </div>
  </section>;
}

export default function ConnectPage() {
  const { creatorId: activeCreatorId, selectCreator } = useActiveCreatorId();
  const [creatorId, setCreatorId] = useState(activeCreatorId);
  const [payload, setPayload] = useState(examplePayload);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "validation" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<CreatorImportResult | null>(null);

  useEffect(() => {
    setCreatorId(activeCreatorId);
  }, [activeCreatorId]);

  const isEmpty = payload.trim() === "";

  const handleImport = () => {
    if (isEmpty) {
      setStatus("validation");
      setMessage("Paste a creator payload to import, or fill the example.");
      return;
    }
    let parsed: unknown;
    try {
      parsed = JSON.parse(payload);
    } catch {
      setStatus("validation");
      setMessage("Paste valid JSON before importing.");
      return;
    }
    const request = parsed as { profile?: unknown; content?: unknown };
    if (!request || typeof request !== "object" || !request.profile) {
      setStatus("validation");
      setMessage("The payload must include a \"profile\" object with creator identity.");
      return;
    }
    setStatus("loading");
    setMessage(null);
    importCreator({ creator_id: creatorId.trim() || DEVELOPMENT_CREATOR_ID, profile: request.profile as ImportedProfileInput, content: Array.isArray(request.content) ? request.content : [] })
      .then((imported) => {
        selectCreator(imported.creator_id);
        setResult(imported);
        setStatus("success");
      })
      .catch((error: unknown) => {
        setMessage(error instanceof Error ? error.message : "Import failed. Check that the Creator OS API is running, then try again.");
        setStatus("error");
      });
  };

  return <div className="page connect-page">
    <PageHeader eyebrow="Connect your creator" title="Import your creator data." description="The authorized-account flow is next. Until then, use the safe development import path below against the real ingestion API." />

    <section className="connect-steps" aria-label="Planned account flow">
      {futureSteps.map((step) => <article className="connect-step" key={step.number}>
        <span className="step-number">{step.number}</span>
        <h3>{step.title}</h3>
        <p>{step.description}</p>
      </article>)}
    </section>

    {status === "success" && result ? <ImportStatus result={result} /> : null}

    <section className="panel import-panel">
      <div className="panel-heading"><div><p className="overline">Development import</p><h2>Import a normalized creator payload</h2></div><span className="period">POST /api/v1/ingestion/import</span></div>
      <p className="import-note">This writes through the real ingestion pipeline: the profile is upserted and each post is created, updated, or skipped idempotently. It never fabricates data — paste only data you actually have.</p>
      <div className="import-fields">
        <label className="import-field"><span>Creator ID</span><input value={creatorId} onChange={(event) => setCreatorId(event.target.value)} aria-label="Creator ID" /></label>
      </div>
      <label className="import-field"><span>Creator payload (JSON)</span><textarea value={payload} onChange={(event) => setPayload(event.target.value)} rows={14} aria-label="Creator payload" placeholder='{ "profile": { "name": "...", "handle": "@..." }, "content": [ ] }' /></label>
      <div className="composer-controls">
        <button className="button button-quiet" onClick={() => { setPayload(examplePayload); setStatus("idle"); setMessage(null); }}>Fill with example</button>
        <button className="button button-primary" disabled={status === "loading"} onClick={handleImport}>{status === "loading" ? "Importing…" : "Import creator data"} <span>→</span></button>
      </div>
      {status === "loading" ? <p className="import-status loading" aria-live="polite">Importing creator data...</p> : null}
      {status === "validation" || status === "error" ? <p className="import-status error" role="alert">{message}</p> : null}
      {status === "idle" && isEmpty ? <p className="import-status empty" aria-live="polite">Nothing to import yet. Paste a payload or fill the example.</p> : null}
    </section>
  </div>;
}
