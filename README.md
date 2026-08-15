# CREATOR OS

**AI-powered Creator Intelligence, Strategy & Content Operating System.**

CREATOR OS is a full-stack portfolio project designed to help content creators understand performance, identify what is working, and turn creator data into practical next-step recommendations.

> **Portfolio status:** Working full-stack prototype with a Next.js dashboard, FastAPI backend, persistent creator/content data, deterministic analytics, ingestion pipeline, and a clean provider boundary for future real platform integrations.

---

## 🚀 What CREATOR OS Does

CREATOR OS brings creator analytics and strategy into one workflow:

- 📊 **Dashboard** — creator performance metrics, trends and content summaries
- 🧠 **Content Intelligence** — per-post performance analysis
- 🧬 **Creator DNA** — format/platform patterns and creative insights
- 📈 **Analytics** — platform breakdowns, top posts, trends and engagement anatomy
- 💡 **Recommendations** — evidence-linked next-move suggestions
- 👤 **Creator Profiles** — persisted creator profiles with active creator selection
- 📥 **Content Ingestion** — single-record and batch content ingestion
- 🔌 **Provider Boundary** — designed for future Instagram/other platform integrations
- 🛡️ **Honest Data States** — the UI distinguishes development data from empty states instead of inventing analytics

---

## 🧠 Product Workflow

```text
Creator Profile / Content Data
             ↓
      Ingestion Pipeline
             ↓
      Persistent Database
             ↓
   ┌─────────┼─────────┐
   ↓         ↓         ↓
Dashboard  Analytics  Content Intelligence
   ↓         ↓         ↓
   └─────────┼─────────┘
             ↓
        Creator DNA
             ↓
      Recommendations
             ↓
      Creator Next Move
```

The architecture keeps data ingestion, persistence, analytics and presentation separated so the product can evolve without rebuilding the entire application.

---

## 🏗️ Architecture

```text
CREATOR OS
│
├── apps/web
│   └── Next.js + TypeScript dashboard
│
├── apps/api
│   ├── FastAPI REST API
│   ├── SQLAlchemy persistence layer
│   ├── Alembic migrations
│   ├── Analytics / creator intelligence domains
│   └── Ingestion + provider boundary
│
├── PostgreSQL
│   └── Source of truth for creator/content data
│
└── Docker
    └── Containerized local development
```

The browser communicates with FastAPI through `NEXT_PUBLIC_API_BASE_URL`. Server-only credentials remain in the API environment.

---

## ✨ Key Features

| Feature | What it does |
|---|---|
| **Creator Dashboard** | Summarizes creator performance, trends and content |
| **Content Intelligence** | Produces deterministic per-post performance insights |
| **Creator DNA** | Identifies format/platform shares, best formats and creative patterns |
| **Analytics** | Shows totals, platform breakdowns, top posts and engagement anatomy |
| **Recommendations** | Generates evidence-linked next-move recommendations |
| **Creator Management** | Supports persisted creator profiles and creator selection |
| **Content Ingestion** | Supports individual and batch content ingestion |
| **Idempotent Imports** | Re-importing the same normalized payload does not duplicate content |
| **Provider Boundary** | Separates external platform integrations from core product logic |
| **Honest Empty States** | Avoids fabricated metrics when creator data is unavailable |

---

## 🛠️ Tech Stack

### Frontend
- **Next.js**
- **TypeScript**

### Backend
- **Python**
- **FastAPI**
- **SQLAlchemy**
- **Alembic**

### Data
- **PostgreSQL** for persistent environments
- **SQLite** fallback for simple local development

### Development
- **Docker / Docker Compose**
- **npm workspaces**
- **Pytest**

---

## 📁 Project Structure

```text
creator-os/
├── apps/
│   ├── web/                 # Next.js + TypeScript frontend
│   └── api/                 # FastAPI backend
│       ├── app/
│       │   └── domains/     # Product domains and ingestion pipeline
│       ├── tests/            # Backend tests
│       ├── requirements.txt
│       └── alembic/          # Database migrations
├── .env.example
├── docker-compose.yml
├── package.json
└── README.md
```

---

## 💻 Run Locally

### Prerequisites

- Node.js 22+
- Python 3.11+
- Docker Desktop (recommended) or a local PostgreSQL-compatible setup

### 1. Clone the repository

```bash
git clone https://github.com/suranjanparth/creator-os.git
cd creator-os
```

### 2. Install dependencies

Frontend:

```bash
npm install
```

Backend:

```bash
python3 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements.txt
```

### 3. Configure environment files

```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Do **not** commit secrets or real platform credentials.

### 4. Start with Docker

```bash
docker compose up --build
```

### Or run without Docker

Start the frontend:

```bash
npm run dev:web
```

Start the API in a second terminal:

```bash
apps/api/.venv/bin/uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

Open:

```text
http://localhost:3000
```

The frontend health card checks the API at `http://localhost:8000/api/v1/health` by default.

---

## 🗄️ Database & Data Model

For local development, if `DATABASE_URL` is not configured, the API automatically uses a file-backed SQLite database and creates the required persistence tables. A documented development dataset is seeded for demonstration.

For PostgreSQL environments, set `DATABASE_URL` in `apps/api/.env` and run migrations:

```bash
cd apps/api
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
```

PostgreSQL is the intended source of truth outside simple local development.

---

## 🔌 Ingestion & Integration Design

The ingestion system accepts normalized creator payloads before writing them to the database. This keeps external platform-specific logic separate from the core product.

Example normalized payload:

```json
{
  "creator_id": "maya-chen",
  "profile": {
    "name": "Maya Chen",
    "handle": "@mayamakes",
    "platform": "Instagram",
    "follower_count": 84200
  },
  "content": [
    {
      "id": "post-1",
      "platform": "Instagram",
      "content_type": "Reel",
      "category": "Creative systems",
      "title": "A reel",
      "views": 12000
    }
  ]
}
```

The import response reports created, updated, skipped and failed items. Re-importing the same payload is designed to be idempotent.

### Provider boundary

External platforms plug into `apps/api/app/domains/ingestion/providers` through a normalized provider interface. The included Instagram integration is intentionally an integration seam: it does not fabricate platform data and remains unconfigured until valid credentials are supplied.

---

## 📡 API Endpoints

All endpoints are served under `/api/v1`.

| Endpoint | Purpose |
|---|---|
| `GET /health` | API health/status |
| `GET /dashboard` | Dashboard metrics and trends |
| `GET /analytics` | Analytics and engagement breakdown |
| `GET /content-intelligence` | Per-post performance analysis |
| `GET /creator-dna` | Creator patterns and creative insights |
| `GET /recommendations` | Evidence-linked recommendations |
| `GET /creators` | List persisted creators |
| `GET /creators/{creator_id}` | Fetch one creator profile |
| `POST /creators` | Create/update creator profile |
| `GET /content` | Retrieve creator content |
| `POST /content` | Ingest one content record |
| `POST /content/ingest` | Batch content ingestion |
| `POST /ingestion/import` | Import normalized creator + content payload |

Most creator-facing endpoints accept an optional `creator_id` query parameter.

---

## 🧪 Tests & Quality Checks

Run the main checks with:

```bash
npm run typecheck:web
npm run test:web
npm run build:web
apps/api/.venv/bin/pytest apps/api/tests
```

The project is structured so frontend type safety, frontend tests, production builds and backend tests can be checked independently.

---

## 🔐 Data & Security Approach

- API secrets remain server-side.
- Platform credentials are supplied through environment variables rather than source code.
- Empty states are shown when real creator data is unavailable.
- Development data is explicitly identified instead of being presented as real platform analytics.
- External platform access is isolated behind a provider boundary.

---

## ⚠️ Current Limitations

- Real Instagram/Meta data requires valid Meta application credentials and approved API access.
- The current development experience uses persisted/seeded data when live platform credentials are unavailable.
- Recommendation logic is deterministic rather than an LLM-powered strategy engine.
- The product is a portfolio-stage prototype, not a production SaaS platform.
- Authentication, multi-user authorization and production observability can be expanded further.

---

## 🔮 Future Improvements

- 🔗 Live Instagram and YouTube integrations
- 🤖 LLM-powered content strategy and recommendation generation
- 📊 Advanced creator benchmarking
- 📈 Historical performance forecasting
- 🧠 AI-assisted content idea generation
- 🔐 User authentication and multi-creator workspaces
- ☁️ Production cloud deployment
- 📱 Mobile-friendly creator workflow
- 🔔 Automated alerts for performance changes

---

## 📌 Project Highlights

**Problem:** Creators often have performance data scattered across platforms, making it difficult to understand what content is working and what to do next.

**Solution:** CREATOR OS centralizes creator data into a dashboard that transforms persisted content into analytics, creator patterns and evidence-linked recommendations.

**Engineering approach:** A modular full-stack architecture separates the Next.js frontend, FastAPI backend, database layer, analytics domains and external-platform ingestion boundary.

**Result:** A working end-to-end creator intelligence prototype designed to evolve from development data into real platform integrations.

---

## 📄 Resume-Ready Description

> **CREATOR OS** — Built a full-stack creator intelligence platform using Next.js, TypeScript, FastAPI and PostgreSQL to analyze creator content, surface performance patterns, generate evidence-linked recommendations, and support extensible social-platform data ingestion through a provider architecture.

---

## 👨‍💻 Portfolio Note

CREATOR OS was built as a student AI/product engineering portfolio project to demonstrate practical skills across **full-stack development, REST APIs, databases, analytics, system architecture, data ingestion and product-oriented UI design**.

---

**Built with Next.js · TypeScript · FastAPI · Python · PostgreSQL · SQLAlchemy · Docker**