"""
Accurate Geographic Relocation Script for MINEGUARD:
1. Mine Panel: Cluster 11 & Cluster 7 (BCCL) Coal Mines (Lat: 23.7695, Lon: 86.4045 - West of NH218)
2. Sensor Nodes 01-20: Distributed throughout the underground seam in the actual mine area
3. Public Infrastructure: Real public civilian infrastructure assets surrounding the mine (NH-218 Highway, Railway Line, Residential Colonies, Hospital, School, Water Pipeline, Power Grid)
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

# Load from .env if present
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

print("Connecting to database...")
engine = create_async_engine(DATABASE_URL, echo=False)

# Actual Coal Mine Working Seam coordinates (Cluster 11 & 7 BCCL Mine area)
MINE_SEAM_LAT = 23.769500
MINE_SEAM_LON = 86.404500

# 20 Sensor nodes arranged in a 4x5 underground grid inside the actual mine area
NODE_POSITIONS = [
    # Extraction Face 1 (North-East Seam - closest to NH-218 Highway & Colony)
    ("NODE_01", 23.7712, 86.4055),
    ("NODE_02", 23.7706, 86.4062),
    ("NODE_03", 23.7700, 86.4068),  # Primary sinking node - closest to NH218 & Water Pipeline!
    ("NODE_04", 23.7694, 86.4072),
    # Extraction Face 2 (Central Seam)
    ("NODE_05", 23.7710, 86.4045),
    ("NODE_06", 23.7704, 86.4050),
    ("NODE_07", 23.7698, 86.4055),
    ("NODE_08", 23.7692, 86.4060),
    # Extraction Face 3 (Deep Core Seam)
    ("NODE_09", 23.7708, 86.4035),
    ("NODE_10", 23.7702, 86.4040),
    ("NODE_11", 23.7696, 86.4045),
    ("NODE_12", 23.7690, 86.4050),
    # Extraction Face 4 (South-West Seam - near Railway track)
    ("NODE_13", 23.7705, 86.4025),
    ("NODE_14", 23.7699, 86.4030),
    ("NODE_15", 23.7693, 86.4035),
    ("NODE_16", 23.7687, 86.4040),
    # Extraction Boundary & Barrier Pillars
    ("NODE_17", 23.7682, 86.4045),
    ("NODE_18", 23.7680, 86.4055),
    ("NODE_19", 23.7678, 86.4065),
    ("NODE_20", 23.7675, 86.4075),
]

# Real Public & Civilian Infrastructure Assets surrounding the mine
PUBLIC_INFRASTRUCTURE = [
    {
        "name": "National Highway NH-218 (Main Jharia-Dhanbad Road)",
        "asset_type": "HIGHWAY",
        "latitude": 23.7700,
        "longitude": 86.4098,  # ~280m east of active sinking zone
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Major 4-lane public highway with heavy commercial and passenger traffic. High risk of road crack/sinkhole if subsidence propagates east.",
    },
    {
        "name": "New Delhi Residential Colony (Civilian Settlement)",
        "asset_type": "RESIDENTIAL_AREA",
        "latitude": 23.7725,
        "longitude": 86.4085,  # ~320m north-east of mine
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Dense civilian settlement of 450+ families. Ground subsidence could cause foundation shear and building collapse.",
    },
    {
        "name": "Municipal Potable Water Supply Pipeline & Pump Main",
        "asset_type": "WATER_SUPPLY",
        "latitude": 23.7702,
        "longitude": 86.4082,  # ~150m east of Node 3
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Primary 600mm diameter drinking water trunk line serving 12,000 residents. Pipe burst risk upon ground displacement.",
    },
    {
        "name": "Kusunda Railway Track & Mineral Freight Siding",
        "asset_type": "RAILWAY",
        "latitude": 23.7685,
        "longitude": 86.4015,  # ~250m west of mine
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Active broad-gauge railway line and coal transport freight corridor. Track misalignment hazard during subsidence.",
    },
    {
        "name": "Kusunda 33kV / 11kV Public Power Distribution Substation",
        "asset_type": "POWER_GRID",
        "latitude": 23.7728,
        "longitude": 86.4045,  # ~350m north of mine
        "criticality": "HIGH",
        "status": "OPERATIONAL",
        "description": "Supplies electrical power to the residential township and local municipal services.",
    },
    {
        "name": "Kenduadih Community Health Centre & Hospital",
        "asset_type": "HOSPITAL",
        "latitude": 23.7660,
        "longitude": 86.3980,  # ~750m south-west
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Public community hospital. Designated emergency casualty receiver for the district.",
    },
    {
        "name": "Government Primary & High School Complex",
        "asset_type": "SCHOOL",
        "latitude": 23.7718,
        "longitude": 86.4105,  # ~400m north-east
        "criticality": "CRITICAL",
        "status": "OPERATIONAL",
        "description": "Public school campus with 600+ students. Must be placed under immediate evacuation protocol upon high alert.",
    },
    {
        "name": "MDR-058 Public Transit Road & Overbridge",
        "asset_type": "BRIDGE",
        "latitude": 23.7665,
        "longitude": 86.4055,  # ~350m south
        "criticality": "HIGH",
        "status": "OPERATIONAL",
        "description": "Key public connecting road bridge over the drainage nullah.",
    },
    {
        "name": "BCCL Workers Residential Township (Sector-4)",
        "asset_type": "RESIDENTIAL_AREA",
        "latitude": 23.7680,
        "longitude": 86.4090,  # ~220m east
        "criticality": "HIGH",
        "status": "OPERATIONAL",
        "description": "Colony housing 280 mine workers and their dependents.",
    },
    {
        "name": "Karkend Commercial Market & Public Bus Stand",
        "asset_type": "COMMERCIAL_AREA",
        "latitude": 23.7645,
        "longitude": 86.3995,  # ~800m south-west
        "criticality": "MEDIUM",
        "status": "OPERATIONAL",
        "description": "Central shopping market, weekly vegetable bazaar, and public transit bus stop.",
    }
]

async def apply_accurate_geography():
    async with engine.begin() as conn:
        # 1. Update Mine Config to Cluster 11/7 Mine coordinates
        await conn.execute(text("""
            INSERT INTO mine_config (key, value, description, updated_at)
            VALUES 
                ('MINE_SITE_LAT', '23.769500', 'Cluster 11 & 7 (BCCL) Coal Mine Latitude', NOW()),
                ('MINE_SITE_LON', '86.404500', 'Cluster 11 & 7 (BCCL) Coal Mine Longitude', NOW()),
                ('MINE_SITE_NAME', 'Cluster 11 & 7 (BCCL) Coal Mines — Jharia', 'Official Mine Name', NOW())
            ON CONFLICT (key) DO UPDATE 
            SET value = EXCLUDED.value, description = EXCLUDED.description, updated_at = NOW();
        """))
        print("[OK] Mine Site Anchor updated to Cluster 11 & 7 Coal Mines (23.7695, 86.4045)")

        # 2. Update Gateway Location (Surface Control Office at mine perimeter)
        await conn.execute(text("""
            UPDATE gateway
            SET latitude = 23.771500, longitude = 86.405000, name = 'MINEGATE Central Gateway (Surface Office)'
            WHERE device_id = 'RPI-ZERO2W-001' OR id = 1;
        """))
        print("[OK] Gateway relocated to mine surface perimeter")

        # 3. Update all 20 nodes inside the actual coal mine seam
        for code, lat, lon in NODE_POSITIONS:
            await conn.execute(text("""
                UPDATE nodes
                SET latitude = :lat, longitude = :lon, zone = 'Cluster 11 Panel Alpha'
                WHERE node_id = :code;
            """), {"lat": lat, "lon": lon, "code": code})
            print(f"[OK] {code} placed in coal mine seam at ({lat:.4f}, {lon:.4f})")

        # Relocate any extra test nodes
        await conn.execute(text("""
            UPDATE nodes
            SET latitude = 23.7695, longitude = 86.4045, zone = 'Cluster 11 Panel Alpha'
            WHERE node_id NOT IN ('NODE_01','NODE_02','NODE_03','NODE_04','NODE_05','NODE_06','NODE_07','NODE_08','NODE_09','NODE_10','NODE_11','NODE_12','NODE_13','NODE_14','NODE_15','NODE_16','NODE_17','NODE_18','NODE_19','NODE_20');
        """))

        # 4. Replace infrastructure assets with actual Public & Civilian Infrastructure
        await conn.execute(text("DELETE FROM infrastructure_assets;"))
        for infra in PUBLIC_INFRASTRUCTURE:
            await conn.execute(text("""
                INSERT INTO infrastructure_assets (name, asset_type, latitude, longitude, criticality, status, description, is_active, created_at)
                VALUES (:name, :asset_type, :latitude, :longitude, :criticality, :status, :description, TRUE, NOW());
            """), infra)
        print(f"[OK] Inserted {len(PUBLIC_INFRASTRUCTURE)} real Public & Civilian Infrastructure assets surrounding the mine.")

    print("\n[SUCCESS] All nodes are now located strictly inside the Coal Mine, and Public Infrastructure assets surround the perimeter!")

asyncio.run(apply_accurate_geography())
