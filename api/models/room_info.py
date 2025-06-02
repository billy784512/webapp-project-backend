from typing import List
from pydantic import BaseModel

class RoomInfo(BaseModel):
    user_ids: List[str]=[]
    image: str=None
    color_list: List[str]=None