from pydantic import BaseModel

class OtpConfirm(BaseModel):
    code: str

class AuthBase(BaseModel):
    is_auth: bool = False
    otp_requested: bool = False

class UpdateOTP(BaseModel):
    otp_requested: bool = False

class UpdateAuth(BaseModel):
    is_auth: bool = False

class AuthCancel(AuthBase):
    pass