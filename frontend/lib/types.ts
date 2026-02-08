/**
 * TypeScript type definitions for the application.
 */

export enum PriorityEnum {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum RecurrenceEnum {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: PriorityEnum | null;
  tags: string[];
  due_date: string | null; // ISO date string (YYYY-MM-DD)
  recurrence: RecurrenceEnum | null;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: PriorityEnum;
  tags?: string[];
  due_date?: string; // YYYY-MM-DD
  recurrence?: RecurrenceEnum;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: PriorityEnum;
  tags?: string[];
  due_date?: string; // YYYY-MM-DD
  recurrence?: RecurrenceEnum;
}

export interface ErrorResponse {
  detail: string;
}

// Agent Types
export enum AgentTypeEnum {
  PRIORITIZER = 'prioritizer',
  DECOMPOSER = 'decomposer',
  SCHEDULER = 'scheduler',
  REMINDER = 'reminder',
  CHAT = 'chat',
}

export interface AgentMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  status?: 'pending' | 'completed' | 'error';
}

export interface PriorityRecommendation {
  task_id: string;
  priority: 'high' | 'medium' | 'low';
  reason: string;
}

export interface SubtaskRecommendation {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  effort: 'small' | 'medium' | 'large';
}

export interface PrioritizeResponse {
  success: boolean;
  priorities: PriorityRecommendation[];
  message: string;
}

export interface DecomposeResponse {
  success: boolean;
  parent_task_id: string;
  subtasks: SubtaskRecommendation[];
  message: string;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  agent_type: AgentTypeEnum;
}

export interface AgentLog {
  id: string;
  agent_type: string;
  status: string;
  input_summary: string;
  output_summary: string;
  execution_time_ms: number | null;
  created_at: string;
}

export interface LLMHealthCheck {
  primary: { status: string; provider?: string; error?: string };
  fallback: { status: string; provider?: string; error?: string };
}

// Phase 3: MCP Chat Types
export interface MCPToolCallRecord {
  tool_name: string;
  tool_input: Record<string, unknown>;
  tool_output: unknown;
}

export interface MCPChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: MCPToolCallRecord[];
}

export interface MCPChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: MCPToolCallRecord[];
}
