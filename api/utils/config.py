import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    class JWT:
        SECRET_KEY=os.getenv("JWT_SECRET_KEY")
        ALGO=os.getenv("JWT_ALGO")
        EXPIRE_MINUTES=86400

    class DIR:
        USER_DATA="volume/user"

config = Config()