"""
Real API server for the ChaosChain Governance OS demo that integrates with CrewAI agents.
"""
import asyncio
import datetime
import json
import os
import sys
import time
import uuid
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

# Set environment variable to enable streaming
os.environ["ENABLE_STREAM"] = "1"

# Ensure the current directory is in the path
sys.path.insert(0, os.path.abspath("."))

# Import our real agent demo
try:
    from agent.agents.quick_demo_fixed import QuickDemo
    print("Successfully imported QuickDemo")
except Exception as e:
    print(f"Error importing QuickDemo: {e}")
    sys.exit(1)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global queue for log messages
log_queue = asyncio.Queue()

# Function to add logs to the queue
async def add_log(agent, level, message):
    """Add a log message to the queue for streaming."""
    await log_queue.put({
        "ts": datetime.datetime.now().isoformat(),
        "agent": agent,
        "level": level,
        "msg": message
    })

async def log_generator():
    """Generate log messages from the queue."""
    while True:
        # Wait for a log message
        log_data = await log_queue.get()
        
        # Convert to JSON and yield
        yield json.dumps(log_data)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/stream")
async def stream_logs():
    """Stream logs as Server-Sent Events (SSE)."""
    print("Client connected to log stream")
    return EventSourceResponse(log_generator())

@app.get("/api/stream")
async def api_stream_logs():
    """Stream logs as Server-Sent Events (SSE) under /api prefix."""
    print("Client connected to log stream via /api/stream")
    return EventSourceResponse(log_generator())

@app.get("/proposals/last")
async def get_last_proposal():
    """Get the last proposal."""
    # We'll use the same mock data structure as before, but the content will be
    # populated by the actual agent results
    global proposal_content
    if proposal_content:
        return {
            "id": "real-proposal-001",
            "title": "EIP-1559 Parameter Optimization",
            "description": "Proposal to optimize gas parameters based on real agent analysis",
            "content": proposal_content,
            "created_at": datetime.datetime.now().isoformat(),
            "attested": True,
            "simulation_id": "real-sim-001"
        }
    else:
        # Return a placeholder while waiting for the agent to complete
        return {
            "id": "pending-proposal-001",
            "title": "EIP-1559 Parameter Optimization (Processing)",
            "description": "Agents are currently analyzing data and generating a proposal...",
            "content": "# Proposal In Progress\n\nThe agents are currently analyzing blockchain data and generating a parameter optimization proposal. Please wait...",
            "created_at": datetime.datetime.now().isoformat(),
            "attested": False,
            "simulation_id": "pending-sim-001"
        }

@app.get("/api/proposals/last")
async def api_get_last_proposal():
    """Get the last proposal under /api prefix."""
    return await get_last_proposal()

@app.get("/simulations/{simulation_id}")
async def get_simulation(simulation_id: str):
    """Get simulation data."""
    # Mock data
    return {
        "id": simulation_id,
        "metrics": [
            {"name": "Gas Used Ratio", "value": 0.68, "unit": "", "change": -0.14},
            {"name": "Base Fee", "value": 18.7, "unit": "gwei", "change": -4.8},
            {"name": "Fee Volatility", "value": 0.47, "unit": "", "change": -0.21},
            {"name": "Throughput", "value": 14.3, "unit": "tx/s", "change": 2.1},
            {"name": "Block Utilization", "value": 72.5, "unit": "%", "change": 7.5}
        ]
    }

@app.get("/api/simulations/{simulation_id}")
async def api_get_simulation(simulation_id: str):
    """Get simulation data under /api prefix."""
    return await get_simulation(simulation_id)

# Global variable to store proposal content
proposal_content = None

# Function to run the agent demo and capture results
def run_agent_demo():
    """Run the agent demo and store the results."""
    global proposal_content
    
    # Log starting message
    asyncio.run(add_log("system", "info", "Starting agent workflow..."))
    
    try:
        # Run the demo
        print("Creating QuickDemo instance...")
        demo = QuickDemo(verbose=True)
        
        print("Running QuickDemo...")
        results = demo.run()
        
        print(f"Demo results: {results.keys()}")
        
        # Store the proposal content
        proposal_content = results.get("Proposal", "No proposal content available")
        
        # Log completion message
        asyncio.run(add_log("system", "info", "Agent workflow completed successfully!"))
    except Exception as e:
        print(f"Error running agent demo: {str(e)}")
        import traceback
        traceback.print_exc()
        # Log error
        asyncio.run(add_log("system", "error", f"Agent workflow failed: {str(e)}"))

# Start the agent demo in a separate thread
@app.on_event("startup")
async def startup_event():
    await add_log("system", "info", "API server started, initializing agent workflow...")
    thread = threading.Thread(target=run_agent_demo)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
