"use client";

import { useCallback, useEffect, useState } from "react";

export const DEVELOPMENT_CREATOR_ID = "maya-chen";

const ACTIVE_CREATOR_STORAGE_KEY = "creator-os.active-creator-id";
const ACTIVE_CREATOR_CHANGE_EVENT = "creator-os:active-creator-changed";

function normalizeCreatorId(creatorId: string | null | undefined): string {
  return creatorId?.trim() || DEVELOPMENT_CREATOR_ID;
}

export function getActiveCreatorId(): string {
  if (typeof window === "undefined") return DEVELOPMENT_CREATOR_ID;
  return normalizeCreatorId(window.localStorage.getItem(ACTIVE_CREATOR_STORAGE_KEY));
}

export function saveActiveCreatorId(creatorId: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACTIVE_CREATOR_STORAGE_KEY, normalizeCreatorId(creatorId));
  window.dispatchEvent(new Event(ACTIVE_CREATOR_CHANGE_EVENT));
}

export function useActiveCreatorId() {
  const [creatorId, setCreatorId] = useState(DEVELOPMENT_CREATOR_ID);

  useEffect(() => {
    const sync = () => setCreatorId(getActiveCreatorId());
    sync();
    window.addEventListener(ACTIVE_CREATOR_CHANGE_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(ACTIVE_CREATOR_CHANGE_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const selectCreator = useCallback((nextCreatorId: string) => {
    saveActiveCreatorId(nextCreatorId);
  }, []);

  return { creatorId, selectCreator };
}
