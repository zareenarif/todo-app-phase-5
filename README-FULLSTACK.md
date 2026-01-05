# Full-Stack Todo Application (Phase 2)

A modern, production-ready todo application built with FastAPI (backend) and Next.js (frontend).

## 🚀 Features

- ✅ **User Authentication** - JWT-based auth with Better Auth
- ✅ **Complete CRUD Operations** - Create, Read, Update, Delete tasks
- ✅ **Task Management** - Priorities, tags, due dates, recurrence
- ✅ **Responsive Design** - Works on mobile, tablet, and desktop
- ✅ **Real-time Updates** - Instant UI feedback with toast notifications
- ✅ **Data Isolation** - Each user sees only their own tasks
- ✅ **Filtering & Sorting** - Filter by status, priority, tags; sort by multiple fields

## 📋 Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **PostgreSQL** (Neon Serverless)
- **SQLModel** for ORM
- **Alembic** for migrations
- **JWT** authentication
- **Pydantic** for validation

### Frontend
- **Next.js 15+** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Better Auth** (authentication)
- **React 18+**

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL database (or Neon account)
- Git

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   - `DATABASE_URL` - Your PostgreSQL connection string
   - `BETTER_AUTH_SECRET` - A secure random string (min 32 chars)
   - `CORS_ORIGINS` - Frontend URL (e.g., http://localhost:3000)

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

   Backend will be available at: http://localhost:8000
   API docs at: http://localhost:8000/docs

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` and set:
   - `BETTER_AUTH_SECRET` - Same as backend
   - `DATABASE_URL` - Same as backend
   - `NEXT_PUBLIC_API_URL` - Backend URL (e.g., http://localhost:8000/api/v1)

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: http://localhost:3000

## 🌐 Deployment

### Quick Deploy with Vercel & Railway

**1. Backend (Railway):**
```bash
cd backend
npm install -g @railway/cli
railway login
railway init
railway up
```

Set environment variables in Railway dashboard:
- `DATABASE_URL` (Railway can provision PostgreSQL for you)
- `BETTER_AUTH_SECRET`
- `CORS_ORIGINS` (your Vercel URL)

**2. Frontend (Vercel):**
```bash
cd frontend
npm install -g vercel
vercel
```

Set environment variables in Vercel dashboard:
- `BETTER_AUTH_SECRET`
- `DATABASE_URL`
- `NEXT_PUBLIC_API_URL` (your Railway backend URL)

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks (with filters)
- `GET /api/v1/tasks/{id}` - Get single task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Toggle completion

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## 🗂️ Project Structure

```
todo-app-phase1/
├── backend/
│   ├── alembic/              # Database migrations
│   ├── src/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core functionality
│   │   ├── middleware/       # Middleware
│   │   ├── models/           # SQLModel models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── main.py           # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── app/                  # Next.js App Router
│   ├── components/           # React components
│   ├── lib/                  # Utilities
│   └── package.json
└── specs/                    # Documentation & specs
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
DEBUG=False
```

### Frontend (.env.local)
```env
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars
DATABASE_URL=postgresql://user:password@host:5432/dbname
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🎯 Implementation Status

**✅ All 67 Tasks Completed (100%)**

- ✅ Phases 1-2: Setup & foundational infrastructure
- ✅ Phase 3: User authentication with JWT
- ✅ Phase 4: View tasks with filtering and sorting
- ✅ Phase 5: Create tasks with form validation
- ✅ Phase 6: Update tasks with inline editing
- ✅ Phase 7: Delete tasks with confirmation
- ✅ Phase 8: Toggle task completion
- ✅ Phase 9: Responsive design for all devices
- ✅ Phase 10: Polish with loading states and notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Status**: ✅ Production Ready

Made with ❤️ using Claude Code
