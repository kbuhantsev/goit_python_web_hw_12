from fastapi import APIRouter, Depends, HTTPException, status, Security
from src.database.models import User
from src.repository.users import get_user_by_email, create_user, update_token
from src.schemas.schemas import UserSchema
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.database.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=["auth"])
get_refresh_token = HTTPBearer()


@router.get("/")
async def root():
    return {"message": "root"}


@router.post("/signup")
async def signup(body: UserSchema, db: AsyncSession = Depends(get_session)):
    #
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    #
    new_user = await create_user(body, db)
    return {"new_user": new_user.email}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    #
    user = await get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await update_token(user, refresh_token, db)
    #
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
        db: AsyncSession = Depends(get_session)):
    #
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await get_user_by_email(email, db)
    if user.refresh_token != token:
        user.refresh_token = None
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await update_token(user, refresh_token, db)
    #
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/secret")
async def read_item(current_user: User = Depends(auth_service.get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}
