from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.core import OutbreakRead
Action=Literal["checkpoint_screening","targeted_vaccination_outreach","route_avoidance_advisory","market_notification"]
class ContainmentCreate(BaseModel): horizon_days: Literal[7,14]; selected_actions:list[Action]=Field(min_length=1)
class ContainmentRead(BaseModel):
 model_config={"from_attributes":True}
 id:int; outbreak:OutbreakRead; horizon_days:int; selected_actions:list[str]; baseline_summary:dict[str,object]; scenario_summary:dict[str,object]; assumptions:list[str]; created_at:datetime
