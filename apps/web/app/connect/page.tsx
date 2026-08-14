"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { createCreatorProfile, fetchCreatorProfiles, type CreatorProfile } from "@/features/creator/api";
import { useActiveCreatorId } from "@/features/creator/scope";
import { importCreator, type CreatorImportResult, type ImportedProfileInput } from "@/features/ingestion/api";

interface CreatorFormData {
  creator_id: string;
  name: string;
  handle: string;
  platform: string;
  profile_url: string;
  niche: string;
  audience: string;
  follower_count: string;
}

export default function ConnectPage() {
  const router = useRouter();
  const { selectCreator } = useActiveCreatorId();
  const [existingCreators, setExistingCreators] = useState<CreatorProfile[]>([]);
  const [showNewCreatorForm, setShowNewCreatorForm] = useState(false);
  const [formData, setFormData] = useState<CreatorFormData>({
    creator_id: "",
    name: "",
    handle: "",
    platform: "Instagram",
    profile_url: "",
    niche: "",
    audience: "",
    follower_count: "",
  });
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error" | "validation">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<CreatorImportResult | null>(null);
  const [importPayload, setImportPayload] = useState("");
  const [showImportForm, setShowImportForm] = useState(false);

  useEffect(() => {
    fetchCreatorProfiles()
      .then(setExistingCreators)
      .catch(() => setExistingCreators([]));
  }, []);

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleCreateCreator = async () => {
    if (!formData.creator_id.trim() || !formData.name.trim()) {
      setStatus("error");
      setMessage("Creator ID and name are required.");
      return;
    }

    setStatus("loading");
    setMessage(null);

    try {
      const profile = await createCreatorProfile({
        creator_id: formData.creator_id,
        name: formData.name,
        handle: formData.handle || null,
        profile_url: formData.profile_url || null,
        platform: formData.platform || null,
        niche: formData.niche || null,
        audience: formData.audience || null,
        follower_count: formData.follower_count ? parseInt(formData.follower_count, 10) : null,
      });

      selectCreator(profile.creator_id);
      setExistingCreators([...existingCreators, profile]);
      setStatus("success");
      setMessage(`Creator "${profile.name}" created successfully!`);
      setShowNewCreatorForm(false);
      setFormData({
        creator_id: "",
        name: "",
        handle: "",
        platform: "Instagram",
        profile_url: "",
        niche: "",
        audience: "",
        follower_count: "",
      });

      setTimeout(() => {
        router.push("/dashboard");
      }, 1500);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Failed to create creator.");
    }
  };

  const handleImportContent = async () => {
    if (!importPayload.trim()) {
      setStatus("validation");
      setMessage("Paste a creator payload to import.");
      return;
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(importPayload);
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

    try {
      const result = await importCreator({
        creator_id: formData.creator_id,
        profile: request.profile as ImportedProfileInput,
        content: Array.isArray(request.content) ? request.content : [],
      });

      selectCreator(result.creator_id);
      setImportResult(result);
      setStatus("success");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Import failed.");
      setStatus("error");
    }
  };

  const handleSelectCreator = (creator: CreatorProfile) => {
    selectCreator(creator.creator_id);
    router.push("/dashboard");
  };

  return (
    <div className="page connect-page">
      <PageHeader
        eyebrow="Connect your creator"
        title="Set up your Creator OS workspace."
        description="Start by creating your creator profile, then optionally import your published content for analysis."
      />

      {existingCreators.length > 0 && !showNewCreatorForm && !showImportForm ? (
        <section className="panel import-panel">
          <div className="panel-heading">
            <div>
              <p className="overline">Your creators</p>
              <h2>Switch to an existing creator</h2>
            </div>
          </div>
          <div className="creator-list">
            {existingCreators.map((creator) => (
              <article className="creator-card" key={creator.creator_id}>
                <div className="creator-info">
                  <strong>{creator.name}</strong>
                  {creator.handle && <small>{creator.handle}</small>}
                  {creator.platform && <small>{creator.platform}</small>}
                </div>
                <button
                  className="button button-primary"
                  onClick={() => handleSelectCreator(creator)}
                >
                  Open <span>→</span>
                </button>
              </article>
            ))}
          </div>
          <div className="composer-controls">
            <button className="button button-primary" onClick={() => setShowNewCreatorForm(true)}>
              Create new creator <span>+</span>
            </button>
          </div>
        </section>
      ) : null}

      {showNewCreatorForm ? (
        <section className="panel import-panel">
          <div className="panel-heading">
            <div>
              <p className="overline">Create a new creator</p>
              <h2>Set up your creator profile</h2>
            </div>
          </div>
          <div className="import-fields">
            <label className="import-field">
              <span>Creator ID *</span>
              <input
                type="text"
                name="creator_id"
                value={formData.creator_id}
                onChange={handleFormChange}
                placeholder="e.g., john-doe"
                aria-label="Creator ID"
              />
              <small>A unique identifier for your creator profile (alphanumeric, lowercase, hyphens OK)</small>
            </label>
            <label className="import-field">
              <span>Name *</span>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleFormChange}
                placeholder="e.g., John Doe"
                aria-label="Creator name"
              />
            </label>
            <label className="import-field">
              <span>Handle / Username</span>
              <input
                type="text"
                name="handle"
                value={formData.handle}
                onChange={handleFormChange}
                placeholder="e.g., @johndoe"
                aria-label="Creator handle"
              />
            </label>
            <label className="import-field">
              <span>Platform</span>
              <select name="platform" value={formData.platform} onChange={handleFormChange} aria-label="Creator platform">
                <option value="Instagram">Instagram</option>
                <option value="TikTok">TikTok</option>
                <option value="LinkedIn">LinkedIn</option>
                <option value="YouTube">YouTube</option>
                <option value="Twitter">Twitter</option>
                <option value="Other">Other</option>
              </select>
            </label>
            <label className="import-field">
              <span>Profile URL</span>
              <input
                type="url"
                name="profile_url"
                value={formData.profile_url}
                onChange={handleFormChange}
                placeholder="https://instagram.com/johndoe"
                aria-label="Profile URL"
              />
            </label>
            <label className="import-field">
              <span>Niche / Content Focus</span>
              <input
                type="text"
                name="niche"
                value={formData.niche}
                onChange={handleFormChange}
                placeholder="e.g., Tech education, sustainable fashion"
                aria-label="Creator niche"
              />
            </label>
            <label className="import-field">
              <span>Target Audience</span>
              <input
                type="text"
                name="audience"
                value={formData.audience}
                onChange={handleFormChange}
                placeholder="e.g., Indie hackers, 25-35"
                aria-label="Target audience"
              />
            </label>
            <label className="import-field">
              <span>Follower Count</span>
              <input
                type="number"
                name="follower_count"
                value={formData.follower_count}
                onChange={handleFormChange}
                placeholder="e.g., 10000"
                aria-label="Follower count"
              />
            </label>
          </div>
          <div className="composer-controls">
            <button className="button button-quiet" onClick={() => setShowNewCreatorForm(false)}>
              Cancel
            </button>
            <button
              className="button button-primary"
              disabled={status === "loading"}
              onClick={handleCreateCreator}
            >
              {status === "loading" ? "Creating…" : "Create creator"}
              <span>→</span>
            </button>
          </div>
          {(status === "validation" || status === "error") && message && (
            <p className="import-status error" role="alert">
              {message}
            </p>
          )}
          {status === "success" && message && (
            <p className="import-status success" role="status">
              {message}
            </p>
          )}
        </section>
      ) : null}

      {!showNewCreatorForm && !showImportForm && existingCreators.length === 0 ? (
        <section className="panel import-panel">
          <div className="panel-heading">
            <div>
              <p className="overline">Get started</p>
              <h2>Create your first creator profile</h2>
            </div>
          </div>
          <p className="import-note">
            Every creator in Creator OS is a separate workspace. You can manage multiple creator profiles and switch between them anytime.
          </p>
          <div className="composer-controls">
            <button className="button button-primary" onClick={() => setShowNewCreatorForm(true)}>
              Create first creator <span>+</span>
            </button>
          </div>
        </section>
      ) : null}

      {importResult ? (
        <section className="import-summary" role="status" aria-label="Import result">
          <div className="panel-heading">
            <div>
              <p className="overline">Import report</p>
              <h2>Creator content imported</h2>
            </div>
            <span className="period">creator_id: {importResult.creator_id}</span>
          </div>
          <div className="import-stats">
            <span>
              <strong>{importResult.profile_status}</strong>
              <small>profile</small>
            </span>
            <span>
              <strong>{importResult.created}</strong>
              <small>created</small>
            </span>
            <span>
              <strong>{importResult.updated}</strong>
              <small>updated</small>
            </span>
            <span>
              <strong>{importResult.skipped}</strong>
              <small>skipped</small>
            </span>
            <span>
              <strong className={importResult.errors ? "negative" : ""}>{importResult.errors}</strong>
              <small>errors</small>
            </span>
          </div>
          <div className="composer-controls">
            <Link className="button button-primary" href="/dashboard">
              Open dashboard <span>→</span>
            </Link>
          </div>
        </section>
      ) : null}

      {showImportForm || (existingCreators.length > 0 && formData.creator_id) ? (
        <section className="panel import-panel">
          <div className="panel-heading">
            <div>
              <p className="overline">Import content (optional)</p>
              <h2>Add your published posts to {formData.name || "this creator"}</h2>
            </div>
          </div>
          <p className="import-note">
            Paste a JSON array of your published posts. Each post should include platform, content type, views, likes, comments, shares, and publication date.
          </p>
          <label className="import-field">
            <span>Content payload (JSON)</span>
            <textarea
              value={importPayload}
              onChange={(e) => setImportPayload(e.target.value)}
              rows={12}
              aria-label="Content payload"
              placeholder="[{ id: ..., platform: ..., content_type: ..., views: ... }]"
            />
          </label>
          <div className="composer-controls">
            <button className="button button-quiet" onClick={() => setShowImportForm(false)}>
              Skip for now
            </button>
            <button
              className="button button-primary"
              disabled={status === "loading"}
              onClick={handleImportContent}
            >
              {status === "loading" ? "Importing…" : "Import content"} <span>→</span>
            </button>
          </div>
          {(status === "validation" || status === "error") && message && (
            <p className="import-status error" role="alert">
              {message}
            </p>
          )}
        </section>
      ) : null}
    </div>
  );
}
