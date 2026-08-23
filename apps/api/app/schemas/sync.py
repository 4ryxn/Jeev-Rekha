from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class SyncOperationRequest(BaseModel):
    client_operation_id: str = Field(min_length=8, max_length=64)
    operation_type: Literal["create_consignment", "create_outbreak"]
    payload: dict[str, object]

class SyncBatchRequest(BaseModel):
    operations: list[SyncOperationRequest] = Field(min_length=1, max_length=50)

class SyncOperationResult(BaseModel):
    client_operation_id: str
    operation_type: str
    status: Literal["synced", "needs_review", "failed"]
    entity_type: str | None = None
    entity_id: int | None = None
    received_at: datetime | None = None
    error: str | None = None
