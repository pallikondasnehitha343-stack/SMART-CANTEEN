'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { 
  UtensilsCrossed, 
  ChefHat, 
  ScanLine, 
  BarChart3, 
  Clock, 
  ShieldCheck, 
  Flame, 
  Layers, 
  ArrowRight,
  Sparkles,
  Zap
} from 'lucide-react';

export default function HomePage() {
  const { quickSwitchDemoUser } = useAuth();

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-10 px-4 sm:py-16 rounded-3xl bg-gradient-to-b from-emerald-900 via-emerald-800 to-slate-900 text-white relative overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-500/20 via-transparent to-transparent pointer-events-none" />
        
        <div className="max-w-3xl mx-auto space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold tracking-wide uppercase">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Campus Real-Time Service Orchestration
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
            Zero Physical Queues. <br className="hidden sm:inline" />
            <span className="text-emerald-400">Dynamic Live ETA & Pickup.</span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto">
            An intelligent campus canteen operating system integrating fair aging queues, live kitchen capacity orchestration, dynamic pickup scheduling, and cryptographic QR verification.
          </p>

          {/* Quick CTA */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/menu"
              className="px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-sm flex items-center gap-2 shadow-lg shadow-emerald-500/30 transition transform hover:-translate-y-0.5"
            >
              <UtensilsCrossed className="w-5 h-5" />
              Order Food Now
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/kitchen"
              className="px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm flex items-center gap-2 border border-white/20 backdrop-blur transition"
            >
              <ChefHat className="w-5 h-5 text-amber-400" />
              Open Kitchen Display
            </Link>
          </div>
        </div>
      </section>

      {/* Role Gateways Hub */}
      <section className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            Interactive Operational Portals
          </h2>
          <p className="text-sm text-slate-500">
            Select an operational persona to test the complete end-to-end campus workflow.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Portal 1: Student */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between group">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                <UtensilsCrossed className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-emerald-600 transition">
                Student Ordering
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Browse menu with stock counters, choose capacity-aware pickup slots, pay digitally, and track live queue countdowns.
              </p>
            </div>
            <div className="pt-5 space-y-2">
              <Link
                href="/menu"
                onClick={() => quickSwitchDemoUser('STUDENT')}
                className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold flex items-center justify-center gap-2 transition"
              >
                Launch Student Portal
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Portal 2: Kitchen KDS */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between group">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                <ChefHat className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-amber-600 transition">
                Kitchen KDS
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Live Kanban workflow (Queued, Preparing, Ready) sorted by fair aging priority and preparation complexity.
              </p>
            </div>
            <div className="pt-5 space-y-2">
              <Link
                href="/kitchen"
                onClick={() => quickSwitchDemoUser('STAFF')}
                className="w-full py-2.5 px-4 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold flex items-center justify-center gap-2 transition"
              >
                Open Kitchen Display
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Portal 3: QR Scanner */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between group">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                <ScanLine className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition">
                Pickup QR Terminal
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Counter scanning terminal with single-use verification, replay attack prevention, and instant food handoff.
              </p>
            </div>
            <div className="pt-5 space-y-2">
              <Link
                href="/staff/scanner"
                onClick={() => quickSwitchDemoUser('STAFF')}
                className="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center justify-center gap-2 transition"
              >
                Launch QR Scanner
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Portal 4: Admin & Analytics */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col justify-between group">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 group-hover:text-purple-600 transition">
                Admin Analytics
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Executive metrics, live bottleneck alarms, peak surge classification, and ML demand forecasts.
              </p>
            </div>
            <div className="pt-5 space-y-2">
              <Link
                href="/admin"
                onClick={() => quickSwitchDemoUser('ADMIN')}
                className="w-full py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold flex items-center justify-center gap-2 transition"
              >
                Open Admin Dashboard
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section className="bg-slate-900 text-white p-8 sm:p-10 rounded-3xl space-y-8">
        <div className="max-w-2xl space-y-2">
          <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
            Technical Differentiation
          </div>
          <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
            Real-Time Canteen Orchestration Engine
          </h2>
          <p className="text-sm text-slate-400">
            Transforming static meal ordering into a continuous capacity-aware feedback loop.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 space-y-2.5">
            <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
              <Clock className="w-4 h-4" />
              <span>Deterministic Dynamic ETA</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Calculates ready time based on cumulative queued workload, active kitchen stations, and item prep complexity.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 space-y-2.5">
            <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
              <Layers className="w-4 h-4" />
              <span>Fair Aging Queue Optimizer</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Prevents order starvation by applying dynamic aging credits to waiting orders during peak bursts.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-800/80 border border-slate-700 space-y-2.5">
            <div className="flex items-center gap-2 text-blue-400 font-bold text-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>Cryptographic QR Security</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              HMAC-SHA256 signed pickup tokens with single-use consumption guarantee and replay attack protection.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
