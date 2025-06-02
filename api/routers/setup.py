import base64

from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse

from services.matchup_service import MatchupService
from services.user_service import UserService

router = APIRouter(prefix="/setup")
match_service = MatchupService.get_instance()
user_service = UserService()

@router.get("/users")
def get_room_users(room_id: str = Query(...)):
    try:
        user_ids = match_service.get_userid_by_roomid(room_id)
        if not user_ids:
            result = {
                "status": "failed",
                "message": "Not Found"
            }
            return JSONResponse(content=result, status_code=status.HTTP_404_NOT_FOUND) 
        
        users = []
        for user_id in user_ids:
            user = user_service.dao.get_by_userid(user_id)
            users.append([user.user_id, user.account_name])
        result = {
            "status": "success",
            "users": users
        }
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except Exception as e:
        result = {
            "status": "failed",
            "message": "Internal Server Error"
        }
        return JSONResponse(content=result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get("/game")
def get_room_image(room_id: str = Query(...)):
    try:
        image_path = match_service.get_image_path_by_roomid(room_id)
        color_list = match_service.get_color_list_by_roomid(room_id)

        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
        result = {
            "status": "success",
            "image_base64": encoded,
            "color_list": color_list
        }
        return JSONResponse(content=result, status_code=status.HTTP_200_OK)
    except Exception as e:
        result = {
            "status": "failed",
            "message": "Internal Server Error"
        }
        return JSONResponse(content=result, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)