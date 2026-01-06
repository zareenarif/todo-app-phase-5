/**
 * Login page - Better Auth login form.
 * Allows existing users to sign in with beautiful animations.
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!email || !password) {
      setError('Email and password are required');
      return;
    }

    setLoading(true);

    try {
      // TODO: Replace with actual Better Auth login
      // For now, this is a placeholder that demonstrates the expected flow
      // In actual implementation:
      // const result = await signIn({ email, password });
      // if (result.success) { ... }

      // Placeholder: simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Store mock JWT (in actual implementation, Better Auth handles this)
      localStorage.setItem('jwt_token', 'mock-jwt-token');

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Login card */}
      <div className="max-w-md w-full relative z-10">
        {/* Logo/Brand */}
        <div className="text-center mb-8 animate-fade-in-down">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-lg rounded-3xl shadow-2xl mb-4 border border-white/30">
            <span className="text-5xl animate-bounce-in">✓</span>
          </div>
          <h1 className="text-4xl font-extrabold text-white mb-2 drop-shadow-lg">
            Welcome Back
          </h1>
          <p className="text-white/90 text-lg">
            Sign in to continue your productivity journey
          </p>
        </div>

        {/* Login form card */}
        <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/50 animate-scale-in">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-xl bg-red-50 border-2 border-red-200 p-4 animate-fade-in-up">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">⚠️</span>
                  <p className="text-sm text-red-800 font-medium">{error}</p>
                </div>
              </div>
            )}

            <div className="space-y-5">
              {/* Email input */}
              <div className="group">
                <label htmlFor="email" className="block text-sm font-bold text-gray-700 mb-2 transition-colors group-focus-within:text-indigo-600">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-400 text-xl">📧</span>
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="block w-full pl-12 pr-4 py-3.5 border-2 border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 text-base"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              {/* Password input */}
              <div className="group">
                <label htmlFor="password" className="block text-sm font-bold text-gray-700 mb-2 transition-colors group-focus-within:text-indigo-600">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span className="text-gray-400 text-xl">🔒</span>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-12 pr-4 py-3.5 border-2 border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-100 focus:border-indigo-500 transition-all duration-200 text-base"
                    placeholder="Enter your password"
                  />
                </div>
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
              className="relative w-full flex justify-center items-center gap-3 py-4 px-6 border border-transparent text-base font-bold rounded-xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-2xl"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <span className="text-xl">→</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="mt-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t-2 border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500 font-medium">New to Todo App?</span>
            </div>
          </div>

          {/* Register link */}
          <div className="mt-6 text-center">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 text-base font-bold text-indigo-600 hover:text-indigo-800 transition-colors"
            >
              <span>Create an account</span>
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </Link>
          </div>
        </div>

        {/* Back to home */}
        <div className="mt-6 text-center animate-fade-in-up">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-white/90 hover:text-white font-medium transition-colors"
          >
            <span>←</span>
            <span>Back to home</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
