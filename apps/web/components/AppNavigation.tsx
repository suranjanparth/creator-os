"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchCreatorProfile, fetchCreatorProfiles, type CreatorProfile } from "@/features/creator/api";
import { useActiveCreatorId } from "@/features/creator/scope";

const navigationItems = [
  ["Dashboard", "/dashboard"],
  ["Content", "/content"],
  ["Intelligence", "/content-intelligence"],
  ["Analytics", "/analytics"],
  ["Creator DNA", "/creator-dna"],
  ["Recommendations", "/recommendations"],
  ["Connect", "/connect"],
] as const;

function profileInitials(name: string) {
  return name.split(" ").filter(Boolean).map((part) => part[0]).join("").slice(0, 2).toUpperCase();
}

export function AppNavigation() {
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [profiles, setProfiles] = useState<CreatorProfile[]>([]);
  const [unavailable, setUnavailable] = useState(false);
  const { creatorId, selectCreator } = useActiveCreatorId();

  useEffect(() => {
    let active = true;
    fetchCreatorProfiles().then((fetched) => {
      if (active) setProfiles(fetched);
    }).catch(() => {
      if (active) setProfiles([]);
    });
    return () => {
      active = false;
    };
  }, [creatorId]);

  useEffect(() => {
    let active = true;
    setProfile(null);
    setUnavailable(false);
    fetchCreatorProfile(creatorId)
      .then((fetched) => {
        if (active) setProfile(fetched);
      })
      .catch(() => {
        if (active) setUnavailable(true);
      });
    return () => {
      active = false;
    };
  }, [creatorId]);

  return (
    <nav className="navigation" aria-label="Primary navigation">
      <Link href="/dashboard" className="brand"><span className="brand-mark">C</span><span>CREATOR<br />OS</span></Link>
      <div className="nav-links">{navigationItems.map(([label, href]) => (
        <Link href={href} key={href}>
          {label}
        </Link>
      ))}</div>
      <div className="profile-chip">
        <span className="avatar">{profile ? profileInitials(profile.name) : "C"}</span>
        <span>
          <strong>{profile?.name ?? "Creator"}</strong>
          <small>{profile?.handle ?? (unavailable ? "Profile unavailable" : "Loading profile…")}</small>
        </span>
        {profiles.length > 1 ? <label className="creator-switcher">
          <span className="sr-only">Active creator</span>
          <select aria-label="Active creator" value={creatorId} onChange={(event) => selectCreator(event.target.value)}>
            {profiles.map((creator) => <option key={creator.creator_id} value={creator.creator_id}>{creator.name}</option>)}
          </select>
        </label> : null}
      </div>
    </nav>
  );
}
