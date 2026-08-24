from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Location
from app.models.core import OutbreakStatus, RiskState, VaccinationEvidence
from app.services.advisory import AdvisoryService

class PublicMovementCheckService:
 """Read-only pre-travel check; it deliberately persists nothing."""
 def __init__(self, advisory:AdvisoryService|None=None): self.advisory=advisory or AdvisoryService()
 def check(self,db:Session,origin_id:int,destination_id:int,species:str,count:int,vehicle_reference:str|None,vaccination:VaccinationEvidence|None):
  origin=db.get(Location,origin_id);destination=db.get(Location,destination_id)
  if not origin or not destination: raise HTTPException(404,"Origin or destination location was not found")
  if origin.id==destination.id: raise HTTPException(422,"Origin and destination must be different")
  now=datetime.now(UTC)
  class Preview: pass
  preview=Preview();preview.origin_location_id=origin.id;preview.destination_location_id=destination.id;preview.origin_location=origin;preview.destination_location=destination;preview.vaccination_evidence=vaccination or VaccinationEvidence.UNKNOWN;preview.vehicle_id=1 if vehicle_reference and vehicle_reference.strip() else None;preview.departure_at=now;preview.movement_events=[type("Event",(),{"event_type":type("EventType",(),{"value":"departure"})()})()]
  all_outbreaks=self.advisory.repository.list_relevant_outbreaks(db,now-timedelta(days=self.advisory.rules.confirmed_outbreak_window_days))
  confirmed=[x for x in all_outbreaks if x.status==OutbreakStatus.CONFIRMED and x.detected_at>=now-timedelta(days=self.advisory.rules.confirmed_outbreak_window_days) and self.advisory._is_relevant(preview,x)]
  suspected=[x for x in all_outbreaks if x.status==OutbreakStatus.SUSPECTED and x.detected_at>=now-timedelta(days=self.advisory.rules.suspected_outbreak_window_days) and self.advisory._is_relevant(preview,x)]
  origin_update=self.advisory.repository.latest_surveillance(db,origin.id);destination_update=self.advisory.repository.latest_surveillance(db,destination.id)
  date=min(x.updated_at for x in [origin_update,destination_update] if x) if origin_update and destination_update else None
  surveillance,_=self.advisory._surveillance_score(date,now);verification,_=self.advisory._verification_score(origin_update,destination_update)
  vaccination_score=25 if vaccination==VaccinationEvidence.VERIFIED else 15 if vaccination==VaccinationEvidence.DECLARED else 0
  movement=25 if preview.vehicle_id else 10;coverage=surveillance+verification+vaccination_score+movement
  state,reasons,action=self.advisory._determine_state(preview,confirmed,suspected,coverage)
  coverage_text="Sufficient information is available for this advisory." if coverage>=70 else "Information is incomplete; obtain current veterinary verification."
  return {"risk_state":state,"reasons":[x["text"] for x in reasons],"evidence_coverage_score":coverage,"information_coverage":coverage_text,"recommended_action":action,"advisory_disclaimer":"This is a pre-travel advisory. An authorised veterinary official makes the final decision.","generated_at":now}
