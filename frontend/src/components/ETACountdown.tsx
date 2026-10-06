'use client';

import React, { useState, useEffect } from 'react';
import { Timer, CheckCircle, Bell } from 'lucide-react';
import { OrderStatus } from '@/lib/types';

interface ETACountdownProps {
  status: OrderStatus;
  estimatedReadyTime?: string;
  initialEtaMinutes?: number;
}

export default function ETACountdown({
  status,
  estimatedReadyTime,
  initialEtaMinutes = 10,
}: ETACountdownProps) {
  const [secondsRemaining, setSecondsRemaining] = useState<number>(initialEtaMinutes * 60);

  useEffect(() => {
    if (!estimatedReadyTime) {
      setSecondsRemaining(initialEtaMinutes * 60);
      return;
    }

    const target = new Date(estimatedReadyTime).getTime();
    
    const updateCountdown = () => {
      const now = new Date().getTime();
      const diff = Math.max(0, Math.floor((target - now) / 1000));
      setSecondsRemaining(diff);
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [estimatedReadyTime, initialEtaMinutes]);

  const isReady = status === 'READY' || status === 'PICKED_UP' || secondsRemaining === 0;
  const isPreparing = status === 'PREPARING';

  const mins = Math.floor(secondsRemaining / 60);
  const secs = secondsRemaining % 60;

  if (status === 'READY') {
    return (
      <div className="flex items-center gap-3 p-4 bg-emerald-500 text-white rounded-2xl shadow-lg shadow-emerald-200 animate-pulse">
        <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
          <Bell className="w-6 h-6 animate-bounce" />
        </div>
        <div>
          <div className="text-xs font-black uppercase tracking-wider text-emerald-100">
            Order Status
          </div>
          <div className="text-xl font-black">
            YOUR FOOD IS READY!
          </div>
          <div className="text-xs font-medium text-emerald-50">
            Show your QR Token at the pickup counter.
          </div>
        </div>
      </div>
    );
  }

  if (status === 'PICKED_UP') {
    return (
      <div className="flex items-center gap-3 p-4 bg-slate-800 text-white rounded-2xl shadow-md">
        <CheckCircle className="w-8 h-8 text-emerald-400 flex-shrink-0" />
        <div>
          <div className="text-sm font-bold">Food Picked Up Successfully</div>
          <div className="text-xs text-slate-400">Enjoy your campus meal!</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl shadow-lg border border-slate-700">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
          <Timer className="w-4 h-4 text-emerald-400" />
          <span>Dynamic Live ETA</span>
        </div>
        {isPreparing && (
          <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full animate-pulse">
            Active in Kitchen
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-black tracking-tight text-white">
          {mins}:{secs.toString().padStart(2, '0')}
        </span>
        <span className="text-sm font-semibold text-slate-400">
          mins remaining
        </span>
      </div>

      <div className="mt-2 text-xs text-slate-300 flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
        <span>Continuously updated based on live kitchen workload</span>
      </div>
    </div>
  );
}
