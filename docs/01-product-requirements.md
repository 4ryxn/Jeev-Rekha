# Jeev Rekha — Product Requirements Document

**Version:** 1.0  
**Status:** Hackathon MVP specification  
**Problem Statement:** SIH 2026 SC-05 — *Livestock & Zoonotic Outbreak Database and Movement Alerts*  
**Product type:** Offline-capable web application / Progressive Web App (PWA)

---

## 1. Product summary

**Jeev Rekha** is an explainable livestock-outbreak intelligence and movement-advisory platform. It converts verified animal-disease evidence, veterinary symptom signals and livestock consignment movements into a clear answer before travel:

> **Is this livestock movement safe enough to proceed, does it need precautions, or should it be investigated first?**

The platform is designed for shared devices at veterinary centres, livestock markets and checkposts. It does **not** assume every farmer owns a smartphone or every animal has an ear tag.

## 2. Problem

When an animal disease outbreak begins in one village, animals and vehicles can still move through markets, checkposts and neighbouring districts. Existing records can show where an outbreak was reported, but they do not turn that information into a route decision, a safer alternative or a time-aware contact trace.

This creates five practical gaps:

1. Buyers and transporters cannot easily assess outbreak risk before movement.
2. Untagged animals cannot be tracked individually through normal digital health-card workflows.
3. Authorities lose time tracing where an outbreak may have come from and where it may have travelled.
4. Areas with poor reporting can look falsely safe.
5. Zoonotic exposure requires a reviewable animal-to-public-health handoff.

## 3. Vision and value proposition

**Vision:** Protect livestock, rural livelihoods and public health by making every disease-related movement decision evidence-aware and explainable.

**Value proposition:** Jeev Rekha follows the **consignment movement**, not only an individual animal identity. It shows Green, Amber, Red or Grey risk, explains why, suggests a safer corridor where possible, and traces likely exposure paths after a confirmed outbreak.

## 4. Users and roles

| User | Primary job | Access |
|---|---|---|
| Veterinary officer | Verify outbreaks, review conflicts, issue action advice | Full operational access |
| Diagnostic laboratory staff | Submit laboratory findings | Lab evidence only |
| Market/checkpost operator | Register a consignment and view movement advice | Registration + advisory |
| Animal-health worker | Submit structured symptom signals | Signal submission |
| Buyer/seller/transporter | Receive a printed, SMS or voice advisory | Minimum-disclosure advisory |
| District administrator | Review map, tracing and response priorities | Dashboard + reports |

## 5. Goals

### 5.1 Hackathon MVP goals

1. Register verified, suspected and closed outbreak events.
2. Register tagless livestock consignments at a shared kiosk.
3. Produce Green, Amber, Red and Grey movement advisories with clear reasons.
4. Calculate an Evidence Coverage Score for every advisory.
5. Recommend a safer route when the preferred route intersects an active risk zone.
6. Trace movement contacts backward and forward within a disease-relevant time window.
7. Flag a surveillance blind spot when movement exists but recent health/surveillance evidence is weak.
8. Generate an officer-readable veterinary action report and a reviewable zoonotic-exposure package.
9. Work during a simulated network outage and synchronise later without losing events.

### 5.2 Success criteria for the demo

- A judge can register a consignment and receive a reasoned advisory in under 60 seconds.
- Injecting a laboratory-confirmed outbreak changes a previously safe route to Red or Amber when rules require it.
- A low-information area receives Grey—not Green.
- Backward and forward tracing visibly identifies relevant markets, vehicles and destination villages.
- Every advisory displays the evidence used and a recommended next action.

## 6. Non-goals and guardrails

The MVP will **not**:

- claim live integration with INAPH, Bharat Pashudhan, NADRES, IDSP or any government API;
- issue legal movement permits, bans or official public-health alerts;
- predict human infection or declare a public-health emergency;
- use facial recognition, Aadhaar verification or a mandatory ear tag;
- identify an individual animal when only consignment information is available;
- replace the decision of a veterinary or public-health authority.

All synthetic demo data must be visibly labelled as synthetic.

## 7. Core user journeys

### Journey A — Register and advise a livestock consignment

1. Market/checkpost operator opens the kiosk PWA.
2. Operator enters origin, destination, species, approximate count, vehicle number, departure time and vaccination evidence.
3. The system checks active outbreaks, time windows, route zones, evidence freshness and relevant prior movements.
4. The system returns Green, Amber, Red or Grey status with reasons.
5. The operator prints or shares a movement-advisory receipt.

### Journey B — Outbreak confirmation and containment

1. Veterinary officer records a laboratory-confirmed outbreak.
2. The risk engine recalculates affected movement paths.
3. The officer views **Outbreak Rewind** for possible incoming paths.
4. The officer views **Fast-Forward Trace** for potentially exposed destinations.
5. The officer exports an action package for screening, disinfection, inspection or vaccination prioritisation.

### Journey C — Missing evidence must not look safe

1. Operator selects an origin with old or absent health and vaccination updates.
2. The Evidence Coverage Score falls below the safe-decision threshold.
3. The platform returns a Grey advisory.
4. The receipt recommends field verification or precaution before movement.

## 8. Functional requirements

| ID | Requirement | Priority | MVP acceptance criteria |
|---|---|---:|---|
| FR-01 | Outbreak registry | Must | Create, view and filter suspected, confirmed and closed outbreaks by disease, status, date and location. |
| FR-02 | Consignment passport | Must | Register an untagged consignment with required route and vehicle information. |
| FR-03 | Movement advisory | Must | Return one of Green, Amber, Red or Grey with at least one human-readable reason. |
| FR-04 | Evidence Coverage Score | Must | Display a 0–100 score and freshness factors used in the advisory. |
| FR-05 | Route assessment | Must | Compare a requested route against configured risk zones. |
| FR-06 | Safe Corridor | Should | Show one safer alternative with distance/time trade-off when available. |
| FR-07 | Outbreak Rewind | Must | List relevant upstream movements, vehicles and locations inside the incubation window. |
| FR-08 | Fast-Forward Trace | Must | List potentially exposed downstream destinations and contacts. |
| FR-09 | Symptom signals | Should | Capture a structured pre-confirmation veterinary signal without marking an outbreak confirmed. |
| FR-10 | Blind-spot detection | Should | Flag a location with high movement activity but stale health/surveillance evidence. |
| FR-11 | Action reports | Must | Generate printable/downloadable movement and veterinary action reports. |
| FR-12 | Offline queue | Should | Save new kiosk events locally when offline and sync after connectivity returns. |
| FR-13 | Conflict review | Should | Preserve conflicting health/vaccination events for veterinary review; never silently overwrite. |
| FR-14 | Scenario simulator | Could | Compare exposure-path ranges before and after a selected intervention. |

## 9. Advisory rules

| Advisory | Meaning | Example trigger | Default next action |
|---|---|---|---|
| **Green** | Lower risk with sufficient evidence | No relevant active exposure; recent surveillance available | Proceed; retain receipt |
| **Amber** | Precaution required | Near suspected/recent outbreak or incomplete vaccination evidence | Inspect, verify vaccination, consider safer route |
| **Red** | High-risk exposure | Route/origin/destination connected to a confirmed outbreak in the relevant window | Do not proceed until authorised veterinary guidance |
| **Grey** | Evidence insufficient | Stale or missing veterinary, laboratory, movement or vaccination data | Field verification/precaution required |

**Important rule:** Grey is not a disease-positive result. It means the platform cannot responsibly confirm low risk.

## 10. Evidence Coverage Score

The Evidence Coverage Score is shown beside every movement advisory. It is calculated from a transparent weighted checklist:

- recency of veterinary updates;
- availability of laboratory confirmation/status;
- vaccination-record freshness;
- movement-registration coverage;
- time since last field update.

For the MVP, the score will use configurable rules and synthetic data—not a black-box model.

## 11. High-level data model

| Entity | Key fields |
|---|---|
| Location | id, name, type, LGD code (where available), latitude, longitude |
| Outbreak | disease, species, status, location, detected_at, confirmed_at, morbidity, mortality, verification level |
| Consignment | origin, destination, species, animal_count, vehicle_ref, departure_time, vaccination_evidence |
| Movement event | consignment, from_location, to_location, timestamp, route reference |
| Vehicle | registration/reference, movement history |
| Symptom signal | location, species, symptoms, count, observed_at, reporter role |
| Vaccination event | location/consignment, vaccine, date, verification level |
| Advisory | consignment, risk_state, reasons, evidence_score, recommended_action |
| Trace result | outbreak, direction, connected entity, evidence, confidence |

## 12. Screens required for MVP

1. **Operations dashboard** — outbreak summary, active advisories and quick actions.
2. **Outbreak map** — locations, status filters and risk zones.
3. **Register outbreak** — authorised form for suspected/confirmed/closed events.
4. **Register consignment** — simple shared-kiosk form.
5. **Movement advisory result** — colour state, reasons, score and safer route.
6. **Trace workspace** — Rewind and Fast-Forward graph/timeline.
7. **Blind-spot view** — stale-evidence locations requiring verification.
8. **Reports view** — printable advisory, veterinary action report and One Health package.
9. **Sync/review queue** — pending offline events and conflicting updates.

## 13. Non-functional requirements

- **Explainability:** no advisory without visible reasons and evidence freshness.
- **Privacy:** public views must not show personal farmer/transporter information.
- **Role-based access:** outbreak editing, evidence verification and public viewing are separate permissions.
- **Auditability:** keep append-only event history, actor role and timestamps.
- **Low connectivity:** core registration must work through an offline queue.
- **Performance:** local demo advisory response within 2 seconds after submission.
- **Accessibility:** keyboard-operable forms, meaningful labels, high-contrast risk colours paired with text labels.
- **Security:** validation on all forms; no secret/API key in the frontend repository.

## 14. Technical direction

| Layer | Initial choice |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Offline | Service Worker + IndexedDB |
| Backend | FastAPI + Pydantic |
| Database | PostgreSQL + PostGIS |
| Maps | MapLibre or Leaflet |
| Graph/tracing | Python + NetworkX |
| Simulation | Python + NumPy |
| Deployment | Vercel (frontend), Render/Railway (backend), Neon PostgreSQL |

The implementation will begin with a controlled, transparent graph of villages, markets, vehicles and checkposts. Real administrative nodes may be used where publicly available; movement events will be synthetic for the hackathon demo.

## 15. Demo scenario

1. Register an untagged cattle consignment from Village A to Market B.
2. Receive a Green advisory because there is recent evidence and no relevant active outbreak.
3. Register another movement from a poorly monitored village; receive Grey advisory.
4. Add a laboratory-confirmed outbreak near Village A's preferred route.
5. Re-run the first consignment; receive Red advisory and a safer-route alternative.
6. Open Outbreak Rewind; identify a vehicle and upstream market inside the time window.
7. Open Fast-Forward Trace; identify two downstream villages requiring verification.
8. Export a veterinary action report.

## 16. Evaluation metrics

- advisory agreement with predefined expert rules;
- correct time-window tracing on the controlled graph;
- percentage of low-evidence locations marked Grey;
- time to identify affected destinations after an outbreak is added;
- route-risk reduction versus added travel distance/time;
- offline-event sync success and conflict-detection accuracy;
- false-alert rate on deliberately non-exposed demo movements;
- average time to register a tagless consignment.

## 17. Delivery milestones

| Milestone | Deliverable |
|---|---|
| M0 | Repository, PRD, architecture and design-system documents |
| M1 | Frontend shell, navigation and synthetic demo data |
| M2 | Outbreak and consignment APIs with database migrations |
| M3 | Advisory rules, Evidence Coverage Score and result screen |
| M4 | Route assessment and safe-corridor prototype |
| M5 | Rewind/Fast-Forward trace workspace and reports |
| M6 | Offline queue, conflict review, tests and deployed demo |

## 18. Definition of done for the hackathon MVP

The MVP is ready only when a judge can complete the demo scenario end to end: create a movement, see a reasoned advisory, inject a confirmed outbreak, observe the risk change, view the trace, receive a safer-route option and export an action report.

## 19. Research anchors

- SIH 2026 SC-05 problem statement.
- Department of Animal Husbandry & Dairying — National Animal Disease Control Programme: https://dahd.gov.in/en/schemes/programmes/nadcp
- ICAR–NIVEDI — NADRES: https://nivedi.res.in/Nadres_v2/
- Local Government Directory: https://lgdirectory.gov.in/
- NCDC — Integrated Disease Surveillance Programme: https://ncdc.mohfw.gov.in/includes/About/CentresAndDivision/IDSP.php
- World Organisation for Animal Health — Codes and Manuals: https://www.woah.org/en/what-we-do/standards/codes-and-manuals/

