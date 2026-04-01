# APITester.py
import os
import json
import logging
from typing import Callable, Any, Dict, List, Tuple

from DataProcessingRequests.DataProcessingRequester import (
    Get_Options_Dict,
    Get_KPI_Data,
    Service_Check,
    Get_Program_To_NOC_Data,
    Get_NOC_Historical,
    Get_NOC_Forecast,
    Get_Province_Clustered_Series
)

#Setup the output directory
OUTPUT_DIR = "DataProcessingRequests/TestOutcomes/DashAppRequester"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create dedicated logger for this test
logger = logging.getLogger("APITesterLogger")
logger.setLevel(logging.INFO)

log_file_path = os.path.join(OUTPUT_DIR, "APITester.log")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# Each entry: function -> list of argument tuples (Empty List if there are no args)
api_functions: Dict[str, Tuple[Callable, List[Tuple[Any, ...]]]] = {
    "Service_Check": (Service_Check, []),
    "Get_Options_Dict": (Get_Options_Dict, []),
    "Get_KPI_Data": (Get_KPI_Data, []),
    "Get_Program_To_NOC_Data": (Get_Program_To_NOC_Data, [(4,), (3,)]),
    "Get_NOC_Historical": (Get_NOC_Historical, [(30, 35, '2021A000235')]),
    "Get_NOC_Forecast": (Get_NOC_Forecast, [(30, 35)]),
    "Get_Province_Clustered_Series": (Get_Province_Clustered_Series, [(35, 3, 1)])
}


#Function Tester
def test_requester_functions(function_dict: Dict[str, Tuple[Callable, List[Tuple[Any, ...]]]]):
   
    for func_name, (func, args_list) in function_dict.items():
        # No arguments
        if not args_list:
            try:
                logger.info(f"Testing {func_name}...")
                print(f"Testing {func_name}...")

                result = func()
                file_path = os.path.join(OUTPUT_DIR, f"{func_name}.json")
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)

                logger.info(f"Output saved to {file_path}")
                print(f"Output saved to {file_path}\n")

            except Exception as e:
                logger.exception(f"Error testing {func_name}: {e}")
                print(f"Error testing {func_name}: {e}")

        # Functions with arguments
        else:
            for arg_tuple in args_list:
                try:
                    args_str = "_".join(str(a) for a in arg_tuple)
                    test_name = f"{func_name}_{args_str}"

                    logger.info(f"Testing {test_name}...")
                    print(f"Testing {test_name}...")

                    result = func(*arg_tuple)
                    file_path = os.path.join(OUTPUT_DIR, f"{test_name}.json")
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=4)

                    logger.info(f"Output saved to {file_path}")
                    print(f"Output saved to {file_path}\n")

                except Exception as e:
                    logger.exception(f"Error testing {test_name}: {e}")
                    print(f"Error testing {test_name}: {e}")



if __name__ == "__main__":
    test_requester_functions(api_functions)
    logger.info("All tests completed.")