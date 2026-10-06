'use client';

import React from 'react';
import { Users, Clock, AlertCircle } from 'lucide-react';
import { PeakLevel } from '@/lib/types';
import { getPeakBadgeColor } from '@/lib/utils';

interface LiveQueueBadgeProps {
  queuePosition?: number;
  ordersAhead?: number;
  workloadLevel?: PeakLevel;
}

export default function LiveQueueBadge({
  queuePosition = 1,
  ordersAhead = 0,
  workloadLevel = 'NORMAL',
}: LiveQueueBadgeProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200">
      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white rounded-lg border border-slate-200 shadow-sm text-xs font-bold text-slate-800">
        <Users className="w-4 h-4 text-emerald-600" />
        <span>Queue Position:</span>
        <span className="text-emerald-600 font-extrabold text-sm">#{queuePosition}</span>
      </div>

      <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white rounded-lg border border-slate-200 shadow-sm text-xs font-bold text-slate-700">
        <span>Orders Ahead:</span>
        <span className="text-slate-900 font-extrabold">{ordersAhead}</span>
      </div>

      <div className={`px-2.5 py-1 rounded-lg text-xs font-bold shadow-sm ${getPeakBadgeColor(workloadLevel)}`}>
        Workload: {workloadLevel}
      </div>
    </div>
  );
}
