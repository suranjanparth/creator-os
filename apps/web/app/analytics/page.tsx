"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { TrendChart } from "@/components/TrendChart";
import { fetchAnalytics, type AnalyticsData } from "@/features/analytics/api";
import { useActiveCreatorId } from "@/features/creator/scope";

function formatDate(isoDate: string | undefined) {
  if (!isoDate) return "—";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(`${isoDate}T12:00:00`));
}

function compact(value: number | null | undefined) {
  if (value === null || value === undefined) return "--";
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [error, setError] = useState(false);
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setAnalytics(null);
    setError(false);
    if (!creatorId) return;
    void fetchAnalytics(creatorId).then(setAnalytics).catch(() => setError(true));
  }, [creatorId]);

  if (error) {
    return <div className="page analytics-page">
      <PageHeader eyebrow="Performance intelligence" title="The story behind the numbers." description="Your analytics could not be reached." />
      <section className="dashboard-message" role="alert">
        <h2>We couldn&apos;t load your analytics.</h2>
        <p>Check that the Creator OS API is running, then try again.</p>
        <button className="button button-primary" onClick={() => { setError(false); if (creatorId) void fetchAnalytics(creatorId).then(setAnalytics).catch(() => setError(true)); }}>Try again</button>
      </section>
    </div>;
  }

  if (!analytics) {
    return <div className="page analytics-page">
      <PageHeader eyebrow="Performance intelligence" title="The story behind the numbers." description="Loading your performance analytics." />
      <div className="dashboard-loading" aria-live="polite"><span /><span /><span /></div>
    </div>;
  }

  const totals = analytics.totals;
  const hasData = analytics.total_posts > 0;
  const trendValues = analytics.trend.map((point) => point.views);
  const anatomy = analytics.engagement_anatomy;
  const topPost = analytics.top_posts[0];

  return <div className="page analytics-page">
    <PageHeader eyebrow="Performance intelligence" title="The story behind the numbers." description="Every number here is derived from your persisted published content — no estimates."><span className="confidence">{analytics.total_posts} posts analyzed</span></PageHeader>

    {!hasData || !totals ? <section className="dashboard-message">
      <h2>No published content to analyze yet.</h2>
      <p>Import published content with performance data and your analytics will appear here.</p>
      <Link className="button button-primary" href="/content">Import content <span>→</span></Link>
    </section> : <>
      <section className="metrics-grid">{[
        { label: "Total views", value: compact(totals.views), detail: "Across published content" },
        { label: "Engagement rate", value: `${totals.average_engagement_rate.toFixed(1)}%`, detail: "Average per published post" },
        { label: "Total engagements", value: compact(totals.engagements), detail: "Likes + comments + shares" },
        { label: "Total content", value: String(analytics.total_posts), detail: "Published posts" },
      ].map((metric) => <article className="metric" key={metric.label}><p>{metric.label}</p><strong>{metric.value}</strong><small>{metric.detail}</small></article>)}</section>

      <section className="dashboard-grid top-grid">
        <article className="panel">
          <div className="panel-heading"><div><p className="overline">Performance trend</p><h2>Views per published post</h2></div><span className="period">Published content</span></div>
          {analytics.trend.length > 1 ? <><TrendChart data={trendValues} label="Views per published post" /><div className="chart-axis"><span>{formatDate(analytics.trend[0]?.date)}</span><span>{formatDate(analytics.trend.at(-1)?.date)}</span></div></> : <div className="chart-empty"><span className="chart-empty-line" /><p>More published posts are needed to build a trend.</p></div>}
        </article>
        <article className="next-action">
          <p className="overline">Top post</p>
          <h2>{topPost?.title ?? "No standout post yet"}</h2>
          <p>{topPost ? `${topPost.platform} · ${topPost.content_type} with ${compact(topPost.views)} views and ${topPost.engagement_rate?.toFixed(1) ?? "--"}% engagement.` : "Your top performing post will appear here once content data is available."}</p>
          <p className="insight-evidence">{compact(totals.views)} total views across {analytics.total_posts} published posts.</p>
          <Link href="/recommendations" className="text-link">Turn this into a plan <span>→</span></Link>
        </article>
      </section>

      <section className="dashboard-grid lower-grid">
        <article className="panel">
          <div className="panel-heading"><div><p className="overline">Platform comparison</p><h2>Where your ideas travel</h2></div></div>
          {analytics.platform_breakdown.length ? <div className="dashboard-content-list">{analytics.platform_breakdown.map((platform) => <div className="dashboard-post" key={platform.platform}><span className="post-art" aria-hidden="true">{platform.platform.slice(0, 1)}</span><div><strong>{platform.platform}</strong><small>{platform.posts} post{platform.posts === 1 ? "" : "s"} · {compact(platform.views)} views</small></div><div className="post-stat"><strong>{platform.share}%</strong><small>of views</small></div></div>)}</div> : <p className="dashboard-empty">Platform breakdown will appear here once content is available.</p>}
        </article>
        <article className="panel">
          <div className="panel-heading"><div><p className="overline">Best performing</p><h2>Posts worth repeating</h2></div><Link className="text-link" href="/content">Create similar <span>→</span></Link></div>
          {analytics.top_posts.length ? <div className="dashboard-content-list">{analytics.top_posts.map((post) => <div className="dashboard-post" key={post.id}><span className="post-art" aria-hidden="true">{post.platform.slice(0, 1)}</span><div><strong>{post.title}</strong><small>{post.platform} · {post.content_type}</small></div><div className="post-stat"><strong>{post.engagement_rate === null ? "--" : `${post.engagement_rate.toFixed(1)}%`}</strong><small>engagement</small></div></div>)}</div> : <p className="dashboard-empty">Top posts will appear here once content is available.</p>}
        </article>
      </section>

      {anatomy ? <article className="panel" style={{ marginTop: 18 }}>
        <p className="overline">Engagement anatomy</p>
        <h2>How your audience interacts.</h2>
        <p>Split of likes, comments, and shares across {anatomy.sample_size} published posts.</p>
        <div className="dashboard-content-list">{[["Likes", anatomy.likes_share], ["Shares", anatomy.shares_share], ["Comments", anatomy.comments_share]].map(([label, share]) => <div className="dashboard-post" key={label}><span className="post-art" aria-hidden="true">{String(label).slice(0, 1)}</span><div><strong>{label}</strong><small>{share}% of all engagements</small></div></div>)}</div>
      </article> : null}
    </>}
  </div>;
}
