import { useState, useRef } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [screen, setScreen] = useState('role-select')
  const [candidateName, setCandidateName] = useState('')
  const [role, setRole] = useState('software_engineer')
  const [difficulty, setDifficulty] = useState('entry')
  const [background, setBackground] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [currentType, setCurrentType] = useState('')
  const [questionNum, setQuestionNum] = useState(1)
  const [totalQuestions, setTotalQuestions] = useState(4)
  const [answer, setAnswer] = useState('')
  const [lastFeedback, setLastFeedback] = useState(null)
  const [scoreHistory, setScoreHistory] = useState([])
  const [finalResult, setFinalResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [agentStatus, setAgentStatus] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')  // '', 'success', 'error'
  const [uploadMessage, setUploadMessage] = useState('')
  const fileInputRef = useRef(null)

  const uploadResume = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadStatus('error')
      setUploadMessage('Please upload a PDF file only.')
      return
    }
    setIsUploading(true)
    setUploadStatus('')
    setUploadMessage('')
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post(`${API_BASE}/upload-resume`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setBackground(res.data.text)
      setUploadStatus('success')
      setUploadMessage(`✓ Resume parsed successfully! Text extracted and filled below.`)
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to parse the PDF. Please paste your background manually.'
      setUploadStatus('error')
      setUploadMessage(detail)
    } finally {
      setIsUploading(false)
      // reset the input so the same file can be re-uploaded if needed
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const startInterview = async () => {
    setLoading(true)
    setAgentStatus(background.trim() ? 'Tailoring a question to your background...' : 'Preparing your questions...')

    const res = await axios.post(`${API_BASE}/start-interview`, {
      candidate_name: candidateName,
      role: role,
      difficulty: difficulty,
      background: background
    })

    setSessionId(res.data.session_id)
    setCurrentQuestion(res.data.first_question)
    setCurrentType(res.data.first_question_type)
    setTotalQuestions(res.data.total_questions)
    setScreen('interview')
    setAgentStatus('')
    setLoading(false)
  }

  const submitAnswer = async () => {
    setLoading(true)
    setAgentStatus('Interviewer reviewing your answer...')

    await new Promise((r) => setTimeout(r, 500))
    setAgentStatus('Evaluator scoring your response...')

    const res = await axios.post(`${API_BASE}/submit-answer`, {
      session_id: sessionId,
      answer: answer
    })

    setAgentStatus('Preparing follow-up...')
    await new Promise((r) => setTimeout(r, 400))

    setLastFeedback({
      evaluation: res.data.evaluation,
      followup: res.data.followup,
      score: res.data.score
    })
    setScoreHistory((prev) => [...prev, res.data.score])
    setAnswer('')
    setAgentStatus('')

    if (res.data.is_last_question) {
      setAgentStatus('Coach compiling your session feedback...')
      const endRes = await axios.post(`${API_BASE}/end-session/${sessionId}`)
      setFinalResult(endRes.data)
      setAgentStatus('')
      setScreen('summary')
    } else {
      setCurrentQuestion(res.data.next_question)
      setCurrentType(res.data.next_question_type)
      setQuestionNum((n) => n + 1)
    }
    setLoading(false)
  }

  const downloadReport = () => {
    let content = `Interview prep coach — session report\n`
    content += `Candidate: ${finalResult.candidate_name}\n`
    content += `Role: ${finalResult.role}\n`
    content += `Average score: ${finalResult.average_score}/10\n`
    content += `\n${'='.repeat(50)}\n\n`

    finalResult.full_results.forEach((r, i) => {
      content += `Q${i + 1}: ${r.question}\n`
      content += `Answer: ${r.answer}\n`
      content += `${r.evaluation}\n`
      content += `Follow-up: ${r.followup}\n\n`
    })

    content += `${'='.repeat(50)}\n\nCoach feedback:\n${finalResult.final_feedback}\n\n`
    content += `Progress: ${finalResult.progress}\n`

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${finalResult.candidate_name}_interview_report.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      {screen === 'role-select' && (
        <div className="screen">
          <h1>Interview prep coach</h1>
          <p className="subtitle">Practice with an AI interviewer, evaluator, and coach</p>

          <input
            placeholder="Your name"
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
          />

          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="software_engineer">Software engineer</option>
            <option value="data_analyst">Data analyst</option>
            <option value="product_manager">Product manager</option>
            <option value="marketing">Marketing</option>
            <option value="hr_recruiter">HR / recruiter</option>
          </select>

          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="entry">Entry-level</option>
            <option value="experienced">Experienced</option>
          </select>

          <textarea
            placeholder="Optional: paste a short background about your experience for a tailored question, or upload your PDF resume below."
            value={background}
            onChange={(e) => setBackground(e.target.value)}
            rows={3}
          />

          <div className="upload-resume-section">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={uploadResume}
              style={{ display: 'none' }}
              id="resume-upload-input"
            />
            <button
              type="button"
              className="upload-btn"
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              disabled={isUploading || loading}
            >
              {isUploading ? '⏳ Parsing PDF...' : '📄 Upload PDF Resume'}
            </button>
            {uploadMessage && (
              <p className={`upload-message upload-message--${uploadStatus}`}>
                {uploadMessage}
              </p>
            )}
          </div>

          <button onClick={startInterview} disabled={!candidateName || loading}>
            {loading ? 'Starting...' : 'Start mock interview'}
          </button>
        </div>
      )}

      {screen === 'interview' && (
        <div className="screen">
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{ width: `${(questionNum / totalQuestions) * 100}%` }}
            />
          </div>

          {scoreHistory.length > 0 && (
            <div className="score-history">
              {scoreHistory.map((s, i) => (
                <div key={i} className="score-dot" title={`Q${i + 1}: ${s}/10`}>
                  {s !== null ? s : '—'}
                </div>
              ))}
            </div>
          )}

          <div className="question-card">
            <div className="question-label-row">
              <p className="question-label">Question {questionNum} of {totalQuestions}</p>
              <span className={`type-badge type-${currentType}`}>{currentType}</span>
            </div>
            <p className="question">{currentQuestion}</p>
          </div>

          {agentStatus && (
            <div className="agent-trace">
              <div className="agent-dot"></div>
              <span><strong>Agent active:</strong> {agentStatus}</span>
            </div>
          )}

          <textarea
            placeholder="Type your answer here."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={5}
          />
          <button onClick={submitAnswer} disabled={!answer || loading}>
            {loading ? 'Evaluating...' : 'Submit answer'}
          </button>

          {lastFeedback && (
            <div className="feedback-box">
              <div className="feedback-label-row">
                <p className="feedback-label">Previous evaluation</p>
                {lastFeedback.score !== null && (
                  <span className="score-pill">{lastFeedback.score}/10</span>
                )}
              </div>
              <p className="feedback-text">{lastFeedback.evaluation}</p>
              <p className="feedback-label">Follow-up</p>
              <p className="feedback-text" style={{ marginBottom: 0 }}>{lastFeedback.followup}</p>
            </div>
          )}
        </div>
      )}

      {screen === 'summary' && finalResult && (
        <div className="screen">
          <h1>Session complete</h1>
          <div style={{ textAlign: 'center' }}>
            <div className="score-badge">
              <span className="num">{finalResult.average_score}</span>
              <span className="denom">/10 average</span>
            </div>
          </div>

          <div className="score-history" style={{ justifyContent: 'center', marginBottom: '1.5rem' }}>
            {finalResult.full_results.map((r, i) => (
              <div key={i} className="score-dot" title={`Q${i + 1}`}>
                {r.score !== null ? r.score : '—'}
              </div>
            ))}
          </div>

          <div className="summary-block">
            <p className="feedback-label" style={{ marginBottom: 8 }}>Coach feedback</p>
            <p>{finalResult.final_feedback}</p>
          </div>

          <div className="summary-block">
            <p className="feedback-label" style={{ marginBottom: 8 }}>Progress</p>
            <p>{finalResult.progress}</p>
          </div>

          <button onClick={downloadReport} style={{ marginBottom: 10 }}>
            Download session report
          </button>
          <button onClick={() => window.location.reload()}>Start new session</button>
        </div>
      )}
    </div>
  )
}

export default App