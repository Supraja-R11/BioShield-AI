import asyncio
import random
from datetime import datetime
from sqlmodel import Session
from .models import BioDataPoint
from .database import engine

class BioSimulator:
    def __init__(self):
        self.is_running = False
        self.data_history = []

    async def generate_data(self):
        """Simulate real-time bio-data metrics matching Bacteria, Fungi, and Virus cases."""
        while self.is_running:
            # Randomly select a scenario for simulation
            scenario = random.choices(['normal', 'medium', 'high', 'spike'], weights=[60, 20, 10, 10])[0]
            
            if scenario == 'normal':
                bac = random.uniform(700, 900)
                fun = random.uniform(50, 120)
                vir = random.uniform(2, 10)
                status = "nominal"
            elif scenario == 'medium':
                bac = random.uniform(1400, 1600)
                fun = random.uniform(200, 400)
                vir = random.uniform(15, 30)
                status = "warning"
            elif scenario == 'high':
                bac = random.uniform(2400, 2600)
                fun = random.uniform(500, 800)
                vir = random.uniform(40, 70)
                status = "critical"
            else: # spike
                bac = random.uniform(2800, 5000)
                fun = random.uniform(800, 1500)
                vir = random.uniform(80, 200)
                status = "emergency"
            
            point = BioDataPoint(
                location="Lab A",
                bacterial_count=bac,
                fungal_count=fun,
                viral_count=vir,
                temperature=random.uniform(35.0, 39.0),
                humidity=random.uniform(60.0, 80.0),
                status=status
            )
            
            # Persist to Database
            with Session(engine) as session:
                session.add(point)
                session.commit()
                session.refresh(point)
            
            self.data_history.append(point)
            if len(self.data_history) > 100:
                self.data_history.pop(0)
            
            await asyncio.sleep(2)

    def start(self):
        self.is_running = True
        asyncio.create_task(self.generate_data())

    def stop(self):
        self.is_running = False

simulator = BioSimulator()
