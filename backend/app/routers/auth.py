from fastapi import APIRouter, HTTPException, Depends, status
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from datetime import timedelta

from ..models import UserRegister, UserLogin, UserResponse, Token
from ..database import db
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    # Prepare user document
    user_dict = {
        "username": user_in.username.strip(),
        "email": user_in.email.strip().lower(),
        "hashed_password": get_password_hash(user_in.password),
    }
    try:
        result = await db.users.insert_one(user_dict)
        inserted_id = str(result.inserted_id)
        return UserResponse(
            id=inserted_id,
            username=user_dict["username"],
            email=user_dict["email"]
        )
    except DuplicateKeyError as e:
        # Check which field was duplicate
        err_msg = str(e)
        if "username" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken."
            )
        elif "email" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists."
            )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    # Lookup user by username or email
    user = await db.users.find_one({
        "$or": [
            {"username": credentials.username.strip()},
            {"email": credentials.username.strip().lower()}
        ]
    })
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Create access token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"]
    )
