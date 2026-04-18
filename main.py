import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import io
from sqlmodel import Session, select
from .models import BioDataPoint, Alert, AgentThought
from .agents import bio_workflow
from .database import engine, create_db_and_tables

app = FastAPI(title="BioThreat Monitoring System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/analytics")
async def get_analytics():
    with Session(engine) as session:
        statement = select(BioDataPoint).order_by(BioDataPoint.timestamp.desc()).limit(50)
        results = session.exec(statement).all()
        return results

@app.get("/alerts")
async def get_alerts():
    with Session(engine) as session:
        statement = select(Alert).order_by(Alert.timestamp.desc()).limit(100)
        results = session.exec(statement).all()
        return results

@app.post("/analyze-upload")
async def analyze_upload(file: UploadFile = File(...)):
    contents = await file.read()
    
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    required = ['bacterial_count', 'temperature', 'humidity', 'location']
    
    if not all(col in df.columns for col in required):
        return {"error": f"Missing required columns. Expected: {required}"}

    results = []
    
    for _, row in df.iterrows():
        point = BioDataPoint(
            location=str(row['location']),
            bacterial_count=float(row['bacterial_count']),
            fungal_count=float(row.get('fungal_count', 0.0)),
            viral_count=float(row.get('viral_count', 0.0)),
            temperature=float(row['temperature']),
            humidity=float(row['humidity']),
            timestamp=datetime.now()
        )
        
        initial_state = {
            "data": point,
            "risk_level": "Low",
            "thoughts": [],
            "alerts": [],
            "final_recommendation": ""
        }
        
        agent_result = bio_workflow.invoke(initial_state)
        
        # Optionally persist analysis to DB for history/analytics views
        with Session(engine) as session:
            session.add(point)
            for a in agent_result["alerts"]:
                session.add(a)
            session.commit()
        
        results.append({
            "data": point.model_dump(),
            "risk_level": agent_result["risk_level"],
            "recommendation": agent_result["final_recommendation"]
        })

    summary = {
        "total": len(results),
        "high_risk": len([r for r in results if r['risk_level'] == 'High']),
        "medium_risk": len([r for r in results if r['risk_level'] == 'Medium']),
        "low_risk": len([r for r in results if r['risk_level'] == 'Low' or r['risk_level'] == 'Elevated']),
    }

    return {"summary": summary, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
