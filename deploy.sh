#!/bin/bash
echo "=== Todo App Deployment ==="

# Backend to Railway
echo "1. Deploy Backend to Railway"
cd backend
railway init
railway add --plugin postgresql  
railway up --detach
BACKEND_URL=$(railway domain)
echo "Backend: $BACKEND_URL"
cd ..

# Frontend to Vercel  
echo "2. Deploy Frontend to Vercel"
cd frontend
vercel --prod
echo "Done!"
