import datetime
from uuid import uuid4

import bcrypt
import jwt

from utils.config import config
from utils.thread_pool import ThreadPoolManager
from utils.userdao import UserDAO
from models.user import User

class UserService:
    def __init__(self):
        self.dao = UserDAO()
        self.JWT_SECRET_KEY = config.JWT.SECRET_KEY

    def register(self, account_name: str, password: str, user_id: str=None) -> dict:
        if not user_id:
            user_id = uuid4().hex
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = User(
            user_id=user_id,
            account_name=account_name,
            password_name=hashed_pw
        )

        try:
            future = ThreadPoolManager.instance().write_pool.submit(self.dao.save, new_user)
            future.result()
            return {
                "status": "success"
            }
        except ValueError as ve:
            return {
                "status": "error",
                "message": str(ve)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {e}"
            }
        
    def login(self, account_name: str, password: str) -> dict:
        try:
            future = ThreadPoolManager.instance().read_pool.submit(
                self.dao.get_by_account_name, account_name
            )
            user:User = future.result()

            if not user:
                return {"status": "error", "message": "Account not found"}

            if not bcrypt.checkpw(password.encode("utf-8"), user.password_name.encode("utf-8")):
                return {"status": "error", "message": "Incorrect password"}

            token_payload = {
                "account_name": user.account_name
            }
            access_token = self._create_access_token(token_payload)

            return {
                "status": "success",
                "access_token": access_token,
                "token_type": "bearer",
            }            

        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}
        
    def _create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + (datetime.timedelta(minutes=config.JWT.EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT.SECRET_KEY, algorithm=config.JWT.ALGO)
        return encoded_jwt

