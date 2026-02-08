---
id: 004
title: Create Phase 3 MCP Chatbot Constitution
stage: constitution
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: DC
command: /sp.constitution
labels: ["constitution", "phase3", "mcp", "chatbot", "hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

You are operating under a hackathon evaluation environment.

PROJECT CONTEXT:
This is Phase III of a Todo application hackathon.
The goal is to build an AI-powered conversational Todo chatbot using MCP (Model Context Protocol) architecture.

ABSOLUTE RULES (NON-NEGOTIABLE):
- Follow the Agentic Dev Stack strictly: Constitution → Spec → Plan → Tasks → Implementation
- NO manual coding by the human
- ALL logic must be generated via Claude Code
- NO assumptions beyond provided specifications
- NO UI or backend work unless explicitly defined in the spec
- The server MUST be stateless
- Conversation state MUST be persisted in the database
- MCP tools MUST be stateless
- MCP tools MUST ONLY expose task operations
- AI agent MUST use MCP tools for all task actions
- No direct database access by the agent
- No business logic inside the frontend
- Follow hackathon requirements EXACTLY — no feature creep

TECHNOLOGY CONSTRAINTS:
Frontend: OpenAI ChatKit
Backend: Python FastAPI
AI Logic: OpenAI Agents SDK
MCP Server: Official MCP SDK
ORM: SQLModel
Database: Neon Serverless PostgreSQL
Auth: Better Auth

EVALUATION CRITERIA AWARENESS:
- Architectural correctness > UI polish
- Stateless correctness is critical
- Tool usage accuracy is critical
- Natural language → tool mapping must be exact
- MCP compliance is mandatory

Your role:
Act as a senior AI systems architect and backend engineer.
You must not proceed until the full Phase III specification is written and approved.

Acknowledge this constitution and wait.

## Response snapshot

Created Phase 3 constitution (v3.0.0) with complete architectural transformation from full-stack web app to AI-powered conversational chatbot with MCP architecture. Key changes: replaced Next.js with OpenAI ChatKit, added OpenAI Agents SDK, added Official MCP SDK, added 3 new principles (MCP Tool Discipline, Conversation State Persistence, AI Agent Boundary Discipline), added MCP Architecture and AI Agent Architecture sections, added Evaluation Criteria Awareness section. All 10 principles enforce statelessness, MCP compliance, and agent boundaries as required by hackathon evaluation criteria.

## Outcome

- Impact: Major constitutional amendment (v2.0.0 → v3.0.0) establishing Phase 3 MCP chatbot architecture
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md (updated)
- Next prompts: /sp.specify to create the Phase 3 feature specification
- Reflection: Clean transformation preserving SDD principles while completely restructuring for MCP/agent architecture

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
