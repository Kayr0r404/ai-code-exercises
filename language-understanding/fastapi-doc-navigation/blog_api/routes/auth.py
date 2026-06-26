from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..models.schemas import UserRegister, UserPublic, Token
from ..auth.hashing import hash_password, verify_password
from ..auth.jwt import create_access_token
from ..auth.deps import users_db, users_by_username, next_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister):
    if body.username in users_by_username:
        raise HTTPException(status_code=409, detail="Username already taken")

    user_id = len(users_db) + 1
    user_record = {
        "id": user_id,
        "username": body.username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
    }
    users_db[user_id] = user_record
    users_by_username[body.username] = user_id
    return UserPublic(id=user_id, username=body.username, email=body.email)


@router.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    from ..auth.deps import get_user_by_username

    user = get_user_by_username(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(data={"sub": user["username"]})
    return Token(access_token=token)
