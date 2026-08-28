import random
import string
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, or_
from fastapi import HTTPException, status

from app.models.node import Node, NodeRegistrationCode
from app.models.panel import Panel
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert
from app.models.ai_prediction import AIPrediction
from app.schemas.node import NodeCreate, NodeRegisterRequest, NodeUpdate, RegistrationCodeCreate

class NodeService:

    @staticmethod
    async def get_nodes(
        db: AsyncSession,
        panel_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        query = select(Node).offset(skip).limit(limit).order_by(Node.id)
        if not include_archived:
            query = query.where(or_(Node.is_archived.is_(False), Node.is_archived.is_(None)))
        if panel_id is not None:
            query = query.where(Node.panel_id_fk == panel_id)
        if status_filter:
            query = query.where(Node.status == status_filter.upper())
        
        result = await db.execute(query)
        nodes = result.scalars().all()
        
        # Batch query latest AI predictions to get true dynamic risk levels
        preds_res = await db.execute(
            select(AIPrediction).order_by(desc(AIPrediction.id)).limit(200)
        )
        recent_preds = preds_res.scalars().all()
        latest_pred_map: Dict[str, AIPrediction] = {}
        for p in recent_preds:
            if p.node_id_fk not in latest_pred_map:
                latest_pred_map[p.node_id_fk] = p

        output = []
        for n in nodes:
            pred = latest_pred_map.get(n.node_id)
            risk_lvl = pred.risk_level if pred else "NORMAL"
            risk_sc = pred.risk_score if pred else 5.0

            # If node status is offline or archived, reflect it
            current_status = "ARCHIVED" if n.is_archived else (n.status or "ONLINE")
            if current_status == "ONLINE" and risk_lvl == "CRITICAL":
                current_status = "CRITICAL"
            elif current_status == "ONLINE" and risk_lvl == "HIGH":
                current_status = "WARNING"

            output.append({
                "id": n.id,
                "node_id": n.node_id,
                "node_code": n.node_id,
                "device_id": n.node_id,
                "name": n.name or f"Station {n.node_id}",
                "zone": n.zone or "North Shaft",
                "site_id": n.site_id or "MINE-CENTRAL-01",
                "panel_id": n.panel_id_fk or "PANEL-A",
                "connection_type": n.connection_type or "LoRa",
                "gateway_id": n.gateway_id or "MINEGATE-01",
                "sensor_types": n.sensor_types or ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"],
                "thresholds": n.thresholds or {
                    "warning_disp_mm": 15.0, "critical_disp_mm": 25.0,
                    "warning_tilt_deg": 2.0, "critical_tilt_deg": 3.5,
                    "warning_crack_mm": 1.5, "critical_crack_mm": 3.0
                },
                "latitude": n.latitude,
                "longitude": n.longitude,
                "status": current_status,
                "risk_level": risk_lvl,
                "risk_score": risk_sc,
                "battery_level": n.battery_level,
                "battery": n.battery_level,
                "signal_strength": n.signal_strength or -70.0,
                "is_archived": n.is_archived or False,
                "installed_at": n.installed_at.isoformat() if n.installed_at else None,
                "last_seen": n.updated_at.isoformat() if n.updated_at else (n.installed_at.isoformat() if n.installed_at else None)
            })
        return output

    @staticmethod
    async def get_node_summary(db: AsyncSession) -> Dict[str, int]:
        """Calculates live fleet summary statistics from PostgreSQL."""
        nodes = await NodeService.get_nodes(db, include_archived=False)
        total = len(nodes)
        online = sum(1 for n in nodes if n["status"] == "ONLINE")
        warning = sum(1 for n in nodes if n["status"] == "WARNING" or n["risk_level"] in ["WATCH", "HIGH"])
        critical = sum(1 for n in nodes if n["status"] == "CRITICAL" or n["risk_level"] == "CRITICAL")
        offline = sum(1 for n in nodes if n["status"] == "OFFLINE")

        return {
            "total_nodes": total,
            "online": online,
            "warning": warning,
            "critical": critical,
            "offline": offline
        }

    @staticmethod
    async def create_node(db: AsyncSession, payload: NodeCreate) -> Dict[str, Any]:
        """Creates and persists a new monitoring station in PostgreSQL."""
        existing = await NodeService.get_node_by_code(db, payload.node_id.strip().upper())
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Node ID '{payload.node_id}' already exists in PostgreSQL database."
            )

        # Ensure target panel exists to satisfy foreign key constraint
        target_panel = (payload.panel_id or "PANEL-A").strip().upper()
        p_res = await db.execute(select(Panel).where(Panel.panel_id == target_panel))
        existing_panel = p_res.scalars().first()
        if not existing_panel:
            new_p = Panel(panel_id=target_panel, name=f"Panel {target_panel}", status="ACTIVE")
            db.add(new_p)
            await db.flush()

        now = datetime.now()
        node = Node(
            node_id=payload.node_id.strip().upper(),
            name=payload.name or f"Station {payload.node_id.strip().upper()}",
            zone=payload.zone or "North Shaft",
            site_id=payload.site_id or "MINE-CENTRAL-01",
            panel_id_fk=target_panel,
            connection_type=payload.connection_type or "LoRa",
            gateway_id=payload.gateway_id or "MINEGATE-01",
            sensor_types=payload.sensor_types or ["Displacement", "Tilt", "Crack", "Temperature", "Vibration"],
            thresholds=payload.thresholds or {
                "warning_disp_mm": 15.0, "critical_disp_mm": 25.0,
                "warning_tilt_deg": 2.0, "critical_tilt_deg": 3.5,
                "warning_crack_mm": 1.5, "critical_crack_mm": 3.0
            },
            latitude=payload.latitude or 23.7500,
            longitude=payload.longitude or 86.4200,
            status=payload.status or "ONLINE",
            battery_level=payload.battery_level or 100.0,
            installed_at=now,
            is_archived=False
        )
        db.add(node)
        await db.commit()
        await db.refresh(node)

        return {
            "id": node.id,
            "node_id": node.node_id,
            "node_code": node.node_id,
            "name": node.name,
            "zone": node.zone,
            "site_id": node.site_id,
            "panel_id": node.panel_id_fk,
            "connection_type": node.connection_type,
            "gateway_id": node.gateway_id,
            "sensor_types": node.sensor_types,
            "thresholds": node.thresholds,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "status": node.status,
            "battery_level": node.battery_level,
            "installed_at": node.installed_at.isoformat() if node.installed_at else None
        }

    @staticmethod
    async def archive_node(db: AsyncSession, node_id_or_code: Any) -> Dict[str, Any]:
        """Soft-archives a node in PostgreSQL while preserving historical telemetry."""
        if str(node_id_or_code).isdigit():
            node = await NodeService.get_node_by_id(db, int(node_id_or_code))
        else:
            node = await NodeService.get_node_by_code(db, str(node_id_or_code))

        if not node:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

        node.is_archived = True
        node.status = "ARCHIVED"
        await db.commit()
        await db.refresh(node)

        return {
            "id": node.id,
            "node_id": node.node_id,
            "is_archived": True,
            "status": "ARCHIVED",
            "message": f"Node {node.node_id} successfully archived. Telemetry history preserved for compliance audit."
        }

    @staticmethod
    async def get_node_by_id(db: AsyncSession, node_id: int) -> Optional[Node]:
        query = select(Node).where(Node.id == node_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_node_by_code(db: AsyncSession, node_id_str: str) -> Optional[Node]:
        query = select(Node).where(Node.node_id == node_id_str)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_node(
        db: AsyncSession,
        node_id_or_code: Any,
        update_data: NodeUpdate
    ) -> Dict[str, Any]:
        if str(node_id_or_code).isdigit():
            node = await NodeService.get_node_by_id(db, int(node_id_or_code))
        else:
            node = await NodeService.get_node_by_code(db, str(node_id_or_code))

        if not node:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            if k == "panel_id":
                node.panel_id_fk = v
            elif hasattr(node, k):
                setattr(node, k, v)

        await db.commit()
        await db.refresh(node)
        return {
            "id": node.id,
            "node_id": node.node_id,
            "name": node.name,
            "zone": node.zone,
            "status": node.status,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "battery_level": node.battery_level
        }

    @staticmethod
    async def get_node_readings(
        db: AsyncSession,
        node_id_or_code: Any,
        limit: int = 100
    ) -> List[SensorReading]:
        node_code = str(node_id_or_code)
        if isinstance(node_id_or_code, int) or node_code.isdigit():
            node = await NodeService.get_node_by_id(db, int(node_code))
            if node:
                node_code = node.node_id

        query = select(SensorReading).where(SensorReading.node_id == node_code).order_by(desc(SensorReading.recorded_at)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_node_alerts(
        db: AsyncSession,
        node_id_or_code: Any,
        limit: int = 50
    ) -> List[Alert]:
        node_code = str(node_id_or_code)
        if isinstance(node_id_or_code, int) or node_code.isdigit():
            node = await NodeService.get_node_by_id(db, int(node_code))
            if node:
                node_code = node.node_id

        query = select(Alert).where(Alert.node_id_fk == node_code).order_by(desc(Alert.detected_at)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
