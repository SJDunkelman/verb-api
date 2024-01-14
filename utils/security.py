from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from gotrue.errors import AuthApiError
from api.db import supabase_client
from api.dependencies import get_db
from gotrue.types import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(token: dict = Depends(oauth2_scheme), db=Depends(get_db)) -> User:
    try:
        user_response = db.auth.get_user(token)
    except AuthApiError:
        raise HTTPException(status_code=401, detail="User not found")
    return user_response.user


def get_user_from_token(token: str) -> User | bool:
    try:
        user_response = supabase_client.auth.get_user(token)
    except AuthApiError:
        return False
    return user_response.user
