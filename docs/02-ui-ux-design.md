# Jeev Rekha — UI/UX Design Document

**Version:** 1.0  
**Product:** Jeev Rekha — Livestock Outbreak Intelligence and Movement Advisory System  
**Reference direction:** Creative-agency editorial web design, adapted for a high-trust operational web product  
**Companion document:** `01-product-requirements.md`

---

## 1. Design objective

Jeev Rekha must make a complex epidemiological decision feel immediate, understandable and trustworthy. A veterinary officer should be able to understand an outbreak situation at a glance; a market operator should be able to register a consignment without training-heavy software; and a transporter should receive a clear action, not a confusing data dashboard.

The visual direction takes inspiration from contemporary creative-agency sites: bold editorial type, strong use of space, unexpected but intentional composition, premium details and confident colour. It **does not** copy the reference design or turn an emergency-response tool into a decorative landing page.

**Core rule:** Expressive design for the product shell; calm, high-clarity design for high-risk operational decisions.

## 2. Design principles

1. **Decision before data.** Always lead with the movement status and next action; supporting data follows.
2. **Never colour alone.** Green, Amber, Red and Grey must have a text label, icon and explanation.
3. **Missing data is visible.** Grey should feel deliberate and serious—not like a disabled state.
4. **Progressive disclosure.** A kiosk operator sees only the fields needed now; officers can open evidence, maps and traces.
5. **Human authority is explicit.** Show “Advisory only—vet review required” wherever a decision could be misunderstood as a legal restriction.
6. **Touchpoint-first.** Design for shared desktop/tablet kiosks before personal smartphone usage.
7. **Premium but practical.** Use editorial polish in hierarchy, image treatment and motion, never in a way that slows registration or hides risk.

## 3. Brand expression

### 3.1 Personality

| Attribute | Design expression |
|---|---|
| Assured | Large, precise headlines; restrained layouts |
| Protective | Clear guardrails, shields, route boundaries |
| Scientific | Evidence timestamps, confidence labels, structured data |
| Rural-aware | Plain English/Hindi-ready microcopy; shared-kiosk flows |
| Accountable | Visible reasons, sources and review status |

### 3.2 Suggested visual direction

- **Base:** warm off-white or deep ink background, depending on page purpose.
- **Editorial moments:** oversized section titles, irregular cropping, thin rules, one expressive illustration/map per key screen.
- **Operational surfaces:** white/light panels, dark text, high contrast, generous spacing.
- **Map language:** muted terrain and roads; risk layers are the strongest colour on the screen.
- **Motion:** subtle 150–220 ms transitions; no animation when a user is reading risk status or taking emergency action.

## 4. Design tokens

### 4.1 Colour system

| Token | Hex | Use |
|---|---:|---|
| Ink | `#0D1B1E` | Navigation, headline, primary text |
| Paper | `#F7F6F1` | Main background |
| Surface | `#FFFFFF` | Forms, tables, cards |
| Teal | `#0F766E` | Primary action, trusted/verified signal |
| Electric Lime | `#C9F542` | Editorial accent, selected state—never risk status |
| Blue | `#2563EB` | Links, map route, information |
| Green | `#198754` | Green advisory |
| Amber | `#B45309` | Amber advisory |
| Red | `#B42318` | Red advisory |
| Grey | `#475569` | Grey advisory / insufficient evidence |
| Border | `#D8DDD5` | Dividers and field boundaries |

### 4.2 Typography

| Role | Font recommendation | Size |
|---|---|---:|
| Display headline | Space Grotesk / Sora | 48–64 px desktop |
| Page title | Space Grotesk / Sora | 32–40 px |
| Section title | Inter / Manrope | 20–24 px |
| Body | Inter / Manrope | 16 px |
| Form/table text | Inter / Manrope | 14–16 px |
| Metadata | Inter / Manrope | 12–13 px |

Use one display typeface and one highly legible UI typeface. Never use condensed display type in tables, forms or advisory explanations.

### 4.3 Spacing, radius and elevation

- 8 px spacing grid.
- 12 px radius for cards; 10 px for inputs; pill styling only for short status metadata.
- Borders over heavy shadows. Use a single soft shadow only on floating action panels.
- Content max width: 1440 px; core operational reading column: 720–840 px.

## 5. Information architecture

```text
Public Safety View
└── Current advisories / outbreak notices

Operations Workspace
├── Command Centre (dashboard)
├── Register
│   ├── New consignment
│   ├── Outbreak evidence
│   └── Symptom signal
├── Map & Advisories
├── Trace Lab
│   ├── Outbreak Rewind
│   └── Fast-Forward Trace
├── Reports
├── Review Queue
└── Settings / Data status
```

### Primary navigation

- A left vertical rail on desktop: icon + label, always visible.
- A compact top bar for location, sync state, role and alerts.
- On tablet, collapse the rail into an icon drawer.
- Do not show a complex public dashboard to market/checkpoint operators; open them directly in **New Consignment** mode.

## 6. Core screen specifications

### 6.1 Command Centre

**Purpose:** Give veterinary/district staff a live understanding of the situation and a single obvious next action.

**Layout**

```text
[Page title: Good morning, District Vet Team]        [Sync state] [Profile]

[ACTIVE RISK STRIP: 3 Red | 7 Amber | 4 Grey | View map →]

[Large map: outbreak zones + routes]  [Priority action feed]
                                   ├─ Confirmed outbreak requires trace
                                   ├─ 4 Grey areas need field verification
                                   └─ 2 sync conflicts awaiting review

[Recent consignments]                [Evidence freshness by area]
```

**Creative-agency influence:** oversized “Situation Brief” title, a strong map composition and one bright lime action accent.  
**Operational rule:** the Red/Amber/Grey numbers must use their actual status colours, never the decorative accent.

### 6.2 New Consignment — Kiosk flow

**Purpose:** Register a movement quickly without requiring animal-level tags.

**Pattern:** one primary task per step, with a visible 4-step progress bar.

```text
Step 1: Origin & destination
Step 2: Animals & vehicle
Step 3: Vaccination evidence
Step 4: Review & get advisory
```

**Required fields**

- Origin and destination: searchable location picker + recent locations.
- Species and approximate count.
- Vehicle number/reference.
- Departure date and time.
- Vaccination evidence: Verified / Declared / Unknown.

**UX rules**

- Mark only essential fields as required.
- Use large controls (minimum 44 px height) and a persistent Back button.
- Save an offline draft automatically after each step.
- Explain why vaccination evidence is requested in one sentence, not a tooltip maze.

### 6.3 Movement Advisory Result — the signature screen

**Purpose:** Turn complex data into one safe next action.

**Hero layout**

```text
           [ADVISORY: RED]
   High-risk exposure identified

   Do not proceed until authorised veterinary guidance.

 [Why this result?] [Evidence score: 86/100] [Print / Share]

 ┌──────────────────────────┐  ┌───────────────────────────────┐
 │ Your route               │  │ Safer alternative             │
 │ 82 km · crosses outbreak │  │ 97 km · avoids active zone    │
 └──────────────────────────┘  └───────────────────────────────┘

 [Evidence timeline]         [Map with route overlay]
```

**Status language**

| State | Headline | Action |
|---|---|---|
| Green | Lower risk; evidence is current | Proceed with advisory receipt |
| Amber | Precaution required | Verify and consider safer route |
| Red | High-risk exposure identified | Seek authorised veterinary guidance |
| Grey | Evidence is insufficient | Request field verification before movement |

The advisory hero uses a solid background only for the status band; keep the body calm and readable.

### 6.4 Outbreak map

**Purpose:** Show what is active, where it is located and which movement routes are relevant.

**Layers**

- Confirmed outbreak zone.
- Suspected outbreak zone.
- Active consignment paths.
- Markets, checkposts and veterinary centres.
- Surveillance blind spots.

**Controls**

- Disease, status, species and date-range filters.
- Map legend always visible.
- “Focus highest risk” action.
- Side-sheet on marker select—avoid cluttering the map with permanent labels.

### 6.5 Trace Lab

**Purpose:** Make a time-aware contact trace understandable to a human reviewer.

**Layout**

```text
[Outbreak selector] [Disease incubation window] [Date range]

          [REWIND] ← OUTBREAK NODE → [FAST-FORWARD]

[Timeline of contacts]            [Network map]

[Evidence table: movement, time, location, confidence, action]
```

**UX rules**

- Use direction labels: “Possible source path” and “Potential exposure path.”
- Display confidence as **High / Medium / Low**, with a reason; do not show unexplained precision.
- Never label a person, farmer or transporter as responsible.

### 6.6 Evidence and review queue

**Purpose:** Let authorised veterinary officers review conflicting or incomplete data safely.

**Row structure**

```text
[Severity] [Entity] [Conflict / missing evidence] [Last updated] [Review]
```

Opening a record shows original events side by side. The reviewer can verify, reject or request clarification. The event history remains visible after a decision.

### 6.7 Reports

**Purpose:** Convert digital work into a field-usable handoff.

- Movement advisory receipt: status, reasons, evidence score, next action and QR/reference number.
- Veterinary action report: exposed locations/vehicles, trace direction and recommended priority.
- One Health review package: zoonotic context, exposure window and relevant settlements. Clearly label: **For officer review—not an automatic alert.**

## 7. Experience flows

### 7.1 Consignment advisory flow

```text
Start registration
  → Enter route and consignment details
  → Validate required inputs
  → Risk + evidence evaluation
  → Advisory result
       ├─ Green: print/share receipt
       ├─ Amber: show precautions + route option
       ├─ Red: show vet guidance + safer route
       └─ Grey: request verification / hold for review
```

### 7.2 Outbreak response flow

```text
Record evidence → Vet verifies outbreak → Active paths re-evaluated
→ Rewind trace + Fast-Forward trace → Review action package → Export report
```

### 7.3 Offline flow

```text
No network detected → show “Saved on this device” banner
→ allow registration → queue signed event
→ connection returns → sync → show success or review-conflict state
```

## 8. Components and interaction patterns

| Component | Requirement |
|---|---|
| Risk badge | Icon + text + colour; never colour only |
| Evidence chip | “Lab confirmed”, “Fresh 2 days”, “Vaccination unknown” |
| Reason list | 2–4 plain-language reasons beneath every advisory |
| Map marker | Status ring + type icon; expands to side-sheet |
| Timeline item | Time, entity, evidence type, confidence and action |
| Sync indicator | Online / Offline saved / Syncing / Review needed |
| Empty state | Explain next useful action, not generic “No data” |
| Toast | Confirm low-risk actions; never use as only confirmation for a Red decision |

## 9. Responsive and accessibility requirements

### Desktop (1280 px and above)

- Two-column command centre and trace workspace.
- Full map, data table and persistent navigation.

### Tablet/shared kiosk (768–1279 px)

- Single-column data entry; map moves below result summary.
- Large touch targets and sticky primary action.

### Small mobile

- Public advisory receipt and alerts only for MVP.
- Do not force complex map editing or evidence review onto a small screen.

### Accessibility

- WCAG AA contrast minimum.
- Complete keyboard navigation and visible focus states.
- Status conveyed through icon, text and colour.
- Use plain-language labels; avoid acronyms without expansion on first use.
- Provide Hindi/local-language readiness in all layouts: allow 25–35% text expansion.
- Respect reduced-motion settings.

## 10. Content design

**Voice:** calm, direct, specific, non-accusatory.

| Avoid | Use instead |
|---|---|
| “Movement blocked” | “High-risk exposure identified—seek authorised veterinary guidance” |
| “Unsafe village” | “Evidence is insufficient in this area” |
| “Infected transporter” | “Vehicle connected to a relevant exposure path” |
| “AI says…” | “Advisory based on active outbreak evidence and route data” |

## 11. Motion and visual polish

- Route line draws only after the advisory is calculated; duration under 300 ms.
- Map panel opens with a short fade/slide, not a dramatic animation.
- Evidence timeline may progressively reveal entries, but provide an instant “Show all” option.
- Red advisory: one subtle pulse on initial appearance only; never continuous flashing.
- Animate no more than one visual layer at a time.

## 12. Design handoff checklist

Before frontend implementation, provide:

1. Figma pages for each MVP screen and state.
2. Colour, typography, spacing and icon tokens.
3. Desktop and tablet layouts for every primary screen.
4. Empty, loading, error, offline and conflict states.
5. Green, Amber, Red and Grey versions of the advisory screen.
6. Clickable prototype for the end-to-end demo scenario.
7. Asset licences and source list for any map tiles, icons or imagery.

## 13. MVP visual acceptance criteria

- A first-time operator can finish a consignment registration without assistance.
- Every advisory shows status, action, reasons and evidence score above the fold.
- Grey is understandable as “insufficient evidence,” not “low risk.”
- A veterinary officer can distinguish confirmed from suspected evidence instantly.
- No critical action relies only on hover, colour or a hidden menu.
- The design remains usable at 200% browser zoom and on a shared tablet.

## 14. Source note

This document is inspired by the high-level visual concept of a creative-agency web experience referenced by the team. It deliberately translates that style into a distinct operational UX for Jeev Rekha; it does not copy the reference layout, assets or branded content.

