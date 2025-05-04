from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

class UserBrowse(BaseModel):
    username: str
    age: Optional[int] = Field(None, ge=18, le=100)
    city: Optional[str]
    avatar: Optional[str] 
    userid: str
    faceverified: bool
    last_active: Optional[str]
    is_new: bool = Field(False, alias='newmember')
    is_popular: bool = Field(False, alias='ispop')
    is_online: bool

class UserPlay(BaseModel):
    name: str
    photoid: Optional[str] = None
    uri: Optional[str] = None
    userid: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    city: Optional[str] = None
    headline:  Optional[str] = ""
    description:  Optional[str] = ""
    gender:  Optional[str] = "unknown"
    verified:  Optional[bool] = False


class UserMatch(BaseModel):
    id: Optional[str] = None
    premium: str
    avatar: Optional[str] = None
    username: str
    age: int = Field(..., ge=18, le=100)
    gender: str
    city: str
    text: str
    time: str # timestamp
    label: Optional[str] =None

class UserMessage(BaseModel):
    ago: str
    username: str
    id: str
    reaction: str
    text: str
    them: Optional[int] = None 
    datestring: Optional[str] = None

from datetime import date
from pydantic import BaseModel
from typing import Dict, Literal

class ProfileVisibility(BaseModel):
    maleformale: Literal["visible", "hidden"]
    maleforfemale: Literal["visible", "hidden"]
    femaleformale: Literal["visible", "hidden"]
    femaleforfemale: Literal["visible", "hidden"]
    ladyboy: Literal["visible", "hidden"]

class Photo(BaseModel):
    count: int
    Uri: str
    ID: int
    Size: int
    moderated: int
    order: int
    crate: int
    verified: int
    views: int
    likes: int

class UserProfile(BaseModel):
    countryoforigin: str
    premiummessages: str
    hideprofilenotlogged: str
    hideyouvisiting: str
    hidelastactive: int
    haschildren: int
    wantschildren: int
    weight: int
    height: int
    dateofbirth: date
    username: str
    profileimage: Optional[str] = None
    profilevisibility: Optional[ProfileVisibility] = None
    jointime: int
    headline: str
    description: str
    age: int
    gender: str
    lookingfor: str
    minage: int
    maxage: int
    country: str
    city: str
    area: int
    education: int
    englishability: str
    thaiability: str
    photos: Optional[Dict[str, Photo]] = None
    faceverified: int
    sa: Optional[str] = None
    sb: Optional[str] = None