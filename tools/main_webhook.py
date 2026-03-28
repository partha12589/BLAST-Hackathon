from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import logging
import os
from dotenv import load_dotenv

# Load `.env` from the root directory when uvicorn boots the app
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", ".env")
load_dotenv(dotenv_path=env_path)

from graph_traversal import trace_wallet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

app = FastAPI(title="B.L.A.S.T Webhook Engine")

# Allow Next.js requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TraceRequest(BaseModel):
    target_wallet: str
    max_depth: int = 3

@app.post("/trace")
async def run_trace(request: TraceRequest):
    start_time = time.time()
    
    try:
        logging.info(f"Received TRACE request for {request.target_wallet}")
        
        # Call the core graph traversal engine
        payload = trace_wallet(request.target_wallet, request.max_depth)
        
        elapsed = time.time() - start_time
        logging.info(f"Trace completed in {elapsed:.3f}s")
        
        # Enforce latencies reporting (Goal <500ms)
        payload["metadata"] = {"latency_ms": round(elapsed * 1000, 2)}
        
        return payload
    except Exception as e:
        logging.error(f"Webhook failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mempool")
async def get_mempool():
    import os
    from databricks import sql
    host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    
    try:
        connection = sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token
        )
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT from_address, to_address, value, transaction_hash, block_timestamp 
            FROM bronze_transactions 
            ORDER BY block_timestamp DESC 
            LIMIT 50
        """)
        results = cursor.fetchall()
        
        mempool_data = []
        for row in results:
            mempool_data.append({
                "from_address": row[0],
                "to_address": row[1],
                "value": row[2],
                "transaction_hash": row[3],
                "block_timestamp": str(row[4])
            })
            
        cursor.close()
        connection.close()
        return mempool_data
    except Exception as e:
        logging.error(f"Mempool fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts():
    import os
    from databricks import sql
    host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    
    try:
        connection = sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token
        )
        cursor = connection.cursor()
        
        # Databricks SQL: parse the " ETH" string to FLOAT if > 10 ETH
        cursor.execute("""
            SELECT from_address, to_address, value, transaction_hash, block_timestamp 
            FROM bronze_transactions 
            WHERE CAST(REPLACE(value, ' ETH', '') AS FLOAT) > 10
            ORDER BY block_timestamp DESC
            LIMIT 20
        """)
        results = cursor.fetchall()
        
        alerts_data = []
        for row in results:
            alerts_data.append({
                "from_address": row[0],
                "to_address": row[1],
                "value": row[2],
                "transaction_hash": row[3],
                "block_timestamp": str(row[4])
            })
            
        cursor.close()
        connection.close()
        return alerts_data
    except Exception as e:
        logging.error(f"Alerts fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Booting the ASGI server matching the Phase 3 MVP guidelines
    uvicorn.run("main_webhook:app", host="0.0.0.0", port=8000, reload=True)
