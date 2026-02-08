/**
 * API client for backend communication.
 * Handles JWT authentication and error handling.
 */

import {
  Task,
  TaskCreate,
  TaskUpdate,
  AgentTypeEnum,
  PrioritizeResponse,
  DecomposeResponse,
  ChatResponse,
  AgentLog,
  LLMHealthCheck,
  MCPChatResponse,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend-production-5055.up.railway.app/api/v1';

/**
 * Get JWT token from storage (placeholder - actual implementation depends on Better Auth).
 */
function getJWT(): string | null {
  // In actual implementation, this would retrieve JWT from Better Auth session
  // For now, placeholder that assumes JWT is in localStorage
  if (typeof window !== 'undefined') {
    return localStorage.getItem('jwt_token');
  }
  return null;
}

/**
 * Handle API responses and errors.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = 'An error occurred';
    try {
      const error = await response.json();
      detail = error.detail || detail;
    } catch {
      detail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null as T; // No content
  }

  return response.json();
}

// ============================================
// Authentication API Methods
// ============================================

/**
 * Register a new user.
 */
export async function register(email: string, password: string): Promise<{ access_token: string }> {
  const url = `${API_URL}/auth/register`;
  let response: Response;

  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
  } catch (err: any) {
    throw new Error(`Network error: Could not reach the server. URL: ${url} - ${err.message}`);
  }

  const data = await handleResponse<{ access_token: string }>(response);

  // Store JWT token
  if (typeof window !== 'undefined' && data.access_token) {
    localStorage.setItem('jwt_token', data.access_token);
  }

  return data;
}

/**
 * Login an existing user.
 */
export async function login(email: string, password: string): Promise<{ access_token: string }> {
  const url = `${API_URL}/auth/login`;
  let response: Response;

  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
  } catch (err: any) {
    throw new Error(`Network error: Could not reach the server. URL: ${url} - ${err.message}`);
  }

  const data = await handleResponse<{ access_token: string }>(response);

  // Store JWT token
  if (typeof window !== 'undefined' && data.access_token) {
    localStorage.setItem('jwt_token', data.access_token);
  }

  return data;
}

/**
 * Logout the current user.
 */
export async function logout(): Promise<void> {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('jwt_token');
  }
}

// ============================================
// Tasks API Methods
// ============================================

/**
 * List all tasks for authenticated user.
 */
export async function listTasks(filters?: {
  status?: 'pending' | 'completed';
  priority?: 'high' | 'medium' | 'low';
  tags?: string;
  sort?: 'created_at' | 'due_date' | 'priority' | 'title';
  order?: 'asc' | 'desc';
}): Promise<Task[]> {
  // Filter out undefined values before creating URLSearchParams
  const cleanFilters: Record<string, string> = {};
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        cleanFilters[key] = value;
      }
    });
  }
  const params = new URLSearchParams(cleanFilters);
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/tasks?${params}`, {
    headers: {
      'Authorization': `Bearer ${jwt}`,
    },
  });

  return handleResponse<Task[]>(response);
}

/**
 * Create a new task.
 */
export async function createTask(data: TaskCreate): Promise<Task> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/tasks`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  return handleResponse<Task>(response);
}

/**
 * Update an existing task.
 */
export async function updateTask(id: string, data: TaskUpdate): Promise<Task> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/tasks/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  return handleResponse<Task>(response);
}

/**
 * Delete a task.
 */
export async function deleteTask(id: string): Promise<void> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/tasks/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${jwt}`,
    },
  });

  return handleResponse<void>(response);
}

/**
 * Toggle task completion status.
 */
export async function toggleTaskCompletion(id: string): Promise<Task> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/tasks/${id}/complete`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${jwt}`,
    },
  });

  return handleResponse<Task>(response);
}

// ============================================
// Agent API Methods
// ============================================

/**
 * Request AI to prioritize tasks.
 */
export async function prioritizeTasks(
  taskIds: string[],
  context?: string
): Promise<PrioritizeResponse> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/agents/prioritize`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task_ids: taskIds,
      context: context,
    }),
  });

  return handleResponse<PrioritizeResponse>(response);
}

/**
 * Request AI to decompose a task into subtasks.
 */
export async function decomposeTask(
  taskId: string,
  maxSubtasks: number = 10,
  detailLevel: 'brief' | 'medium' | 'detailed' = 'medium'
): Promise<DecomposeResponse> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/agents/decompose`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      task_id: taskId,
      max_subtasks: maxSubtasks,
      detail_level: detailLevel,
    }),
  });

  return handleResponse<DecomposeResponse>(response);
}

/**
 * Chat with AI agent.
 */
export async function chatWithAgent(
  message: string,
  agentType: AgentTypeEnum = AgentTypeEnum.CHAT
): Promise<ChatResponse> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/agents/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      agent_type: agentType,
    }),
  });

  return handleResponse<ChatResponse>(response);
}

/**
 * Get agent execution logs.
 */
export async function getAgentLogs(limit: number = 20): Promise<AgentLog[]> {
  const jwt = getJWT();

  const response = await fetch(`${API_URL}/agents/logs?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${jwt}`,
    },
  });

  return handleResponse<AgentLog[]>(response);
}

/**
 * Check LLM health status.
 */
export async function checkLLMHealth(): Promise<LLMHealthCheck> {
  const response = await fetch(`${API_URL}/agents/health`);
  return handleResponse<LLMHealthCheck>(response);
}

// ============================================
// Phase 3: MCP Chat API Methods
// ============================================

/**
 * Extract user_id from JWT payload (base64 decode, no verification).
 */
export function getUserIdFromJWT(): string | null {
  const jwt = getJWT();
  if (!jwt) return null;

  try {
    const payload = JSON.parse(atob(jwt.split('.')[1]));
    return payload.user_id || null;
  } catch {
    return null;
  }
}

/**
 * Send a message to the MCP chat agent.
 */
export async function mcpChat(
  message: string,
  conversationId?: string | null,
): Promise<MCPChatResponse> {
  const jwt = getJWT();
  const userId = getUserIdFromJWT();

  if (!userId) {
    throw new Error('Not authenticated');
  }

  const body: Record<string, string> = { message };
  if (conversationId) {
    body.conversation_id = conversationId;
  }

  const response = await fetch(`${API_URL}/chat/${userId}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  return handleResponse<MCPChatResponse>(response);
}
