from datetime import datetime
from pydantic import BaseModel
class RouteAssessRequest(BaseModel): consignment_id:int
class RouteAssessmentRead(BaseModel):
 model_config={"from_attributes":True}
 id:int;consignment_id:int;preferred_route:dict;safer_route:dict|None;preferred_distance_km:float;preferred_minutes:int;safer_distance_km:float|None;safer_minutes:int|None;risk_reduction:str;route_reasons:list[str];assessed_at:datetime
