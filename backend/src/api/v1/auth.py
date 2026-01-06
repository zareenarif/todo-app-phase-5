"""
Authentication endpoints - login and register.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from uuid import UUID, uuid4

from src.core.database import get_session
from src.core.config import settings
from src.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "user_id": str(user_id),
        "exp": expire
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt


@router.post("/register", response_model=AuthResponse)
async def register(
    data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register a new user.

    Creates a new user account and returns an access token.
    """
    # Check if user already exists
    statement = select(User).where(User.email == data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        id=uuid4(),
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login with email and password.

    Returns an access token for authenticated requests.
    """
    # Find user by email
    statement = select(User).where(User.email == data.email)
    user = session.exec(statement).first()

    if not user or not hasattr(user, 'password_hash'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate token
    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    )


@router.get("/me")
async def get_current_user(
    session: Session = Depends(get_session),
    user_id: str = Depends(lambda: "mock-user-id")  # TODO: Get from JWT
):
    """Get current user info."""
    statement = select(User).where(User.id == UUID(user_id))
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name
    }
