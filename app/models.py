from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class EmailRequest(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=50)
    company: str = Field(..., min_length=1, max_length=200)
    message: Optional[str] = Field(None, max_length=500)

    @field_validator('fullname', 'phone', 'company', 'message')
    @classmethod
    def sanitize_text(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.replace('\r', '').replace('\n', ' ').replace('\x00', '').strip()
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: EmailStr) -> EmailStr:
        email_str = str(v)
        if '\r' in email_str or '\n' in email_str or '\x00' in email_str:
            raise ValueError('Invalid email format')
        return v


class EmailResponse(BaseModel):
    success: bool
    message: str
