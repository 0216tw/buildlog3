# BuildLog 개발 환경

## 1. 현재 확인된 환경

Phase 0에서 읽기 전용 명령으로 확인한 결과입니다.

| 항목 | 확인 결과 |
| --- | --- |
| 운영체제 셸 | Windows PowerShell |
| Python | 3.13.14 |
| pip | 26.1.2 |
| Python 가상환경 모듈 | 사용 가능 |
| SQLite | 3.50.4 |
| Node.js | 24.22.1 |
| npm | 11.19.1 |

PowerShell 실행 정책 때문에 `npm.ps1` 실행은 차단됩니다. npm 자체는 정상 설치되어 있으므로 현재 환경에서는 다음처럼 `npm.cmd`를 사용합니다.

```powershell
npm.cmd --version
```

실행 정책을 변경할 필요는 없습니다.

## 2. 확정한 실행 구성

- 프론트엔드: React + TypeScript
- 백엔드: Python + FastAPI
- 실제 서비스 DB: Supabase PostgreSQL
- 자동 테스트 DB: SQLite3
- DB 연결: SQLAlchemy
- DB 변경 관리: Alembic

## 3. 환경 변수

실제 값은 프로젝트 루트의 `.env`에 저장하고 Git에 기록하지 않습니다. `.env.example`에는 다음 항목 이름과 비밀이 아닌 예시만 기록합니다.

```dotenv
DATABASE_URL=
TEST_DATABASE_URL=sqlite+pysqlite:///:memory:
AUTH_SECRET_KEY=
FRONTEND_URL=http://localhost:5173
VITE_API_URL=http://localhost:8000
```

`DATABASE_URL`과 `AUTH_SECRET_KEY`의 실제 값은 공개 문서나 React 코드에 넣지 않습니다.

## 4. 현재 로컬 DB와 Supabase 준비 시점

현재 Phase 2와 Phase 3은 Supabase 대신 로컬 SQLite3로 진행했습니다. 프로젝트를 실행하면 `database/buildlog.sqlite3`가 만들어지며, 이 파일은 Git에서 제외됩니다.

Supabase 프로젝트는 아직 필요하지 않습니다. 이후 수업을 마치고 DB 전환을 시작할 때 다음 항목을 준비합니다.

1. Supabase에서 BuildLog용 프로젝트를 만듭니다.
2. 데이터베이스 비밀번호를 안전한 곳에 보관합니다.
3. PostgreSQL 연결 주소를 확인합니다.
4. 연결 주소를 로컬 `.env`의 `DATABASE_URL`에 입력합니다.

연결 주소와 비밀번호는 채팅이나 Git에 올리지 않습니다.

## 5. 백엔드 설치와 실행

프로젝트 루트에서 처음 한 번 실행합니다.

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
```

FastAPI 개발 서버를 실행합니다.

```powershell
Set-Location backend
./.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

서버가 실행되면 다음 주소에서 상태를 확인할 수 있습니다.

```text
http://localhost:8000/api/health
```

백엔드 자동 테스트는 다음과 같이 실행합니다.

```powershell
Set-Location backend
./.venv/Scripts/python.exe -m pytest
```

## 6. 프론트엔드 설치와 실행

처음 한 번 패키지를 설치합니다. 현재 PowerShell 환경에서는 `npm` 대신 `npm.cmd`를 사용합니다.

```powershell
Set-Location frontend
npm.cmd install
```

React 개발 서버를 실행합니다.

```powershell
Set-Location frontend
npm.cmd run dev
```

브라우저에서 다음 주소를 엽니다.

```text
http://localhost:5173
```

프론트엔드 검사와 빌드는 다음과 같이 실행합니다.

```powershell
Set-Location frontend
npm.cmd run lint
npm.cmd run build
```

React 화면에서 FastAPI 연결 성공 안내를 보려면 두 개발 서버를 서로 다른 터미널에서 함께 실행합니다.

## 7. 현재 진행 상태

완료한 작업:

- SQLite3 사용자 테이블과 연결
- 회원가입·로그인·로그인 상태 확인
- 닉네임 변경
- SQLite3 자동 테스트

아직 진행하지 않은 작업:

- SQLAlchemy와 Alembic 전환
- Supabase 프로젝트와 실제 DB 연결
- Supabase PostgreSQL용 마이그레이션
