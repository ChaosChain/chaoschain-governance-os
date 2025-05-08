import React, { useEffect, useState, useRef } from 'react';

interface LogMessage {
  ts: string;
  agent: string;
  level: string;
  msg: string;
}

interface LiveFeedProps {
  height?: string;
}

const LiveFeed: React.FC<LiveFeedProps> = ({ height = '600px' }) => {
  const [messages, setMessages] = useState<LogMessage[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Map agent names to colors
  const agentColors: Record<string, string> = {
    'System': '#6c757d',
    'Gas Metrics Researcher': '#007bff', 
    'Parameter Optimizer': '#28a745',
    'Unknown Agent': '#17a2b8'
  };

  // Map log levels to colors
  const levelColors: Record<string, string> = {
    'info': '#212529',
    'warning': '#ff9800',
    'error': '#dc3545',
    'debug': '#6c757d'
  };

  // Format timestamp
  const formatTime = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
      return timestamp;
    }
  };

  // Auto-scroll to bottom when new messages arrive (if autoScroll is enabled)
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  // Handle scrolling behavior
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (!container) return;
      
      const atBottom = Math.abs(
        (container.scrollHeight - container.scrollTop) - container.clientHeight
      ) < 50;
      
      setAutoScroll(atBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Set up event source for SSE
  useEffect(() => {
    if (isPaused) return;

    const eventSource = new EventSource('/api/stream');
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      // Try to reconnect after a short delay
      setTimeout(() => {
        eventSource.close();
        if (eventSourceRef.current === eventSource && !isPaused) {
          const newEventSource = new EventSource('/api/stream');
          eventSourceRef.current = newEventSource;
        }
      }, 5000);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as LogMessage;
        setMessages(prev => [...prev, data]);
      } catch (e) {
        console.error('Error parsing SSE message:', e);
      }
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [isPaused]);

  // Toggle pause/resume
  const togglePause = () => {
    setIsPaused(prev => {
      if (!prev) {
        // Pausing, close the connection
        eventSourceRef.current?.close();
      }
      return !prev;
    });
  };

  // Clear messages
  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <div className="live-feed-container">
      <div className="live-feed-header" style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 0', 
        marginBottom: '10px'
      }}>
        <h3 style={{ margin: 0 }}>Live Agent Activity</h3>
        <div>
          <span style={{ 
            display: 'inline-block',
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: isConnected ? '#28a745' : '#dc3545',
            marginRight: '5px'
          }}></span>
          <span style={{ marginRight: '15px', fontSize: '14px' }}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
          <button
            onClick={togglePause}
            style={{
              backgroundColor: isPaused ? '#007bff' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 8px',
              marginRight: '8px',
              cursor: 'pointer'
            }}
          >
            {isPaused ? 'Resume' : 'Pause'}
          </button>
          <button
            onClick={clearMessages}
            style={{
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 8px',
              cursor: 'pointer'
            }}
          >
            Clear
          </button>
        </div>
      </div>

      <div 
        ref={containerRef}
        className="live-feed-messages" 
        style={{ 
          height, 
          overflowY: 'auto', 
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          padding: '10px',
          backgroundColor: '#f8f9fa',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#6c757d', padding: '20px' }}>
            Waiting for agent activities...
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '8px', lineHeight: '1.5' }}>
            <span style={{ color: '#6c757d' }}>[{formatTime(msg.ts)}]</span>{' '}
            <span 
              style={{ 
                backgroundColor: agentColors[msg.agent] || agentColors['Unknown Agent'],
                color: 'white',
                padding: '2px 6px',
                borderRadius: '4px',
                fontSize: '12px',
                fontWeight: 'bold'
              }}
            >
              {msg.agent}
            </span>{' '}
            <span style={{ color: levelColors[msg.level] || 'inherit' }}>
              {msg.msg}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {!autoScroll && messages.length > 0 && (
        <div 
          style={{ 
            textAlign: 'center', 
            padding: '5px', 
            fontSize: '12px',
            color: '#6c757d',
            cursor: 'pointer'
          }}
          onClick={() => {
            setAutoScroll(true);
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          }}
        >
          ↓ New messages below - click to scroll down ↓
        </div>
      )}
    </div>
  );
};

export default LiveFeed; 