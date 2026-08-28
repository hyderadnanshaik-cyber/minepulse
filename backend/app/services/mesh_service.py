from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc, func
from fastapi import HTTPException, status

from app.models.node import Node
from app.models.mesh_connection import MeshConnection
from app.models.connectivity_event import NodeConnectivityEvent
from app.schemas.mesh import (
    MeshTopologyGraph, MeshTopologyNode, MeshTopologyLink,
    MeshHealthResponse, ConnectivityEventResponse
)
from app.ws.manager import ws_manager

class MeshService:

    @staticmethod
    async def update_mesh_connections(
        db: AsyncSession,
        node_id_str: str,
        neighbors: List[Dict[str, Any]],
        route_path: Optional[List[Any]] = None,
        hop_count: Optional[int] = None,
        parent_node_id: Optional[str] = None
    ):
        now = datetime.now()

        # Update mesh_connections table
        for neighbor in neighbors:
            neigh_id = str(neighbor.get("node_id") or neighbor.get("neighbor_id") or "")
            if not neigh_id:
                continue
            
            sig_strength = float(neighbor.get("signal_strength", -65.0))
            hops = int(neighbor.get("hop_count", 1))

            query = select(MeshConnection).where(
                MeshConnection.node_id == node_id_str,
                MeshConnection.neighbor_node_id == neigh_id
            )
            res = await db.execute(query)
            conn = res.scalar_one_or_none()

            if conn:
                conn.hop_count = hops
                conn.signal_strength = sig_strength
                conn.is_active = True
                conn.last_seen = now
            else:
                conn = MeshConnection(
                    node_id=node_id_str,
                    neighbor_node_id=neigh_id,
                    hop_count=hops,
                    signal_strength=sig_strength,
                    route_path=route_path,
                    is_active=True,
                    last_seen=now,
                    created_at=now
                )
                db.add(conn)

        await db.commit()

        # Broadcast mesh topology update
        await ws_manager.broadcast_mesh({
            "type": "mesh_updated",
            "node_id": node_id_str,
            "hop_count": hop_count or 1,
            "timestamp": now.isoformat()
        })

    @staticmethod
    async def get_mesh_topology_graph(db: AsyncSession) -> MeshTopologyGraph:
        nodes_res = await db.execute(select(Node).order_by(Node.id))
        nodes = list(nodes_res.scalars().all())

        conns_res = await db.execute(select(MeshConnection).where(MeshConnection.is_active == True))
        conns = list(conns_res.scalars().all())

        topo_nodes = [
            MeshTopologyNode(
                id=n.id,
                node_code=n.node_id,
                name=f"MINEGUARD {n.node_id}",
                status=n.status or "ONLINE",
                battery=n.battery_level or 100.0,
                hop_count=1,
                parent_node_id=None,
                signal_strength=-68.0,
                latitude=n.latitude,
                longitude=n.longitude
            )
            for n in nodes
        ]

        topo_links = [
            MeshTopologyLink(
                source=c.node_id,
                target=c.neighbor_node_id,
                signal_strength=c.signal_strength or -70.0,
                hop_count=c.hop_count or 1,
                is_active=c.is_active
            )
            for c in conns
        ]

        gateway_nodes = [n.id for n in nodes if n.status == "ONLINE"]
        online_count = sum(1 for n in nodes if n.status == "ONLINE")
        total_count = len(nodes)
        health_score = 100.0 if total_count == 0 else round((online_count / total_count) * 100.0, 1)

        return MeshTopologyGraph(
            nodes=topo_nodes,
            links=topo_links,
            gateway_connected_nodes=gateway_nodes,
            total_nodes=total_count,
            online_nodes=online_count,
            mesh_health_score=health_score
        )

    @staticmethod
    async def get_mesh_health(db: AsyncSession) -> MeshHealthResponse:
        nodes_res = await db.execute(select(Node))
        nodes = list(nodes_res.scalars().all())

        total = len(nodes)
        online = [n for n in nodes if n.status == "ONLINE"]
        online_count = len(online)
        health_score = 100.0 if total == 0 else round((online_count / total) * 100.0, 1)

        return MeshHealthResponse(
            total_nodes=total,
            online_nodes=online_count,
            avg_hop_count=1.0,
            max_hop_count=1,
            isolated_nodes_count=0,
            avg_rssi=-68.5,
            mesh_health_score=health_score
        )

    @staticmethod
    async def get_connectivity_events(
        db: AsyncSession,
        limit: int = 50
    ) -> List[NodeConnectivityEvent]:
        query = select(NodeConnectivityEvent).order_by(desc(NodeConnectivityEvent.occurred_at)).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
