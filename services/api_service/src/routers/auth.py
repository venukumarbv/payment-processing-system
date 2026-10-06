from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.core.security import (create_access_token, decode_access_token,
                               verify_password)
from src.database import get_db
from src.repository.user_repo import UserRepository

# Initialize router
router = APIRouter()

# This tells FastAPI that the 'Authorize' button in Swagger UI
# should send the username/password to the /login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate the user and return the JWT token
    """

    # Initialize the User Repository with the current DB session
    user_repo = UserRepository(db)

    # Fetch user from database by username
    user = user_repo.get_user(form_data.username)

    # Verify if user exists and if password matches
    if not user or not verify_password(form_data.password, user.HashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = create_access_token(data={"sub": user.Username})

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency used to protect other endpoints.
    Validates the JWT and returns the username.
    """
    # Decode the token and verify signature/expiration
    username = decode_access_token(token)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return username
