"""
Update all sensor nodes coordinates in PostgreSQL to surround the authoritative Jharia Mine Site.
Mine Anchor: 23.7692838, 86.4110045 (Jharia Coalfield, BCCL)
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:adnan2007?@localhost:5432/mine_monitoring"
)

# Try reading from .env
env_path = "backend/.env"
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "DATABASE_URL":
                    DATABASE_URL = v.strip()
                    break

print(f"Connecting to database...")
engine = create_async_engine(DATABASE_URL, echo=False)

BASE_LAT = 23.7692838
BASE_LON = 86.4110045

# Offsets for 20 nodes distributed in the underground mine working panel
# around the infrastructure assets and mine entrance (~50m to ~250m grid)
node_offsets = [
    # Row 1 (North panel)
    ( 0.0007, -0.0008), ( 0.0007, -0.0003), ( 0.0007,  0.0003), ( 0.0007,  0.0008),
    # Row 2 (Central entrance / haulage drift)
    ( 0.0003, -0.0009), ( 0.0003, -0.0003), ( 0.0003,  0.0003), ( 0.0003,  0.0009),
    # Row 3 (Core working face — near Node 3 & 2)
    (-0.0001, -0.0008), (-0.0001, -0.0003), (-0.0001,  0.0003), (-0.0001,  0.0008),
    # Row 4 (South panel / deep extraction)
    (-0.0005, -0.0008), (-0.0005, -0.0003), (-0.0005,  0.0003), (-0.0005,  0.0008),
    # Row 5 (East/West extraction boundary)
    (-0.0009, -0.0008), (-0.0009, -0.0003), (-0.0009,  0.0003), (-0.0009,  0.0008),
]

async def relocate_nodes():
    async with engine.begin() as conn:
        for i in range(1, 21):
            code = f"NODE_{i:02d}"
            dlat, dlon = node_offsets[i - 1]
            new_lat = BASE_LAT + dlat
            new_lon = BASE_LON + dlon
            await conn.execute(text("""
                UPDATE nodes 
                SET latitude = :lat, longitude = :lon 
                WHERE node_id = :code
            """), {"lat": new_lat, "lon": new_lon, "code": code})
            print(f"[UPDATED] {code} -> ({new_lat:.6f}, {new_lon:.6f})")

        # Also update any extra evaluation or test nodes if they exist
        await conn.execute(text("""
            UPDATE nodes 
            SET latitude = :lat, longitude = :lon 
            WHERE node_id NOT LIKE 'NODE_%' OR node_id IN ('NODE_21', 'NODE_22', 'NODE_EVAL_01')
        """), {"lat": BASE_LAT - 0.0003, "lon": BASE_LON + 0.0005})
        print("[UPDATED] Extra nodes relocated.")

    print("[SUCCESS] All nodes now accurately aligned with Jharia Mine Site & Infrastructure!")

asyncio.run(relocate_nodes())
