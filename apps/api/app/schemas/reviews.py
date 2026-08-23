from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, model_validator

class ReviewCasePatch(BaseModel):
 status: Literal["acknowledged","resolved"]
 resolution_note: str|None=None
 @model_validator(mode="after")
 def resolution_requires_note(self):
  if self.status=="resolved" and not (self.resolution_note or "").strip(): raise ValueError("resolution_note is required when resolving a review case")
  return self
class ReviewCaseRead(BaseModel):
 model_config={"from_attributes":True}
 id:int; source_type:str; source_id:str; category:str; priority:str; title:str; summary:str; status:str; resolution_note:str|None; created_at:datetime; acknowledged_at:datetime|None; resolved_at:datetime|None; source_summary:str; source_href:str
