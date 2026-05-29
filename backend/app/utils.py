from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashPassword(password: str):
    return pwd_context.hash(password)


def verifyPassword(plainPassword: str, hashedPassword: str):
    try:
        if pwd_context.verify(plainPassword, hashedPassword):
            return True
    except Exception:
        pass

    return plainPassword == hashedPassword
