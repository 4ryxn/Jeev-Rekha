from datetime import UTC, datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Advisory, Outbreak, ReviewCase, SyncReceipt, TraceFinding, TraceRun
from app.models.core import LocationDataSource
from app.models.core import RiskState

class ReviewService:
 def refresh(self,db:Session):
  sources=[]
  for a in db.scalars(select(Advisory).where((Advisory.risk_state==RiskState.GREY)|((Advisory.risk_state==RiskState.RED)&(Advisory.route_state.is_not(None))))):
   sources.append(("advisory",str(a.id),"evidence_gap","high","Evidence coverage requires veterinary review",f"Grey advisory with evidence coverage score {a.evidence_coverage_score}."))
  for receipt in db.scalars(select(SyncReceipt).where(SyncReceipt.status=="needs_review")):
   sources.append(("sync_operation",receipt.client_operation_id,"sync_exception","medium","Offline registration requires review",f"{receipt.operation_type.replace('_',' ')} could not be accepted during sync."))
  for finding in db.scalars(select(TraceFinding).where(TraceFinding.review_status=="requires_veterinary_review")):
   sources.append(("trace_finding",str(finding.id),"trace_contact","medium","Trace contact requires veterinary review",finding.explanation))
  for source_type,source_id,category,priority,title,summary in sources:
   if not db.scalar(select(ReviewCase.id).where(ReviewCase.source_type==source_type,ReviewCase.source_id==source_id,ReviewCase.category==category)):
    db.add(ReviewCase(source_type=source_type,source_id=source_id,category=category,case_type=category,priority=priority,title=title,summary=summary))
  db.commit()
 def list(self,db,status=None,category=None,source:LocationDataSource|None=None):
  self.refresh(db); q=select(ReviewCase)
  if status:q=q.where(ReviewCase.status==status)
  if category:q=q.where(ReviewCase.category==category)
  cases=list(db.scalars(q.order_by(ReviewCase.created_at.desc())))
  return [item for item in cases if source is None or self.source_data_source(item, db)==source]
 def get(self,db,id): self.refresh(db); return db.get(ReviewCase,id)
 def update(self,db,item,status,note):
  now=datetime.now(UTC)
  if status=="acknowledged": item.status="acknowledged";item.acknowledged_at=now
  else: item.status="resolved";item.resolution_note=note.strip();item.resolved_at=now
  db.commit();db.refresh(item);return item
 def source_data_source(self,item,db):
  if item.source_type=="advisory":
   advisory=db.get(Advisory,int(item.source_id)); return advisory.data_source if advisory else None
  if item.source_type=="trace_finding":
   finding=db.get(TraceFinding,int(item.source_id));
   if not finding:return None
   trace=db.get(TraceRun,finding.trace_run_id); return trace.data_source if trace else None
  if item.source_type=="sync_operation":
   receipt=db.scalar(select(SyncReceipt).where(SyncReceipt.client_operation_id==item.source_id)); return receipt.data_source if receipt else None
  if item.source_type=="outbreak":
   outbreak=db.get(Outbreak,int(item.source_id)); return outbreak.data_source if outbreak else None
  return None
 def source_meta(self,item,db):
  href={"advisory":f"/advisories/{item.source_id}","trace_finding":"/trace-lab","sync_operation":"/register","outbreak":"/"}[item.source_type]
  return {"source_summary":item.summary,"source_href":href,"data_source":self.source_data_source(item,db)}
