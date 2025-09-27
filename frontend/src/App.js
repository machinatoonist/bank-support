import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, AlertTriangle, Shield, Clock, Info } from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showNameInput, setShowNameInput] = useState(true);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getRiskBadgeColor = (risk) => {
    if (risk <= 2) return 'bg-green-100 text-green-800 border-green-300';
    if (risk <= 5) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    if (risk <= 8) return 'bg-orange-100 text-orange-800 border-orange-300';
    return 'bg-red-100 text-red-800 border-red-300';
  };

  const getRiskCategoryIcon = (category) => {
    switch (category) {
      case 'routine': return <Info className="w-4 h-4" />;
      case 'concerning': return <Clock className="w-4 h-4" />;
      case 'urgent': return <AlertTriangle className="w-4 h-4" />;
      case 'critical': return <Shield className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (customerName.trim()) {
      setShowNameInput(false);
      setMessages([{
        type: 'system',
        content: `Welcome ${customerName}! I'm your AI banking assistant. I can help you with account inquiries, security concerns, and other banking needs. How can I assist you today?`
      }]);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/support`, {
        question: inputValue,
        customer_name: customerName,
        customer_id: 123,
        include_pending: true
      });

      const agentMessage = {
        type: 'agent',
        content: response.data.support_advice,
        data: response.data,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'error',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([]);
    setCustomerName('');
    setShowNameInput(true);
    setInputValue('');
  };

  if (showNameInput) {
    return (
      <div className="app">
        <div className="name-input-container">
          <div className="name-input-card">
            <div className="header-section">
              <Bot className="header-icon" />
              <h1>Bank Support AI Agent</h1>
              <p className="subtitle">
                Powered by <strong>Pydantic AI</strong> and <strong>Logfire</strong>
              </p>
            </div>

            <div className="intro-section">
              <h2>AI-Powered Risk Assessment</h2>
              <p>
                This demonstration showcases an intelligent banking support system that uses
                advanced AI to assess customer inquiries, evaluate risk levels, and make
                automated decisions about account security measures.
              </p>

              <div className="features-grid">
                <div className="feature-item">
                  <Bot className="feature-icon" />
                  <span>AI-Powered Analysis</span>
                </div>
                <div className="feature-item">
                  <Shield className="feature-icon" />
                  <span>Risk Assessment</span>
                </div>
                <div className="feature-item">
                  <AlertTriangle className="feature-icon" />
                  <span>Automated Decisions</span>
                </div>
                <div className="feature-item">
                  <Info className="feature-icon" />
                  <span>Real-time Monitoring</span>
                </div>
              </div>
            </div>

            <form onSubmit={handleNameSubmit} className="name-form">
              <label htmlFor="customerName">Enter your name to begin:</label>
              <input
                id="customerName"
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="Your name"
                required
              />
              <button type="submit">Start Chat</button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <Bot className="header-icon" />
            <div>
              <h1>Bank Support AI Agent</h1>
              <p>Customer: {customerName}</p>
            </div>
          </div>
          <button onClick={resetChat} className="reset-button">
            New Session
          </button>
        </div>

        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              {message.type === 'user' && (
                <div className="message-content">
                  <div className="message-header">
                    <User className="message-icon" />
                    <span className="message-name">{customerName}</span>
                    <span className="message-time">{message.timestamp}</span>
                  </div>
                  <div className="message-text">{message.content}</div>
                </div>
              )}

              {message.type === 'agent' && (
                <div className="message-content">
                  <div className="message-header">
                    <Bot className="message-icon" />
                    <span className="message-name">AI Agent</span>
                    <span className="message-time">{message.timestamp}</span>
                  </div>
                  <div className="message-text">{message.content}</div>

                  {message.data && (
                    <div className="agent-data">
                      <div className="data-row">
                        <div className="data-item">
                          <span className="data-label">Risk Level:</span>
                          <span className={`risk-badge ${getRiskBadgeColor(message.data.risk)}`}>
                            {getRiskCategoryIcon(message.data.risk_category)}
                            {message.data.risk}/10 ({message.data.risk_category})
                          </span>
                        </div>
                        <div className="data-item">
                          <span className="data-label">Card Status:</span>
                          <span className={`status-badge ${message.data.block_card ? 'blocked' : 'active'}`}>
                            {message.data.block_card ? 'BLOCKED' : 'ACTIVE'}
                          </span>
                        </div>
                      </div>

                      <div className="data-explanation">
                        <span className="data-label">Risk Analysis:</span>
                        <span className="explanation-text">{message.data.risk_explanation}</span>
                      </div>

                      {message.data.risk_signals && message.data.risk_signals.length > 0 && (
                        <div className="risk-signals">
                          <span className="data-label">Risk Signals:</span>
                          <div className="signals-list">
                            {message.data.risk_signals.map((signal, i) => (
                              <span key={i} className="signal-tag">{signal}</span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {(message.type === 'system' || message.type === 'error') && (
                <div className="system-message">
                  <div className="system-content">
                    {message.content}
                  </div>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="message agent">
              <div className="message-content">
                <div className="message-header">
                  <Bot className="message-icon" />
                  <span className="message-name">AI Agent</span>
                </div>
                <div className="loading-indicator">
                  <div className="loading-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                  <span>Analyzing your request...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-form">
          <div className="input-container">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading || !inputValue.trim()}>
              <Send className="send-icon" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;