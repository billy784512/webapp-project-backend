import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models.requests import MatchRequest
from services.matchup_service import MatchupService

router = APIRouter()
match_service = MatchupService()

@router.post(
    "/match", 
    status_code=200,
    responses={
        408: {"description": "Match timeout"}
    })
async def match_user(req: MatchRequest):
    try:
        room_id = await match_service.join_queue(req.user_id)
        result = {
            "status": "matched",
            "room_id": room_id
        }
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except asyncio.TimeoutError:
        return JSONResponse(content={"message": "Match timeout"}, status_code=status.HTTP_408_REQUEST_TIMEOUT)