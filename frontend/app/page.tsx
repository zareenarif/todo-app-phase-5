/**
 * Landing page - public entry point for the application.
 * Shows welcome message with links to login/register.
 */

import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 relative overflow-hidden">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Hero Section */}
      <div className="min-h-screen flex flex-col items-center justify-center px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main Heading */}
          <div className="mb-8">
            <div className="inline-flex items-center justify-center mb-6 animate-bounce-in">
              <div className="w-24 h-24 bg-white/20 backdrop-blur-lg rounded-3xl shadow-2xl flex items-center justify-center border border-white/30">
                <span className="text-6xl">✓</span>
              </div>
            </div>
            <h1 className="text-6xl md:text-7xl font-extrabold text-white mb-6 drop-shadow-lg animate-fade-in-up">
              Todo App
            </h1>
            <p className="text-2xl md:text-3xl text-white/90 mb-4 font-light animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              Your Personal Productivity Hub
            </p>
            <p className="text-lg md:text-xl text-white/80 max-w-2xl mx-auto animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              Organize tasks, set priorities, track deadlines, and achieve more with our powerful task management system.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up" style={{ animationDelay: '300ms' }}>
            <Link
              href="/register"
              className="group px-8 py-4 bg-white text-indigo-600 font-bold text-lg rounded-xl hover:bg-gray-100 transform hover:scale-105 transition-all duration-200 shadow-xl hover:shadow-2xl flex items-center justify-center gap-2"
            >
              <span>Get Started Free</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </Link>
            <Link
              href="/login"
              className="group px-8 py-4 bg-white/20 backdrop-blur-md text-white font-bold text-lg rounded-xl border-2 border-white/50 hover:bg-white/30 transform hover:scale-105 transition-all duration-200 shadow-lg flex items-center justify-center gap-2"
            >
              <span>Sign In</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
            <div className="p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 hover:-translate-y-2 transition-all duration-300 animate-fade-in-up" style={{ animationDelay: '400ms' }}>
              <div className="text-5xl mb-4 animate-float">🎯</div>
              <h3 className="text-xl font-bold text-white mb-3">
                Set Priorities
              </h3>
              <p className="text-white/80">
                High, medium, or low - organize tasks by importance and never miss what matters most.
              </p>
            </div>

            <div className="p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 hover:-translate-y-2 transition-all duration-300 animate-fade-in-up" style={{ animationDelay: '500ms' }}>
              <div className="text-5xl mb-4 animate-float" style={{ animationDelay: '500ms' }}>🏷️</div>
              <h3 className="text-xl font-bold text-white mb-3">
                Tag & Organize
              </h3>
              <p className="text-white/80">
                Use tags to categorize tasks - work, personal, urgent, or create your own custom tags.
              </p>
            </div>

            <div className="p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 hover:bg-white/20 transform hover:scale-105 hover:-translate-y-2 transition-all duration-300 animate-fade-in-up" style={{ animationDelay: '600ms' }}>
              <div className="text-5xl mb-4 animate-float" style={{ animationDelay: '1s' }}>📅</div>
              <h3 className="text-xl font-bold text-white mb-3">
                Track Deadlines
              </h3>
              <p className="text-white/80">
                Set due dates and recurring tasks with automatic overdue detection to stay on schedule.
              </p>
            </div>
          </div>

          {/* Additional Features */}
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 transform hover:scale-110 transition-all duration-200 animate-scale-in" style={{ animationDelay: '700ms' }}>
              <div className="text-3xl mb-2">✅</div>
              <p className="text-white/90 text-sm font-semibold">Quick Toggle</p>
            </div>
            <div className="p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 transform hover:scale-110 transition-all duration-200 animate-scale-in" style={{ animationDelay: '800ms' }}>
              <div className="text-3xl mb-2">🔍</div>
              <p className="text-white/90 text-sm font-semibold">Smart Search</p>
            </div>
            <div className="p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 transform hover:scale-110 transition-all duration-200 animate-scale-in" style={{ animationDelay: '900ms' }}>
              <div className="text-3xl mb-2">🔄</div>
              <p className="text-white/90 text-sm font-semibold">Recurring Tasks</p>
            </div>
            <div className="p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 transform hover:scale-110 transition-all duration-200 animate-scale-in" style={{ animationDelay: '1000ms' }}>
              <div className="text-3xl mb-2">📱</div>
              <p className="text-white/90 text-sm font-semibold">Mobile Ready</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
