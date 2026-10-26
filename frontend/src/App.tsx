import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

type ApiStatus = 'loading' | 'connected' | 'error'
type AuthMode = 'login' | 'register'

type User = {
  id: number
  email: string
  nickname: string
}

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function readError(response: Response): Promise<string> {
  const body = await response.json().catch(() => null)
  if (Array.isArray(body?.detail)) {
    return body.detail.map((item: { msg?: string }) => item.msg ?? '입력값을 확인해 주세요.').join(' ')
  }
  return body?.detail ?? '요청을 처리하지 못했습니다.'
}

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('loading')
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [user, setUser] = useState<User | null>(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [nickname, setNickname] = useState('')
  const [newNickname, setNewNickname] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const health = await fetch(`${apiUrl}/api/health`)
        if (!health.ok) throw new Error('health check failed')
        setApiStatus('connected')
      } catch {
        setApiStatus('error')
      }

      try {
        const response = await fetch(`${apiUrl}/api/auth/me`, { credentials: 'include' })
        if (response.ok) setUser(await response.json())
      } finally {
        setAuthChecked(true)
      }
    }

    void load()
  }, [])

  const submitAuth = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setMessage('')
    setIsSubmitting(true)
    const path = authMode === 'register' ? '/api/auth/register' : '/api/auth/login'
    const body = authMode === 'register' ? { email, password, nickname } : { email, password }

    try {
      const response = await fetch(`${apiUrl}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })
      if (!response.ok) throw new Error(await readError(response))
      const savedUser: User = await response.json()

      if (authMode === 'register') {
        setAuthMode('login')
        setNickname('')
        setPassword('')
        setMessage('가입이 완료되었습니다. 로그인해 주세요.')
      } else {
        setUser(savedUser)
        setPassword('')
        setMessage('로그인되었습니다.')
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '요청을 처리하지 못했습니다.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateNickname = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setMessage('')
    setIsSubmitting(true)
    try {
      const response = await fetch(`${apiUrl}/api/auth/me/nickname`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ nickname: newNickname }),
      })
      if (!response.ok) throw new Error(await readError(response))
      const savedUser: User = await response.json()
      setUser(savedUser)
      setNewNickname('')
      setMessage('닉네임이 변경되었습니다.')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : '요청을 처리하지 못했습니다.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="status-card" aria-labelledby="page-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="page-title">공부 기록을 시작해 보세요</h1>
        <p className="description">공부 내용과 오류 해결 과정을 한곳에 모읍니다.</p>

        <div className={`api-status api-status--${apiStatus}`} aria-live="polite">
          <span className="status-dot" aria-hidden="true" />
          {apiStatus === 'loading' && 'FastAPI 연결을 확인하고 있습니다.'}
          {apiStatus === 'connected' && 'FastAPI에 연결되었습니다.'}
          {apiStatus === 'error' && 'FastAPI 서버를 실행한 뒤 다시 확인해 주세요.'}
        </div>

        {authChecked && user ? (
          <section className="auth-panel" aria-labelledby="account-title">
            <p className="panel-label">로그인 상태</p>
            <h2 id="account-title">{user.nickname}님, 환영합니다.</h2>
            <p className="muted">{user.email}</p>
            <form className="form" onSubmit={updateNickname}>
              <label htmlFor="new-nickname">새 닉네임</label>
              <input
                id="new-nickname"
                value={newNickname}
                onChange={(event) => setNewNickname(event.target.value)}
                placeholder="2~20자의 닉네임"
                required
              />
              <button type="submit" disabled={isSubmitting}>닉네임 변경</button>
            </form>
          </section>
        ) : (
          <section className="auth-panel" aria-labelledby="auth-title">
            <div className="tabs" role="tablist" aria-label="계정 메뉴">
              <button
                type="button"
                className={authMode === 'login' ? 'tab active' : 'tab'}
                onClick={() => { setAuthMode('login'); setError(''); setMessage('') }}
              >로그인</button>
              <button
                type="button"
                className={authMode === 'register' ? 'tab active' : 'tab'}
                onClick={() => { setAuthMode('register'); setError(''); setMessage('') }}
              >회원가입</button>
            </div>
            <h2 id="auth-title">{authMode === 'login' ? '다시 만나서 반가워요' : '새 계정 만들기'}</h2>
            <form className="form" onSubmit={submitAuth}>
              <label htmlFor="email">이메일</label>
              <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
              <label htmlFor="password">비밀번호</label>
              <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} maxLength={64} required />
              {authMode === 'register' && (
                <>
                  <label htmlFor="nickname">닉네임</label>
                  <input id="nickname" value={nickname} onChange={(event) => setNickname(event.target.value)} minLength={2} maxLength={20} required />
                </>
              )}
              <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? '처리 중...' : authMode === 'login' ? '로그인' : '회원가입'}
              </button>
            </form>
          </section>
        )}

        {message && <p className="notice success" role="status">{message}</p>}
        {error && <p className="notice error" role="alert">{error}</p>}
      </section>
    </main>
  )
}

export default App
