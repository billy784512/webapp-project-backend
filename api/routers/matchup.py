from fastapi import APIRouter, Query, Response, status
from fastapi.responses import JSONResponse

from services.matchup_service import matchup_service  

router = APIRouter(prefix="/match", tags=["Matchup"])

@router.get("/game_image")
async def get_game_image(userid: str = Query(..., alias="userid")):
    """
    Spec1: 回傳對戰用的圖片 bytes，Content-Type: image/jpeg
    """
    image_data = matchup_service.get_game_image_for_user(userid)
    if image_data:
        return Response(content=image_data, media_type="image/jpeg")
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Image not found or user not matched"})


@router.get("/game_color")
async def get_game_color(userid: str = Query(..., alias="userid")):
    """
    Spec2: 回傳顏色列表，格式為 JSON
    """
    room_id = matchup_service.get_room_id(userid)
    if not room_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "User not matched"})

    data = matchup_service.get_game_data_for_user(userid)
    if data:
        return JSONResponse(content={"color": data.get("colors", [])})
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"error": "Color data not found"})
