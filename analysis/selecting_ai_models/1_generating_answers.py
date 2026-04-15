import json
import logging
import inspect
import os
from tqdm import tqdm
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
import time
from itertools import product

#region [Setting Paths and Logger]
log_path = f'Logs'

os.makedirs(log_path, exist_ok=True)

script_name = os.path.splitext(os.path.basename(inspect.getfile(inspect.currentframe())))[0]
log_file = os.path.join(log_path, f"{script_name}.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s",
    filemode="w"
)

logger = logging.getLogger(__name__)

logger.info(f"{script_name} - Started")
#endregion


#region [Load Data Set]
logger.info("Loading Data Set into Dict")

try:
    with open('DataSets/Full_Ground_Truth_Data_Set.json', "r", encoding="utf-8") as f:
        DataSet = json.load(f)
    logger.info("Data Set Loaded")
except Exception as e:
    logger.exception(f"Error loading data set => {e}")
    exit()
#endregion


#region [Prompt Template]
Chat_Assisstant_Prompt_Template = PromptTemplate(
    input_variables=["context", "user_query", "num_sentences"],
    template=(
        "You are an information summarizer. You are responsible for answering ther User Query based on the context provided.\n\n"

        "## Instructions ##\n"
        "- Use the Context to formulate an answer to the Users Query.\n"
        "- Do not inject unsupported facts or irrelevant information.\n"
        "- Restrict your answer to {num_sentences} sentences.\n"

        "## Context ##\n"
        "{context}"

        "\n## User Query ##\n"
        "{user_query}"

    )
)
#endregion


#region [Model Parameters]
temperatures = [0.2, 0.5, 0.9]
top_ps = [0.5,0.7,0.9]
top_ks = [20, 40, 90]
#endregion

#region [Models to Test]
models = ['qwen2.5:14b-instruct-q4_K_M','llama3.1:8b-instruct-q4_K_M', 'gemma2:9b-instruct-q4_K_M', 'granite3.3:8b']
#endregion

#region [Setting Configurations]
configs = list(product(models, temperatures, top_ps, top_ks))
#endregion


#region [Helper Functions]
def Initilize_Model(model,temperature, top_p, top_k):
    method = inspect.currentframe().f_code.co_name
    try:
        # logger.info(f"{method}() Called")

        llm = ChatOllama(
            model=model,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        return llm
    

    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None


def Ask_Model(user_query, context, num_sentences,llm):
    method = inspect.currentframe().f_code.co_name
    try:
        # logger.info(f"{method}() Called")

        augmented_prompt = Chat_Assisstant_Prompt_Template.format(
            context=json.dumps(context),
            user_query=user_query,
            num_sentences=num_sentences
        )

        response = llm.invoke([
            HumanMessage(content=augmented_prompt)
        ])

        answer = response.content

        return answer
    

    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None

def Structure_Response(model,temperature, top_p, top_k, model_answer, original_dict, runtime):
    method = inspect.currentframe().f_code.co_name
    try:
        # logger.info(f"{method}() Called")

        append_dict = {
            'model':model,
            'temperature':temperature,
            'top_p':top_p,
            'top_k':top_k,
            'runtime':runtime,
            'model_answer':model_answer
        }

        new_dict = {**original_dict, **append_dict}
        return new_dict

    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None
#endregion


#region [Main Loop]

'''
   {
        "Prompt":"What credentials do I need to become a Data Scientist?",
        "Ground_Truth_Answer":"To become a Data Scientist, individuals typically require a strong educational background in quantitative or technical fields. This usually includes a bachelor’s degrees in statistics, mathematics, computer science, computer systems engineering or related disciplines, or a completion of a college program in computer science. Additionally, Data Science roles may also require a master’s or doctoral degree in the fields of such as data science, machine learning, or another related quantitative area. In addition to formal education, practical experience in programming, statistical modeling, and machine learning is commonly expected to effectively analyze data and build predictive models.",
        "Context":[
            "A bachelor’s degree in statistics, mathematics, computer science, computer systems engineering or a related discipline or completion of a college program in computer science is usually required.",
            "A master’s or doctoral degree in machine learning, data science, or a related quantitative field is usually required.",
            "Experience in programming is usually required.",
            "Experience in statistical modelling and machine learning is usually required."
        ],
        "Content_Type":"NOC"
    }


'''

def main():
    method = inspect.currentframe().f_code.co_name
    try:
        logger.info(f"{method}() Called")

        All_Answers = []
        for prompt_dict in tqdm(DataSet, desc='Processing Prompts', unit='Prompt'):
            user_query = prompt_dict.get('Prompt',None)
            context = prompt_dict.get('Context',None)
            num_sentences = prompt_dict.get('Num_Sentences', None)

            if any(x is None for x in (user_query, context, num_sentences)):
                logger.error(f"Null Detected - Skipping Loop")
                continue

            for config in tqdm(configs, desc="Processing Models", unit='Model'):
                    
                    # print(config)
                    model, temperature, top_p, top_k = config

                    # print(f"Model:{model}")
                    # print(f"Temperature:{temperature}")
                    # print(f"Top P:{top_p}")
                    # print(f"Top K:{top_k}")

                    llm = Initilize_Model(model=model, temperature=temperature, top_p=top_p, top_k=top_k)



                    if llm:

                        start_time = time.perf_counter()
                        model_answer = Ask_Model(user_query=user_query, context=context, num_sentences=num_sentences, llm=llm)
                        end_time = time.perf_counter()

                        runtime = end_time - start_time

                        answer_dict = Structure_Response(model=model, 
                                                                 temperature=temperature, 
                                                                 top_p=top_p, 
                                                                 top_k=top_k,
                                                                 model_answer=model_answer,
                                                                 original_dict=prompt_dict,
                                                                 runtime=runtime
                                                                )
                        All_Answers.append(answer_dict)
                    else:
                        logger.error(f"{method} => LLM is Model")

        logger.info(f"{method} main loop done.")
        logger.info(f"{method} Output results lenght = {len(All_Answers)}")

        with open("DataSets/Results/llm_answers.json","w", encoding="utf-8") as f:
            json.dump(All_Answers, f, indent=4, ensure_ascii=False)

        logger.info(f"{method} results saved.")


    except Exception as e:
        logger.exception(f"{method} Error => {e}")



if __name__ == "__main__":
    main()