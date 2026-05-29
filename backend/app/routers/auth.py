from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas, utils


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(userCredentials: schemas.LoginRequest, db: Session = Depends(database.getDatabase)):
    user = db.query(models.User).filter(models.User.email == userCredentials.email, models.User.active == True).first()

    if not user or not utils.verifyPassword(userCredentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email hoặc mật khẩu không đúng",
        )

    accessToken = oauth2.createAccessToken(data={"userID": str(user.userID), "role": user.role})
    return {"access_token": accessToken, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def getMe(currentUser: models.User = Depends(oauth2.getCurrentUser)):
    return currentUser
