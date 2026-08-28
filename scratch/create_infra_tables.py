"""Create infrastructure_assets and mine_config tables"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Read DB URL from backend config
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mine_monitoring"
)

# Try to load from .env
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

print(f"Connecting to: {DATABASE_URL[:40]}...")
engine = create_async_engine(DATABASE_URL, echo=False)

async def create_tables():
    async with engine.begin() as conn:
        # 1. Add lat/lon to gateway table
        await conn.execute(text("ALTER TABLE gateway ADD COLUMN IF NOT EXISTS latitude FLOAT"))
        await conn.execute(text("ALTER TABLE gateway ADD COLUMN IF NOT EXISTS longitude FLOAT"))
        print("[OK] Gateway lat/lon columns ensured")

        # 2. Create infrastructure_assets table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS infrastructure_assets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(256) NOT NULL,
                asset_type VARCHAR(64) NOT NULL,
                latitude FLOAT,
                longitude FLOAT,
                status VARCHAR(32) DEFAULT 'OPERATIONAL',
                criticality VARCHAR(16) DEFAULT 'MEDIUM',
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP
            )
        """))
        print("[OK] infrastructure_assets table created/verified")

        # 3. Create mine_config table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS mine_config (
                id SERIAL PRIMARY KEY,
                key VARCHAR(128) UNIQUE NOT NULL,
                value VARCHAR(512),
                description TEXT,
                updated_at TIMESTAMP
            )
        """))
        print("[OK] mine_config table created/verified")

    print("[DONE] All infrastructure tables ready.")

asyncio.run(create_tables())
