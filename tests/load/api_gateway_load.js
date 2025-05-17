import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const agentRegistrations = new Counter('agent_registrations');
const actionsLogged = new Counter('actions_logged');
const outcomesRecorded = new Counter('outcomes_recorded');
const studiosCreated = new Counter('studios_created');
const tasksCreated = new Counter('tasks_created');
const reputationQueries = new Counter('reputation_queries');
const failedRequests = new Rate('failed_requests');
const requestDuration = new Trend('request_duration', true);

// Configuration
const API_BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';
const agentTokens = new Map();
const actionIds = new Map();
const studioIds = new Map();

// Shared helper functions
function getRandomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

export const options = {
  stages: [
    { duration: '30s', target: 200 },   // Ramp-up to 200 users over 30 seconds
    { duration: '1m', target: 500 },    // Ramp-up to 500 users over 1 minute
    { duration: '1m', target: 1000 },   // Ramp-up to 1000 users over 1 minute
    { duration: '2m', target: 1000 },   // Stay at 1000 users for 2 minutes
    { duration: '30s', target: 0 }      // Ramp-down to 0 users over 30 seconds
  ],
  thresholds: {
    'http_req_duration': ['p(99)<500'], // 99% of requests must complete within 500ms
    'failed_requests': ['rate<0.01'],    // Less than 1% of requests can fail
  },
};

// Register a new agent
function registerAgent() {
  const payload = JSON.stringify({
    name: `Load Test Agent ${randomString(8)}`,
    email: `agent-${randomString(8)}@loadtest.com`,
    metadata: {
      role: 'Load Testing',
      expertise: 'Performance',
      version: '1.0.0'
    }
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = http.post(`${API_BASE_URL}/agents`, payload, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'agent registration successful': (r) => r.status === 201,
  }) || failedRequests.add(1);

  if (response.status === 201) {
    const data = JSON.parse(response.body);
    const agentId = data.agent_id;
    const token = data.token;
    agentTokens.set(agentId, token);
    agentRegistrations.add(1);
    return agentId;
  }
  
  return null;
}

// Get a registered agent's token or register a new one
function getOrCreateAgentToken() {
  if (agentTokens.size > 0) {
    // Return a random existing agent if we have some (70% chance)
    if (Math.random() < 0.7) {
      const agentIds = Array.from(agentTokens.keys());
      const randomAgentId = getRandomElement(agentIds);
      return { agentId: randomAgentId, token: agentTokens.get(randomAgentId) };
    }
  }
  
  // Register a new agent
  const agentId = registerAgent();
  if (agentId) {
    return { agentId, token: agentTokens.get(agentId) };
  }
  
  // Fallback to first agent if we have any
  if (agentTokens.size > 0) {
    const firstAgentId = agentTokens.keys().next().value;
    return { agentId: firstAgentId, token: agentTokens.get(firstAgentId) };
  }
  
  return null;
}

// Log an action
function logAction() {
  const agent = getOrCreateAgentToken();
  if (!agent) return null;
  
  const actionTypes = ['ANALYZE', 'PROPOSE', 'REVIEW', 'SIMULATE', 'IMPLEMENT'];
  const payload = JSON.stringify({
    action_type: getRandomElement(actionTypes),
    description: `Load test action ${randomString(8)}`,
    data: {
      test_id: randomString(16),
      parameters: {
        sample_value: Math.random() * 1000
      }
    }
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${agent.token}`
    },
  };

  const response = http.post(`${API_BASE_URL}/actions`, payload, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'action logging successful': (r) => r.status === 201,
  }) || failedRequests.add(1);

  if (response.status === 201) {
    const data = JSON.parse(response.body);
    const actionId = data.id;
    actionIds.set(actionId, agent.agentId);
    actionsLogged.add(1);
    return actionId;
  }
  
  return null;
}

// Record an outcome for an action
function recordOutcome() {
  if (actionIds.size === 0) {
    const newActionId = logAction();
    if (!newActionId) return;
    sleep(0.1); // Small delay to allow action to be processed
  }
  
  const actionIds = Array.from(actionIds.keys());
  const randomActionId = getRandomElement(actionIds);
  const agentId = actionIds.get(randomActionId);
  const token = agentTokens.get(agentId);
  
  if (!token) return;
  
  const payload = JSON.stringify({
    success: Math.random() > 0.2, // 80% success rate
    results: {
      details: `Outcome details ${randomString(12)}`,
      metrics: {
        performance: Math.random() * 100,
        accuracy: Math.random() * 100
      }
    },
    impact_score: Math.random()
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
  };

  const response = http.post(`${API_BASE_URL}/actions/${randomActionId}/outcomes`, payload, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'outcome recording successful': (r) => r.status === 201,
  }) || failedRequests.add(1);

  if (response.status === 201) {
    outcomesRecorded.add(1);
  }
}

// Create a studio
function createStudio() {
  const agent = getOrCreateAgentToken();
  if (!agent) return null;
  
  const domains = ['governance', 'finance', 'science', 'policy', 'content'];
  const payload = JSON.stringify({
    name: `Load Test Studio ${randomString(8)}`,
    description: `A studio for load testing with ID ${randomString(12)}`,
    metadata: {
      domain: getRandomElement(domains),
      version: '1.0.0',
      tags: ['load-test', 'performance', randomString(5)]
    }
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${agent.token}`
    },
  };

  const response = http.post(`${API_BASE_URL}/studios`, payload, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'studio creation successful': (r) => r.status === 201,
  }) || failedRequests.add(1);

  if (response.status === 201) {
    const data = JSON.parse(response.body);
    const studioId = data.id;
    studioIds.set(studioId, agent.agentId);
    studiosCreated.add(1);
    return studioId;
  }
  
  return null;
}

// Create a task in a studio
function createTask() {
  if (studioIds.size === 0) {
    const newStudioId = createStudio();
    if (!newStudioId) return;
    sleep(0.1); // Small delay to allow studio to be created
  }
  
  const studioIdsArray = Array.from(studioIds.keys());
  const randomStudioId = getRandomElement(studioIdsArray);
  const agentId = studioIds.get(randomStudioId);
  const token = agentTokens.get(agentId);
  
  if (!token) return;
  
  const payload = JSON.stringify({
    name: `Load Test Task ${randomString(8)}`,
    description: `A task for load testing with ID ${randomString(12)}`,
    parameters: {
      priority: getRandomElement(['high', 'medium', 'low']),
      deadline: '2025-12-31',
      effort: Math.floor(Math.random() * 10) + 1,
      complexity: Math.random()
    }
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
  };

  const response = http.post(`${API_BASE_URL}/studios/${randomStudioId}/tasks`, payload, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'task creation successful': (r) => r.status === 201,
  }) || failedRequests.add(1);

  if (response.status === 201) {
    tasksCreated.add(1);
  }
}

// Query agent reputation
function queryAgentReputation() {
  if (agentTokens.size === 0) {
    registerAgent();
    sleep(0.1); // Small delay to allow agent to be registered
  }
  
  const agentIds = Array.from(agentTokens.keys());
  const randomAgentId = getRandomElement(agentIds);
  const token = agentTokens.get(randomAgentId);
  
  if (!token) return;
  
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`
    },
  };

  const response = http.get(`${API_BASE_URL}/reputation/agents/${randomAgentId}`, params);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'reputation query successful': (r) => r.status === 200,
  }) || failedRequests.add(1);

  if (response.status === 200) {
    reputationQueries.add(1);
  }
}

// Health check
function healthCheck() {
  const response = http.get(`${API_BASE_URL}/health`);
  
  requestDuration.add(response.timings.duration);
  
  check(response, {
    'health check successful': (r) => r.status === 200,
  }) || failedRequests.add(1);
}

// Main execution function
export default function() {
  // First ensure we have some agents
  if (agentTokens.size < 10) {
    registerAgent();
    sleep(0.1);
    return;
  }

  // Then select a random API operation to perform
  const randomValue = Math.random();
  
  if (randomValue < 0.15) {
    registerAgent();
  } else if (randomValue < 0.35) {
    logAction();
  } else if (randomValue < 0.5) {
    recordOutcome();
  } else if (randomValue < 0.65) {
    createStudio();
  } else if (randomValue < 0.8) {
    createTask();
  } else if (randomValue < 0.95) {
    queryAgentReputation();
  } else {
    healthCheck();
  }
  
  // Add some think time between operations
  sleep(Math.random() * 0.5 + 0.1);
} 