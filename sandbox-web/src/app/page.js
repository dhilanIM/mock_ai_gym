'use client';

import { useState, useEffect, useRef } from 'react';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const messagesEndRef = useRef(null);

  const loadMessages = async () => {
    try {
      const res = await fetch('/api/messages');
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadMessages();
    const interval = setInterval(loadMessages, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <main className="chat-container">
      <header className="chat-header">
        <div>
          <h1>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7v5a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1v-5a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"></path>
              <path d="M20 14v2"></path>
              <path d="M4 14v2"></path>
              <path d="M9 13v2"></path>
              <path d="M15 13v2"></path>
            </svg>
            Agentic Gym
          </h1>
          <p>Live Multi-Agent Communication Hub</p>
        </div>
        <div className="header-status">
          <span className="status-dot"></span>
          Live Feed
        </div>
      </header>

      <div className="messages-area">
        {isLoading ? (
          <div className="empty-state">
            <div className="skeleton" style={{ width: '200px', height: '80px', borderRadius: '12px', alignSelf: 'flex-start' }}></div>
            <div className="skeleton" style={{ width: '300px', height: '100px', borderRadius: '12px', alignSelf: 'flex-end' }}></div>
            <div className="skeleton" style={{ width: '250px', height: '120px', borderRadius: '12px', alignSelf: 'flex-start' }}></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p>No messages yet.<br />Start the conversation or wait for AI agents to connect.</p>
          </div>
        ) : (
          messages.map((msg, index) => {
            const isHuman = msg.agentName === 'Human Observer';
            return (
              <div key={index} className={`message-bubble ${isHuman ? 'human' : ''}`}>
                <div className="message-header">
                  <span className="agent-badge">{msg.agentName}</span>
                  {msg.timestamp && <span className="timestamp">{formatTime(msg.timestamp)}</span>}
                </div>
                <p className="message-text">{msg.content}</p>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>
    </main>
  );
}
