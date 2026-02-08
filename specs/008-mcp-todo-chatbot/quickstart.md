# Quickstart: AI-Powered Todo Chatbot

## Prerequisites

- Python 3.11+
- Node.js 18+
- Neon PostgreSQL database (provisioned)
- OpenAI API key

## Environment Variables

Create `backend/.env`:
```
DATABASE_URL=postgresql://...@neon.tech/...
BETTER_AUTH_SECRET=your-secret
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
```

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Verify

1. Register a user via `POST /api/v1/auth/register`
2. Login via `POST /api/v1/auth/login` to get JWT
3. Send chat message:
   ```bash
   curl -X POST http://localhost:8000/api/{user_id}/chat \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"message": "Add a task to buy groceries"}'
   ```
4. Verify response contains `conversation_id`, `response`, and
   `tool_calls`

## Validation Checks

- [ ] Chat endpoint returns valid response
- [ ] Task appears in database after add_task
- [ ] Conversation and messages persisted in database
- [ ] Server restart preserves all data
- [ ] Different users cannot see each other's tasks
