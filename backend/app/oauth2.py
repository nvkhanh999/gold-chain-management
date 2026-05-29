from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import database, models
from .config import settings
from .schemas import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def createAccessToken(data: dict):
    toEncode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)


def verifyAccessToken(token: str, credentialsException):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userID: str = payload.get("userID")
        if userID is None:
            raise credentialsException
        tokenData = TokenData(id=userID)
    except JWTError:
        raise credentialsException
    return tokenData


def getCurrentUser(token: str = Depends(oauth2_scheme), db: Session = Depends(database.getDatabase)):
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    tokenData = verifyAccessToken(token, credentialsException)
    user = db.query(models.User).filter(models.User.userID == tokenData.id, models.User.active == True).first()
    if user is None:
        raise credentialsException
    return user
