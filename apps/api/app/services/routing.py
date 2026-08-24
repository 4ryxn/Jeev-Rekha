from datetime import UTC, datetime, timedelta
import heapq
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models import Consignment, Outbreak, RouteAssessment, RouteSegment
from app.models.core import OutbreakStatus
from app.models.core import LocationDataSource
from app.services.advisory import haversine_km
from app.services.road_routing import RoadRoutingProvider

class RouteService:
 def __init__(self, provider:RoadRoutingProvider|None=None): self.provider=provider or RoadRoutingProvider()
 def assess(self,db:Session,consignment_id:int):
  c=db.scalar(select(Consignment).options(selectinload(Consignment.origin_location),selectinload(Consignment.destination_location)).where(Consignment.id==consignment_id))
  if not c: raise ValueError("Consignment not found")
  if c.data_source == LocationDataSource.PILOT_ENTERED:
   return self.pilot_assess(db,c)
  segs=list(db.scalars(select(RouteSegment).where(RouteSegment.active.is_(True))))
  risky={o.location_id for o in db.scalars(select(Outbreak).where(Outbreak.status.in_([OutbreakStatus.CONFIRMED,OutbreakStatus.SUSPECTED]),Outbreak.detected_at>=datetime.now(UTC)-timedelta(days=21)))}
  pref=self.path(segs,c.origin_location_id,c.destination_location_id,set())
  if not pref: raise ValueError("No controlled route is available")
  direct=c.origin_location_id in risky or c.destination_location_id in risky
  safe=None if direct else self.path(segs,c.origin_location_id,c.destination_location_id,risky)
  safer=safe if safe and safe["segment_ids"]!=pref["segment_ids"] else None
  reasons=["Requested route intersects an active outbreak-risk location." if set(pref["location_ids"])&risky else "Requested route does not intersect a configured active outbreak-risk location."]
  if direct: reasons.append("Origin or destination is directly affected; a route change cannot resolve this exposure.")
  elif safer: reasons.append("A longer controlled-network alternative avoids configured outbreak-risk locations.")
  else: reasons.append("No safer route is currently available. Authorised veterinary guidance is required.")
  a=RouteAssessment(consignment_id=c.id,preferred_route=pref,safer_route=safer,preferred_distance_km=pref["distance_km"],preferred_minutes=pref["minutes"],safer_distance_km=safer["distance_km"] if safer else None,safer_minutes=safer["minutes"] if safer else None,risk_reduction="Reduced" if safer else ("Unchanged" if direct else "Low"),route_reasons=reasons)
  db.add(a);db.commit();db.refresh(a);return a
 def pilot_assess(self,db,c):
  direct=round(haversine_km(c.origin_location.latitude,c.origin_location.longitude,c.destination_location.latitude,c.destination_location.longitude),1)
  preferred={"segment_ids":[],"location_ids":[c.origin_location_id,c.destination_location_id],"coordinates":[[c.origin_location.longitude,c.origin_location.latitude],[c.destination_location.longitude,c.destination_location.latitude]],"distance_km":direct,"minutes":0}
  try:
   route=self.provider.route((c.origin_location.longitude,c.origin_location.latitude),(c.destination_location.longitude,c.destination_location.latitude))
   preferred={**preferred,"coordinates":route.geometry,"distance_km":route.distance_km,"minutes":route.minutes}
   item=RouteAssessment(consignment_id=c.id,preferred_route=preferred,safer_route=None,preferred_distance_km=route.distance_km,preferred_minutes=route.minutes,safer_distance_km=None,safer_minutes=None,risk_reduction="Unchanged",route_reasons=["Road route is informational only; no safer-route recommendation is generated for pilot records."],route_provider=route.provider,route_geometry=route.geometry,route_fallback_reason=None)
  except RuntimeError:
   item=RouteAssessment(consignment_id=c.id,preferred_route=preferred,safer_route=None,preferred_distance_km=direct,preferred_minutes=0,safer_distance_km=None,safer_minutes=None,risk_reduction="Unchanged",route_reasons=["Road route unavailable; no navigation recommendation is shown."],route_provider=None,route_geometry=None,route_fallback_reason="Road route unavailable; no navigation recommendation is shown.")
  db.add(item);db.commit();db.refresh(item);return item
 def path(self,segs,start,end,blocked):
  g={}
  for s in segs:
   if s.start_location_id in blocked or s.end_location_id in blocked: continue
   g.setdefault(s.start_location_id,[]).append((s.end_location_id,s));g.setdefault(s.end_location_id,[]).append((s.start_location_id,s))
  q=[(0,0,start,[],[start],0)];seen={};counter=0
  while q:
   d,_,n,used,nodes,mins=heapq.heappop(q)
   if n==end:return {"segment_ids":[s.id for s in used],"location_ids":nodes,"coordinates":sum([s.path if i==0 else s.path[1:] for i,s in enumerate(used)],[]),"distance_km":round(d,1),"minutes":mins}
   if seen.get(n,1e9)<=d:continue
   seen[n]=d
   for nxt,s in g.get(n,[]):
    counter+=1;heapq.heappush(q,(d+s.distance_km,counter,nxt,used+[s],nodes+[nxt],mins+s.estimated_minutes))
  return None
