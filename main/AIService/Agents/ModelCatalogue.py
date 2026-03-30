import os
from typing import Optional, Type
from pydantic import BaseModel
from langchain_ollama import ChatOllama
import logging
from enum import Enum

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


#region [Model Catalogue]
#Each type of model has its own strenghts and weaknesses. Its also worth noting that we are using quantized version
#for the QWEN models. 

class ModelEnum(str, Enum):
    QWEN_14 = "qwen2.5:14b-instruct-q4_K_M"
    QWEN_7 = "qwen2.5:7b-instruct"
    GRANITE = "granite3.3:8b"
    LLAMA = "llama3.1:8b"

MODEL_CONFIG = {
    ModelEnum.QWEN_14: {"threads": 4},
    ModelEnum.QWEN_7: {"threads": 4},
    ModelEnum.GRANITE: {"threads": 6},
    ModelEnum.LLAMA: {"threads": 6},
}
#endregion


#region [Model Creation]
#A generic function for creating an Ollama based chat model  
def CreateModel(
    model: ModelEnum,
    *,
    schema: Optional[Type[BaseModel]] = None,
    is_docker: Optional[bool] = None
):
    try:
        config = MODEL_CONFIG.get(model, {"threads": 4})

        llm = ChatOllama(
            model=model.value,
            base_url=OLLAMA_BASE_URL,
            options={"num_threads": config["threads"]}
        )

        if schema is not None:
            llm = llm.with_structured_output(schema)

        return llm

    except Exception as e:
        logger.exception(f"[CreateModel] {model}: {e}")
        raise
#endregion