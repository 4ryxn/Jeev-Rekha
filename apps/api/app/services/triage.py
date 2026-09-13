from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.triage_rules import TRIAGE_RULES, match_high_concern_profile
from app.models import Outbreak, ReviewCase
from app.models.core import ReviewCaseType
from app.schemas.core import OutbreakCreate


class TriageService:
    def flag_if_needed(self, db: Session, outbreak: Outbreak, payload: OutbreakCreate) -> Outbreak:
        if not payload.reporter_type:
            return outbreak
        profile = match_high_concern_profile(payload.symptoms)
        mortality_rate = outbreak.mortality_count / payload.animals_affected
        if not profile and mortality_rate <= TRIAGE_RULES.mortality_rate_threshold:
            return outbreak
        if profile:
            outbreak.disease_name = profile.disease_name
            reason = f"All configured high-concern symptoms for {profile.disease_name} were reported."
            priority = profile.priority
        else:
            reason = f"Reported mortality rate is {mortality_rate:.0%}, above the configured {TRIAGE_RULES.mortality_rate_threshold:.0%} threshold."
            priority = "high"
        existing = db.scalar(select(ReviewCase.id).where(
            ReviewCase.source_type == "outbreak", ReviewCase.source_id == str(outbreak.id), ReviewCase.category == "evidence_gap"
        ))
        if not existing:
            db.add(ReviewCase(
                source_type="outbreak", source_id=str(outbreak.id), category="evidence_gap",
                case_type=ReviewCaseType.EVIDENCE_GAP, priority=priority,
                title="Symptom and mortality report requires veterinary review",
                summary=f"{reason} {TRIAGE_RULES.disclaimer}",
            ))
        db.commit()
        db.refresh(outbreak)
        return outbreak
