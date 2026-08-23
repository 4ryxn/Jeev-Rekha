# Jeev Rekha — Local synthetic operations workspace

Jeev Rekha is a livestock outbreak intelligence and movement-advisory project using a local PostGIS-backed synthetic demonstration workspace.

All stored records are synthetic demonstration data. There is no live INAPH, NADRES, IDSP, or other government API connection. Safe Corridor routing, tracing, offline sync, simulation, reports, real authentication, external integrations, and deployment are intentionally deferred.

## Prerequisites

- Git
- Node.js 20.9+ and npm (Node 24 was used to verify this repository)
- Python 3.12 (Python 3.12.13 was used to verify this repository)
- Docker Desktop with Docker Compose

## 1. Configure local environment files

From the repository root:

```bash
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
```

The committed example values are local-development defaults only. Do not commit real credentials.

## 2. Start local PostgreSQL + PostGIS

```bash
docker compose up -d
docker compose ps
```

The database is available at `localhost:5432` and stores data in the named `jeev_rekha_postgres_data` volume.

To stop it:

```bash
docker compose down
```

## 3. Start the FastAPI service

In a second terminal:

```bash
cd apps/api
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m app.demo_reset
uvicorn app.main:app --reload --port 8000
```

Verify it in another terminal:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"ok","service":"jeev-rekha-api","environment":"development"}
```

Run backend tests (the suite applies the local migration and uses synthetic data):

```bash
cd apps/api
source .venv/bin/activate
pytest
```

## 4. Start the Next.js frontend

In a third terminal:

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The dashboard reads the local API and includes working outbreak and consignment registration forms. All displayed and submitted records must remain synthetic.

Run frontend linting:

```bash
cd apps/web
npm run lint
```

## Repository layout

```text
apps/web/          Next.js App Router frontend, dashboard, and registration workflows
apps/api/          FastAPI, SQLAlchemy models, Alembic migrations, seed command, and tests
docs/              Product, UI/UX, and technical specifications
data/demo/         Reserved synthetic demo-data location
infra/             Local infrastructure notes
docker-compose.yml PostgreSQL + PostGIS only
```

## Synthetic demo records

`python -m app.demo_reset` upgrades the schema and idempotently creates fictional locations, vehicles, outbreak records, consignments, evidence, routes, and advisory examples. It never deletes existing database records.

The four advisory demonstrations are:

- Asha Nagar → Kaveri Cattle Market: **Green**
- Navjeevan → Madhavpura: **Amber**
- Haritpur → Nandipur: **Red**
- Bhoomi Village → Navjeevan: **Grey**

Each advisory is an explainable synthetic demonstration, not an official movement decision.

## Next phase recommendation

Build Safe Corridor routing only after validating the deterministic advisory rules with domain experts. Keep route recommendations separate from the advisory decision and clearly disclose their limitations.
