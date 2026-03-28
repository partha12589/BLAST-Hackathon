import os
import logging
from dotenv import load_dotenv

# Set up logging for our verification feedback loop
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
load_dotenv()

def verify_quicknode():
    quicknode_url = os.getenv("QUICKNODE_HTTP_URL")
    if not quicknode_url:
        logging.error("QUICKNODE_HTTP_URL missing in .env.")
        return False
        
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider(quicknode_url))
        if w3.is_connected():
            block = w3.eth.block_number
            logging.info(f"QuickNode Web3 Connected! Current block: {block}")
            return True
        else:
            logging.error("QuickNode Web3 Connection failed: is_connected() returned False.")
            return False
    except ImportError:
        logging.error("Web3 library not installed. Run 'pip install web3'.")
        return False
    except Exception as e:
        logging.error(f"QuickNode Web3 Connection Exception: {e}")
        return False

def verify_databricks_sql():
    host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    token = os.getenv("DATABRICKS_TOKEN")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    
    if not http_path or not host or not token:
        logging.warning("Databricks credentials missing in .env.")
        return False
        
    try:
        from databricks import sql
        connection = sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        logging.info(f"Databricks SQL Connected! Test query returned: {result[0]}")
        cursor.close()
        connection.close()
        return True
    except ImportError:
        logging.error("databricks-sql-connector library not installed.")
        return False
    except Exception as e:
        logging.error(f"Databricks SQL Connection failed: {e}")
        return False

def main():
    logging.info("Starting Phase 2 Link Verification Matrix (QuickNode Pivot)...\n")
    
    qn_ok = verify_quicknode()
    sql_ok = verify_databricks_sql()
    
    print("\n--- Summary ---")
    if qn_ok and sql_ok:
        logging.info("Core API connections (QuickNode & Databricks SQL) are SUCCESSFUL.")
    else:
        logging.warning("Some required connections failed. Check the logs above.")

if __name__ == "__main__":
    main()
