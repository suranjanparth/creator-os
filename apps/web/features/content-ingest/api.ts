export type ContentIngestItemInput = {
  id: string;
  platform: string;
  content_type: string;
  category: string;
  title: string;
  views?: number | null;
  likes?: number | null;
  comments?: number | null;
  shares?: number | null;
  engagement_rate?: number | null;
  published_at?: string | null;
};

export type ContentIngestItemResult = {
  id: string;
  status: "created" | "skipped";
  detail: string | null;
};

export type ContentIngestResult = {
  creator_id: string;
  received: number;
  created: number;
  skipped: number;
  items: ContentIngestItemResult[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function ingestContentBatch(
  creatorId: string,
  items: ContentIngestItemInput[],
): Promise<ContentIngestResult> {
  const response = await fetch(`${apiBaseUrl}/api/v1/content/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ creator_id: creatorId, items }),
  });

  if (!response.ok) {
    throw new Error(`Content ingest request failed with status ${response.status}`);
  }

  return (await response.json()) as ContentIngestResult;
}
