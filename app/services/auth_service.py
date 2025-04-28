from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.models.schemas import UserInDB, TokenData, User
from app.services.db_service import db

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash"""
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user by email and password"""
    user = await db.get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str) -> Optional[User]:
    """Get the current user from a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        return None
    
    user = await db.get_user_by_email(token_data.email)
    if user is None:
        return None
    
    return User(id=user.id, email=user.email, student_name=user.student_name)

async def register_user(email: str, password: str, student_name: str) -> Optional[User]:
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.get_user_by_email(email)
    if existing_user:
        return None
    
    # Create new user
    hashed_password = get_password_hash(password)
    user_data = {
        "email": email,
        "hashed_password": hashed_password,
        "student_name": student_name
    }
    
    user_id = await db.create_user(user_data)
    return User(id=user_id, email=email, student_name=student_name)
