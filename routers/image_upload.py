import os
import time
import uuid
import base64
import aiohttp
import asyncio
from fastapi import APIRouter
from dotenv import load_dotenv
from typing import List, Dict, Union
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

import prompts
from Utilities import Utilities
from routers.helpers.image_upload_utils import *
from logs import get_app_logger, get_error_logger

load_dotenv()

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

class ImageDescriptionResponse(BaseModel):
    description: str = Field(description = "The Information present in the image with same structure present in the image")
    summary: str = Field(description = "The summary of the image description with the help of topics, the summary should be elaborative (but not too long), and it should be in points for easy/better understanding")
    alert: Union[str, None] = Field(description = "If the image description contains any sensitive information it gives an alert message, else None", default = None)
    reason: Union[str, None] = Field(description = "If the image description contains any sensitive information it gives the reason for the alert message, else None", default = None)
    
class QueryResponse(BaseModel):
    answer: Union[Dict, None] = Field(description = "The answer for the question asked in query in the given image description.It is a Dictionary with key as query/question and value as answer. Every realted query should be present and should get answered", default = None)
    related_queries: Union[List, None] = Field(description = "The queries/query from list of queries which are asnwered, if None got answered return None or List of queries/query answered", default = None)
    
app_logger = get_app_logger()
error_logger = get_error_logger()
llm = Utilities().llm()
structured_llm = llm.with_structured_output(ImageDescriptionResponse, include_raw = True)
    
async def describe_image( encoded_image: str, name: str):
    """
    Description of the Image using base64 format of an image.

    Args:
        encoded_image (str): Base64 encoded image string.
    Returns:
        image_description(str): Description of the Image
    """
    app_logger.info(f"getting description of {name = }")
    try:
        messages = [
            {"role" : "system", "content" : prompts.IMAGE_DESCRIPTION_PROMPT},
            {"role" : "user", "content" : [{"type" : "image_url", "image_url" : {"url" : f"data:image/png;base64,{encoded_image}", "detail": "auto"}}]}
        ]
        response = await structured_llm.ainvoke(messages)
        app_logger.info(f"Got the image description...")
        return response["parsed"].description, response["parsed"].summary, response["parsed"].alert, response["parsed"].reason , response["raw"].response_metadata
    except Exception as e:
        error_logger.error(f"Error processing image: {str(e)}")
         
async def get_answer(image_description: str, queries: Union[List, str]):
    try:
        prompt = ChatPromptTemplate([
            ("system", prompts.ANSWER_PROMPT),
            ("human", "Image Description: {image_description}\nQueries: {queries}")
        ])

        answer_llm = prompt | llm.with_structured_output(QueryResponse)
        response = await answer_llm.ainvoke({"image_description" : image_description, "queries" : queries})
        app_logger.info(f"got the answer for the given text....")
        return response.answer, response.related_queries
    except Exception as e:
        error_logger.error(f"An unexpected e occurred: {type(e).__name__, str(e)}")
        
            
async def run(session, image_content: Attachment, access_token: str, user_id: str, queries: Union[str, None]):
    try:
        if image_content.contentType == "application/vnd.microsoft.teams.file.download.info":
            filename = f"{uuid.uuid3(uuid.NAMESPACE_URL, f"{image_content.content.uniqueId},{image_content.contentUrl},{user_id}")}.png"
            async with session.get(image_content.content.downloadUrl) as response:
                img_bytes = await response.read()
        if image_content.contentType == "image/*": # smba.trafficmanager.net
            filename = f"{uuid.uuid3(uuid.NAMESPACE_URL, f"{image_content.contentUrl},{user_id}")}.png"
            headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json;odata=verbose"
                }
            async with session.get(image_content.contentUrl, headers = headers) as response:
                img_bytes = await response.read()
        image_size = response.headers.get('Content-Length')
        app_logger.info(f"Image size: {image_size} bytes") if image_size else app_logger.info("Content-Length header not available")
    except Exception as e:
        error_logger.error(f"An unexpected e occurred: {type(e).__name__, str(e)}")
    
    try:
        name = f"{image_content.name}" if image_content.contentType == "application/vnd.microsoft.teams.file.download.info" else "Copy/Paste"
        encoded_image = base64.b64encode(img_bytes).decode("utf-8")
        app_logger.info(f"Converted Image to base65 {name}")
        description, summary, alert, reason, metadata = await describe_image(encoded_image, name)
        answer, related_queries = None, None
        if (queries is not None) and (queries != "") and (len(queries) > 0):
            answer, related_queries = await get_answer(image_description=description, queries=queries)
        description = f"The {name} Image is about:\n\n" + description
        return {"description" : description, "summary" : summary, "answer" : answer, "alert" : alert, "reason" : reason,"related_queries" : related_queries, "metadata" : metadata, "filename" : filename, "name" : name}
    except Exception as e:
        error_logger.error(f"An unexpected e occurred: {type(e).__name__, str(e)}")
        return {"description" : "Something went wrong while processing the image. Please try again later.", "status" : "error"}
    
async def process_run(image_contents: List[Attachment], access_token: str, user_id: str, queries: Union[List, str, None]):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(10)
        async def limited_download(image_content, access_token, user_id, queries):
            async with semaphore:
                return await run(session, image_content, access_token, user_id, queries)
        tasks = [limited_download(image_content, access_token, user_id, queries) for image_content in image_contents]
        return await asyncio.gather(*tasks)
    
@router.post("/image-uploading")
def image_uploading(attachments: Attachments):
    try:
        image_contents = attachments.image_contents
        user_id = attachments.user_id
        access_token = attachments.access_token
        queries = attachments.queries
        start = time.perf_counter()
        response = asyncio.run(process_run(image_contents, access_token, user_id, queries))
        end = time.perf_counter()
        return {"response" : response, "time_taken" : f"{end - start} second(s)"}
    except Exception as e:
        error_logger.error(f"An unexpected e occurred: {type(e).__name__, str(e)}")
        return {"response" : "Something went wrong while processing the image(s). Please try again later.", "status" : "error"}