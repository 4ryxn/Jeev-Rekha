from datetime import UTC, datetime
from fastapi.testclient import TestClient
from app.main import app
from app.seed import seed

client=TestClient(app)
def payload():
 seed(); locations=client.get('/api/v1/locations?type=village').json(); return {"client_operation_id":"sync-test-0001","operation_type":"create_consignment","payload":{"origin_location_id":locations[0]['id'],"destination_location_id":locations[1]['id'],"species":"Goat","animal_count":4,"vehicle_reference":"SYNC-001","departure_at":datetime.now(UTC).isoformat(),"vaccination_evidence":"declared"}}
def test_sync_is_idempotent_and_mixed_results_are_per_operation():
 good=payload(); bad={"client_operation_id":"sync-test-0002","operation_type":"create_outbreak","payload":{"disease_name":""}}
 first=client.post('/api/v1/sync/operations',json={"operations":[good,bad]});assert first.status_code==200; results=first.json();assert results[0]['status']=='synced' and results[1]['status']=='needs_review'; entity=results[0]['entity_id']
 retry=client.post('/api/v1/sync/operations',json={"operations":[good]});assert retry.status_code==200;assert retry.json()[0]['entity_id']==entity
