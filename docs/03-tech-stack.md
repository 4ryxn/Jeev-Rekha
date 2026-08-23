# Jeev Rekha — Technical Stack and Engineering Architecture

**Version:** 1.0  
**Status:** Hackathon MVP technical decision record  
**Companion documents:** `01-product-requirements.md`, `02-ui-ux-design.md`

---

## 1. Engineering objective

Build a credible, deployed web application that can register livestock movement events, evaluate outbreak-related route risk, trace exposure paths and work through temporary connectivity loss.

The engineering strategy is deliberately simple:

> **One modern web client + one Python API + one spatial PostgreSQL database + one explainable graph-analysis module.**

This gives us a serious architecture without adding Kafka, a separate graph database, WebRTC, RFID hardware or a complex microservice mesh before the core decision workflow works.

## 2. Chosen stack at a glance

| Layer | Choice | Why it fits Jeev Rekha |
|---|---|---|
| Web application | Next.js + React + TypeScript | Strong web UI, file-based routing, deployable PWA shell |
| Styling | Tailwind CSS + reusable local components | Fast, consistent implementation of the UI/UX document |
| Client state | TanStack Query + React state | Cache API data and handle loading/error states cleanly |
| Forms | React Hook Form + Zod | Fast kiosk forms with type-safe validation |
| Offline storage | IndexedDB via Dexie | Queue events locally when connectivity drops |
| Maps | MapLibre GL JS | Interactive, web-native mapping with custom risk layers |
| API | FastAPI + Pydantic | Python-native, typed API that shares language with graph/risk logic |
| Persistence | PostgreSQL + PostGIS | One database for operational records, time data and geospatial queries |
| ORM/migrations | SQLAlchemy 2 + Alembic | Typed persistence layer and reproducible schema changes |
| Risk and tracing | Python rules + NetworkX | Explainable rules plus time-aware graph traversal |
| Scenario simulation | NumPy | Small stochastic simulations without a separate ML platform |
| Authentication | JWT + role-based API guards | Separate operator, vet, lab and admin permissions |
| Testing | Vitest/React Testing Library, pytest, Playwright | Test UI, rules/API and end-to-end demo flow |
| Local development | Docker Compose | Reproducible PostGIS database for every team member |
| Deployment | Vercel + Render + managed Postgres | Clear frontend/API/database separation; PostGIS-ready database option |

## 3. Architecture overview

```text
┌─────────────────────────────────────────────────────────┐
│  Next.js PWA                                              │
│  dashboard · kiosk forms · maps · reports · offline queue │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / JSON
                        ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI                                                   │
│  auth · validation · advisory · trace · reports · sync    │
└────────────┬────────────────────────────┬───────────────┘
             │ SQLAlchemy                 │ NetworkX/NumPy
             ▼                            ▼
┌──────────────────────────┐     ┌────────────────────────┐
│ PostgreSQL + PostGIS      │     │ Rule & graph services   │
│ locations · outbreaks     │     │ 4-state advisory        │
│ movements · events        │     │ rewind/forward trace    │
└──────────────────────────┘     │ scenario simulation     │
                                 └────────────────────────┘
```

## 4. Frontend stack

### 4.1 Framework

- **Next.js App Router**
- **React**
- **TypeScript**
- **Node.js 20.9+**

Use the App Router because it provides layouts, route conventions and a clean split between server-rendered page shells and client-only interactive screens. The official Next.js PWA guide also supports a manifest and service-worker workflow without needing a separate mobile application. [Next.js App Router](https://nextjs.org/docs/app), [Next.js PWA guide](https://nextjs.org/docs/app/guides/progressive-web-apps)

### 4.2 Frontend packages

| Package | Use |
|---|---|
| `tailwindcss` | Design tokens, layout and responsive styling |
| `clsx` + `tailwind-merge` | Safe conditional classes |
| `lucide-react` | Accessible icons for status, maps, sync and actions |
| `react-hook-form` | Consignment/outbreak form state |
| `zod` | Client-side form schemas; mirror critical backend validation |
| `@hookform/resolvers` | Connect Zod to React Hook Form |
| `@tanstack/react-query` | API cache, mutation state and refetching |
| `dexie` | IndexedDB wrapper for draft and offline event queue |
| `maplibre-gl` | Map, routes, risk zones and markers |
| `date-fns` | Date/time display and time-window formatting |
| `recharts` | Small evidence/metric charts only |

Do not add a generic component library until the visual system is implemented. Build the product components locally from the UI/UX document so the app does not look like a default template.

### 4.3 Frontend route map

```text
/
├── /login
├── /dashboard
├── /register/consignment
├── /register/outbreak
├── /register/symptom-signal
├── /map
├── /advisories/[id]
├── /trace/[outbreakId]
├── /reports
├── /review-queue
└── /settings/sync
```

### 4.4 PWA and offline design

The PWA is for **offline capture**, not for making every advanced feature offline.

| Capability | Offline behaviour |
|---|---|
| App shell and cached UI | Available |
| New consignment draft | Saved in IndexedDB |
| New event submission | Added to local sync queue |
| Previously opened advisory | Available from local cache |
| Full map tile coverage | Not guaranteed; show cached/limited state |
| Complex route/simulation computation | Requires a synced backend |
| Conflict resolution | Requires authorised review after sync |

**Sync protocol for MVP**

1. Every local event gets a UUID, device timestamp, actor role and `pending` status.
2. The client posts queued events to `POST /sync/events` when online.
3. The backend stores events append-only.
4. Non-conflicting events become `synced`.
5. Conflicting health/vaccination events become `review_required`—they are never last-write-wins.

## 5. Backend stack

### 5.1 Core packages

| Package | Use |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn` | Local/dev ASGI server |
| `pydantic` + `pydantic-settings` | Validation and environment configuration |
| `sqlalchemy` | ORM and database access |
| `alembic` | Database migrations |
| `psycopg` | PostgreSQL database driver |
| `python-jose` or `PyJWT` | JWT issue/verification |
| `pwdlib` or `passlib[bcrypt]` | Password hashing if local login is implemented |
| `networkx` | Graph representation and tracing algorithms |
| `numpy` | Repeatable stochastic scenario simulation |
| `httpx` | Integration testing and future external clients |
| `pytest` | Unit/integration tests |

FastAPI is chosen because the outbreak rules, graph traversal and simulator are Python workloads; its typed Pydantic models also make request contracts explicit. [FastAPI documentation](https://fastapi.tiangolo.com/)

### 5.2 Backend module boundaries

```text
app/
├── api/             # Routers and request/response contracts
├── core/            # Config, security, logging
├── db/              # Session, base model, migrations helpers
├── models/          # SQLAlchemy entities
├── schemas/         # Pydantic request/response models
├── services/
│   ├── advisory.py  # Green/Amber/Red/Grey rules + explanations
│   ├── evidence.py  # Evidence Coverage Score
│   ├── routing.py   # Preferred and safer-route assessment
│   ├── tracing.py   # Rewind/Fast-Forward graph analysis
│   ├── simulation.py# Scenario runner
│   └── sync.py      # Append-only event ingest + conflict detection
├── repositories/    # Query/read-write operations
└── tests/
```

### 5.3 API style

- REST + JSON only for the MVP.
- Version all endpoints under `/api/v1`.
- Validate every request in Pydantic before it reaches the service layer.
- Return an `explanation` array for any advisory, never only a colour/status.
- Use ISO 8601 UTC timestamps in APIs; localise only in the frontend.

Example endpoint groups:

```text
POST   /api/v1/auth/login
GET    /api/v1/locations
POST   /api/v1/outbreaks
POST   /api/v1/consignments
POST   /api/v1/advisories/evaluate
GET    /api/v1/advisories/{id}
GET    /api/v1/outbreaks/{id}/trace?direction=rewind
POST   /api/v1/outbreaks/{id}/simulate
POST   /api/v1/sync/events
GET    /api/v1/reports/advisory/{id}
```

## 6. Database and spatial model

### 6.1 Database choice

Use **PostgreSQL with PostGIS** rather than adding a database per problem type.

- PostgreSQL handles transactional operational data.
- PostGIS handles points, zones and route-risk intersection queries.
- The graph is created in memory from SQL query results for the small hackathon dataset.

PostGIS provides the geospatial features required for map filtering, geofencing and route-zone checks. [PostGIS documentation](https://postgis.net/documentation/)

### 6.2 Core tables

```text
users                    roles, authentication metadata
locations                village / market / checkpost / vet centre, point geometry
outbreaks                disease, status, counts, location, verification timestamps
consignments             species, count, origin, destination, vehicle reference
movement_events          time-stamped consignment/location/vehicle events
vehicles                 reference number and display metadata
symptom_signals          pre-confirmation observations
vaccination_events       claimed/verified vaccination evidence
advisories               result, score, reasons, route comparison
event_log                immutable offline/online history
review_cases             conflicts and authorised resolution
trace_runs               trace request metadata
trace_results            relevant entities and evidence paths
```

### 6.3 Spatial operations required

| Operation | Example |
|---|---|
| Geofence | Is the origin/destination inside an active outbreak zone? |
| Route intersection | Does the planned route intersect the relevant risk buffer? |
| Nearby search | Which villages/markets are within the configured radius? |
| Map bounds | Fetch only events visible in the current map viewport |

Use WGS 84 (`SRID 4326`) for stored location data. Create spatial indexes before testing map-heavy screens.

## 7. Risk, graph and simulation layer

### 7.1 Advisory engine: rules first

The advisory decision is a deterministic, configurable rule engine—not a black-box classifier.

```text
Inputs: outbreak status + route exposure + time window + vaccination evidence + coverage score
  ↓
Evaluate Red conditions first
  ↓
Evaluate Amber conditions
  ↓
Evaluate Grey coverage threshold
  ↓
Otherwise Green
  ↓
Return state + evidence score + reasons + recommended action
```

This ordering prevents low data coverage from accidentally looking Green.

### 7.2 Contact tracing

Use a NetworkX directed multigraph:

- **Nodes:** locations, consignments and vehicles.
- **Edges:** time-stamped movement or shared-contact events.
- **Filters:** disease incubation window, event type and verification status.

NetworkX is appropriate for a transparent controlled graph and supports graphs with attributed nodes and edges. [NetworkX](https://networkx.org/en/)

### 7.3 Scenario simulation

The simulator runs repeatable, small-scale Monte Carlo scenarios:

- use a seed for demo reproducibility;
- vary transmission/exposure assumptions within documented ranges;
- compare a baseline with one intervention (e.g., market closure or safer-route diversion);
- present ranges and percentages, never a single false-certainty prediction.

Simulation output is advisory only and remains separate from the formal four-state rule engine.

## 8. Authentication, roles and privacy

### MVP authentication plan

Use seeded demo accounts for the hackathon, each with a role:

```text
admin@jeevrekha.demo      → Administrator
vet@jeevrekha.demo        → Veterinary officer
operator@jeevrekha.demo   → Market/checkpost operator
lab@jeevrekha.demo        → Laboratory staff
```

Store hashed passwords only. Use short-lived access tokens and a refresh-token approach only if time permits.

### Minimum permissions

| Action | Operator | Vet | Lab | Admin |
|---|:---:|:---:|:---:|:---:|
| Register consignment | ✓ | ✓ | — | ✓ |
| Submit lab evidence | — | ✓ | ✓ | ✓ |
| Confirm/close outbreak | — | ✓ | — | ✓ |
| Resolve conflicts | — | ✓ | — | ✓ |
| View public-safe advisory | ✓ | ✓ | ✓ | ✓ |

Do not expose names, phone numbers or unnecessary farmer/transporter data on public map or report views.

## 9. Testing strategy

| Layer | Tool | What must be tested |
|---|---|---|
| Frontend UI | Vitest + React Testing Library | Forms, validation, risk badges and reason lists |
| Backend services | pytest | Advisory thresholds, coverage score, tracing time windows |
| API | pytest + httpx | Role checks, validation and report outputs |
| Database | Alembic migration tests | Fresh database reaches current schema |
| E2E | Playwright | Register consignment → Green → inject outbreak → Red → trace |
| Manual demo | Browser DevTools offline mode | Queue events, reconnect and verify sync/review state |

## 10. Local development environment

```text
Jeev-Rekha/
├── apps/
│   ├── web/            # Next.js PWA
│   └── api/            # FastAPI
├── packages/
│   └── shared-types/   # Optional; add only when useful
├── docs/
├── data/
│   └── demo/           # Synthetic seed data; no real personal data
├── docker-compose.yml  # Local PostGIS
├── .env.example
└── README.md
```

### Required local tools

- Git
- Node.js 20.9+ and npm/pnpm
- Python 3.11 or 3.12
- Docker Desktop
- VS Code with Codex available

### Environment variables (never commit real values)

```env
# Web
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_MAP_STYLE_URL=<map-style-url>

# API
DATABASE_URL=postgresql+psycopg://jeevrekha:jeevrekha@localhost:5432/jeevrekha
JWT_SECRET=<long-random-secret>
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
APP_ENV=development
```

## 11. Deployment plan

| Component | Target | Notes |
|---|---|---|
| Frontend | Vercel | Deploy the Next.js PWA from `apps/web` |
| API | Render or Railway | Run the FastAPI container/service from `apps/api` |
| Database | Render Postgres with PostGIS, or a verified managed Postgres provider | Require PostGIS before selecting a provider |
| Demo data | Seed script | Runs after migrations in a demo environment only |

Render documents support for the PostGIS extension; verify the selected database plan and extension before deployment. [Render PostgreSQL extensions](https://render.com/docs/postgresql-extensions)

## 12. Explicitly deferred items

These are valuable but are **not** first-build dependencies:

- Live INAPH/Bharat Pashudhan/NADRES/IDSP integration.
- SMS, IVR and WhatsApp Business API delivery.
- RFID/NFC reader support.
- Kafka/RabbitMQ message queue.
- Neo4j or a dedicated graph database.
- Real road-routing engine or OSRM self-hosting.
- Full multilingual voice interface.
- Continuous background sync in every browser.
- Production-grade epidemiological calibration with field data.

## 13. Engineering milestones

| Phase | Scope | Exit condition |
|---|---|---|
| 0 | Repo, formatting, local PostGIS, seed data | Every teammate can run the empty stack locally |
| 1 | UI shell and synthetic map | Navigation and visual design system are working |
| 2 | Database, outbreaks and consignments | Records persist through API and appear in UI |
| 3 | Rule engine + Evidence Coverage Score | All four statuses return reasoned results |
| 4 | Map risk layer + safer-route prototype | A risky route and alternative are demonstrated |
| 5 | Rewind/Fast-Forward trace + reports | Outbreak injection shows relevant movement paths |
| 6 | Offline queue, review states, tests and deployment | End-to-end demo is reliable online and offline |

## 14. Final technology decision

**Build the MVP as a modular monolith.**

Next.js handles the polished web/PWA experience. FastAPI owns the authoritative business rules and API. PostgreSQL + PostGIS stores the event and geographic data. NetworkX runs time-aware tracing on a controlled graph. This is technically credible, fully demoable and small enough to complete without hiding unfinished work behind an overengineered architecture.

