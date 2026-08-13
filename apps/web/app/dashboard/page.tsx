"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { TrendChart } from "@/components/TrendChart";
import { useActiveCreatorId } from "@/features/creator/scope";
import { fetchDashboard, type DashboardContent, type DashboardData, type DashboardMetric } from "@/features/dashboard/api";

const metricDefinitions = [
  { label: "Total views", key: "total views", detail: "Across published content" },
  { label: "Engagement rate", key: "engagement rate", detail: "Audience interactions per view" },
  { label: "Total content", key: "total content", detail: "Published posts" },
] as const;

function formatMetric(metric: DashboardMetric | undefined, label: string) {
  if (metric?.value === null || metric?.value === undefined) return "--";
  if (label === "Engagement rate") return `${metric.value.toFixed(1)}%`;
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(metric.value);
}

function ContentList({ content, emptyMessage }: { content: DashboardContent[]; emptyMessage: string }) {
  if (!content.length) return <p className="dashboard-empty">{emptyMessage}</p>;

  return <div className="dashboard-content-list">
    {content.map((post) => <article className="dashboard-post" key={post.id}>
      <span className="post-art" aria-hidden="true">{post.platform.slice(0, 1)}</span>
      <div><strong>{post.title}</strong><small>{post.platform} · {post.content_type} · {post.category}</small><small className="post-engagement">{post.likes?.toLocaleString() ?? "--"} likes · {post.comments?.toLocaleString() ?? "--"} comments · {post.shares?.toLocaleString() ?? "--"} shares</small></div>
      <div className="post-stat"><strong>{post.views === null ? "--" : new Intl.NumberFormat("en", { notation: "compact" }).format(post.views)}</strong><small>views</small></div>
      <div className="post-stat"><strong>{post.engagement_rate === null ? "--" : `${post.engagement_rate.toFixed(1)}%`}</strong><small>{post.published_at ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(`${post.published_at}T12:00:00`)) : "engagement"}</small></div>
    </article>)}
  </div>;
}

function DashboardLoading() {
  return <div className="dashboard-loading" aria-live="polite"><span /><span /><span /></div>;
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [error, setError] = useState(false);
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setDashboard(null);
    setError(false);
    void fetchDashboard(creatorId).then(setDashboard).catch(() => setError(true));
  }, [creatorId]);

  if (error) return <div className="page dashboard-page"><PageHeader eyebrow="Dashboard" title="Your creator workspace" description="Your dashboard could not be reached." /><section className="dashboard-message" role="alert"><h2>We couldn&apos;t load your dashboard.</h2><p>Check that the Creator OS API is running, then try again.</p><button className="button button-primary" onClick={() => { setError(false); void fetchDashboard(creatorId).then(setDashboard).catch(() => setError(true)); }}>Try again</button></section></div>;

  if (!dashboard) return <div className="page dashboard-page"><PageHeader eyebrow="Dashboard" title="Your creator workspace" description="Loading your creator intelligence." /><DashboardLoading /></div>;

  const creator = dashboard.creator;
  const metricFor = (key: string) => dashboard.metrics.find((metric) => metric.label.toLowerCase() === key);
  const hasTrend = dashboard.performance_trend.length > 1;
  const trendValues = dashboard.performance_trend.map((point) => point.views);
  const trendStart = dashboard.performance_trend[0]?.date;
  const trendEnd = dashboard.performance_trend.at(-1)?.date;

  return <div className="page dashboard-page">
    <PageHeader eyebrow="Creator dashboard" title={creator ? `Welcome back, ${creator.name.split(" ")[0]}.` : "Your creator workspace"} description={creator ? "A focused view of your performance, content, and next opportunity." : "Connect your creator data to turn every post into a clearer next move."}>
      <Link className="button button-primary" href="/content">New content idea <span>+</span></Link>
    </PageHeader>

    <section className="creator-overview" aria-label="Creator overview">
      <div className="creator-mark">{creator?.name.slice(0, 1) ?? "C"}</div>
      <div><p className="overline">Creator overview</p><h2>{creator?.name ?? "No creator connected"}</h2><p>{creator ? [creator.handle, creator.niche, creator.audience].filter(Boolean).join(" · ") : "Add creator and content data to begin tracking your performance."}</p></div>
      {creator?.followers !== null && creator?.followers !== undefined ? <strong className="follower-count">{new Intl.NumberFormat("en", { notation: "compact" }).format(creator.followers)}<small>followers</small></strong> : null}
    </section>

    <section className="metrics-grid" aria-label="Performance metrics">{metricDefinitions.map((definition) => {
      const metric = metricFor(definition.key);
      return <article className="metric" key={definition.key}><p>{definition.label}</p><strong>{formatMetric(metric, definition.label)}</strong>{metric?.change !== null && metric?.change !== undefined ? <span className={metric.change >= 0 ? "positive" : "negative"}>{metric.change >= 0 ? "+" : ""}{metric.change.toFixed(1)}%</span> : <span className="metric-pending">Awaiting data</span>}<small>{metric?.detail ?? definition.detail}</small></article>;
    })}</section>

    <section className="dashboard-grid top-grid">
      <article className="panel momentum-panel"><div className="panel-heading"><div><p className="overline">Performance trend</p><h2>Content momentum</h2></div><span className="period">Published content</span></div>{hasTrend ? <><TrendChart data={trendValues} label="Creator performance trend" /><div className="chart-axis"><span>{trendStart ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(`${trendStart}T12:00:00`)) : "Earlier"}</span><span>{trendEnd ? new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(`${trendEnd}T12:00:00`)) : "Today"}</span></div></> : <div className="chart-empty"><span className="chart-empty-line" /><p>Performance trends will appear as content data arrives.</p></div>}</article>
      <article className="next-action"><p className="overline">Initial intelligence</p><div className="orbital-mark"><span>AI</span></div><h2>{dashboard.insight.title}</h2><p>{dashboard.insight.summary}</p>{dashboard.insight.evidence ? <p className="insight-evidence">{dashboard.insight.evidence}</p> : null}{dashboard.insight.method ? <small className="insight-method">{dashboard.insight.method}</small> : null}<Link href="/recommendations" className="text-link">Explore recommendations <span>→</span></Link></article>
    </section>

    <section className="dashboard-grid lower-grid">
      <article className="panel activity-panel"><div className="panel-heading"><div><p className="overline">Best performing content</p><h2>Posts worth learning from</h2></div><Link className="text-link" href="/analytics">All analytics <span>→</span></Link></div><ContentList content={dashboard.best_performing_content} emptyMessage="Your top-performing posts will appear here once performance data is available." /></article>
      <article className="panel activity-panel"><div className="panel-heading"><div><p className="overline">Recent content</p><h2>Latest published work</h2></div><Link className="text-link" href="/content">Open content <span>→</span></Link></div><ContentList content={dashboard.recent_content} emptyMessage="Published content will appear here when it is connected to Creator OS." /></article>
    </section>
  </div>;
}
