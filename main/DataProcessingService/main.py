import os
import uvicorn
import logging
from datetime import datetime

# pull the environment variable to know if we're running locally or in docker
env = os.getenv("ENV", "LOCAL").upper()  # 'DOCKER' or 'LOCAL'

# current date string used for naming the log file
date_str = datetime.now().strftime("%Y-%m-%d")

# point the log folder to the right place depending on the env
log_folder = "/logs" if env == "DOCKER" else "./logs"

# create the log folder if it does not already exist
os.makedirs(log_folder, exist_ok=True)

# log file name includes the environment and date so its easy to track
log_filename = f"dataprocessingservice_{env}_{date_str}.log"
log_path = os.path.join(log_folder, log_filename)

# setup logging to write to both the log file and the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()  
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Logging initialized | ENV={env} | log_path={log_path}")

if __name__ == "__main__":
    # debug mode is controlled by an env variable, defaults to true
    debug = os.getenv("DEBUG", "true").lower() == "true"

    # start the FastAPI app on port 8012
    uvicorn.run(
        "app:app",   
        host="0.0.0.0",
        port=8012,
        reload=debug
    )