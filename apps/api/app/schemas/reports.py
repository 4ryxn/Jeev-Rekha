from pydantic import BaseModel
from app.models.core import LocationDataSource

class ReportSourceRead(BaseModel):
 id:int
 href:str
 title:str
 data_source:LocationDataSource
class ReportIndexRead(BaseModel):
 advisories:list[ReportSourceRead]
 traces:list[ReportSourceRead]
 containment:list[ReportSourceRead]
