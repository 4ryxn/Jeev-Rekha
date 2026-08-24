from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from app.models.core import RiskState, VaccinationEvidence

class PublicMovementCheckRequest(BaseModel):
 origin_location_id:int=Field(gt=0)
 destination_location_id:int=Field(gt=0)
 species:str=Field(min_length=2,max_length=80)
 approximate_animal_count:int=Field(gt=0,le=100000)
 vehicle_reference:str|None=Field(default=None,max_length=64)
 vaccination_evidence:VaccinationEvidence|None=None
 @model_validator(mode="after")
 def distinct_locations(self):
  if self.origin_location_id==self.destination_location_id: raise ValueError("origin and destination must be different")
  return self

class PublicMovementCheckResponse(BaseModel):
 risk_state:RiskState
 reasons:list[str]
 evidence_coverage_score:int=Field(ge=0,le=100)
 information_coverage:str
 recommended_action:str
 advisory_disclaimer:str
 generated_at:datetime
