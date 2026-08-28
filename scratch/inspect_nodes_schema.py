import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect(user='postgres', password='adnan2007?', database='mine_monitoring', host='localhost', port=5432)
    cols = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'nodes';")
    print("NODES COLUMNS:")
    for c in cols:
        print(f" - {c['column_name']}: {c['data_type']}")
    await conn.close()

if __name__ == '__main__':
    asyncio.run(check())
