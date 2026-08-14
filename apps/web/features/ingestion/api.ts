export type ImportedContentItemInput = {
  id: string;
  platform: string;
  url?: string | null;
  content_type: string;
  category: string;
  title: string;
  views?: number | null;
  likes?: number | null;
  comments?: number | null;
  shares?: number | null;
  saves?: number | null;
  reach?: number | null;
  impressions?: number | null;
  engagement_rate?: number | null;
  published_at?: string | null;
};

export type ImportedProfileInput = {
  name: string;
  handle?: string | null;
  profile_url?: string | null;
  niche?: string | null;
  platform?: string | null;
  audience?: string | null;
  follower_count?: number | null;
};

export type CreatorImportPayload = {
  creator_id: string;
  profile: ImportedProfileInput;
  content?: ImportedContentItemInput[];
};

export type ContentItemOutcome = {
  id: string;
  status: "created" | "updated" | "skipped" | "error";
  detail: string | null;
};

export type CreatorImportResult = {
  creator_id: string;
  profile_status: "created" | "updated" | "unchanged";
  content_received: number;
  created: number;
  updated: number;
  skipped: number;
  errors: number;
  items: ContentItemOutcome[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function importCreator(payload: CreatorImportPayload): Promise<CreatorImportResult> {
  const response = await fetch(`${apiBaseUrl}/api/v1/ingestion/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }

  return (await response.json()) as CreatorImportResult;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item: { msg?: string }) => item.msg ?? "Invalid value")
        .join("; ");
    }
  } catch {
    // Non-JSON error body; fall through to the status-based message.
  }
  return `Creator import request failed with status ${response.status}`;
}
