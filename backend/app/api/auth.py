from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.db.deps import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, RegisterResponse, AuthResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    if payload.phone:
        existing_phone = db.execute(
            select(User).where(User.phone == payload.phone)
        ).scalar_one_or_none()
        if existing_phone:
            raise HTTPException(status_code=400, detail="手机号已存在")

    user = User(
        username=payload.username,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "register success",
        "user": user,
    }

@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(
            or_(
                User.username == payload.identifier,
                User.phone == payload.identifier,
            )
        )
    ).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/手机号或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
