'use client';

import AuthGuard from '@/components/auth/AuthGuard';
import AppLayout from '@/components/layout/AppLayout';
import ChatInterface from '@/components/chat/ChatInterface';

export default function ChatPage() {
  return (
    <AuthGuard>
      <AppLayout>
        <div className="h-[calc(100vh-4rem)]">
          <ChatInterface />
        </div>
      </AppLayout>
    </AuthGuard>
  );
}
