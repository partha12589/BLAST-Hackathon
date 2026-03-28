# Discovery Findings

## North Star
Sub-500ms real-time API webhook acting as a "Taint & Risk Scoring Engine". Ingests live crypto transaction hashes, performs multi-hop BFS graph traversal, detects ties to known criminal wallets, and returns a Risk Score (0-100) with a provenance graph. BLOCKED status triggers a fiat withdrawal "Hold" on the exchange internal ledger.

## Integrations
- **Blockchain Data**: Alchemy and QuickNode via WSS.
- **Off-Chain Data**: Internal Exchange Relational Databases (SQL) for KYC, session IPs, P2P info.
- **Core Compute**: Databricks (SQL Warehouses, Delta Live Tables).
- **Graph Engine**: Memgraph or Neo4j (strictly NO Spark GraphX).
- **Caching**: Redis.
- **Keys**: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `ALCHEMY_API_KEY`.

## Source of Truth
Databricks Medallion Architecture:
- **Bronze**: Raw on-chain blocks/mempool streams, raw off-chain exchange data (KYC/IP).
- **Silver**: Cleaned/normalized Tx, Heuristic Tags (e.g. "Peeling Chains", terminal convergence). Batch clustering via GraphFrames.
- **Gold**: Optimized entity maps joining on-chain clusters with off-chain User IDs.
