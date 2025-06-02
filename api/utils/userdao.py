import json
from pathlib import Path
from typing import Optional

from .config import config
from models.user import User


class UserDAO:
    def __init__(self):
        self._base_dir = Path(config.DIR.USER_DATA).resolve()
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _user_path(self, user_id: str) -> Path:
        return self._base_dir / f"{user_id}.json"

    def save(self, user: User):
        existing = self.get_by_userid(user.user_id)
        if existing:
            raise ValueError(f"user_id '{user.user_id}' already exists.")
        path = self._user_path(user.user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user.model_dump(), f, indent=2)

    def get_by_userid(self, user_id: str) -> Optional[User]:
        path = self._user_path(user_id)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return User(**data)

    def get_by_account_name(self, account_name: str) -> Optional[User]:
        for json_file in self._base_dir.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("account_name") == account_name:
                return User(**data)
        return None
