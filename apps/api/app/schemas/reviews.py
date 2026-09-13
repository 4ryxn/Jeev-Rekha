from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from app.models.core import LocationDataSource, ReviewCaseType, SampleStatus

class ReviewCasePatch(BaseModel):
 status: Literal["acknowledged","resolved"]
 resolution_note: str|None=None
class SampleStatusUpdate(BaseModel):
 sample_status: SampleStatus
class ReviewCaseRead(BaseModel):
 model_config={"from_attributes":True}
 id:int; source_type:str; source_id:str; category:str; case_type:ReviewCaseType; sample_status:SampleStatus; priority:str; title:str; summary:str; status:str; resolution_note:str|None; created_at:datetime; acknowledged_at:datetime|None; resolved_at:datetime|None; source_summary:str; source_href:str; data_source:LocationDataSource|None=None
