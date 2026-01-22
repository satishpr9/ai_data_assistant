import { useState, useEffect, useRef } from 'react';
import { sendQuery, uploadPDF, ingestBusinessData, testConnection } from './api';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [uploadProgress, setUploadProgress] = useState('');
  const [ingestProgress, setIngestProgress] = useState('');
  const [apiStatus, setApiStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [responses, loading]);

  // Check API connection on mount
  useEffect(() => {
    const checkAPI = async () => {
      console.log('🔗 Checking API connection...');
      const result = await testConnection();
      if (result.success) {
        setApiStatus('connected');
        console.log('✅ API is connected');
      } else {
        setApiStatus('disconnected');
        console.error('❌ API is not reachable:', result.error);
      }
    };
    
    checkAPI();
  }, []);

  // Handle Query Submission
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (apiStatus === 'disconnected') {
      alert('⚠️ API is not connected. Check your backend.');
      return;
    }

    setLoading(true);
    const userMessage = {
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    setResponses(prev => [...prev, userMessage]);
    
    const currentQuery = query;
    setQuery('');

    console.log('🤖 Sending query:', currentQuery);
    const result = await sendQuery(currentQuery);
    
    console.log('📥 Full result received:', result);
    console.log('   Success:', result.success);
    console.log('   Mode:', result.mode);
    console.log('   Answer:', result.answer);
    console.log('   Error:', result.error);

    // Build assistant message with all response data
    const assistantMessage = {
      type: 'assistant',
      mode: result.mode,
      answer: result.answer,
      error: result.error,
      chart: result.chart,
      sources: result.sources,
      success: result.success,
      timestamp: new Date(),
    };

    console.log('💬 Adding assistant message:', assistantMessage);

    setResponses(prev => {
      const updated = [...prev, assistantMessage];
      console.log('📊 Updated responses array:', updated);
      return updated;
    });

    setLoading(false);
  };

  // Handle PDF Upload
  const handlePDFUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (apiStatus === 'disconnected') {
      alert('⚠️ API is not connected. Check your backend.');
      return;
    }

    setUploadProgress('Uploading...');
    console.log('📄 Uploading file:', file.name);
    
    const result = await uploadPDF(file);
    console.log('✅ Upload result:', result);

    if (result.success) {
      setUploadProgress(`✓ Success! Created ${result.chunks} chunks`);
    } else {
      setUploadProgress(`✗ Error: ${result.error}`);
    }

    setTimeout(() => setUploadProgress(''), 3000);
    e.target.value = '';
  };

  // Handle Business Data Ingestion
  const handleIngestData = async () => {
    if (apiStatus === 'disconnected') {
      alert('⚠️ API is not connected. Check your backend.');
      return;
    }

    setIngestProgress('Ingesting...');
    console.log('📊 Starting MySQL ingest');
    
    const result = await ingestBusinessData();
    console.log('✅ Ingest result:', result);

    if (result.success) {
      setIngestProgress(`✓ Ingested ${result.rows} rows`);
    } else {
      setIngestProgress(`✗ Error: ${result.error}`);
    }

    setTimeout(() => setIngestProgress(''), 3000);
  };

  // Render assistant message content
  const renderAssistantContent = (msg) => {
    console.log('🎨 Rendering message:', msg.mode, msg);

    if (!msg.success) {
      return (
        <div className="error-message">
          <p>❌ Error:</p>
          <p className="error-text">{msg.answer || msg.error}</p>
        </div>
      );
    }

    // Chart mode
    if (msg.mode === 'chart' && msg.chart) {
      console.log('📊 Rendering chart:', msg.chart);
      return (
        <div className="chart-box">
          <p>📊 <strong>{msg.chart.type?.toUpperCase()} Chart</strong></p>
          <pre className="chart-data">{JSON.stringify(msg.chart, null, 2)}</pre>
        </div>
      );
    }

    // Aggregation mode
    if (msg.mode === 'aggregation') {
      console.log('📈 Rendering aggregation');
      return (
        <div className="aggregation-box">
          <p>📈 <strong>Results</strong></p>
          <p className="answer-text">{msg.answer}</p>
        </div>
      );
    }

    // RAG mode (default)
    console.log('🧠 Rendering RAG response');
    return (
      <div className="rag-box">
        <p className="answer-text">{msg.answer}</p>
        {msg.sources && msg.sources.length > 0 && (
          <div className="sources">
            <small>
              <strong>📚 Sources ({msg.sources.length}):</strong>
              <div className="sources-list">
                {msg.sources.map((src, i) => (
                  <div key={i} className="source-item">
                    {Object.entries(src).map(([key, value]) => (
                      <span key={key} className="source-detail">
                        <strong>{key}:</strong> {String(value)}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </small>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🤖 AI Data Assistant</h1>
            <p>Hybrid Search + RAG + Analytics</p>
          </div>
          <div className={`api-status ${apiStatus}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {apiStatus === 'checking' && '🔄 Checking...'}
              {apiStatus === 'connected' && '✅ Connected'}
              {apiStatus === 'disconnected' && '❌ Disconnected'}
            </span>
          </div>
        </div>
      </header>

      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="tabs">
            <button
              className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              💬 Chat
            </button>
            <button
              className={`tab-button ${activeTab === 'ingest' ? 'active' : ''}`}
              onClick={() => setActiveTab('ingest')}
            >
              📥 Data
            </button>
          </div>

          {/* Ingest Tab */}
          {activeTab === 'ingest' && (
            <div className="ingest-panel">
              <h3>Ingest Data</h3>

              <div className="upload-section">
                <h4>Upload PDF</h4>
                <label className="upload-button">
                  📄 Choose File
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handlePDFUpload}
                    disabled={loading || apiStatus === 'disconnected'}
                  />
                </label>
                {uploadProgress && <p className="status">{uploadProgress}</p>}
              </div>

              <div className="upload-section">
                <h4>Business Data</h4>
                <button
                  className="ingest-button"
                  onClick={handleIngestData}
                  disabled={loading || apiStatus === 'disconnected'}
                >
                  📊 Ingest MySQL Data
                </button>
                {ingestProgress && <p className="status">{ingestProgress}</p>}
              </div>

              <div className="info-box">
                <h4>ℹ️ How it works</h4>
                <ul>
                  <li>Upload PDFs for document Q&A</li>
                  <li>Ingest business data for analytics</li>
                  <li>Use hybrid search for better results</li>
                </ul>
              </div>
            </div>
          )}
        </aside>

        {/* Main Chat Area */}
        <main className="chat-area">
          <div className="messages">
            {responses.length === 0 ? (
              <div className="empty-state">
                <h2>👋 Welcome!</h2>
                <p>Ask questions about your data</p>
                <div className="suggestions">
                  <button
                    onClick={() => {
                      setQuery('Show sales by month');
                    }}
                    className="suggestion-btn"
                  >
                    📊 Show sales by month
                  </button>
                  <button
                    onClick={() => {
                      setQuery('Who is the top customer?');
                    }}
                    className="suggestion-btn"
                  >
                    👤 Top customer
                  </button>
                  <button
                    onClick={() => {
                      setQuery('Summarize the document');
                    }}
                    className="suggestion-btn"
                  >
                    📄 Summarize
                  </button>
                </div>
              </div>
            ) : (
              responses.map((msg, idx) => (
                <div
                  key={idx}
                  className={`message ${msg.type}`}
                >
                  {msg.type === 'user' ? (
                    <div className="user-message">
                      <p>{msg.content}</p>
                    </div>
                  ) : (
                    <div className="assistant-message">
                      {renderAssistantContent(msg)}
                    </div>
                  )}
                </div>
              ))
            )}

            {loading && (
              <div className="message assistant">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Query Input */}
          <form onSubmit={handleQuerySubmit} className="query-form">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={
                apiStatus === 'disconnected' 
                  ? "⚠️ API not connected..." 
                  : "Ask anything..."
              }
              disabled={loading || apiStatus === 'disconnected'}
              className="query-input"
            />
            <button
              type="submit"
              disabled={loading || !query.trim() || apiStatus === 'disconnected'}
              className="send-button"
            >
              {loading ? '⏳' : '➤'}
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}

export default App;