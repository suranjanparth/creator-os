"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { BackendStatus } from "@/features/health/BackendStatus";
import { fetchCreatorProfiles, type CreatorProfile } from "@/features/creator/api";

export default function HomePage() {
  const [creators, setCreators] = useState<CreatorProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCreatorProfiles()
      .then(setCreators)
      .catch(() => setCreators([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="hero">
      <p className="eyebrow">Creator intelligence foundation</p>
      <h1>CREATOR OS</h1>
      <p className="lead">
        AI-powered Creator Intelligence, Strategy and Content Operating System.
      </p>
      <BackendStatus />

      {loading ? (
        <div style={{ marginTop: "2rem", textAlign: "center" }}>
          <p>Loading your creators...</p>
        </div>
      ) : creators.length === 0 ? (
        <div style={{ marginTop: "2rem", textAlign: "center" }}>
          <p className="success">You don't have any creators yet.</p>
          <Link href="/connect" className="button button-primary" style={{ marginTop: "1rem" }}>
            Create your first creator <span>→</span>
          </Link>
        </div>
      ) : (
        <div style={{ marginTop: "2rem", textAlign: "center" }}>
          <p className="success">You have {creators.length} creator(s) connected.</p>
          <Link href="/dashboard" className="button button-primary" style={{ marginTop: "1rem" }}>
            Open dashboard <span>→</span>
          </Link>
        </div>
      )}
    </section>
  );
}
