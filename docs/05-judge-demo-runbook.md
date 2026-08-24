# Five-minute judge-demo runbook

Jeev Rekha is an explainable decision-support prototype. It does not issue a movement permit, legal restriction, or automated veterinary decision. All demonstration records are controlled fictional data unless a screen explicitly identifies a manually entered pilot record.

## Before the walkthrough

1. Start PostGIS and the API, then run `python -m app.demo_reset` from `apps/api` for a local synthetic setup.
2. Start the web app and open the Operations workspace.
3. Confirm `GET /api/v1/health` and `GET /api/v1/readiness` return healthy responses.

## Five-minute flow

1. **Demo workspace (45 seconds).** On Dashboard and Map & Advisories, point out the Demo data context, synthetic-outbreak status badges, evidence coverage, and controlled synthetic network. Explain that it is not live INAPH, NADRES, IDSP, LGD, or government data.
2. **Animal Owner / Trader (35 seconds).** Switch workspace and run a Pre-Travel Animal Movement Check. Show the simple advisory status, action, and printable advisory slip. It is advisory only; it stores no public personal identity and issues no permit.
3. **District Vet Team movement (55 seconds).** Register a synthetic consignment, then evaluate it. Show the reasons, Evidence Coverage Score, and Safe Corridor comparison where a persisted route assessment exists.
4. **Trace Lab (45 seconds).** Choose the confirmed synthetic FMD outbreak and run Rewind contacts. Show the configured review window, timeline, and neutral “requires veterinary review” wording. Trace results identify contacts; they do not confirm disease transmission.
5. **Containment Lab (40 seconds).** Select the same confirmed outbreak, choose actions and a horizon, then show baseline versus scenario workload. These are transparent synthetic assumptions, not epidemiological predictions or orders.
6. **Pilot Mode (35 seconds).** In Workspace Settings, add or select a pilot-entered location. Explain that Pilot Geographic View uses only manually entered coordinates and can show a road-route provider result or a truthful route-unavailable fallback. Review radii require authorised veterinary validation and are not official containment orders.
7. **Review Queue and Reports (25 seconds).** Open a source-linked case, explain that acknowledging it never changes the advisory or source evidence, and open a printable operational brief.

## What is real in this prototype

- Typed FastAPI endpoints, PostGIS-backed persistence, Alembic migrations, deterministic advisory rules, trace runs, route assessments, review cases, offline queue receipts, and browser-printable briefs.
- Controlled data-context separation between fictional demo records and manually entered pilot records.
- Safe local/offline capture for the two registration workflows, with idempotent sync receipts.

## What is intentionally not claimed

- Live government system integration, official disease surveillance, permits, automatic restrictions, automatic disease-transmission conclusions, authentication, or deployment authority.
- Real-road navigation when the configured routing provider is unavailable.

## 30-second connectivity fallback

If external tiles or the routing provider are unavailable, switch to the controlled synthetic network / local-coordinate fallback already displayed by the app. Continue the demo with persisted reasons, Evidence Coverage Score, trace timeline, and printable brief. State plainly that the missing external route is unavailable and no navigation recommendation is shown.
