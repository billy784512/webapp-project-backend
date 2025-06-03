from typing import List
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    account_name: str
    password: str

class LoginRequest(BaseModel):
    account_name: str
    password: str

class MatchRequest(BaseModel):
    user_id: str
    user_name: str
    passkey: str=None

class SubmitRequest(BaseModel):
    base64_strs: List[str]
    room_id: str