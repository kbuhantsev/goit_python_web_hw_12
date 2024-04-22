from fastapi import APIRouter, Depends, HTTPException, status, Security
from src.database.models import User
from src.repository.auth import create_access_token, create_refresh_token, get_email_form_refresh_token, get_current_user, Hash
from src.schemas.schemas import UserSchema
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from src.database.db import get_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/auth', tags=["auth"])
hash_handler = Hash()
security = HTTPBearer()


@router.get("/")
async def root():
    return {"message": "root"}


@router.post("/signup")
async def signup(body: UserSchema, db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == body.email)
    res = await db.execute(query)
    exist_user = res.scalars().first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    new_user = User(
        name=body.username,
        email=body.email,
        password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"new_user": new_user.email}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    query = select(User).where(User.email == body.username)
    res = await db.execute(query)
    user = res.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    await db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: AsyncSession = Depends(get_session)):
    #
    token = credentials.credentials
    email = await get_email_form_refresh_token(token)
    query = select(User).where(User.email == email)
    res = await db.execute(query)
    user = res.scalars().first()
    if user.refresh_token != token:
        user.refresh_token = None
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"sub": email})
    refresh_token = await create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    await db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}
