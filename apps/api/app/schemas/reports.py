from pydantic import BaseModel

class ReportSourceRead(BaseModel):
 id:int
 href:str
 title:str
class ReportIndexRead(BaseModel):
 advisories:list[ReportSourceRead]
 traces:list[ReportSourceRead]
 containment:list[ReportSourceRead]
