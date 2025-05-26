from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models.requests import RegisterRequest, LoginRequest
from services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.post(
    "/auth/register", 
    status_code=201, 
    responses={
        400: {"description": "Bad Request (e.g. duplicate account)"}
    })
def register_user(req: RegisterRequest):
    result = user_service.register(req.account_name, req.password)

    if result["status"] != "success":
        return JSONResponse(content=result, status_code=status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(content=result, status_code=status.HTTP_201_CREATED)

@router.post(
    "/auth/login",
    status_code=200,
    responses={
        401: {"description": "Account name not existed or wrong password"}
    })
def login(req: LoginRequest):
    result = user_service.login(req.account_name, req.password)

    if result["status"] != "success":
        return JSONResponse(content=result, status_code=status.HTTP_401_UNAUTHORIZED)
    
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)