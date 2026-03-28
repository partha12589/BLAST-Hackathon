import os
import logging
from dotenv import load_dotenv
from web3 import Web3
from databricks import sql

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
load_dotenv()

QUICKNODE_URL = os.getenv("QUICKNODE_HTTP_URL")
DB_HOST = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DB_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DB_TOKEN = os.getenv("DATABRICKS_TOKEN")

def fetch_latest_transactions():
    """Fetch the latest 5 blocks and extract relevant transactions to simulate mempool"""
    logging.info("Connecting to QuickNode Web3 RPC...")
    
    if not QUICKNODE_URL:
        logging.error("Missing QUICKNODE_HTTP_URL in .env")
        return []
        
    w3 = Web3(Web3.HTTPProvider(QUICKNODE_URL))
    
    if not w3.is_connected():
        logging.error("Failed to connect to QuickNode Provider.")
        return []

    latest_block = w3.eth.block_number
    logging.info(f"Connected! Latest blockchain block: {latest_block}")
    
    extracted_txs = []
    
    # Fetch the latest 5 blocks
    blocks_to_fetch = 5
    for block_num in range(latest_block, latest_block - blocks_to_fetch, -1):
        logging.info(f"Fetching block {block_num}...")
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            timestamp = block.timestamp
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp)
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            # We process normal value-carrying transactions for our graph
            for tx in block.transactions:
                # To protect databricks MVP limits, let's only grab value > 0 transfers
                # To simulate, we filter txs bearing value
                if getattr(tx, 'to', None) and getattr(tx, 'value', 0) > 0:
                    val_eth = w3.from_wei(tx.value, 'ether')
                    
                    extracted_txs.append((
                        tx['from'].lower(),
                        tx['to'].lower(),
                        f"{val_eth:.6f} ETH",
                        tx['hash'].hex(),
                        dt_str
                    ))
        except Exception as e:
            logging.error(f"Error fetching block {block_num}: {e}")
            
    logging.info(f"Extracted {len(extracted_txs)} value-bearing transactions from the last {blocks_to_fetch} blocks.")
    return extracted_txs

def seed_to_databricks(transactions):
    """Seed extracted Web3 transactions into Databricks Delta Table via SQL Connector"""
    if not transactions:
        logging.warning("No transactions to seed.")
        return

    logging.info("Connecting to Databricks SQL Warehouse...")
    try:
        connection = sql.connect(
            server_hostname=DB_HOST,
            http_path=DB_PATH,
            access_token=DB_TOKEN
        )
        cursor = connection.cursor()
        
        # Ensure the Delta Table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bronze_transactions (
              from_address STRING,
              to_address STRING,
              value STRING,
              transaction_hash STRING,
              block_timestamp TIMESTAMP
            )
        """)
        logging.info("Ensured bronze_transactions table exists.")
        
        # Batch insert
        logging.info("Inserting transactions into Databricks...")
        insert_query = """
            INSERT INTO bronze_transactions (from_address, to_address, value, transaction_hash, block_timestamp) 
            VALUES (?, ?, ?, ?, ?)
        """
        
        # Execute many
        cursor.executemany(insert_query, transactions)
        connection.commit()
        
        logging.info(f"Successfully seeded {len(transactions)} Web3 transactions into Databricks.")
        
    except Exception as e:
        logging.error(f"Databricks SQL insertion failed: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    if not QUICKNODE_URL or not DB_HOST:
        logging.error("Missing critical environment variables. Check .env")
        exit(1)
        
    txs = fetch_latest_transactions()
    seed_to_databricks(txs)
    logging.info("Web3 QuickNode to Databricks ingestion complete.")
