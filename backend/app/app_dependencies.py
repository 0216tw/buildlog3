import sqlite3

from fastapi import Cookie, Depends, HTTPException, status

from app.core.security import read_session_token
from app.db.sqlite import get_db

SESSION_COOKIE = "buildlog_session"


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    db: sqlite3.Connection = Depends(get_db),
) -> sqlite3.Row:
    user_id = read_session_token(session_token) if session_token else None
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    user = db.execute("SELECT id, email, nickname FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인이 필요합니다.")
    return user
