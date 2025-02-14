from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from passlib.context import CryptContext
from functools import wraps

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Search in all collections
    user = await db["admins"].find_one({"email": email}) or \
           await db["consumers"].find_one({"email": email}) or \
           await db["workers"].find_one({"email": email})

    if not user:
        raise credentials_exception

    return user



def role_required(allowed_roles: list):
    """
    Decorator to enforce role-based access control.
    :param allowed_roles: List of allowed roles ('admin', 'consumer', 'worker').
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
            # Infer role from collection name
            if "total_points" in current_user:
                role = "consumer"
            elif "profile_image" in current_user:
                role = "worker" if "workers" in current_user else "admin"
            else:
                raise HTTPException(status_code=500, detail="Role could not be determined")

            if role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Access forbidden: insufficient permissions")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str):
    user = await db["admins"].find_one({"email": email}) or \
           await db["consumers"].find_one({"email": email}) or \
           await db["workers"].find_one({"email": email})

    if not user or not verify_password(password, user["password"]):
        return None
    return user


