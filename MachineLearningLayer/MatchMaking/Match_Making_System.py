# Ed Wang - 2026-02-22
# Core logic for the Match making system.

from JobDescriptor import Descriptor
from Retriever import Retriever
from MatchMaker import Matcher
import logging
import inspect
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# Set up logging to a file with a timestamp in the filename for better organization of logs over time
timestamp = datetime.now().strftime("%Y-%m-%d_%H")

logging.basicConfig(
        filename=f"Logs/{timestamp}_MatchMakingLog.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
        )
    
logging.getLogger(__name__).info(f"---Booting Match Making System Components---")

MatcherObj = Matcher()
RetrieverObj = Retriever()
DescriptorObj = Descriptor()

# Main function that connects all the components together to generate the final response for the student based on their input competencies
def Get_All_Matches(user_input: list[int]):
    method = inspect.currentframe().f_code.co_name
    try:
        MatchedList = MatcherObj.Get_Jobs(user_input=user_input)

        RetrievedDescriptions = RetrieverObj.Query(MatchedList=MatchedList)

        Job_Summaries = DescriptorObj.Describe(MatchedList=MatchedList, Context=RetrievedDescriptions)

        response = "## 🎯 Matches\n\n"

        for match in Job_Summaries['Matches']:
            response += f"### {match['Occupation Title']}\n\n"

            response += f"**Description**  \n"
            response += f"{match['Description']}\n\n"

            response += f"**Education / Credentials Required**  \n"
            response += f"{match['Education/Credentials Required']}\n\n"

            response += "---\n\n"   # divider line between matches

        return response


    except Exception as e:
        logging.getLogger(__name__).exception(f'{method} => Error [{e}]')

