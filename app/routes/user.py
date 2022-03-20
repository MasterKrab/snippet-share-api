from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.bcrypt import hash, verify
from app.oauth2 import create_access_token
from app.oauth2 import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=schemas.Token,
)
def login(
        user_credentials: schemas.UserCreate,
        db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.username == user_credentials.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = models.User(
        username=user_credentials.username,
        hash=hash(user_credentials.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user", response_model=schemas.UserOutput)
def get_user(
        current_user=Depends(get_current_user),
):
    return current_user


@router.put("/user", response_model=schemas.UserOutput)
def update_user(
        user_update: schemas.UserUpdate,
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if user_update.username and user_update.username != user.username:
        user_with_username = db.query(models.User).filter(
            models.User.username == user_update.username
        ).first()

        if user_with_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        user.username = user_update.username

    if user_update.password:
        if not verify(user_update.old_password, user.hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password",
            )

        user.hash = hash(user_update.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
):
    db.delete(user)
    db.commit()
