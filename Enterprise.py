from pydantic import BaseModel

class BioData(BaseModel):
    location: str
    bacterial_count: float
    temperature: float
    humidity: float
    timestamp: str