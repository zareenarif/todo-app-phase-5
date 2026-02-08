'use client';

import Link from 'next/link';
import Logo from '@/components/ui/Logo';
import {
  Zap,
  BarChart3,
  Calendar,
  Bot,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

const features = [
  {
    icon: Zap,
    title: 'AI Task Prioritization',
    description:
      'Let AI analyze and prioritize your tasks based on deadlines, importance, and your work patterns.',
    color: 'from-purple-500 to-violet-500',
  },
  {
    icon: BarChart3,
    title: 'Progress Analytics',
    description:
      'Track your productivity with detailed analytics, insights, and beautiful visualizations.',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Bot,
    title: 'AI Assistant',
    description:
      'Chat with AI to break down complex tasks, get suggestions, and optimize your workflow.',
    color: 'from-pink-500 to-rose-500',
  },
  {
    icon: Calendar,
    title: 'Smart Scheduling',
    description:
      'Automatically schedule tasks based on your availability and optimal work hours.',
    color: 'from-green-500 to-emerald-500',
  },
];

const stats = [
  { value: '10K+', label: 'Active Users' },
  { value: '1M+', label: 'Tasks Completed' },
  { value: '99.9%', label: 'Uptime' },
  { value: '4.9/5', label: 'User Rating' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen w-full bg-white dark:bg-gray-950">
      {/* Navigation */}
      <nav className="animate-fade-in-down sticky top-0 z-50 w-full border-b border-gray-100 bg-white/80 backdrop-blur-xl dark:border-gray-800/50 dark:bg-gray-950/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center">
              <Logo size="md" />
            </Link>
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
              >
                Sign In
              </Link>
              <Link href="/register" className="btn-primary text-sm">
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="w-full px-4 pt-20 pb-24 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <div className="animate-fade-in-up mb-6 inline-flex items-center gap-2 rounded-full bg-purple-100 px-4 py-1.5 dark:bg-purple-900/30">
              <Sparkles className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <span className="text-sm font-medium text-purple-700 dark:text-purple-300">
                AI-Powered Productivity
              </span>
            </div>

            {/* Headline */}
            <h1 className="animate-fade-in-up mb-6 text-4xl font-bold leading-tight tracking-tight text-gray-900 dark:text-white sm:text-5xl lg:text-6xl">
              Organize your work,
              <br />
              <span className="text-gradient-hero">amplify your life</span>
            </h1>

            {/* Subheadline */}
            <p className="animate-fade-in-up mx-auto mb-10 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
              TaskFlow combines intelligent task management with AI assistance to
              help you focus on what matters most. Plan smarter, achieve more.
            </p>

            {/* CTA Buttons */}
            <div className="animate-fade-in-up flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/register" className="btn-primary px-8 py-3 text-base">
                Start Free Trial
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/login" className="btn-secondary px-8 py-3 text-base">
                Sign In
              </Link>
            </div>

            {/* Social Proof */}
            <div className="animate-fade-in mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[
                    'bg-purple-500',
                    'bg-blue-500',
                    'bg-pink-500',
                    'bg-indigo-500',
                  ].map((bg, i) => (
                    <div
                      key={i}
                      className={`h-8 w-8 shrink-0 rounded-full border-2 border-white dark:border-gray-900 ${bg}`}
                    />
                  ))}
                </div>
                <span>10,000+ users</span>
              </div>
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <svg
                    key={i}
                    width={16}
                    height={16}
                    className="h-4 w-4 shrink-0 fill-current text-yellow-400"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                ))}
                <span className="ml-1">4.9/5 rating</span>
              </div>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="animate-fade-in-up relative mt-20">
            <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl dark:border-gray-800 dark:bg-gray-900">
              {/* Browser Header */}
              <div className="flex items-center gap-2 border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-red-400" />
                  <div className="h-3 w-3 rounded-full bg-yellow-400" />
                  <div className="h-3 w-3 rounded-full bg-green-400" />
                </div>
                <div className="flex-1 text-center">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    taskflow.app/dashboard
                  </span>
                </div>
              </div>
              {/* Dashboard Content */}
              <div className="grid grid-cols-3 gap-4 p-6">
                {/* Sidebar Preview */}
                <div className="col-span-1 space-y-3">
                  <div className="h-8 w-24 rounded bg-purple-100 dark:bg-purple-900/30" />
                  <div className="space-y-2">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className={`h-8 rounded-lg ${
                          i === 1
                            ? 'bg-purple-500/20'
                            : 'bg-gray-100 dark:bg-gray-800'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                {/* Main Content Preview */}
                <div className="col-span-2 space-y-4">
                  <div className="flex gap-4">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="flex-1 rounded-lg bg-gradient-to-br from-purple-100 to-blue-100 p-3 dark:from-purple-900/20 dark:to-blue-900/20"
                      >
                        <div className="mb-2 h-3 w-12 rounded bg-gray-300 dark:bg-gray-700" />
                        <div className="h-6 w-8 rounded bg-gray-400 dark:bg-gray-600" />
                      </div>
                    ))}
                  </div>
                  <div className="space-y-2">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="flex h-14 items-center gap-3 rounded-lg border border-gray-200 p-3 dark:border-gray-700"
                      >
                        <div className="h-5 w-5 rounded border-2 border-purple-400" />
                        <div className="h-3 flex-1 rounded bg-gray-200 dark:bg-gray-700" />
                        <div className="h-5 w-16 rounded-full bg-purple-100 dark:bg-purple-900/30" />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full bg-gray-50/80 px-4 py-24 dark:bg-gray-900/50 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
              Everything you need to stay productive
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-400">
              Powerful features designed to help you manage tasks efficiently and
              achieve your goals faster.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-2xl border border-gray-200 bg-white p-6 transition-all hover:border-purple-200 hover:shadow-xl dark:border-gray-800 dark:bg-gray-900 dark:hover:border-purple-800"
              >
                <div
                  className={`mb-4 inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${feature.color}`}
                >
                  <feature.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="w-full px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="text-center"
              >
                <div className="text-gradient mb-1 text-3xl font-bold">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-purple-600 via-violet-600 to-blue-600 p-12 text-center">
            <h2 className="mb-4 text-3xl font-bold text-white">
              Ready to boost your productivity?
            </h2>
            <p className="mx-auto mb-8 max-w-lg text-purple-100">
              Join thousands of professionals who are already managing their
              tasks smarter with TaskFlow.
            </p>
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-8 py-3 font-medium text-purple-600 transition-colors hover:bg-purple-50"
            >
              Get Started Free
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full border-t border-gray-100 px-4 py-8 dark:border-gray-800 sm:px-6 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 sm:flex-row">
          <Logo size="sm" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            &copy; 2024 TaskFlow. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
