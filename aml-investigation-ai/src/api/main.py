"""FastAPI application for AML Investigation AI."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

from ..config import settings
from ..models.investigation_case import InvestigationCase, AlertType
from ..models.investigation_result import InvestigationResult
from ..investigators.react_investigator import ReACTInvestigator

# Create FastAPI app
app = FastAPI(
    title="AML Investigation AI",
    description="AI-powered Anti-Money Laundering investigation system using ReACT framework",
    version="1.0.0",
    docs_url=f"{settings.api_prefix}/docs",
    openapi_url=f"{settings.api_prefix}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for investigations (in production, use database)
investigations: Dict[str, InvestigationResult] = {}


# Request/Response models
class InvestigationRequest(BaseModel):
    """Request to start an investigation."""
    customer_id: str
    account_id: str
    alert_type: AlertType
    description: str
    priority: str = "medium"
    amount: Optional[float] = None
    time_period_days: int = 30
    customer_explanation: Optional[str] = None
    alert_source: Optional[str] = None


class InvestigationStatusResponse(BaseModel):
    """Investigation status response."""
    investigation_id: str
    case_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AML Investigation AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Root endpoint
@app.get(settings.api_prefix)
async def root():
    """API root endpoint."""
    return {
        "message": "AML Investigation AI API",
        "version": "1.0.0",
        "docs": f"{settings.api_prefix}/docs",
        "endpoints": {
            "health": "/health",
            "start_investigation": f"{settings.api_prefix}/investigations",
            "get_investigation": f"{settings.api_prefix}/investigations/{{investigation_id}}",
            "list_investigations": f"{settings.api_prefix}/investigations"
        }
    }


@app.post(
    f"{settings.api_prefix}/investigations",
    response_model=InvestigationResult,
    status_code=status.HTTP_201_CREATED
)
async def start_investigation(request: InvestigationRequest):
    """
    Start a new AML investigation.
    
    This endpoint initiates a ReACT-based investigation using AI agents to analyze
    suspicious financial activity and determine if SAR filing is required.
    """
    # Generate case ID
    case_id = f"CASE_{datetime.now().strftime('%Y%m%d')}_{len(investigations) + 1:04d}"
    
    # Create investigation case
    case = InvestigationCase(
        case_id=case_id,
        customer_id=request.customer_id,
        account_id=request.account_id,
        alert_type=request.alert_type,
        description=request.description,
        priority=request.priority,
        amount=request.amount,
        time_period_days=request.time_period_days,
        customer_explanation=request.customer_explanation,
        alert_source=request.alert_source,
    )
    
    try:
        # Create investigator and run investigation
        investigator = ReACTInvestigator()
        result = investigator.investigate(case, verbose=False)
        
        # Store result
        investigations[result.investigation_id] = result
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )


@app.get(f"{settings.api_prefix}/investigations/{{investigation_id}}")
async def get_investigation(investigation_id: str):
    """
    Get investigation results by ID.
    
    Returns the complete investigation report including evidence, findings,
    and recommendations.
    """
    if investigation_id not in investigations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found"
        )
    
    return investigations[investigation_id]


@app.get(f"{settings.api_prefix}/investigations")
async def list_investigations(
    limit: int = 10,
    offset: int = 0,
    sar_required: Optional[bool] = None,
    min_risk_score: Optional[float] = None
):
    """
    List all investigations with optional filtering.
    
    Supports pagination and filtering by SAR requirement and risk score.
    """
    results = list(investigations.values())
    
    # Apply filters
    if sar_required is not None:
        results = [r for r in results if r.sar_required == sar_required]
    
    if min_risk_score is not None:
        results = [r for r in results if r.final_risk_score >= min_risk_score]
    
    # Sort by completion time (most recent first)
    results.sort(key=lambda x: x.completed_at or datetime.now(), reverse=True)
    
    # Apply pagination
    total = len(results)
    results = results[offset:offset + limit]
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "investigations": results
    }


@app.delete(f"{settings.api_prefix}/investigations/{{investigation_id}}")
async def delete_investigation(investigation_id: str):
    """Delete an investigation (for testing/cleanup)."""
    if investigation_id not in investigations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation {investigation_id} not found"
        )
    
    del investigations[investigation_id]
    return {"message": f"Investigation {investigation_id} deleted"}


@app.get(f"{settings.api_prefix}/stats")
async def get_stats():
    """Get investigation statistics."""
    results = list(investigations.values())
    
    if not results:
        return {
            "total_investigations": 0,
            "sar_filed": 0,
            "sar_rate": 0.0,
            "avg_risk_score": 0.0,
            "avg_duration_seconds": 0.0
        }
    
    sar_count = sum(1 for r in results if r.sar_required)
    total_risk = sum(r.final_risk_score for r in results)
    total_duration = sum(r.investigation_duration_seconds or 0 for r in results)
    
    return {
        "total_investigations": len(results),
        "sar_filed": sar_count,
        "sar_rate": round(sar_count / len(results) * 100, 2),
        "avg_risk_score": round(total_risk / len(results), 2),
        "avg_duration_seconds": round(total_duration / len(results), 2),
        "by_alert_type": _group_by_alert_type(results),
        "by_risk_level": _group_by_risk_level(results)
    }


def _group_by_alert_type(results: List[InvestigationResult]) -> Dict:
    """Group investigations by alert type."""
    groups = {}
    for result in results:
        # Extract alert type from case (if available in reasoning)
        alert_type = "unknown"  # In production, store this in result
        groups[alert_type] = groups.get(alert_type, 0) + 1
    return groups


def _group_by_risk_level(results: List[InvestigationResult]) -> Dict:
    """Group investigations by risk level."""
    groups = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for result in results:
        if result.final_risk_score >= 8:
            groups["critical"] += 1
        elif result.final_risk_score >= 6:
            groups["high"] += 1
        elif result.final_risk_score >= 4:
            groups["medium"] += 1
        else:
            groups["low"] += 1
    return groups


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )

