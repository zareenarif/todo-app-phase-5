/**
 * Dashboard page - main protected page for authenticated users.
 * Landing page with quick links to main features.
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import AuthGuard from '@/components/auth/AuthGuard';
import { listTasks } from '@/lib/api';
import { Task } from '@/lib/types';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch tasks for statistics
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const fetchedTasks = await listTasks();
        setTasks(fetchedTasks);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  // Calculate statistics
  const completedTasks = tasks.filter(task => task.completed).length;
  const pendingTasks = tasks.filter(task => !task.completed).length;
  const totalTasks = tasks.length;
  const overdueTasks = tasks.filter(task =>
    !task.completed && task.due_date && new Date(task.due_date) < new Date()
  ).length;

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Welcome Header */}
          <div className="mb-12 text-center animate-fade-in-down">
            <h1 className="text-5xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-4">
              Welcome Back! 👋
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Ready to tackle your tasks? Let's make today productive!
            </p>
          </div>

          {/* Quick Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {/* View Tasks Card */}
            <Link
              href="/tasks"
              className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 border border-white transform hover:scale-105 hover:-translate-y-2 animate-fade-in-up"
            >
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">📋</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">
                View Tasks
              </h3>
              <p className="text-gray-600 text-lg mb-4">
                See all your tasks, filter by priority, status, and manage them efficiently.
              </p>
              <div className="flex items-center text-indigo-600 font-bold group-hover:gap-3 transition-all duration-300">
                <span>Go to Tasks</span>
                <span className="transform group-hover:translate-x-2 transition-transform duration-300">→</span>
              </div>
            </Link>

            {/* Create Task Card */}
            <Link
              href="/tasks"
              className="group bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 border border-white/20 transform hover:scale-105 hover:-translate-y-2 animate-fade-in-up"
              style={{ animationDelay: '100ms' }}
            >
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">➕</div>
              <h3 className="text-2xl font-bold text-white mb-3">
                Create Task
              </h3>
              <p className="text-white/90 text-lg mb-4">
                Add new tasks with priorities, tags, due dates, and recurrence.
              </p>
              <div className="flex items-center text-white font-bold group-hover:gap-3 transition-all duration-300">
                <span>Create Now</span>
                <span className="transform group-hover:translate-x-2 transition-transform duration-300">→</span>
              </div>
            </Link>

            {/* Statistics Card - Coming Soon */}
            <div className="relative bg-white/40 backdrop-blur-sm rounded-2xl shadow-lg p-8 border border-white/50 overflow-hidden animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <div className="absolute top-4 right-4">
                <span className="px-3 py-1 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full">
                  Coming Soon
                </span>
              </div>
              <div className="text-6xl mb-4 opacity-50">📊</div>
              <h3 className="text-2xl font-bold text-gray-700 mb-3">
                Statistics
              </h3>
              <p className="text-gray-500 text-lg">
                View your productivity stats, task completion trends, and insights.
              </p>
            </div>
          </div>

          {/* Feature Highlights */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-8 border border-white animate-scale-in" style={{ animationDelay: '300ms' }}>
            <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
              ✨ Powerful Features
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-4xl mb-2">🎯</div>
                <p className="text-sm font-bold text-gray-700">Set Priorities</p>
                <p className="text-xs text-gray-500">High, Medium, Low</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">🏷️</div>
                <p className="text-sm font-bold text-gray-700">Add Tags</p>
                <p className="text-xs text-gray-500">Organize by category</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">📅</div>
                <p className="text-sm font-bold text-gray-700">Due Dates</p>
                <p className="text-xs text-gray-500">Never miss deadlines</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">🔄</div>
                <p className="text-sm font-bold text-gray-700">Recurring</p>
                <p className="text-xs text-gray-500">Daily, Weekly, Monthly</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">🔍</div>
                <p className="text-sm font-bold text-gray-700">Filter Tasks</p>
                <p className="text-xs text-gray-500">Find what you need</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">📊</div>
                <p className="text-sm font-bold text-gray-700">Sort Options</p>
                <p className="text-xs text-gray-500">Multiple sort methods</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">✏️</div>
                <p className="text-sm font-bold text-gray-700">Quick Edit</p>
                <p className="text-xs text-gray-500">Update tasks easily</p>
              </div>
              <div className="text-center">
                <div className="text-4xl mb-2">✅</div>
                <p className="text-sm font-bold text-gray-700">Toggle Done</p>
                <p className="text-xs text-gray-500">Track completion</p>
              </div>
            </div>
          </div>

          {/* Quick Stats Preview */}
          <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Total Tasks */}
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
              <div className="text-5xl mb-2">📊</div>
              <p className="text-sm font-medium opacity-90">Total Tasks</p>
              <p className="text-5xl font-extrabold">
                {loading ? '...' : totalTasks}
              </p>
            </div>

            {/* Completed Tasks */}
            <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200 animate-fade-in-up" style={{ animationDelay: '500ms' }}>
              <div className="text-5xl mb-2">✅</div>
              <p className="text-sm font-medium opacity-90">Completed</p>
              <p className="text-5xl font-extrabold">
                {loading ? '...' : completedTasks}
              </p>
              {!loading && totalTasks > 0 && (
                <p className="text-xs opacity-75 mt-1">
                  {Math.round((completedTasks / totalTasks) * 100)}% done
                </p>
              )}
            </div>

            {/* Pending Tasks */}
            <div className="bg-gradient-to-br from-yellow-500 to-orange-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200 animate-fade-in-up" style={{ animationDelay: '600ms' }}>
              <div className="text-5xl mb-2">⏳</div>
              <p className="text-sm font-medium opacity-90">Pending</p>
              <p className="text-5xl font-extrabold">
                {loading ? '...' : pendingTasks}
              </p>
              {!loading && totalTasks > 0 && (
                <p className="text-xs opacity-75 mt-1">
                  {Math.round((pendingTasks / totalTasks) * 100)}% remaining
                </p>
              )}
            </div>

            {/* Overdue Tasks */}
            <div className="bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200 animate-fade-in-up" style={{ animationDelay: '700ms' }}>
              <div className="text-5xl mb-2">⚠️</div>
              <p className="text-sm font-medium opacity-90">Overdue</p>
              <p className="text-5xl font-extrabold">
                {loading ? '...' : overdueTasks}
              </p>
              {!loading && overdueTasks > 0 && (
                <p className="text-xs opacity-75 mt-1">Need attention!</p>
              )}
            </div>
          </div>

          {/* Quick Action Reminder */}
          {!loading && totalTasks === 0 && (
            <div className="mt-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl shadow-lg p-8 text-center text-white animate-scale-in" style={{ animationDelay: '800ms' }}>
              <div className="text-6xl mb-4 animate-bounce-in">🚀</div>
              <h3 className="text-2xl font-bold mb-2">Ready to Get Started?</h3>
              <p className="text-lg mb-6 opacity-90">Create your first task and start being productive!</p>
              <Link
                href="/tasks"
                className="inline-block px-8 py-4 bg-white text-indigo-600 font-bold rounded-xl hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 shadow-lg"
              >
                Create Your First Task
              </Link>
            </div>
          )}
        </div>
      </div>
    </AuthGuard>
  );
}
