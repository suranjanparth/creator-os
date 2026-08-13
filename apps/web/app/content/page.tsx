"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import {
  fetchContentIntelligence,
  type ContentIntelligenceItem,
} from "@/features/content-intelligence/api";
import {
  ingestContentBatch,
  type ContentIngestItemInput,
  type ContentIngestResult,
} from "@/features/content-ingest/api";
import { useActiveCreatorId } from "@/features/creator/scope";

export default function ContentPage() {
  const [platform, setPlatform] = useState("Instagram");
  const [idea, setIdea] = useState("");
  const [items, setItems] = useState<ContentIntelligenceItem[]>([]);
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [ingestOpen, setIngestOpen] = useState(false);
  const [importJson, setImportJson] = useState("");
  const [ingestStatus, setIngestStatus] = useState<"idle" | "loading" | "success" | "validation" | "error">("idle");
  const [ingestResult, setIngestResult] = useState<ContentIngestResult | null>(null);
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setItems([]);
    setSelectedItemId(null);
    setError(false);
    setLoading(true);
    void fetchContentIntelligence(creatorId)
      .then((intelligence) => {
        setItems(intelligence.items);
        setSelectedItemId(intelligence.items[0]?.content.id ?? null);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [creatorId]);

  const selectedItem = items.find((item) => item.content.id === selectedItemId) ?? null;

  const handleImport = () => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(importJson);
    } catch {
      setIngestStatus("validation");
      return;
    }
    if (!Array.isArray(parsed) || !parsed.length) {
      setIngestStatus("validation");
      return;
    }
    setIngestStatus("loading");
    ingestContentBatch(creatorId, parsed as ContentIngestItemInput[])
      .then((result) => {
        setIngestResult(result);
        setIngestStatus("success");
      })
      .catch(() => setIngestStatus("error"));
  };

  return <div className="page content-page">
    <PageHeader eyebrow="Content studio" title="Build from what your content shows." description="Select an analyzed post to carry its next recommended action into a new draft." />
    <section className="composer">
      <div className="composer-top"><span className="ai-badge">Content intelligence</span><span className="composer-status">Based on the available analyzed posts</span></div>
      <textarea value={idea} onChange={(event) => setIdea(event.target.value)} placeholder="Draft your next post idea…" aria-label="Content idea" />
      <div className="composer-controls">
        <div className="platform-tabs">{["Instagram", "LinkedIn", "TikTok"].map((item) => <button key={item} onClick={() => setPlatform(item)} className={platform === item ? "selected" : ""}>{item}</button>)}</div>
        <button className="button button-primary" disabled={!selectedItem} onClick={() => selectedItem && setIdea(selectedItem.recommended_next_action)}>Generate angle <span>→</span></button>
        <button className="button button-primary" onClick={() => setIngestOpen((open) => !open)}>{ingestOpen ? "Close import" : "Import"} <span>→</span></button>
      </div>
    </section>
    {ingestOpen ? <section className="panel ingest-panel">
      <div className="panel-heading"><div><p className="overline">Import published content</p><h2>Add your posts</h2></div><span className="period">JSON batch</span></div>
      <textarea value={importJson} onChange={(event) => setImportJson(event.target.value)} placeholder='[{ "id": "post-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative practice", "title": "My post", "views": 12000, "likes": 900, "comments": 60, "shares": 200, "engagement_rate": 9.5, "published_at": "2026-08-10" }]' aria-label="Content JSON" />
      <div className="composer-controls">
        <button className="button button-primary" disabled={ingestStatus === "loading"} onClick={handleImport}>{ingestStatus === "loading" ? "Importing…" : "Import posts"} <span>→</span></button>
        {ingestStatus === "success" && ingestResult ? <span className="success" role="status">{ingestResult.created} imported · {ingestResult.skipped} skipped</span> : null}
        {ingestStatus === "validation" ? <span className="error" role="alert">Paste a valid JSON array of posts before importing.</span> : null}
        {ingestStatus === "error" ? <span className="error" role="alert">Import failed. Check that the Creator OS API is running, then try again.</span> : null}
      </div>
    </section> : null}
    <section className="content-grid">
      <div className="idea-workbench">
        <div className="workbench-heading"><div><p className="overline">Analyzed content</p><h2>Choose a post to learn from</h2></div><span className="platform-tag">{platform}</span></div>
        {loading ? <p className="dashboard-empty" aria-live="polite">Loading analyzed posts...</p> : null}
        {error ? <p className="dashboard-empty" role="alert">Content Intelligence could not be reached. Start the Creator OS API and try again.</p> : null}
        {!loading && !error && !items.length ? <p className="dashboard-empty">No analyzed posts are available yet.</p> : null}
        {items.length ? <label>
          <span className="sr-only">Select analyzed content</span>
          <select value={selectedItemId ?? ""} onChange={(event) => setSelectedItemId(event.target.value)}>
            {items.map((item) => <option key={item.content.id} value={item.content.id}>{item.content.title}</option>)}
          </select>
        </label> : null}
      </div>
      {selectedItem ? <aside className="improve-panel">
        <p className="overline">Content Intelligence</p>
        <h2>{selectedItem.content.title}</h2>
        <p>{selectedItem.performance_tier} performance, score {selectedItem.performance_score}.</p>
        <div className="rewrite"><small>WHY THIS POST PERFORMED</small><strong>{selectedItem.primary_reason}</strong></div>
        <p>Pattern: {selectedItem.detected_pattern}</p>
        <div className="rewrite"><small>RECOMMENDED NEXT ACTION</small><strong>{selectedItem.recommended_next_action}</strong></div>
        <button className="button button-quiet" onClick={() => setIdea(selectedItem.recommended_next_action)}>Apply suggestion <span>→</span></button>
      </aside> : null}
    </section>
  </div>;
}
