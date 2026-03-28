# Project Constitution

## Data Schemas
**Delivery Payload (JSON)**:
```json
{
  "transaction_hash": "string",
  "overall_risk_score": "integer (0-100)",
  "status": "string (BLOCKED | FLAGGED | CLEARED)",
  "flagged_entities": ["array of strings"],
  "taint_distance_hops": "integer",
  "matched_heuristics": ["array of strings, e.g., 'Peeling Chain Detected'"],
  "provenance_graph": {
    "nodes": ["involved addresses and Exchange User IDs"],
    "edges": ["transaction flow amounts"]
  }
}
```

## Behavioral Rules
1. **Graph Constraints**: Use Breadth-First Search (BFS) and Shortest Path for real-time tracing. Strictly DO NOT use legacy Spark GraphX.
2. **Databricks Rule**: All Python scripts in `tools/` MUST use the `databricks-sql-connector` for real-time Gold layer lookups and the `databricks-sdk` for batch processing in Silver.
3. **Latency & Hard Lock**: API response must aim for <500ms. Databricks SQL Warehouse is the strictly enforced CORE engine. No fallback mocks. All traversals MUST hit the `bronze_transactions` Delta Table. All RPC fetches MUST route directly through the premium `QUICKNODE_HTTP_URL` via the `web3` library; Alchemy SDK is strictly prohibited to guarantee lowest possible latency.
4. **Obfuscation Rule**: If funds pass through a mixer, tracking breaks deterministically. Flag the "Mixer Hop", switch to probabilistic scoring, and apply exponential decay to risk score.

## Architectural Invariants
- **Layer 1: Architecture (`architecture/`)**
  - Golden Rule: If logic changes, update the SOP before updating the code.
- **Layer 2: Navigation**
  - Route data between SOPs and Tools. Do not perform complex tasks without executing tools.
- **Layer 3: Tools (`tools/`)**
  - Deterministic Python scripts. Atomic and testable.
  - `.env` for credentials.
  - `.tmp/` for intermediate file ops.
- **The Data-First Rule:** Coding only begins once the "Payload" shape is confirmed.
- **Self-Annealing Loop:** Analyze error -> Patch Python script -> Test -> Update Architecture.
