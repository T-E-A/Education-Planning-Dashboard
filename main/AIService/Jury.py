from langchain_core.runnables import RunnableParallel
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
import logging
import inspect
from Evaluators.Metrics import Metrics


#region [Metric Struct]
class Metric_Struct(BaseModel):
    score: float = Field(description="Score of answer.")
    reasoning: str = Field(description="Reasoning for evaluation in 2 to 4 sentences.")
    verdict: bool = Field(description="Whether of not the answer is adequate.")
#endregion 

#region [Prompt Structures]
Hallucination_Prompt = PromptTemplate(
    input_variables=['Hallucination_Definition','Hallucination_Instructions','Prompt','Context','Test_Answer'],
    template=(
    "You are an hallucinations checker, you job is to reference the prompt and context to check if the LLM's answer contains any hallucination.\n"

    "##Definitions##\n"
    "{Hallucination_Definition}\n"

    "##Instructions##\n"
    "{Hallucination_Instructions}\n"

    "##Instructions##\n"
    "\t- Score each answer from 0 to 1."
    "\t- Provide your reasoning for the score."
    "\t- Provide a verdict, with True or False, as to if the answer passed your evaluation."

    "Return ONLY structured output."

    "##Prompt##\n"
    '{Prompt}\n'

    "##Context in JSON Format##\n"
    "{Context}\n"

    "##Answer##\n"
    "{Test_Answer}\n"
    

    
))
Faithfulness_Prompt = PromptTemplate(
    input_variables=['Faithfulness_Definition','Faithfulness_Instructions','Prompt','Context','Test_Answer'],
    template=(
    "You are a faithfulness checker, your job is to reference the prompt and context to check if the LLM's answer remains faithful to the context.\n"

    "##Definitions##\n"
    "{Faithfulness_Definition}\n"

    "##Instructions##\n"
    "{Faithfulness_Instructions}\n"

    "##Instructions##\n"
    "\t- Score each answer from 0 to 1."
    "\t- Provide your reasoning for the score."
    "\t- Provide a verdict, with True or False, as to if the answer passed your evaluation."

    "Return ONLY structured output."

    "##Prompt##\n"
    '{Prompt}\n'

    "##Context in JSON Format##\n"
    "{Context}\n"

    "##Answer##\n"
    "{Test_Answer}\n"
    
    
    
))
Prompt_Alignment_Prompt = PromptTemplate(

input_variables=['Prompt_Alignment_Definition','Prompt_Alignment_Instructions','Prompt','Test_Answer'],
template=(
    "You are an prompt alignment checker, you job is to reference the prompt to check if the LLM's answer aligns with the instructions of the prompt.\n"

    "##Definitions##\n"
    "{Prompt_Alignment_Definition}\n"

    "##Instructions##\n"
    "{Prompt_Alignment_Instructions}\n"

    "##Instructions##\n"
    "\t- Score each answer from 0 to 1."
    "\t- Provide your reasoning for the score."
    "\t- Provide a verdict, with True or False, as to if the answer passed your evaluation."

    "Return ONLY structured output."

    "##Prompt##\n"
    '{Prompt}'

    "##Answer##\n"
    "{Test_Answer}\n"

    
))
Constraint_Statisfaction_Prompt = PromptTemplate(
    input_variables=['Constraint_Satisfaction_Definition','Constraint_Satisfaction_Instructions','Prompt','Test_Answer'],
    template=(
    "You are an constraint satisfaction checker, you job is to refernce the prompt to check if the LLM's answer follows all explicit constraint presented in the prompt.\n"

    "##Definitions##\n"
    "{Constraint_Satisfaction_Definition}\n"

    "##Instructions##\n"
    "{Constraint_Satisfaction_Instructions}\n"

    "##Instructions##\n"
    "\t- Score each answer from 0 to 1."
    "\t- Provide your reasoning for the score."
    "\t- Provide a verdict, with True or False, as to if the answer passed your evaluation."

    "Return ONLY structured output."

    "##Prompt##\n"
    '{Prompt}'

    "##Answer##\n"
    "{Test_Answer}\n"

    
    
))
Answer_Relevancy_Prompt = PromptTemplate(
    input_variables=['Answer_Relevancy_Definition','Answer_Relevancy_Instructions','Test_Answer'],
    template=("You are a answer relevancy checker, you job is to reference the prompt to check to see if the LLM's generated answer directly addresses the prompt and utilizes the context effectively.\n"

    "##Definitions##\n"
    "{Answer_Relevancy_Definition}\n"

    "##Instructions##\n"
    "{Answer_Relevancy_Instructions}\n"

    "##Instructions##\n"
    "\t- Score the answer from 0 to 1."
    "\t- Provide your reasoning for the score."
    "\t- Provide a verdict, with True or False, as to if the answer passed your evaluation."

    "Return ONLY structured output."

    
    "##Prompt##\n"
    '{Prompt}'

    "##Context in JSON Format##\n"
    "{Context}\n"

    "##Answer##\n"
    "{Test_Answer}\n"

    
    
    
    ))
#endregion

#region [Model Instances]
Hallucination_and_Faithfullness_Model = ChatOllama(
                model='granite3.3:8b',
                options={"num_threads": 1},
                temperature=0,
            ).with_structured_output(Metric_Struct)

Prompt_Alignment_and_Constraint_Satisifaction_Model = ChatOllama(
                model='qwen2.5:7b-instruct-q4_K_M',
                options={"num_threads": 1},
                temperature=0,
).with_structured_output(Metric_Struct)

Answer_Relevancy_Model = ChatOllama(
    model='llama3.1:8b-instruct-q4_K_M',
    options={"num_threads": 1},
    temperature=0,
).with_structured_output(Metric_Struct)
#endregion

#region [Chains]
Hallucination_Chain = Hallucination_Prompt | Hallucination_and_Faithfullness_Model
Faithfulness_Chain = Faithfulness_Prompt | Hallucination_and_Faithfullness_Model

Prompt_Alignment_Chain = Prompt_Alignment_Prompt | Prompt_Alignment_and_Constraint_Satisifaction_Model
Constraint_Satisfaction_Chain = Constraint_Statisfaction_Prompt | Prompt_Alignment_and_Constraint_Satisifaction_Model

Answer_Relevancy_Chain = Answer_Relevancy_Prompt | Answer_Relevancy_Model 
#endregion

#region [Parallel Chains]
Context_Parallel_Chain = RunnableParallel({
    'Hallucination': Hallucination_Chain,
    'Faithfulness': Faithfulness_Chain,
    'Answer Relevancy': Answer_Relevancy_Chain
})

Alignment_Parallel_Chain = RunnableParallel({
    'Prompt Alignment': Prompt_Alignment_Chain,
    'Constraint Satisfaction': Constraint_Satisfaction_Chain
})
#endregion

logging.getLogger(__name__).info(f'Jury Components Initilized')

#region [JURY CLASS]
class Jury:
    def __init__(self, prompt, answer, context, Context_Parallel_Chain=Context_Parallel_Chain,Alignment_Parallel_Chain=Alignment_Parallel_Chain ):
        try:
            self.prompt = prompt
            self.answer = answer
            self.context = context

            self.Context_Parallel_Chain = Context_Parallel_Chain
            self.Alignment_Parallel_Chain = Alignment_Parallel_Chain

            self.Context_Input_Dict = self.Structure_Context_Input()
            self.Alignment_Input_Dict = self.Structure_Alignment_Input()
        
        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
    
    def Structure_Context_Input(self):
        try:
            
            context_input_dict = {
                "Hallucination_Definition": Metrics['Hallucination']['Definition'],
                "Hallucination_Instructions": Metrics['Hallucination']['Instructions'],
                "Faithfulness_Definition": Metrics['Faithfulness']['Definition'],
                "Faithfulness_Instructions": Metrics['Faithfulness']['Instructions'],
                "Answer_Relevancy_Definition": Metrics['Answer Relevancy']['Definition'],
                "Answer_Relevancy_Instructions": Metrics['Answer Relevancy']['Instructions'],
                "Faithfulness_Definition": Metrics['Faithfulness']['Definition'],
                "Faithfulness_Instructions": Metrics['Faithfulness']['Instructions'],
                "Test_Answer":self.answer,
                "Prompt":self.prompt,
                "Context":self.context
            }

            return context_input_dict

        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
    
    def Structure_Alignment_Input(self):
        try:
            prompt_input_dict = {
                "Prompt_Alignment_Definition": Metrics['Hallucination']['Definition'],
                "Prompt_Alignment_Instructions": Metrics['Hallucination']['Instructions'],
                "Constraint_Satisfaction_Definition": Metrics['Constraint Satisfaction']['Definition'],
                "Constraint_Satisfaction_Instructions": Metrics['Constraint Satisfaction']['Instructions'],
                "Test_Answer":self.answer,
                "Prompt":self.prompt,
                "Context":self.context
            }

            return prompt_input_dict

        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
    
    def Run_Context_Chain(self, Evaluation_Dict: dict, Score_Dict: dict) -> dict:
        try:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).info(f'{method} Invoked')
            results = self.Context_Parallel_Chain.invoke(input=self.Context_Input_Dict)

            keys = results.keys()
            for key in keys:
                Evaluation_Dict[key] = {
                    'score':results[key].score,
                    'reasoning':results[key].reasoning,
                    'verdict': 'PASS' if results[key].verdict else 'FAIL'
                }

                Score_Dict[key] = results[key].score
            
            return Evaluation_Dict, Score_Dict

        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
            return Evaluation_Dict, Score_Dict
    
    def Run_Alignment_Chain(self, Evaluation_Dict: dict, Score_Dict: dict) -> dict:
        try:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).info(f'{method} Invoked')
            results = self.Alignment_Parallel_Chain.invoke(input=self.Alignment_Input_Dict)

            keys = results.keys()
            for key in keys:
                Evaluation_Dict[key] = {
                    'score':results[key].score,
                    'reason':results[key].reasoning,
                    'verdict': 'PASS' if results[key].verdict else 'FAIL'
                }

                Score_Dict[key] = results[key].score
            
            return Evaluation_Dict, Score_Dict

        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
            return Evaluation_Dict, Score_Dict
    
    def Deliberate(self) -> dict:
        try:
            Evaluation_Dict = {}
            Score_Dict = {}

            Evaluation_Dict, Score_Dict = self.Run_Context_Chain(Evaluation_Dict=Evaluation_Dict, Score_Dict=Score_Dict)
            Evaluation_Dict, Score_Dict = self.Run_Alignment_Chain(Evaluation_Dict=Evaluation_Dict, Score_Dict=Score_Dict)

            Output = {
                'Eval':Evaluation_Dict,
                'Scores': Score_Dict
            }

            return Output

        except Exception as e:
            method = inspect.currentframe().f_code.co_name
            logging.getLogger(__name__).exception(f'{self.className} - {method} => Error [{e}]')
            return {}
#endregion