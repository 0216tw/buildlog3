import { useEffect, useState } from 'react'
import './App.css'

type ApiStatus = 'loading' | 'connected' | 'error'

function App() {
  const [apiStatus, setApiStatus] = useState<ApiStatus>('loading')

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

    fetch(`${apiUrl}/api/health`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('API health check failed')
        }

        return response.json()
      })
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('error'))
  }, [])

  return (
    <main className="app-shell">
      <section className="status-card" aria-labelledby="page-title">
        <p className="eyebrow">BUILDLOG</p>
        <h1 id="page-title">개발 환경이 준비되었습니다</h1>
        <p className="description">
          공부 기록을 한곳에 모으는 첫 번째 실행 화면입니다.
        </p>
        <div className={`api-status api-status--${apiStatus}`} aria-live="polite">
          <span className="status-dot" aria-hidden="true" />
          {apiStatus === 'loading' && 'FastAPI 연결을 확인하고 있습니다.'}
          {apiStatus === 'connected' && 'React와 FastAPI가 정상적으로 연결되었습니다.'}
          {apiStatus === 'error' && 'FastAPI 서버를 실행한 뒤 다시 확인해 주세요.'}
        </div>
      </section>
    </main>
  )
}

export default App
