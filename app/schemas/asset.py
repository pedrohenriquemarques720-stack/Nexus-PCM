from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssetBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    asset_type: str = "equipment"
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    critical_level: int = 3

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: str
    total_operating_hours: float
    failure_count: int
    status: str
    created_at: datetime