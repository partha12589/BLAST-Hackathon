# B.L.A.S.T. 🚀
**(Blockchain Link Analytics & Suspicious Tracking)**

An enterprise-grade Anti-Money Laundering (AML) and compliance engine built entirely natively on **Databricks**. 

We bypass third-party graph databases and delayed indexing layers, bringing high-performance Breadth-First Search (BFS) graph analytics directly to the Data Lake compute layer.

## ⚠️ The Problem: The Illicit Capital Flight Crisis

While cryptocurrency ledgers are publicly transparent, they completely lack direct linkage to real-world identities. Criminals actively exploit this anonymity by fracturing stolen funds across hundreds of wallets and pushing them through smart-contract mixers. 

* **Anonymous Wallets ➔** Zero real-world identity linkage.
* **Complex Transaction Chains ➔** Unprocessable by conventional database tools in real-time.
* **Reactive Compliance ➔** By the time conventional engines index the data and flag the breach, the criminals have already cashed out.

## 💡 The Solution: Zero-Latency Risk Analytics

**“Bring the Graph to the Data Lake.”**

Instead of moving massive blockchain ledgers into a secondary graph database, B.L.A.S.T. utilizes the raw compute power of **Databricks SQL Warehouse**. 

We ingest live Ethereum mempool data natively into a Delta Table via QuickNode, and execute complex **Recursive CTE (Breadth-First Search)** queries directly on the compute layer. This allows us to trace multi-hop capital flows, identify connected mixer contracts, and assign proximity risk scores dynamically in under **500 milliseconds**.

## 🛠 Tech Stack

**The Core Engine (Data & Compute)**
* **Databricks SQL Serverless** (Core compute for recursive graph queries)
* **Databricks Delta Lake** (Immutable storage layer for `bronze_transactions`)

**The Data Pipeline (Ingestion & API)**
* **Python 3 / Web3.py** (Real-time hex-data ingestion daemon)
* **QuickNode** (Enterprise RPC streaming live Ethereum Mainnet blocks)
* **FastAPI / Uvicorn** (Asynchronous REST API routing frontend searches)

**The Presentation Layer (UI & Visualization)**
* **Next.js 16 (App Router) & React 19** (High-performance server-side frontend)
* **Tailwind CSS v4 & Framer Motion** (Premium, glassmorphic UI styling and animations)
* **React Flow (`@xyflow/react`)** (Interactive physics-based graph rendering)

## ⚙️ Architecture Pipeline

1. **Ingestion (Live Mempool Streaming):** `seed_databricks.py` hooks into the Ethereum Mainnet via QuickNode RPC. We stream raw transaction blocks and write them natively into our unified `bronze_transactions` Delta Lake table.
2. **Medallion Architecture (Dynamic Tagging):** As data rests in the Delta Layer, our Python FastAPI gateway dynamically filters massive capital flights and matches addresses against known heuristic entity lists (e.g. Tornado Cash).
3. **Graph Analytics (Native SQL BFS):** We execute high-performance **Recursive CTEs** natively inside Databricks SQL Serverless. This traverses massive network graphs and computes exact taint distances instantly.
4. **Real-Time Alerting (The UI Dashboard):** The B.L.A.S.T engine passes the exact JSON graph payload to our interactive Next.js / React Flow UI, issuing automated visually-rendered holds and alerts milliseconds before the bad actor attempts to cash-out.

## 🚀 Future Roadmap
* **Multi-Chain Expansion:** Scale ingestion pipelines to include Solana, Polygon, and Bitcoin ledgers.
* **Medallion Architecture Completion:** Launch automated Delta Live Tables (DLT) for streaming Silver (filtered) and Gold (Wallet-Entity) aggregations.
* **Predictive AI:** Integrate Databricks MLX to train isolation-forest models on peeling-chain behaviors to halt transactions *before* they even hit the darknet mixer.
