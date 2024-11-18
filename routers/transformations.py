import os
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import APIRouter
from pydantic import BaseModel
from logs import get_app_logger, get_error_logger
from Utilities import Utilities
import prompts

from langchain_core.prompts import ChatPromptTemplate
from routers.helpers.transformations_utils import *

load_dotenv()

class DecompositionResponses(BaseModel):
    queries: List[str] = Field(description="List of decomposed quereies generated")

app_logger = get_app_logger()
error_logger = get_error_logger()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GENIE_ACCESS_TOKEN = os.getenv("GENIE_ACCESS_TOKEN")
llm = Utilities().llm()
structured_llm = llm.with_structured_output(DecompositionResponses)
app_logger.info(f"breaking down the large query info small sub queries...")

router = APIRouter(
    prefix="/transformation",
    tags=["Transformation"]
)

def run(query):  
    template = prompts.DECOMPOSITION_SYSTEM_PROMPT
    try:
        prompt = ChatPromptTemplate.from_messages([("system", template),("human", "Input: {query}")])
        chain = prompt | structured_llm
        response = chain.invoke({"query" : query})
        app_logger.info(f"Decomposition done...")
        return response.queries
    except Exception as e:
        error_logger.error(f"An unexpected e occurred: {type(e).__name__, str(e)}")
        raise
    
@router.post("/decompose")
def decomposition(transformQuery :TransformQuery):
    print(f"{transformQuery.text = }")
    if (transformQuery.text is not None) and (transformQuery.text != ""):
        response = run(transformQuery.text)
        return {"response" : response}
    return {"response": None}
    