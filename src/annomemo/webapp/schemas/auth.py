from pydantic import BaseModel, EmailStr, field_validator


class RegistrationForm(BaseModel):
    fullName: str
    email: EmailStr
    password: str = ...  # type: ignore
    confirmPassword: str

    @field_validator("password")
    @classmethod
    def pw_not_blank(cls, v, info):
        """validate that the password field is at least 8 chars long"""
        if v is None or len(v) < 8:
            raise ValueError("Passwords must be at least 8 characters long")

        return v

    @field_validator("confirmPassword")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v
