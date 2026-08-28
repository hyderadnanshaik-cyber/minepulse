from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.auth.firebase_auth import get_current_user, require_role
from app.schemas.ai import (
    AIStatusResponse, AITrainResponse,
    AIPredictionResponse
)
from app.services.ai_service import AIService
from app.models.ai_prediction import AIPrediction
from app.models.node import Node
from app.models.sensor_reading import SensorReading

router = APIRouter(prefix="/ai", tags=["AI & Machine Learning"])

@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Retrieve status and metrics of the AI Subsidence & Anomaly Detection model."""
    return await AIService.get_ai_status(db)

@router.get("/predictions", response_model=List[AIPredictionResponse])
async def get_predictions(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List recent AI predictions across all nodes."""
    return await AIService.get_recent_predictions(db=db, limit=limit)

@router.get("/predictions/{node_id}", response_model=List[AIPredictionResponse])
async def get_node_predictions(
    node_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List predictions for a specific sensor node."""
    return await AIService.get_recent_predictions(db=db, node_id=node_id, limit=limit)

@router.get("/spatial-analysis")
async def get_spatial_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Calculate multi-node spatial correlation clusters, predicted impact polygons, and evacuation state."""
    return await AIService.get_spatial_correlations(db)

@router.get("/spatial-correlation")
async def get_spatial_correlations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Alias for spatial correlation matrix."""
    return await AIService.get_spatial_correlations(db)

@router.get("/explain/{node_id}")
async def explain_node_risk(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Provides granular, data-driven explainability for a station's current AI risk score and trend."""
    pred_res = await db.execute(
        select(AIPrediction)
        .where(AIPrediction.node_id_fk == node_id)
        .order_by(desc(AIPrediction.id))
        .limit(1)
    )
    pred = pred_res.scalar_one_or_none()
    if not pred:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No predictions found for this node")

    node_res = await db.execute(select(Node).where(Node.node_id == node_id))
    node = node_res.scalar_one_or_none()

    readings_res = await db.execute(
        select(SensorReading)
        .where(SensorReading.node_id == node_id)
        .order_by(desc(SensorReading.id))
        .limit(10)
    )
    readings = list(readings_res.scalars().all())

    return {
        "node_id": node_id,
        "name": node.name if node else node_id,
        "zone": node.zone if node else "Underground Sector",
        "risk_level": pred.risk_level,
        "risk_score": pred.risk_score,
        "anomaly_score": pred.anomaly_score,
        "confidence": pred.confidence,
        "model_version": pred.model_version,
        "features": pred.features,
        "spatial_pattern": pred.spatial_pattern,
        "contributing_factors": (pred.spatial_pattern or {}).get("contributing_factors", []),
        "evacuation_recommended": (pred.spatial_pattern or {}).get("evacuation_recommended", False),
        "recommended_action": (pred.spatial_pattern or {}).get("recommended_action", "Continue standard logging"),
        "recent_samples_count": len(readings),
        "evaluated_at": pred.created_at.isoformat() if pred.created_at else None
    }

@router.post("/train", response_model=AITrainResponse)
async def train_ai_model(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("ADMIN"))
):
    """Trigger retraining and recalibration of the subsidence model (Admin only)."""
    return await AIService.train_model(db)
