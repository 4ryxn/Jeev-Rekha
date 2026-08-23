from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models import Consignment, ContainmentScenario, MovementEvent, Outbreak, RouteAssessment
from app.models.core import MovementEventType, OutbreakStatus

MODIFIERS={"checkpoint_screening":("Checkpoint screening applies a synthetic 20% route/checkpoint workload modifier, rounded to whole recorded items with a minimum one-item effect only when applicable workload exists.",.20),"targeted_vaccination_outreach":("Targeted vaccination outreach improves preparedness review coverage; it does not claim instant immunity or prevention.",0),"route_avoidance_advisory":("Route-avoidance advisory applies a synthetic 20% route-risk workload modifier, rounded to whole recorded items with a minimum one-item effect only when applicable workload exists.",.20),"market_notification":("Market notification applies a synthetic 15% market-contact workload modifier, rounded to whole recorded items with a minimum one-item effect only when applicable workload exists.",.15)}
class ContainmentService:
 def create(self,db:Session,outbreak_id:int,horizon:int,actions:list[str]):
  outbreak=db.scalar(select(Outbreak).options(selectinload(Outbreak.location)).where(Outbreak.id==outbreak_id))
  if not outbreak: raise HTTPException(404,"Outbreak not found")
  if outbreak.status!=OutbreakStatus.CONFIRMED: raise HTTPException(422,"Only confirmed outbreaks can create containment scenarios")
  reference=outbreak.confirmed_at or outbreak.detected_at; end=reference+timedelta(days=horizon)
  rows=list(db.execute(select(MovementEvent,Consignment).join(Consignment).where(MovementEvent.occurred_at>=reference,MovementEvent.occurred_at<=end)))
  cons={c.id for _,c in rows}; locations={e.location_id for e,_ in rows}; vehicles={c.vehicle_id for _,c in rows}; checkpoint=sum(1 for e,_ in rows if e.event_type==MovementEventType.CHECKPOINT); markets=sum(1 for e,_ in rows if e.event_type==MovementEventType.MARKET_ENTRY); other=max(0,len(rows)-checkpoint-markets); exposure=len(list(db.scalars(select(RouteAssessment).join(Consignment).where(Consignment.origin_location_id==outbreak.location_id))))
  baseline={"estimated_review_contacts":len(rows),"route_checkpoint_contacts":checkpoint,"market_contacts":markets,"other_review_contacts":other,"affected_locations":len(locations),"affected_vehicles":len(vehicles),"affected_consignments":len(cons),"baseline_route_risk_exposure_count":exposure}
  route_reduction=max(1,round(checkpoint*.20)) if checkpoint and "checkpoint_screening" in actions else 0; market_reduction=max(1,round(markets*.15)) if markets and "market_notification" in actions else 0; exposure_reduction=max(1,round(exposure*.20)) if exposure and "route_avoidance_advisory" in actions else 0
  action_effects={}
  for action in actions:
   if action=="checkpoint_screening": action_effects[action]={"category":"route/checkpoint contacts","applicable_workload":checkpoint,"reduction":route_reduction}
   elif action=="market_notification": action_effects[action]={"category":"market contacts","applicable_workload":markets,"reduction":market_reduction}
   elif action=="route_avoidance_advisory": action_effects[action]={"category":"route-risk exposure workload","applicable_workload":exposure,"reduction":exposure_reduction}
   else: action_effects[action]={"category":"preparedness review workload","applicable_workload":len(cons),"reduction":0}
  scenario={**baseline,"estimated_review_contacts":max(0,min(len(rows),len(rows)-route_reduction-market_reduction)),"route_checkpoint_contacts":checkpoint-route_reduction,"market_contacts":markets-market_reduction,"scenario_route_risk_exposure_count":max(0,exposure-exposure_reduction),"action_effects":action_effects}
  action_assumptions=[]
  for a in actions:
   if a=="checkpoint_screening" and checkpoint==0: action_assumptions.append("No applicable recorded route/checkpoint workload in this scenario.")
   elif a=="market_notification" and markets==0: action_assumptions.append("No applicable recorded market workload in this scenario.")
   elif a=="route_avoidance_advisory" and exposure==0: action_assumptions.append("No applicable recorded route-risk exposure workload in this scenario.")
   elif a=="targeted_vaccination_outreach" and not cons: action_assumptions.append("No applicable recorded preparedness review workload in this scenario.")
   else: action_assumptions.append(MODIFIERS[a][0])
  assumptions=["Synthetic decision-support scenario only; not an epidemiological prediction or automated order.",f"Scenario horizon is {horizon} days from the confirmed outbreak reference.",*action_assumptions,f"Baseline contact mix: {checkpoint} route/checkpoint, {markets} market, and {other} other review contacts. Requires authorised veterinary review."]
  item=ContainmentScenario(outbreak_id=outbreak.id,horizon_days=horizon,selected_actions=actions,baseline_summary=baseline,scenario_summary=scenario,assumptions=assumptions);db.add(item);db.commit();db.refresh(item);return self.get(db,item.id)
 def get(self,db,id): return db.scalar(select(ContainmentScenario).options(selectinload(ContainmentScenario.outbreak).selectinload(Outbreak.location)).where(ContainmentScenario.id==id))
 def list(self,db,outbreak_id): return list(db.scalars(select(ContainmentScenario).options(selectinload(ContainmentScenario.outbreak).selectinload(Outbreak.location)).where(ContainmentScenario.outbreak_id==outbreak_id).order_by(ContainmentScenario.created_at.desc())))
