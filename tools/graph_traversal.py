import os
import json
import logging
from typing import Dict, Any
from databricks import sql

def trace_wallet(target_wallet: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    Core engine using Databricks Recursive CTE to perform a Breadth-First Search
    up to `max_depth` hops to detect taint and return a provenance graph.
    """
    host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    target_wallet = target_wallet.lower()
    
    # Initialize basic structure
    payload = {
        "transaction_hash": "N/A - Direct Search",
        "target_wallet": target_wallet,
        "overall_risk_score": 0,
        "status": "CLEARED",
        "tainted_volume": "$0.00 USD",
        "taint_distance_hops": 0,
        "provenance_graph": {
            "nodes": [{"id": target_wallet, "type": "origin"}],
            "edges": []
        }
    }
    
    if not host or not token or not http_path:
        logging.error("Missing Databricks configuration. Aborting graph traversal.")
        payload["status"] = "ERROR: Missing Keys"
        return payload

    # The Breadth-First Search Recursive CTE
    # Traversing `bronze_transactions` mapping `from_address` -> `to_address`
    recursive_query = f"""
    WITH RECURSIVE bfs_traversal AS (
        -- Base Case: Starting from the target wallet
        SELECT 
            from_address,
            to_address,
            value,
            transaction_hash,
            1 AS depth
        FROM bronze_transactions
        WHERE from_address = '{target_wallet}' OR to_address = '{target_wallet}'
        
        UNION ALL
        
        -- Recursive Step: Traverse Outwards
        SELECT 
            bt.from_address,
            bt.to_address,
            bt.value,
            bt.transaction_hash,
            bfs.depth + 1 AS depth
        FROM bronze_transactions bt
        INNER JOIN bfs_traversal bfs 
            ON bt.from_address = bfs.to_address 
            OR bt.to_address = bfs.from_address
        WHERE bfs.depth < {max_depth}
    )
    SELECT * FROM bfs_traversal
    LIMIT 150
    """
    
    try:
        connection = sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token
        )
        cursor = connection.cursor()
        
        cursor.execute(recursive_query)
        results = cursor.fetchall()
        
        # Parse into Nodes and Edges
        nodes = {target_wallet: "origin"}
        edges = []
        total_tainted_vol = 0.0
        min_tainted_hops = 999
        found_sanctioned = False

        # Placeholder logic for identifying sanctioned entities (Mixers/Lazarus)
        # Assuming our seeder fetched Tornado Cash, we flag it.
        TORNADO_CASHS = ["0x47ce0c6ed5b0ce3d3a51f243f19474acd4225372", "0x47CE0C6eD5B0Ce3d3A51f243F19474aCD4225372"]

        for row in results:
            # row: from_address, to_address, value, hash, depth
            frm = row[0]
            to = row[1]
            val = row[2]
            depth = row[4]
            
            # Map edge
            edges.append({
                "from": frm[:8] + "..." + frm[-4:] if len(frm)>12 else frm,
                "to": to[:8] + "..." + to[-4:] if len(to)>12 else to,
                "amount": f"{val} ETH"
            })
            
            # Basic entity labeling
            for addr in (frm, to):
                if addr not in nodes:
                    if addr in TORNADO_CASHS:
                        nodes[addr] = "mixer"
                        found_sanctioned = True
                        min_tainted_hops = min(min_tainted_hops, depth)
                        num_val = float(str(val).replace(' ETH', '').strip()) if val else 0.0
                        total_tainted_vol += num_val
                    else:
                        nodes[addr] = "transfer"
                        
        # Formatting Payload Back to UI
        payload["provenance_graph"]["nodes"] = []
        for n_id, type_cls in nodes.items():
             payload["provenance_graph"]["nodes"].append({
                 "id": n_id[:8] + "..." + n_id[-4:] if len(n_id)>12 else n_id,
                 "type": type_cls
             })
        
        payload["provenance_graph"]["edges"] = edges
        
        real_max_depth = max([row[4] for row in results]) if results else 0
        payload["taint_distance_hops"] = real_max_depth
        
        if found_sanctioned:
            payload["status"] = "BLOCKED"
            payload["overall_risk_score"] = 100 - (min_tainted_hops * 10) 
            payload["tainted_volume"] = f"{total_tainted_vol} ETH"
            
    except Exception as e:
        logging.error(f"Graph Traversal failed: {e}")
        payload["status"] = "ERROR: DB Query Failed"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return payload

if __name__ == "__main__":
    import sys
    load_dotenv()
    target = sys.argv[1] if len(sys.argv) > 1 else "0xTestAddress..."
    result = trace_wallet(target)
    print(json.dumps(result, indent=2))
