from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] | None = None
    id: Union[str, int, None] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Any | None = None
    error: Optional[Dict[str, Any]] = None
    id: Union[str, int, None] = None

class SupabaseQueryParams(BaseModel):
    table_name: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    columns: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0
    order_by: Optional[str] = None
    ascending: bool = True

class VectorUpsertParams(BaseModel):
    namespace: str
    ref: str
    embedding: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VectorQueryParams(BaseModel):
    namespace: str
    embedding: List[float]
    top_k: int = 5
