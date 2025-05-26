from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    account_name: str
    password_name: str