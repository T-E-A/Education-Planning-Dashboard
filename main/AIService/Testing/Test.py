import os
import json
import logging


from AIService.app import app
from AIService.MainService.AI_Orchestration import AI_Orchestration

OUTPUT_DIR = "AIService/Testing/AITestOutcomes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

logger = logging.getLogger("AITesterLogger")
logger.setLevel(logging.INFO)

log_file_path = os.path.join(OUTPUT_DIR, "AITester.log")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def test_Query_Match_Making_Agent():
