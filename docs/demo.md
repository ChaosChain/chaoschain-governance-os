# ChaosChain Governance OS Demo

## Live Agent Workflow UI

The ChaosChain Governance OS now features a real-time process UI that allows you to see the agent workflow as it happens. This provides transparency into how our AI agents work together to analyze blockchain data and generate governance proposals.

![LiveFeed Demo](./images/livefeed_demo.gif)

## Features

### Live Agent Feed

The dashboard includes a real-time log stream that shows:

- Agent activities with color-coded badges for different agent roles
- Thought processes and tool usage
- System messages and workflow status updates
- Time-stamped entries for easy tracking

### Controls

The Live Feed includes several controls:

- **Pause/Resume**: Temporarily pause the log stream when you want to focus on specific entries
- **Clear**: Remove all current log entries to start fresh
- **Auto-scroll**: Automatically follows new messages as they arrive (disables when scrolling up manually)

## Running the Demo

### Method 1: Using the run_live_demo.sh script

The simplest way to run the demo with live agent logging:

```bash
# Make sure you have set up your .env file with the required API keys
./run_live_demo.sh
```

This will:
1. Start the frontend development server
2. Launch the API server with streaming enabled
3. Run the governance demo with verbose logging
4. Connect the LiveFeed component to the streaming logs

### Method 2: Manual Setup

If you prefer to run the components separately:

1. Start the API server with streaming enabled:
   ```bash
   cd api
   export ENABLE_STREAM=1
   uvicorn rest.app:app --reload --host 0.0.0.0 --port 8000
   ```

2. In a separate terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. In a third terminal, run the governance demo:
   ```bash
   python -m agent.runtime.demo --stream --verbose
   ```

4. Open your browser to http://localhost:5173

## Implementation Details

### Architecture

The live agent workflow UI uses Server-Sent Events (SSE) to stream log data from the backend to the frontend:

```
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ Agent Runtime │─────>│ Logging Queue │─────>│ SSE Endpoint  │
└───────────────┘      └───────────────┘      └───────────────┘
                                                     │
                                                     ▼
                                             ┌───────────────┐
                                             │ LiveFeed.tsx  │
                                             └───────────────┘
```

### Technical Components

- **Server**: FastAPI endpoint at `/api/stream` that uses Server-Sent Events
- **Client**: React component `LiveFeed.tsx` that connects via `EventSource` API
- **Logging**: Custom logging handlers that add agent context to log messages

## Customizing

### Adding New Agent Types

To add colors for new agent types, modify the `agentColors` mapping in `LiveFeed.tsx`:

```typescript
const agentColors: Record<string, string> = {
  'System': '#6c757d',
  'Gas Metrics Researcher': '#007bff', 
  'Parameter Optimizer': '#28a745',
  'Your New Agent': '#your-color-code',
  'Unknown Agent': '#17a2b8'
};
``` 