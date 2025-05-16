import React, { useEffect, useRef, useState } from 'react';

interface LogMessage {
  ts: string;
  agent: string;
  level: string;
  msg: string;
}

// Agent color mapping
const agentColors: Record<string, string> = {
  'Researcher': '#4caf50',
  'Optimizer': '#2196f3',
  'Developer': '#ff9800',
  'Facilitator': '#9c27b0',
  'system': '#607d8b',
  'TestAgent': '#f44336',
};

// Get a color for an agent, or a default color
const getAgentColor = (agent: string): string => {
  return agentColors[agent] || '#607d8b';
};

// Format timestamp to HH:MM:SS
const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  } catch (e) {
    return timestamp;
  }
};

const LiveFeed: React.FC = () => {
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [connected, setConnected] = useState<boolean>(false);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Connect to the SSE endpoint
    const eventSource = new EventSource('/api/stream');
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnected(true);
      console.log('Connected to log stream');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as LogMessage;
        setLogs((prevLogs) => [...prevLogs, data]);
      } catch (e) {
        console.error('Error parsing log message:', e);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Error with log stream:', error);
      setConnected(false);
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, []);

  // Auto-scroll to the bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  // Get level-specific styling
  const getLevelStyle = (level: string): React.CSSProperties => {
    switch (level.toLowerCase()) {
      case 'error':
        return { color: '#f44336', fontWeight: 'bold' };
      case 'warning':
        return { color: '#ff9800', fontWeight: 'bold' };
      case 'info':
        return { color: '#2196f3' };
      case 'debug':
        return { color: '#9e9e9e' };
      default:
        return {};
    }
  };

  return (
    <div className="live-feed-container" style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      maxHeight: 'calc(100vh - 200px)', 
      overflow: 'hidden' 
    }}>
      <div className="live-feed-header" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 0',
        borderBottom: '1px solid #eee'
      }}>
        <h3 style={{ margin: 0 }}>Live Agent Feed</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: connected ? '#4caf50' : '#f44336'
          }}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
          <button 
            onClick={() => setAutoScroll(!autoScroll)}
            style={{
              padding: '4px 8px',
              backgroundColor: autoScroll ? '#e0e0e0' : '#ffffff',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {autoScroll ? 'Pause Scroll' : 'Auto Scroll'}
          </button>
          <button 
            onClick={() => setLogs([])}
            style={{
              padding: '4px 8px',
              backgroundColor: '#ffffff',
              border: '1px solid #ccc',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Clear
          </button>
        </div>
      </div>
      
      <div 
        ref={logContainerRef} 
        className="live-feed-logs" 
        style={{ 
          overflowY: 'auto',
          padding: '10px',
          flex: 1,
          backgroundColor: '#f9f9f9',
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '14px',
          lineHeight: '1.5'
        }}
      >
        {logs.length === 0 ? (
          <div style={{ 
            padding: '20px', 
            textAlign: 'center', 
            color: '#757575',
            fontStyle: 'italic' 
          }}>
            Waiting for agent activity...
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} style={{ marginBottom: '8px', display: 'flex' }}>
              <span style={{ minWidth: '80px', color: '#757575' }}>
                {formatTimestamp(log.ts)}
              </span>
              <span style={{
                padding: '0 8px',
                margin: '0 8px',
                backgroundColor: getAgentColor(log.agent),
                color: 'white',
                borderRadius: '4px',
                fontWeight: 'bold',
                minWidth: '100px',
                textAlign: 'center'
              }}>
                {log.agent}
              </span>
              <span style={getLevelStyle(log.level)}>{log.msg}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default LiveFeed; 