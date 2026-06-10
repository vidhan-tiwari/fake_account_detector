from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

# --- Auth Models ---

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Scan Models ---

class ManualScanRequest(BaseModel):
    username: str
    fullname: str
    bio_input: str  # Can be text (e.g. "I love travel") or a numeric string (e.g. "150")
    posts: int = Field(default=0, ge=0)
    followers: int = Field(default=0, ge=0)
    follows: int = Field(default=0, ge=0)
    has_pic: bool = True
    is_private: bool = False
    has_url: bool = False
    is_verified: bool = False

class AutoScanRequest(BaseModel):
    username: str

class ScanResponse(BaseModel):
    username: str
    is_fake: bool
    probability: float
    is_verified: bool
    features: Dict[str, Any]

# --- History Models ---

class HistoryResponse(BaseModel):
    id: str
    username: str
    type: str  # "auto" or "manual"
    is_fake: bool
    probability: float
    is_verified: bool
    scanned_at: datetime
    features: Dict[str, Any]
