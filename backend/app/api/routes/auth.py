import sqlite3

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.app_dependencies import get_current_user
from app.core.security import create_session_token, hash_password, verify_password
from app.db.sqlite import get_db
from app.schemas.auth import LoginRequest, NicknameUpdateRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "buildlog_session"


def public_user(row: sqlite3.Row) -> UserResponse:
    return UserResponse(id=row["id"], email=row["email"], nickname=row["nickname"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: sqlite3.Connection = Depends(get_db)) -> UserResponse:
    try:
        cursor = db.execute(
            "INSERT INTO users (email, password_hash, nickname) VALUES (?, ?, ?)",
            (payload.email, hash_password(payload.password), payload.nickname),
        )
        db.commit()
    except sqlite3.IntegrityError as error:
        db.rollback()
        message = "이미 사용 중인 이메일 또는 닉네임입니다."
        raise HTTPException(status_code=409, detail=message) from error

    row = db.execute("SELECT id, email, nickname FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return public_user(row)


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: sqlite3.Connection = Depends(get_db)) -> UserResponse:
    row = db.execute(
        "SELECT id, email, password_hash, nickname FROM users WHERE email = ?",
        (payload.email,),
    ).fetchone()
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(row["id"]),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )
    return public_user(row)


@router.get("/me", response_model=UserResponse)
def me(user: sqlite3.Row = Depends(get_current_user)) -> UserResponse:
    return public_user(user)


@router.patch("/me/nickname", response_model=UserResponse)
def update_nickname(
    payload: NicknameUpdateRequest,
    user: sqlite3.Row = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> UserResponse:
    try:
        db.execute(
            "UPDATE users SET nickname = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (payload.nickname, user["id"]),
        )
        db.commit()
    except sqlite3.IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 사용 중인 닉네임입니다.") from error

    row = db.execute("SELECT id, email, nickname FROM users WHERE id = ?", (user["id"],)).fetchone()
    return public_user(row)
