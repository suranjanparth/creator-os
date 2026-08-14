"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/PageHeader";
import { fetchRecommendations, type RecommendationsData } from "@/features/recommendations/api";
import { useActiveCreatorId } from "@/features/creator/scope";

export default function RecommendationsPage() {
  const [data, setData] = useState<RecommendationsData | null>(null);
  const [error, setError] = useState(false);
  const { creatorId } = useActiveCreatorId();

  useEffect(() => {
    setData(null);
    setError(false);
    if (!creatorId) {
      setError(true);
      return;
    }
    void fetchRecommendations(creatorId).then(setData).catch(() => setError(true));
  }, [creatorId]);

  if (error) {
    return <div className="page recommendations-page">
      <PageHeader eyebrow="Signal-led strategy" title="Do the work that has momentum." description="Your recommendations could not be reached." />
      <section className="dashboard-message" role="alert">
        <h2>We couldn&apos;t load your recommendations.</h2>
        <p>Check that the Creator OS API is running, then try again.</p>
        <button className="button button-primary" onClick={() => { setError(false); if (creatorId) void fetchRecommendations(creatorId).then(setData).catch(() => setError(true)); }}>Try again</button>
      </section>
    </div>;
  }

  if (!data) {
    return <div className="page recommendations-page">
      <PageHeader eyebrow="Signal-led strategy" title="Do the work that has momentum." description="Loading your next moves." />
      <div className="dashboard-loading" aria-live="polite"><span /><span /><span /></div>
    </div>;
  }

  return <div className="page recommendations-page">
    <PageHeader eyebrow="Signal-led strategy" title="Do the work that has momentum." description="Each recommendation connects a next move to the evidence in your published content."><span className="confidence">{data.total_posts} posts analyzed</span></PageHeader>
    {!data.recommendations.length ? <section className="dashboard-message"><h2>Not enough content to recommend next moves yet.</h2><p>{data.priority_copy}</p><a className="button button-primary" href="/content">Import content <span>→</span></a></section> : <>
      <section className="recommendation-intro"><div><p className="overline">Priority signal</p><h2>{data.priority_signal}</h2></div><p>{data.priority_copy}</p></section>
      <section className="recommendation-list">{data.recommendations.map((recommendation, index) => <article className="recommendation" key={recommendation.title}><div className="rec-index">0{index + 1}</div><div className="rec-main"><span className="rec-tag">{recommendation.tag}</span><h2>{recommendation.title}</h2><p>{recommendation.description}</p><a className="button button-primary" href={recommendation.href ?? "/content"}>{recommendation.action} <span>→</span></a></div><div className="rec-evidence"><p className="overline">Why this, now</p><p>{recommendation.evidence}</p><span className="evidence-pill">{recommendation.sample_size !== null && recommendation.sample_size !== undefined ? `${recommendation.sample_size} posts` : "Insufficient data"}</span></div></article>)}</section>
      {data.opportunities.length ? <section className="opportunity-grid">{data.opportunities.map((opportunity, index) => <article className={index % 2 === 1 ? "opportunity-card dark" : "opportunity-card"} key={opportunity.title}><p className="overline">{index % 2 === 0 ? "Topic to explore" : "Improvement area"}</p><h2>{opportunity.title}</h2><p>{opportunity.description}</p><a className="text-link" href={opportunity.href}>{index % 2 === 0 ? "Develop an angle" : "See performance evidence"} <span>→</span></a></article>)}</section> : null}
    </>}
  </div>;
}
