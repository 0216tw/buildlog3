import re

from pydantic import BaseModel, field_validator


NICKNAME_PATTERN = re.compile(r"^[가-힣A-Za-z0-9_]+$")


def validate_email(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) > 254 or "@" not in normalized:
        raise ValueError("올바른 이메일 주소를 입력해 주세요.")
    local, domain = normalized.rsplit("@", 1)
    if not local or not domain or "." not in domain or " " in normalized:
        raise ValueError("올바른 이메일 주소를 입력해 주세요.")
    return normalized


def validate_nickname(value: str) -> str:
    normalized = value.strip()
    if not 2 <= len(normalized) <= 20 or not NICKNAME_PATTERN.fullmatch(normalized):
        raise ValueError("닉네임은 2~20자의 한글, 영문, 숫자, 밑줄만 사용할 수 있습니다.")
    return normalized


class RegisterRequest(BaseModel):
    email: str
    password: str
    nickname: str

    _email = field_validator("email")(validate_email)
    _nickname = field_validator("nickname")(validate_nickname)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not 8 <= len(value) <= 64:
            raise ValueError("비밀번호는 8~64자로 입력해 주세요.")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str

    _email = field_validator("email")(validate_email)


class NicknameUpdateRequest(BaseModel):
    nickname: str

    _nickname = field_validator("nickname")(validate_nickname)


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
