import json
import logging
import inspect
import os
from ragas.metrics.collections import BleuScore
from ragas.metrics.collections import RougeScore
from tqdm import tqdm
from transformers import pipeline
import asyncio
import pandas as pd

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
    with open('DataSets/Results/llm_answers.json', "r", encoding="utf-8") as f:
        DataSet = json.load(f)
    logger.info("Data Set Loaded")
except Exception as e:
    logger.exception(f"Error loading data set => {e}")
    exit()
#endregion

#region [Loading Statistical Scorers]
bleu_scorer = BleuScore()
rouge_precision_scorer = RougeScore(rouge_type='rougeL', mode='precision')
rouge_recall_scorer = RougeScore(rouge_type='rougeL', mode='recall')
rouge_f1_scorer = RougeScore(rouge_type='rougeL', mode='fmeasure')
#endregion

#region [NLI Loading]
nli_model = pipeline(
    "text-classification",
    model="roberta-large-mnli",
    return_all_scores=True,
    top_k=None,
    truncation=True
)
#endregion

#region [Model Names]
models = ['qwen2.5:14b-instruct-q4_K_M','llama3.1:8b-instruct-q4_K_M', 'gemma2:9b-instruct-q4_K_M', 'granite3.3:8b']
Model_Names = {
    'qwen2.5:14b-instruct-q4_K_M': 'QWEN 2.5',
    'llama3.1:8b-instruct-q4_K_M': 'LLAMA 3.1',
    'gemma2:9b-instruct-q4_K_M': 'GEMMA 2',
    'granite3.3:8b': 'GRANITE 3.3'
}

#endregion


#region [Statistical Scoring]
def Generate_Statistical_Scores(reference, response):
    method = inspect.currentframe().f_code.co_name
    try:
        bleu_task = bleu_scorer.score(reference=reference, response=response)
        precision_task = rouge_precision_scorer.score(reference=reference, response=response)
        recall_task = rouge_recall_scorer.score(reference=reference, response=response)
        f1_task = rouge_f1_scorer.score(reference=reference, response=response)


        return {
            "BLEU": bleu_task.value,
            "Precision": precision_task.value,
            "Recall": recall_task.value,
            "F1 Score": f1_task.value
        }
    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None
#endregion

#region [NLI Scoring]
def Generate_NLI_Scores(response, full_context):
    method = inspect.currentframe().f_code.co_name
    try:
        nli_result = nli_model(
        {"text": full_context, "text_pair": response},
        return_all_scores=True
        )

        scores = {item["label"]: item["score"] for item in nli_result}
        return scores

        
    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None
#endregion

#region [Structure Results]
def Structure_Json_Save(Og_dict, stat_scores, nli_scores):
    method = inspect.currentframe().f_code.co_name
    try:
        
        new_dict = {**Og_dict, **stat_scores, **nli_scores}
        return new_dict

        
    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None

def Structure_DF_Save(Og_dict, stat_scores, nli_scores):
    method = inspect.currentframe().f_code.co_name
    try:
        
        og_subset = {
            'Prompt_ID':Og_dict['Prompt_ID'],
            'Content_Type': Og_dict['Content_Type'],
            'Model': Model_Names[Og_dict['model']],
            "temperature": Og_dict['temperature'],
            "top_p": Og_dict['top_p'],
            "top_k": Og_dict['top_k'],
            "runtime": Og_dict['runtime'],
        }

        new_dict = {**og_subset, **stat_scores, **nli_scores}
        return new_dict

    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        return None
#endregion


def main():
    method = inspect.currentframe().f_code.co_name
    All_Results_Json = []
    All_Results_DF = []
    try:
        
        for Sample in tqdm(DataSet, desc='Processing LLM Answers', unit='LLM Answer'):
            
            reference = Sample.get('Ground_Truth_Answer', None)
            response = Sample.get('model_answer', None)
            full_context = " ".join(Sample.get("Context",[]))   

            stat_scores = Generate_Statistical_Scores(reference=reference, response=response)
            nli_scores = Generate_NLI_Scores(response=response, full_context=full_context)

            if any(x is None for x in (stat_scores, nli_scores)):
                logger.error(f"Null Detected - Skipping Loop")
                continue

            json_result_dict = Structure_Json_Save(Og_dict=Sample, stat_scores=stat_scores, nli_scores=nli_scores)
            df_result_dict = Structure_DF_Save(Og_dict=Sample, stat_scores=stat_scores, nli_scores=nli_scores)

            All_Results_Json.append(json_result_dict)
            All_Results_DF.append(df_result_dict)
        
        logger.info(f'{method} => Main Loop finished, saving results now')
        
        with open('DataSets/Scores/LLM_Answer_Scores.json','w', encoding='utf-8') as f:
            json.dump(All_Results_Json, f, indent=4, ensure_ascii=False)

        df_All_Results = pd.DataFrame(All_Results_DF)

        df_All_Results.to_csv('DataSets/Scores/LLM_Answer_Scores.csv',index=False)

        logger.info(f"{method} => Results Saved Exiting()")
        logger.info(f"{method} => results size = {len(df_All_Results)}")
        exit()
        
    except Exception as e:
        logger.exception(f"{method} Error => {e}")
        exit()
    

if __name__ == '__main__':
    main()