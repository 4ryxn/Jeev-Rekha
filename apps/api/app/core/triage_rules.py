"""Structured, non-diagnostic symptom triage rules for veterinary review."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SymptomProfile:
    disease_name: str
    symptoms: frozenset[str]
    priority: str = "medium"


@dataclass(frozen=True)
class TriageRules:
    mortality_rate_threshold: float = 0.10
    disclaimer: str = "Requires veterinary review; this triage does not confirm infection."


HIGH_CONCERN_PROFILES: tuple[SymptomProfile, ...] = (
    SymptomProfile("Anthrax", frozenset({"sudden_death", "unclotted_bleeding", "high_fever", "staggering"}), "high"),
    SymptomProfile("Foot-and-mouth disease", frozenset({"fever", "oral_vesicles", "foot_vesicles", "excessive_salivation", "lameness"})),
    SymptomProfile("Lumpy Skin Disease", frozenset({"fever", "multiple_skin_nodules", "swollen_lymph_nodes", "nasal_ocular_discharge"})),
    SymptomProfile("Haemorrhagic septicaemia", frozenset({"high_fever", "throat_submandibular_swelling", "difficulty_breathing", "sudden_death"})),
    SymptomProfile("Black Quarter", frozenset({"high_fever", "lameness", "crepitating_hindquarter_swelling"})),
    SymptomProfile("Peste des petits ruminants", frozenset({"fever", "oral_erosions", "oculonasal_discharge", "diarrhea", "high_mortality_young"})),
    SymptomProfile("Brucellosis", frozenset({"late_term_abortion", "retained_placenta", "reduced_fertility"})),
)

TRIAGE_RULES = TriageRules()


def match_high_concern_profile(symptoms: list[str]) -> SymptomProfile | None:
    selected = {symptom.strip().casefold() for symptom in symptoms}
    return next((profile for profile in HIGH_CONCERN_PROFILES if profile.symptoms.issubset(selected)), None)
