# Deployment guide

This guide describes a recommended hosted layout. It does not deploy Jeev Rekha and does not turn its advisory outputs into permits, restrictions, or official disease notifications.

## Recommended layout

- Frontend: Vercel, rooted at `apps/web`.
- API: Render web service built from `apps/api/Dockerfile`.
- Database: Render PostgreSQL with PostGIS enabled and verified before release.

All demo records are controlled fictional data. Pilot-entered data is manually maintained by local operations staff; neither source is imported from INAPH, NADRES, IDSP, LGD, or another government platform.

## Frontend configuration

Set this Vercel environment variable for each deployment environment:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-api.onrender.com/api/v1
```

Build command: `npm run build`  
Start command: Vercel's standard Next.js runtime  
Root directory: `apps/web`

`NEXT_PUBLIC_API_BASE_URL` is the only client-side API address. Do not place database URLs, secrets, or routing-provider credentials in Vercel client variables. `NEXT_PUBLIC_MAP_TILE_URL` is an optional public raster-tile enhancement for Pilot Geographic View; its local-coordinate fallback must remain usable if tiles fail.

## API configuration

Configure the Render service with these values (substitute real hosted values in the platform, never this repository):

```text
APP_ENV=production
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>
CORS_ORIGINS=https://your-vercel-domain.vercel.app
TRUSTED_HOSTS=your-api.onrender.com
DEMO_SEED_ENABLED=false
ROUTING_PROVIDER_BASE_URL=https://router.project-osrm.org
```

Docker context: `apps/api`  
Dockerfile: `apps/api/Dockerfile`  
Runtime command: the Dockerfile starts Uvicorn on the platform-provided `PORT`.

The container never runs migrations or seeds demo data at startup. `APP_ENV=production` fails fast when `DATABASE_URL` is missing, CORS is wildcarded, trusted hosts are wildcarded, or demo seeding is enabled.

## Release operations

Run database operations explicitly from a one-off Render shell/job using the same API image and production environment:

```bash
python -m alembic upgrade head
```

For a dedicated, controlled demo environment only, seed manually after the migration:

```bash
python -m app.seed
```

Never seed a real pilot environment without an authorised data-preparation decision. Seeding is manual and idempotent; it is not part of web-service startup.

Validate configuration without printing secrets:

```bash
python -m app.production_check
```

After the Vercel URL is known, set the exact origin in `CORS_ORIGINS`, redeploy the API, then use the returned API URL for `NEXT_PUBLIC_API_BASE_URL` and redeploy the frontend.

## Hosted service limitations

Public OSRM-compatible endpoints and OpenStreetMap tiles are appropriate only for light demonstration use, subject to their terms and capacity. Arrange an approved provider or self-hosted capacity before depending on them operationally. If routing or tiles are unavailable, Jeev Rekha must show its existing truthful endpoint/local-coordinate fallback rather than a navigation recommendation.

## Smoke check

After a release, use only safe GET checks:

```bash
SMOKE_API_BASE_URL=https://your-api.onrender.com/api/v1 python -m app.smoke_test
```

The command checks health, readiness, and the locations response shape. It creates, updates, seeds, and deletes no data.
