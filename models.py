from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import List, Optional
import uuid

class BioDataPoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    location: str
    bacterial_count: float
    fungal_count: float = 0.0
    viral_count: float = 0.0
    temperature: float
    humidity: float
    status: str = "nominal"

class Alert(SQLModel, table=True):
    id: str = Field(default_factory=lambda: f"ALT-{uuid.uuid4().hex[:8]}", primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    risk_level: str  # Low, Medium, High
    threat_type: str
    description: str
    status: str = "active"  # active, mitigated, investigating

class AgentThought(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    agent_name: str
    thought: str
    action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
