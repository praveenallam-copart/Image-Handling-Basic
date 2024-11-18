from typing import List, Union
from pydantic import BaseModel


class Content(BaseModel):
    downloadUrl: str
    uniqueId: str
    fileType: str
    
class Attachment(BaseModel):
    contentType: str
    content: Union[Content, None] = None
    contentUrl: str
    name: Union[str, None] = None

class Attachments(BaseModel):
    image_contents: List[Attachment]
    access_token: str
    user_id: str
    queries: Union[List, str, None]

class CategoryUtil(BaseModel):
    text: str