import os
import operator
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from .models import BioDataPoint, Alert, AgentThought

class AgentState(TypedDict):
    data: BioDataPoint
    risk_level: str
    thoughts: Annotated[List[AgentThought], operator.add]
    alerts: Annotated[List[Alert], operator.add]
    final_recommendation: str

class BioAgents:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock

    def monitoring_agent(self, state: AgentState):
        b_cnt = state['data'].bacterial_count
        f_cnt = state['data'].fungal_count
        v_cnt = state['data'].viral_count
        
        thought = AgentThought(
            agent_name="Monitoring Agent",
            thought=f"Triage Analysis: Bacteria={b_cnt:.1f}, Fungi={f_cnt:.1f}, Virus={v_cnt:.1f}. Analyzing multi-microbial risk."
        )
        
        # Risk Triage Logic
        risk = "Low"
        if b_cnt >= 2500 or f_cnt >= 800 or v_cnt >= 80:
            risk = "High"
        elif b_cnt >= 1500 or f_cnt >= 400 or v_cnt >= 30:
            risk = "Medium"
        elif b_cnt >= 800 or f_cnt >= 150 or v_cnt >= 12:
            risk = "Elevated"
            
        return {"thoughts": [thought], "risk_level": risk}

    def threat_detection_agent(self, state: AgentState):
        risk = state['risk_level']
        thought = AgentThought(
            agent_name="Threat Detection Agent",
            thought=f"Critical assessment: {risk}. Microbial concentration exceeds safety profiles."
        )
        
        new_alerts = []
        if risk in ["High", "Medium", "Elevated"]:
            threats = []
            if state['data'].bacterial_count > 1500: threats.append("Bacterial Spike")
            if state['data'].fungal_count > 400: threats.append("Fungal Contamination")
            if state['data'].viral_count > 30: threats.append("Viral Presence")
            
            new_alerts.append(Alert(
                risk_level=risk,
                threat_type=" + ".join(threats) if threats else "System Anomaly",
                description=f"Multi-vector threat detected at {state['data'].location}."
            ))
            
        return {"thoughts": [thought], "alerts": new_alerts}

    def investigation_agent(self, state: AgentState):
        thought = AgentThought(
            agent_name="Investigation Agent",
            thought="Cross-referencing microbial types. Pattern suggests organic leakage or ineffective containment."
        )
        return {"thoughts": [thought]}

    def response_agent(self, state: AgentState):
        risk = state['risk_level']
        if risk == "High":
            rec = "🚨 HIGH ALERT: Immediate evacuation. Deploy Ultra-Violet (UV-C) Sterilization."
        elif risk == "Medium":
            rec = "⚠️ WARNING: Seal lab perimeter. Recalibrate bio-filters."
        elif risk == "Elevated":
            rec = "ℹ️ INFO: Baseline exceeded. Alert maintenance for decontamination review."
        else:
            rec = "✅ NORMAL: Continue routine surveillance."
            
        thought = AgentThought(
            agent_name="Response Agent",
            thought=f"Action recommendation: {rec}",
            action=rec
        )
        return {"thoughts": [thought], "final_recommendation": rec}

def create_bio_workflow():
    agents = BioAgents(use_mock=True)
    workflow = StateGraph(AgentState)
    
    workflow.add_node("monitor", agents.monitoring_agent)
    workflow.add_node("detect", agents.threat_detection_agent)
    workflow.add_node("investigate", agents.investigation_agent)
    workflow.add_node("respond", agents.response_agent)
    
    workflow.set_entry_point("monitor")
    workflow.add_edge("monitor", "detect")
    workflow.add_edge("detect", "investigate")
    workflow.add_edge("investigate", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()

bio_workflow = create_bio_workflow()
