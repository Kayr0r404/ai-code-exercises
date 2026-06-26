"""FastAPI application demonstrating advanced code patterns.

Patterns demonstrated:
  - Generic Repository pattern (Repository[T])
  - Service layer (UserService)
  - Dependency injection chain (get_db → get_current_user → endpoints)
  - Role-based access control via decorator (requires_role)
  - Timing middleware
  - Lifespan event handler (startup/shutdown)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, Type, TypeVar, Generic, List, Any

import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Column, Integer, String, Boolean


# ── Database models ───────────────────────────────

class Base:
    pass


class User(Base):
    __tablename__ = "users"
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


T = TypeVar("T", bound=Base)


# ── Generic Repository pattern ────────────────────

class Repository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[T]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()


class UserRepository(Repository[User]):
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()


# ── Service layer ─────────────────────────────────

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        user = await self.repository.get_by_username(db, username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return True  # placeholder

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, "SECRET_KEY", algorithm="HS256")


# ── DI: DB session ────────────────────────────────

async def get_db() -> AsyncSession:
    async with AsyncSession() as session:
        try:
            yield session
        finally:
            await session.close()


# ── DI: Authentication chain ──────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo = UserRepository(User)
    user = await user_repo.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


# ── RBAC decorator ────────────────────────────────

def requires_role(role: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, current_user: User = Depends(get_current_user), **kwargs: Any) -> Any:
            if role == "admin" and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# ── Middleware ──────────────────────────────────────

class TimingMiddleware:
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = datetime.utcnow()
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        response.headers["X-Process-Time"] = str(process_time)
        return response


# ── Lifespan ──────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")


# ── App instance ─────────────────────────────────

app = FastAPI(lifespan=lifespan)
app.add_middleware(TimingMiddleware)


# ── Schemas ──────────────────────────────────────

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


# ── Endpoints ────────────────────────────────────

@app.post("/token")
async def login(
    username: str,
    password: str,
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(User)
    user_service = UserService(user_repo)
    user = await user_service.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = user_service.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/admin/users/", response_model=List[UserSchema])
@requires_role("admin")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_repo = UserRepository(User)
    users = await user_repo.list(db, skip=skip, limit=limit)
    return users
