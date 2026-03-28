import os
import json
from graph_traversal import trace_wallet
from dotenv import load_dotenv

load_dotenv(dotenv_path="c:/Users/parth/OneDrive/Desktop/Hackbricks/.env")

target = "0x3b258cb07e511174c096c9f7cf194cedab151386"
res = trace_wallet(target)

with open('c:/Users/parth/.gemini/antigravity/tmp/payload.json', 'w') as f:
    json.dump(res, f, indent=2)
