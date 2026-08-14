"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { fetchContentIntelligence, type ContentIntelligenceData, type ContentIntelligenceItem } from "@/features/content-intelligence/api";
import { useActiveCreatorId } from "@/features/creator/scope";

type PerformanceFilter = "All" | "Best performing" | "Needs improvement";

function formatCompact(value: number | null) {
  return value === null ? "--" : new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatDate(value: string | null) {
  return value ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(`${value}T12:00:00`)) : "--";
}

function IntelligenceCard({ item }: { item: ContentIntelligenceItem }) {
  const underperforming = item.performance_tier === "Weak" || item.performance_tier === "Average";
  return <article className="intelligence-card">
    <header className="intelligence-card-heading"><div><span className="content-platform">{item.content.platform}</span><h2>{item.content.title}</h2><p>{item.content.content_type} · {item.content.category} · {formatDate(item.content.published_at)}</p></div><div className={`score-badge ${item.performance_tier.toLowerCase()}`}><strong>{item.performance_score}</strong><span>{item.performance_tier}</span></div></header>
    <div className="content-metrics"><span><strong>{formatCompact(item.content.views)}</strong> views</span><span><strong>{item.content.engagement_rate?.toFixed(1) ?? "--"}%</strong> engagement</span><span><strong>{formatCompact(item.content.shares)}</strong> shares</span></div>
    <div className="intelligence-explanation"><div><p className="overline">{underperforming ? "Why it underperformed" : "Why it worked"}</p><strong>{item.primary_reason}</strong><small>Pattern: {item.detected_pattern}</small></div><div><p className="overline">Next move</p><strong>{item.recommended_next_action}</strong></div></div>
  </article>;
}

export default function ContentIntelligencePage() {
  const [intelligence, setIntelligence] = useState<ContentIntelligenceData | null>(null);
  const [error, setError] = useState(false);
  const [performanceFilter, setPerformanceFilter] = useState<PerformanceFilter>("All");
  const [contentFilter, setContentFilter] = useState("All categories and types");
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setIntelligence(null);
    setError(false);
    if (!creatorId) {
      setError(true);
      return;
    }
    void fetchContentIntelligence(creatorId).then(setIntelligence).catch(() => setError(true));
  }, [creatorId]);

  if (error) return <div className="page intelligence-page"><PageHeader eyebrow="Content intelligence" title="Explain every post." description="The initial intelligence layer could not be reached." /><section className="dashboard-message" role="alert"><h2>We couldn&apos;t load content intelligence.</h2><p>Check that the Creator OS API is running, then try again.</p><button className="button button-primary" onClick={() => { setError(false); if (creatorId) void fetchContentIntelligence(creatorId).then(setIntelligence).catch(() => setError(true)); }}>Try again</button></section></div>;
  if (!intelligence) return <div className="page intelligence-page"><PageHeader eyebrow="Content intelligence" title="Explain every post." description="Loading rule-based performance analysis." /><div className="dashboard-loading" aria-live="polite"><span /><span /><span /></div></div>;
  if (!intelligence.items.length) return <div className="page intelligence-page"><PageHeader eyebrow="Content intelligence" title="Explain every post." description="A clear, rule-based read on what each post earned and what to build next." /><section className="dashboard-message"><h2>No analyzed posts yet.</h2><p>Connect published content with views and engagement data to generate Content Intelligence.</p></section></div>;

  const options = ["All categories and types", ...new Set(intelligence.items.flatMap((item) => [item.content.category, item.content.content_type]))];
  const visibleItems = intelligence.items.filter((item) => {
    const matchesPerformance = performanceFilter === "All" || (performanceFilter === "Best performing" ? ["Excellent", "Strong"].includes(item.performance_tier) : ["Average", "Weak"].includes(item.performance_tier));
    const matchesContent = contentFilter === "All categories and types" || item.content.category === contentFilter || item.content.content_type === contentFilter;
    return matchesPerformance && matchesContent;
  });

  return <div className="page intelligence-page">
    <PageHeader eyebrow="Content intelligence" title="Explain every post." description="A clear, rule-based read on what each post earned and what to build next." />
    <section className="intelligence-method"><span>Initial intelligence layer</span><p>{intelligence.method}</p></section>
    {intelligence.summary && !intelligence.summary.strongest_content_format ? <p className="dashboard-empty">More posts in the same format are needed before Creator OS can compare format performance.</p> : null}
    {intelligence.summary ? <section className="intelligence-summary" aria-label="Content intelligence summary"><article><p className="overline">Strongest format</p><strong>{intelligence.summary.strongest_content_format?.name ?? "--"}</strong><small>{intelligence.summary.strongest_content_format ? `Score ${intelligence.summary.strongest_content_format.average_score} · ${intelligence.summary.strongest_content_format.sample_size} posts` : "Awaiting data"}</small></article><article><p className="overline">Weakest format</p><strong>{intelligence.summary.weakest_content_format?.name ?? "--"}</strong><small>{intelligence.summary.weakest_content_format ? `Score ${intelligence.summary.weakest_content_format.average_score} · ${intelligence.summary.weakest_content_format.sample_size} posts` : "Awaiting data"}</small></article><article><p className="overline">Engagement driver</p><strong>{intelligence.summary.strongest_engagement_driver?.split(" ")[0] ?? "--"}</strong><small>{intelligence.summary.strongest_engagement_driver ?? "Awaiting data"}</small></article><article className="direction-card"><p className="overline">Recommended direction</p><strong>{intelligence.summary.recommended_content_direction ?? "Connect data to receive a direction."}</strong></article></section> : null}
    <section className="intelligence-controls" aria-label="Content filters"><div className="filter-tabs">{(["All", "Best performing", "Needs improvement"] as const).map((filter) => <button className={performanceFilter === filter ? "active" : ""} key={filter} onClick={() => setPerformanceFilter(filter)}>{filter}</button>)}</div><label><span className="sr-only">Filter by content category or type</span><select value={contentFilter} onChange={(event) => setContentFilter(event.target.value)}>{options.map((option) => <option key={option}>{option}</option>)}</select></label></section>
    <section className="intelligence-list" aria-live="polite">{visibleItems.length ? visibleItems.map((item) => <IntelligenceCard item={item} key={item.content.id} />) : <p className="dashboard-empty">No posts match these filters.</p>}</section>
  </div>;
}
