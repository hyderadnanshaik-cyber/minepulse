import asyncio
import asyncpg

async def migrate():
    conn = await asyncpg.connect(user='postgres', password='adnan2007?', database='mine_monitoring', host='localhost', port=5432)
    print("Migrating nodes table for enterprise fleet management...")
    
    statements = [
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS name VARCHAR(128);",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS zone VARCHAR(128) DEFAULT 'North Shaft';",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS site_id VARCHAR(64) DEFAULT 'MINE-CENTRAL-01';",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS connection_type VARCHAR(32) DEFAULT 'LoRa';",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS gateway_id VARCHAR(64) DEFAULT 'MINEGATE-01';",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS sensor_types JSONB DEFAULT '[\"Displacement\", \"Tilt\", \"Crack\", \"Temperature\", \"Vibration\"]'::jsonb;",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS thresholds JSONB DEFAULT '{\"warning_disp_mm\": 15.0, \"critical_disp_mm\": 25.0, \"warning_tilt_deg\": 2.0, \"critical_tilt_deg\": 3.5, \"warning_crack_mm\": 1.5, \"critical_crack_mm\": 3.0}'::jsonb;",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE nodes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW();"
    ]
    
    for stmt in statements:
        await conn.execute(stmt)
        print(f"Executed: {stmt}")
        
    # Populate default name and zone for existing nodes if null
    await conn.execute("""
        UPDATE nodes SET 
            name = COALESCE(name, 'Station ' || node_id),
            zone = COALESCE(zone, CASE 
                WHEN id % 4 = 1 THEN 'North Shaft'
                WHEN id % 4 = 2 THEN 'East Tunnel'
                WHEN id % 4 = 3 THEN 'South Ramp'
                ELSE 'West Incline'
            END)
        WHERE name IS NULL OR zone IS NULL;
    """)
    print("Updated existing nodes with default zones and names.")

    await conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    asyncio.run(migrate())
