from datetime import date, datetime
from typing import List, Optional, Annotated, Union
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    ConfigDict, 
    ValidationInfo,
    BeforeValidator
)
import re

# Type definitions
PyObjectId = Annotated[str, BeforeValidator(str)]

class City(BaseModel):
    name: str = Field("Unknown", description="City name from user profile")

class School(BaseModel):
    name: str = Field(..., description="School name from education history")

class Job(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None

class SwipeUser(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )

    user_id: str = Field(
        ...,
        alias="_id",
        pattern=r'^[a-f\d]{24}$',
        description="MongoDB ObjectID in hex format"
    )
    bio: str = Field("", description="User biography text")
    birth_date: Union[date, str] = Field(
        "No birth date found...",
        description="Either date object or placeholder string"
    )
    name: str = Field(..., min_length=1, description="Full name of user")
    city: City = Field(default_factory=City)
    schools: List[School] = Field([], description="Educational institutions")
    # jobs: List[Job] = Field([], description="Job positions")
    photos: List[str] = Field([], description="List of photo URLs")
    gender: int = Field(..., ge=0, le=2, description="0=Male, 1=Female, 2=Other")
    recently_active: bool = Field(..., description="Activity status")
    distance: float = Field(..., ge=0, description="Distance in miles")
    interests: List[str] = Field([], description="Selected interests")

    @field_validator("gender", mode="before")
    @classmethod
    def clamp_gender_values(cls, v: int) -> int:
        """Ensure gender stays within valid range 0-2"""
        if v < 0:
            return 0  # Treat negative values as Male
        elif v > 2:
            return 2  # Treat values >2 as Other
        return v

    @field_validator("interests", mode="before")
    @classmethod
    def extract_interest_names(
        cls, 
        v: List[Union[str, dict]], 
        info: ValidationInfo
    ) -> List[str]:
        """Extract interest names from API response format"""
        processed = []
        for item in v:
            if isinstance(item, dict):
                # Get name while preserving empty string fallback
                name = item.get("name", "").strip()
                if name:
                    processed.append(name)
            elif isinstance(item, str):
                processed.append(item)
        return processed
   
    @field_validator("user_id", mode="before")
    @classmethod
    def convert_objectid(cls, v: object) -> str:
        """Handle various ObjectID formats"""
        if isinstance(v, bytes):
            return v.hex()
        return str(v)

    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birthdate(cls, v: object) -> Union[date, str]:
        """Convert string dates to date objects"""
        if isinstance(v, str) and v != "No birth date found...":
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                pass
        return v

    @field_validator("city", mode="before")
    @classmethod
    def normalize_city(cls, v: object) -> dict:
        """Handle different city input formats"""
        if isinstance(v, dict):
            return v
        return {"name": v} if isinstance(v, str) else {"name": "Unknown"}

    @field_validator("photos", mode="before")
    @classmethod
    def validate_photos(cls, v: object) -> list:
        """Ensure photos are list of URLs"""
        if not isinstance(v, list):
            raise ValueError("Photos must be a list")
        for url in v:
            if not url.startswith(("http://", "https://")):
                raise ValueError("Invalid photo URL format")
        return v
    
from datetime import datetime
from typing import List, Optional, Union
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    ConfigDict, 
    AliasPath
)

# --------------------------
# Core Data Models
# --------------------------

class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    message_id: str = Field(..., alias="_id")
    sent_date: datetime
    message: str
    from_user: str = Field(..., alias="from")
    to_user: str = Field(..., alias="to")
    match_id: str
    created_at: datetime = Field(..., alias="created_date")

class Person(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    user_id: str = Field(..., alias="_id")
    bio: str = "No bio found..."
    birth_date: Union[datetime, str] = "No birth date found..."
    name: str
    gender: str
    last_active: datetime
    images: List[str] = Field(default_factory=list)
    
    @field_validator("gender", mode="before")
    @classmethod
    def convert_gender(cls, v: int) -> str:
        return "female" if v == 1 else "male"

class Match(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    match_id: str = Field(..., alias="_id")
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(..., alias="created_date")
    user: Person = Field(..., validation_alias=AliasPath("person"))
    distance: Optional[float] = None
    is_super_like: bool = Field(False, alias="is_super_match")

# --------------------------
# Response Models
# --------------------------

class MessageResponse(BaseModel):
    sent_date: datetime
    message_id: str = Field(..., alias="_id")
    match_id: str
    temp_message_id: str
    status: str

class PaginatedMatches(BaseModel):
    matches: List[Match]
    next_page_token: Optional[str] = None

# --------------------------
# Request Models
# --------------------------

class MessageRequest(BaseModel):
    match_id: str
    message: str
    contact_type: Optional[str] = None
    temp_message_id: str
    user_id: str
    other_id: str

# --------------------------
# Validation Utilities
# --------------------------

class MatchValidator:
    @staticmethod
    def validate_match_response(data: dict) -> Match:
        return Match.model_validate(data, from_attributes=True)

    @staticmethod
    def validate_message_response(data: dict) -> MessageResponse:
        return MessageResponse.model_validate(data, from_attributes=True)
    
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator

class LikeRequest(BaseModel):
    """Payload schema for like/superlike requests"""
    s_number: int = Field(..., ge=447198460, le=1147198460)
    user_traveling: Literal[1] = 1  # Fixed value from Tinder's API

class SuperLikeStatus(BaseModel):
    remaining: int
    alc_remaining: int
    new_alc_remaining: int
    allotment: int
    superlike_refresh_amount: int
    superlike_refresh_interval: int
    refresh_interval: int
    resets_at: Optional[str] = None

class LikeResponse(BaseModel):
    """Validated response schema for like/superlike operations"""
    status: int
    match: bool
    user_id: str
    likes_left: Optional[int] = None
    super_likes_left: Optional[int] = None
    rate_limited_until: Optional[float] = None
    superlike_status: Optional[SuperLikeStatus] = None

    @model_validator(mode="before")
    @classmethod
    def extract_remaining_counts(cls, data: dict) -> dict:
        """Extract nested superlike counts from Tinder's response format"""
        if isinstance(data, dict):
            # Handle super like remaining count
            if "super_likes" in data:
                data["superlike_status"] = data.pop("super_likes", {})
                data["super_likes_left"] = data["superlike_status"].get("remaining", 0)
            
            # Handle normal like remaining count
            data["likes_left"] = data.pop("likes_remaining", None)
            
            # Extract rate limit information if present
            if "rate_limited_until" in data.get("meta", {}):
                data["rate_limited_until"] = data["meta"]["rate_limited_until"]
        
        return data

    class Config:
        extra = "ignore"  # Ignore other fields from Tinder's response