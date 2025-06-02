import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models.requests import MatchRequest
from services.matchup_service import MatchupService
from services.user_service import UserService

router = APIRouter(prefix="/match")
match_service = MatchupService.get_instance()
user_service = UserService()

@router.post(
    "/anonymous", 
    status_code=200,
    responses={
        408: {"description": "Match timeout"}
    })
async def match_user(req: MatchRequest):
    try:
        if not user_service.dao.get_by_userid(req.user_id):
            user_service.register(req.user_name, "password", req.user_id)
        result = await match_service.anonymous_match(req.user_id)
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except asyncio.TimeoutError:
        result = {
            "status": "failed",
            "message": "Match timeout"
        }
        return JSONResponse(content=result, status_code=status.HTTP_408_REQUEST_TIMEOUT)

@router.post(
    "/passkey", 
    status_code=200,
    responses={
        408: {"description": "Match timeout"}
    })       
async def match_user_with_passkey(req: MatchRequest):
    try:
        if not user_service.dao.get_by_userid(req.user_id):
            user_service.register(req.user_name, "password", req.user_id)
        result = await match_service.passkey_match(req.user_id, req.passkey)
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except asyncio.TimeoutError:
        result = {
            "status": "failed",
            "message": "Match timeout"
        }
        return JSONResponse(content=result, status_code=status.HTTP_408_REQUEST_TIMEOUT)

@router.post(
    "/cancel",
    status_code=200,
    responses={
        500: {"description": "Internal Server Error"}
    })
async def cancel(req: MatchRequest):
    try:
        await match_service.cancel_match(req.user_id)
        result = {
            "status": "successed"
        }
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except Exception as e:
        resutl = {
            "message": str(e)
        }
        return JSONResponse(content=result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)