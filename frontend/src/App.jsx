import React, { useState } from 'react'

function App() {
  const [url, setUrl] = useState("")
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")

  const handleAnalyze = async () => {
    setError("")
    setResult(null)

    if (!url && !text) {
      setError("Paste a URL or terms text first")
      return
    }

    try {
      setLoading(true)

      const formData = new FormData()

      if (url.trim()) {
        formData.append("source_type", "url")
        formData.append("url", url)
      } else {
        formData.append("source_type", "text")
        formData.append("text", text)
      }

       const response = await fetch(
            "https://term-shield-production.up.railway.app/api/analysis/analyze",
        {
          method: "POST",
          body: formData
        }
      )

      const data = await response.json()

      setResult(data)
    } catch (err) {
      console.error(err)
      setError("AI analysis failed")
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'Safe':
        return '#16a34a'
      case 'Medium':
        return '#f59e0b'
      case 'High':
        return '#ef4444'
      default:
        return '#3b82f6'
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0f172a',
        color: 'white',
        fontFamily: 'Arial',
        padding: '40px'
      }}
    >
      <div
        style={{
          maxWidth: '1100px',
          margin: '0 auto'
        }}
      >
        <div
          style={{
            textAlign: 'center',
            marginBottom: '40px'
          }}
        >
          <h1
            style={{
              fontSize: '42px',
              marginBottom: '10px'
            }}
          >
            🛡️ TermShield AI
          </h1>

          <p
            style={{
              color: '#94a3b8',
              fontSize: '18px'
            }}
          >
            Understand Terms & Conditions in simple language
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '30px'
          }}
        >
          {/* LEFT PANEL */}
          <div
            style={{
              background: '#1e293b',
              padding: '30px',
              borderRadius: '20px'
            }}
          >
            <h2>Analyze Terms</h2>

            <div style={{ marginTop: '20px' }}>
              <label style={{ color: '#cbd5e1' }}>
                Website URL
              </label>

              <input
                type="text"
                placeholder="https://example.com/privacy"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                style={{
                  width: '100%',
                  marginTop: '10px',
                  padding: '14px',
                  borderRadius: '10px',
                  border: 'none',
                  outline: 'none',
                  background: '#0f172a',
                  color: 'white'
                }}
              />
            </div>

            <div style={{ marginTop: '25px' }}>
              <label style={{ color: '#cbd5e1' }}>
                Paste Terms Text
              </label>

              <textarea
                rows="12"
                placeholder="Paste Terms & Conditions here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                style={{
                  width: '100%',
                  marginTop: '10px',
                  padding: '14px',
                  borderRadius: '10px',
                  border: 'none',
                  outline: 'none',
                  resize: 'none',
                  background: '#0f172a',
                  color: 'white'
                }}
              />
            </div>

            {error && (
              <div
                style={{
                  marginTop: '20px',
                  background: '#7f1d1d',
                  padding: '12px',
                  borderRadius: '10px'
                }}
              >
                {error}
              </div>
            )}

            <button
              onClick={handleAnalyze}
              style={{
                width: '100%',
                marginTop: '25px',
                padding: '16px',
                border: 'none',
                borderRadius: '12px',
                background: '#2563eb',
                color: 'white',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              {loading ? 'Analyzing...' : 'Analyze with AI'}
            </button>
          </div>

          {/* RIGHT PANEL */}
          <div
            style={{
              background: '#1e293b',
              padding: '30px',
              borderRadius: '20px',
              overflowY: 'auto'
            }}
          >
            {!result && (
              <div
                style={{
                  textAlign: 'center',
                  marginTop: '120px',
                  color: '#64748b'
                }}
              >
                <h2>AI Analysis Result</h2>
                <p>Your analysis will appear here</p>
              </div>
            )}

            {result && (
              <div>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <h2>Analysis Report</h2>

                  <div
                    style={{
                      background: getRiskColor(result.risk_level),
                      padding: '10px 16px',
                      borderRadius: '999px',
                      fontWeight: 'bold'
                    }}
                  >
                    {result.risk_level}
                  </div>
                </div>

                <div
                  style={{
                    marginTop: '25px',
                    background: '#0f172a',
                    padding: '20px',
                    borderRadius: '14px'
                  }}
                >
                  <h3>📌 Quick Summary</h3>

                  <p
                    style={{
                      color: '#cbd5e1',
                      lineHeight: '1.7'
                    }}
                  >
                    {result.summary}
                  </p>
                </div>

                <div
                  style={{
                    marginTop: '20px',
                    background: '#0f172a',
                    padding: '20px',
                    borderRadius: '14px'
                  }}
                >
                  <h3>🧒 Explain Like I'm 15</h3>

                  <p
                    style={{
                      color: '#cbd5e1',
                      lineHeight: '1.7'
                    }}
                  >
                    {result.eli15}
                  </p>
                </div>

                <div
                  style={{
                    marginTop: '20px',
                    background: '#0f172a',
                    padding: '20px',
                    borderRadius: '14px'
                  }}
                >
                  <h3>⚠️ Risks Found</h3>

                  {result.risks && result.risks.length > 0 ? (
                    <ul>
                      {result.risks.map((risk, index) => (
                        <li
                          key={index}
                          style={{
                            marginBottom: '10px',
                            color: '#fca5a5'
                          }}
                        >
                          {risk}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div
                      style={{
                        background: '#052e16',
                        padding: '14px',
                        borderRadius: '10px',
                        color: '#86efac'
                      }}
                    >
                      No dangerous clauses detected.
                    </div>
                  )}
                </div>

                <div
                  style={{
                    marginTop: '20px',
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '15px'
                  }}
                >
                  <div
                    style={{
                      background: '#0f172a',
                      padding: '20px',
                      borderRadius: '14px'
                    }}
                  >
                    <h4>Risk Score</h4>
                    <h1>{result.risk_score}/100</h1>
                  </div>

                  <div
                    style={{
                      background: '#0f172a',
                      padding: '20px',
                      borderRadius: '14px'
                    }}
                  >
                    <h4>Source Type</h4>
                    <h2>{result.source_type}</h2>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
