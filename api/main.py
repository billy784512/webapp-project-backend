from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.matchup import router as matchup_router
from routers.game import router as setup_router


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(matchup_router)
app.include_router(setup_router)

@app.get("/heartbeat")
async def hello():
    return {"message": "Hello from FastAPI"}