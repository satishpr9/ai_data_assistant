import { useState, useEffect, useRef } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

import {
  sendQueryStream,
  uploadPDF,
  ingestBusinessData,
  testConnection,
  isAuthenticated,
  getCurrentUser,
  logout,
  getConversations,
  createConversation,
  getConversation,
  deleteConversation,
} from "./api";

import LoginSidebar from "./components/LoginSidebar";
import "./App.css";

function App() {
  // Auth state
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [currentUser, setCurrentUser] = useState(getCurrentUser());

  // Conversation state
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);

  // UI state
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const messagesContainerRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // ======================
  // AUTH HANDLERS
  // ======================
  const handleAuthSuccess = (user) => {
    setAuthenticated(true);
    setCurrentUser(user);
    loadConversations();
  };

  const handleLogout = () => {
    logout();
    setAuthenticated(false);
    setCurrentUser(null);
    setConversations([]);
    setCurrentConversation(null);
    setMessages([]);
  };

  // ======================
  // LOAD CONVERSATIONS
  // ======================
  const loadConversations = async () => {
    const convs = await getConversations();
    setConversations(convs);

    // Auto-select most recent or create new
    if (convs.length > 0 && !currentConversation) {
      loadConversation(convs[0].id);
    } else if (convs.length === 0) {
      // Don't auto-create, just show empty state
    }
  };

  // ======================
  // CONVERSATION HANDLERS
  // ======================
  const handleNewConversation = async () => {
    const newConv = await createConversation("New Chat");
    if (newConv) {
      setConversations((prev) => [newConv, ...prev]);
      setCurrentConversation(newConv);
      setMessages([]);
    }
  };

  const loadConversation = async (conversationId) => {
    const conv = await getConversation(conversationId);
    if (conv) {
      setCurrentConversation(conv);

      // Transform messages
      const transformedMessages = conv.messages.map((msg) => {
        if (msg.role === "user") {
          return { type: "user", content: msg.content };
        } else {
          let metadata = null;
          try {
            metadata = msg.metadata ? JSON.parse(msg.metadata) : null;
          } catch (e) {
            console.error("Failed to parse metadata:", e);
          }

          return {
            type: "assistant",
            mode: msg.mode,
            answer: msg.content,
            chart: msg.mode === "chart" ? metadata : null,
            sources: msg.mode === "aggregation" ? metadata : [],
            success: true,
          };
        }
      });

      setMessages(transformedMessages);
    }
  };

  const handleDeleteConversation = async (conversationId, e) => {
    e?.stopPropagation();

    const result = await deleteConversation(conversationId);
    if (result.success) {
      const remaining = conversations.filter((c) => c.id !== conversationId);
      setConversations(remaining);

      // If deleted current conversation
      if (currentConversation?.id === conversationId) {
        if (remaining.length > 0) {
          loadConversation(remaining[0].id);
        } else {
          setCurrentConversation(null);
          setMessages([]);
        }
      }
    }
  };

  
  // FILE UPLOAD
  
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file type
    if (!file.name.endsWith('.pdf')) {
      setUploadStatus("❌ Please upload PDF files only");
      setTimeout(() => setUploadStatus(""), 3000);
      return;
    }

    setUploadingFile(true);
    setUploadStatus("📤 Uploading PDF...");

    try {
      const result = await uploadPDF(file);
      if (result.chunks_created) {
        setUploadStatus(`✅ Uploaded! Created ${result.chunks_created} chunks`);
        
        // Add system message to current conversation
        if (currentConversation) {
          setMessages(prev => [...prev, {
            type: "system",
            content: `📎 Uploaded: ${file.name} (${result.chunks_created} chunks created)`
          }]);
        }
      } else {
        setUploadStatus(`❌ Upload failed: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      setUploadStatus(`❌ Error: ${err.message}`);
    } finally {
      setUploadingFile(false);
      setTimeout(() => setUploadStatus(""), 4000);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

 
  // AUTO SCROLL
 
  useEffect(() => {
    const el = messagesContainerRef.current;
    if (!el) return;
    setTimeout(() => {
      el.scrollTop = el.scrollHeight;
    }, 0);
  }, [messages, loading]);

 
  // AUTO RESIZE TEXTAREA
 
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }, [query]);

 
  // LOAD CONVERSATIONS ON AUTH
 
  useEffect(() => {
    if (authenticated) {
      loadConversations();
    }
  }, [authenticated]);

  // ======================
  // SEND QUERY WITH STREAMING
  // ======================
  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    // Create conversation if needed
    let convId = currentConversation?.id;
    if (!convId) {
      const title = query.slice(0, 50) + (query.length > 50 ? "..." : "");
      const newConv = await createConversation(title);
      if (newConv) {
        convId = newConv.id;
        setConversations((prev) => [newConv, ...prev]);
        setCurrentConversation(newConv);
      }
    }

    setMessages((p) => [...p, { type: "user", content: query }]);

    const q = query;
    setQuery("");
    setLoading(true);

    const responseIndex = messages.length + 1;
    setMessages((p) => [
      ...p,
      {
        type: "assistant",
        mode: "rag",
        streaming: true,
        answer: "",
        success: true,
      },
    ]);

    try {
      await sendQueryStream(
        q,
        convId,
        (token) => {
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[responseIndex]) {
              newMessages[responseIndex] = {
                ...newMessages[responseIndex],
                answer: (newMessages[responseIndex].answer || "") + token,
              };
            }
            return newMessages;
          });
        },
        (data) => {
          setLoading(false);
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[responseIndex]) {
              if (data.mode === "chart") {
                newMessages[responseIndex] = {
                  type: "assistant",
                  mode: "chart",
                  chart: data.chart,
                  success: true,
                  streaming: false,
                };
              } else if (data.mode === "aggregation") {
                newMessages[responseIndex] = {
                  type: "assistant",
                  mode: "aggregation",
                  answer: data.answer,
                  sources: data.sources,
                  success: true,
                  streaming: false,
                };
              } else {
                newMessages[responseIndex].streaming = false;
              }
            }
            return newMessages;
          });
          
          // Reload conversations to update titles/counts
          loadConversations();
        },
        (error) => {
          setLoading(false);
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[responseIndex]) {
              newMessages[responseIndex] = {
                type: "assistant",
                success: false,
                answer: `Error: ${error}`,
                streaming: false,
              };
            }
            return newMessages;
          });
        }
      );
    } catch (err) {
      setLoading(false);
    }
  };

 
  // RENDER ASSISTANT CONTENT

  const renderAssistantContent = (msg) => {
    if (!msg.success) {
      return (
        <div className="error-message">
          <p>{msg.answer || msg.error}</p>
        </div>
      );
    }

    if (msg.mode === "chart") {
      const chartData =
        msg.chart?.labels?.length && msg.chart?.datasets?.[0]?.data
          ? msg.chart.labels.map((label, idx) => ({
              name: label,
              value: msg.chart.datasets[0].data[idx] || 0,
            }))
          : [];

      if (!chartData.length) return <p>No chart data available.</p>;

      return (
        <div className="chart-box">
          <p className="chart-title">
            {msg.chart.datasets?.[0]?.label || "Chart"}
          </p>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.6)" />
                <YAxis stroke="rgba(255,255,255,0.6)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(0,0,0,0.8)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="value" fill="#10a37f" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    return (
      <div>
        <p className="answer-text">
          {msg.answer}
          {msg.streaming && <span className="cursor-blink">▊</span>}
        </p>
        {msg.sources?.length > 0 && (
          <div className="sources">
            <strong>Sources:</strong>
            <div className="sources-list">
              {msg.sources.map((src, i) => (
                <span key={i} className="source-item">
                  {Object.values(src).join(" | ")}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  
  // RENDER
  
  return (
    <div className="chatgpt-app">
      {/* SIDEBAR */}
      <aside className={`chatgpt-sidebar ${sidebarCollapsed ? "collapsed" : ""}`}>
        {!authenticated ? (
          <LoginSidebar onAuthSuccess={handleAuthSuccess} />
        ) : (
          <>
            {/* New Chat Button */}
            <button className="new-chat-button" onClick={handleNewConversation}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M12 5v14m-7-7h14" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>New chat</span>
            </button>

            {/* Conversations List */}
            <div className="conversations-scroll">
              {conversations.length === 0 ? (
                <div className="empty-conversations">
                  <p>No conversations yet</p>
                  <p className="hint">Start a new chat to begin</p>
                </div>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={`conversation-item ${
                      currentConversation?.id === conv.id ? "active" : ""
                    }`}
                    onClick={() => loadConversation(conv.id)}
                  >
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                    >
                      <path
                        d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                        strokeWidth="2"
                      />
                    </svg>
                    <span className="conv-title">{conv.title}</span>
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDeleteConversation(conv.id, e)}
                      title="Delete conversation"
                    >
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path
                          d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                          strokeWidth="2"
                        />
                      </svg>
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* User Menu */}
            <div className="sidebar-footer">
              <div className="user-profile" onClick={() => setShowUserMenu(!showUserMenu)}>
                <div className="user-avatar">
                  {currentUser?.username?.charAt(0).toUpperCase()}
                </div>
                <span className="user-name">{currentUser?.username}</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M6 9l6 6 6-6" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </div>

              {showUserMenu && (
                <div className="user-dropdown">
                  <button onClick={handleLogout}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path
                        d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                    Log out
                  </button>
                </div>
              )}
            </div>
          </>
        )}
      </aside>

      {/* MAIN CONTENT */}
      <main className="chatgpt-main">
        {/* Header Bar */}
        <div className="chat-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 12h18M3 6h18M3 18h18" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>

          {currentConversation && (
            <div className="current-chat-title">
              {currentConversation.title}
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="messages-container" ref={messagesContainerRef}>
          {messages.length === 0 && authenticated && (
            <div className="empty-state">
              <div className="empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" strokeWidth="1.5"/>
                </svg>
              </div>
              <h1>AI Data Assistant</h1>
              <p>How can I help you today?</p>
              <div className="example-prompts">
                <button onClick={() => setQuery("Analyze my sales data")}>
                  📊 Analyze my sales data
                </button>
                <button onClick={() => setQuery("Show me a chart of monthly trends")}>
                  📈 Show monthly trends
                </button>
                <button onClick={() => setQuery("Who is my top customer?")}>
                  👤 Find top customer
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.type}`}>
              <div className="message-content">
                <div className="message-avatar">
                  {msg.type === "user" ? (
                    <div className="user-avatar-small">
                      {currentUser?.username?.charAt(0).toUpperCase()}
                    </div>
                  ) : msg.type === "system" ? (
                    <div className="system-avatar">📎</div>
                  ) : (
                    <div className="ai-avatar">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="message-text">
                  {msg.type === "user" || msg.type === "system" ? (
                    <p>{msg.content}</p>
                  ) : (
                    renderAssistantContent(msg)
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message-content">
                <div className="message-avatar">
                  <div className="ai-avatar">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                    </svg>
                  </div>
                </div>
                <div className="message-text">
                  <div className="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        {authenticated && (
          <div className="input-container">
            {uploadStatus && (
              <div className="upload-status">
                {uploadStatus}
              </div>
            )}
            
            <form className="input-form" onSubmit={handleQuerySubmit}>
              {/* File Upload Button */}
              <button
                type="button"
                className="attach-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingFile}
                title="Upload PDF"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                style={{ display: "none" }}
              />

              <textarea
                ref={textareaRef}
                className="message-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleQuerySubmit(e);
                  }
                }}
                placeholder="Message AI Data Assistant..."
                rows="1"
                disabled={loading}
              />

              <button
                type="submit"
                className="send-btn"
                disabled={loading || !query.trim()}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path
                    d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;