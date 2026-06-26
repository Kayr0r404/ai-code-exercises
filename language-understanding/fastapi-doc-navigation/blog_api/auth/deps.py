from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .jwt import decode_access_token
from ..models.schemas import UserPublic

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Shared in-memory store (imported by routes as well)
users_db: dict[int, dict] = {}
users_by_username: dict[str, int] = {}
next_user_id = 1


def get_user_by_username(username: str):
    uid = users_by_username.get(username)
    return users_db.get(uid) if uid else None


def get_user_by_id(uid: int):
    return users_db.get(uid)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return UserPublic(id=user["id"], username=user["username"], email=user["email"])
