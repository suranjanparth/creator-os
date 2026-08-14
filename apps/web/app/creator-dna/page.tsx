"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { fetchCreatorDna, type DnaData } from "@/features/dna/api";
import { useActiveCreatorId } from "@/features/creator/scope";

function initials(name: string | undefined | null) {
  if (!name) return "C";
  return name.split(" ").filter(Boolean).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

export default function CreatorDnaPage() {
  const [dna, setDna] = useState<DnaData | null>(null);
  const [error, setError] = useState(false);
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setDna(null);
    setError(false);
    if (!creatorId) {
      setError(true);
      return;
    }
    void fetchCreatorDna(creatorId).then(setDna).catch(() => setError(true));
  }, [creatorId]);

  if (error) {
    return <div className="page dna-page">
      <PageHeader eyebrow="Creator intelligence profile" title="Your creative pattern, mapped." description="Your creator DNA could not be reached." />
      <section className="dashboard-message" role="alert">
        <h2>We couldn&apos;t load your creator DNA.</h2>
        <p>Check that the Creator OS API is running, then try again.</p>
        <button className="button button-primary" onClick={() => { setError(false); if (creatorId) void fetchCreatorDna(creatorId).then(setDna).catch(() => setError(true)); }}>Try again</button>
      </section>
    </div>;
  }

  if (!dna) {
    return <div className="page dna-page">
      <PageHeader eyebrow="Creator intelligence profile" title="Your creative pattern, mapped." description="Loading your creator signals." />
      <div className="dashboard-loading" aria-live="polite"><span /><span /><span /></div>
    </div>;
  }

  const identity = dna.identity;
  const hasContent = dna.total_posts > 0;

  return <div className="page dna-page">
    <PageHeader eyebrow="Creator intelligence profile" title="Your creative pattern, mapped." description="A living picture of the signals that make your work recognizable, derived from your persisted content."><span className="confidence">{dna.total_posts} posts analyzed</span></PageHeader>
    <section className="dna-hero">
      <div className="identity-card">
        <div className="dna-avatar">{initials(identity?.name)}</div>
        <div><p className="overline">Creator identity</p><h2>{identity?.name ?? "No creator connected"}</h2><p>{identity ? [identity.handle, identity.niche].filter(Boolean).join(" · ") : "Import a creator profile to begin."}</p></div>
        <div className="identity-summary"><p>{hasContent ? "Your creative pattern is derived from your persisted published content and creator profile." : "No published content yet. Import content to map your creative pattern."}</p><small>{hasContent ? `Derived from ${dna.total_posts} published posts` : "Awaiting content"}</small></div>
      </div>
      <div className="dna-map">{hasContent ? <div className="format-pills">{dna.formats.map((format) => <span key={format.name}>{format.name} · {format.share}%</span>)}</div> : <div className="dna-empty">Format mix will appear here once content is imported.</div>}</div>
    </section>
    <section className="dna-columns">
      <article className="panel profile-facts"><p className="overline">Audience signal</p><h2>Who responds</h2>
        <div className="fact"><span>Core audience</span><strong>{identity?.audience ?? "Awaiting profile data"}</strong></div>
        <div className="fact"><span>Primary platform</span><strong>{dna.platforms[0] ? `${dna.platforms[0].name} · ${dna.platforms[0].share}% of posts` : "No posts yet"}</strong></div>
        <div className="fact"><span>Best format</span><strong>{dna.best_format ? `${dna.best_format.name} · ${dna.best_format.average_engagement_rate}% engagement` : "Not enough data"}</strong></div>
        <div className="fact"><span>Total content</span><strong>{dna.total_posts} posts</strong></div>
      </article>
      <article className="panel voice-profile"><p className="overline">Content signals</p><h2>What you publish</h2>
        {hasContent ? dna.formats.map((format) => <div className="trait" key={format.name}><span>{format.name}</span><div><i style={{ width: `${Math.min(format.share, 100)}%` }} /></div><b>{format.share}%</b></div>) : <p className="profile-note">Format signals will appear here once content is imported.</p>}
      </article>
    </section>
    <section className="dna-insights">
      {dna.insights.length ? dna.insights.map((insight) => <article key={insight.title}><p className="overline">Signal</p><h2>{insight.title}</h2><p>{insight.summary}</p><span className="evidence-pill">{insight.sample_size !== null && insight.sample_size !== undefined ? `${insight.sample_size} posts analyzed` : "Insufficient data"}</span></article>) : <p className="dashboard-empty">Add published content to see your creative signals.</p>}
    </section>
  </div>;
}
