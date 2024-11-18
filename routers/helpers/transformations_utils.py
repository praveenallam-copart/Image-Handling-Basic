from pydantic import BaseModel
from typing import Union

class TransformQuery(BaseModel):
    text: Union[str, None]
    