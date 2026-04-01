'''
This module calls the Generate_Dash_App function to create the Dash application. Once the application is created,
main will run the app on the specified port.
'''
from DashApp import Generate_Dash_App
import os 
import logging
from datetime import datetime

env = os.getenv("ENV", "LOCAL").upper()  # 'DOCKER' or 'LOCAL'

# Current date string
date_str = datetime.now().strftime("%Y-%m-%d")

# Determine log folder
log_folder = "/logs" if env == "DOCKER" else "./logs"

# Make sure the folder exists
os.makedirs(log_folder, exist_ok=True)

# Create a log file that denotes which enviornment we're working with.
log_filename = f"application_{env}_{date_str}.log"
log_path = os.path.join(log_folder, log_filename)

# Configure logging
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
    logger.info('Launching Dashboard')
    app = Generate_Dash_App()

    

    if env == "DOCKER":
        host = "0.0.0.0"
        debug = False
        logger.info(f"Application Launch - Test Version")
        print(f"Application Launch - Test Version")
    else:
        host = "127.0.0.1"
        debug = True
        logger.info(f"Application Launch - DEBUG Version")
        print(f"Application Launch - DEBUG Version")


    app.run(debug=debug, host=host, port=8519)