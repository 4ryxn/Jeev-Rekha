export type LocationType = "village" | "market" | "checkpost" | "veterinary_centre";
export type RegistryLocationType = "village" | "livestock_market" | "checkpost" | "veterinary_centre";
export type LocationDataSource = "demo_seed" | "pilot_entered";
export type OutbreakStatus = "suspected" | "confirmed" | "closed";
export type VaccinationEvidence = "verified" | "declared" | "unknown";

export interface Location { id: number; name: string; type: LocationType; location_type: RegistryLocationType; district: string; state: string; latitude: number; longitude: number; data_source: LocationDataSource; is_active: boolean; created_at: string; updated_at: string }
export interface LocationRegistryPayload { name: string; location_type: RegistryLocationType; district: string; state: string; latitude: number; longitude: number }
export interface Vehicle { id: number; vehicle_reference: string; created_at: string }
export interface Outbreak { id: number; disease_name: string; species: string; status: OutbreakStatus; location_id: number; detected_at: string; confirmed_at: string | null; suspected_cases: number; confirmed_cases: number; mortality_count: number; verification_level: string; notes: string | null; created_at: string; location: Location }
export interface MovementEvent { id: number; location_id: number; event_type: string; occurred_at: string; location: Location }
export interface Consignment { id: number; origin_location_id: number; destination_location_id: number; species: string; animal_count: number; vehicle_id: number; departure_at: string; vaccination_evidence: VaccinationEvidence; created_at: string; origin_location: Location; destination_location: Location; vehicle: Vehicle; movement_events: MovementEvent[] }
export type RiskState = "green" | "amber" | "red" | "grey";
export interface EvidenceFactor { key: string; label: string; score: number; max_score: number; freshness_date: string | null; explanation: string }
export interface Advisory { id: number; consignment_id: number; risk_state: RiskState; evidence_coverage_score: number; reasons: { code: string; text: string }[]; evidence_factors: EvidenceFactor[]; recommended_action: string; evaluated_at: string; rules_version: string; consignment: Consignment }
export interface RoutePath { coordinates:number[][]; distance_km:number; minutes:number; location_ids:number[] }
export interface RouteAssessment { id:number; consignment_id:number; preferred_route:RoutePath; safer_route:RoutePath|null; preferred_distance_km:number; preferred_minutes:number; safer_distance_km:number|null; safer_minutes:number|null; risk_reduction:string; route_reasons:string[]; assessed_at:string }
export type TraceDirection = "rewind" | "fast_forward";
export type TraceEvidenceLevel = "direct" | "indirect";
export interface TraceConfiguration { disease_name: string; review_window_days: number; source_label: string }
export interface TraceFinding { id: number; entity_type: string; entity_id: string; relationship_type: string; event_timestamp: string; evidence_level: TraceEvidenceLevel; explanation: string; review_status: string }
export interface TraceImpactedCounts { findings: number; locations: number; vehicles: number; consignments: number }
export interface TraceRun { id: number; outbreak: Outbreak; direction: TraceDirection; window_start: string; window_end: string; review_window_days: number; source_label: string; findings: TraceFinding[]; timeline: TraceFinding[]; impacted_counts: TraceImpactedCounts; impacted_locations: Location[]; created_at: string; disclaimer: string }
export interface ContainmentActionEffect {category:string;applicable_workload:number;reduction:number}
export interface ContainmentSummary {estimated_review_contacts:number;route_checkpoint_contacts:number;market_contacts:number;other_review_contacts:number;affected_locations:number;affected_vehicles:number;affected_consignments:number;baseline_route_risk_exposure_count:number}
export interface ContainmentScenarioSummary extends ContainmentSummary {scenario_route_risk_exposure_count?:number;action_effects?:Record<string,ContainmentActionEffect>}
export interface ContainmentScenario {id:number;outbreak:Outbreak;horizon_days:number;selected_actions:string[];baseline_summary:ContainmentSummary;scenario_summary:ContainmentScenarioSummary;assumptions:string[];created_at:string}
export interface ReviewCase {id:number;source_type:string;source_id:string;category:"evidence_gap"|"sync_exception"|"trace_contact";priority:"high"|"medium"|"low";title:string;summary:string;status:"open"|"acknowledged"|"resolved";resolution_note:string|null;created_at:string;acknowledged_at:string|null;resolved_at:string|null;source_summary:string;source_href:string}
export interface ReportIndex {advisories:{id:number;href:string;title:string}[];traces:{id:number;href:string;title:string}[];containment:{id:number;href:string;title:string}[]}
export interface PublicMovementCheck {risk_state:RiskState;reasons:string[];evidence_coverage_score:number;information_coverage:string;recommended_action:string;advisory_disclaimer:string;generated_at:string}

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { cache: "no-store", ...options, headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) } });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}
