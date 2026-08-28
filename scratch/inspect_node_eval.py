import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgresql://postgres:adnan2007%3F@localhost:5432/mine_monitoring')
    
    print("--- SENSOR READINGS FOR NODE_EVAL_01 ---")
    readings = await conn.fetch("SELECT id, node_id, displacement, tilt_x, crack_width, recorded_at FROM sensor_readings WHERE node_id = 'NODE_EVAL_01' ORDER BY id DESC LIMIT 5")
    for r in readings:
        print(dict(r))
        
    print("\n--- AI PREDICTIONS FOR NODE_EVAL_01 ---")
    preds = await conn.fetch("SELECT id, node_id, reading_id, anomaly_score, risk_score, risk_level, created_at FROM ai_predictions WHERE node_id = 'NODE_EVAL_01' ORDER BY id DESC LIMIT 5")
    for p in preds:
        print(dict(p))

    print("\n--- ALERTS FOR NODE_EVAL_01 ---")
    alerts = await conn.fetch("SELECT id, node_id, alert_type, severity, title, risk_score, status, detected_at FROM alerts WHERE node_id = 'NODE_EVAL_01' ORDER BY id DESC LIMIT 5")
    for a in alerts:
        print(dict(a))

    await conn.close()

asyncio.run(check())
