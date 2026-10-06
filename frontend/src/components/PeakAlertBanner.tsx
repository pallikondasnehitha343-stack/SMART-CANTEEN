'use client';

import React, { useEffect, useState } from 'react';
import { Flame, AlertTriangle, Clock, CheckCircle2 } from 'lucide-react';
import { ApiClient } from '@/lib/api';
import { PeakLevel } from '@/lib/types';
import { useWebSocket } from '@/context/WebSocketContext';

interface PeakState {
  peak_status: PeakLevel;
  active_orders_count: number;
  recommendation: string;
}

export default function PeakAlertBanner() {
  const [peak, setPeak] = useState<PeakState>({
    peak_status: 'NORMAL',
    active_orders_count: 0,
    recommendation: 'Optimal canteen throughput. Orders prepared swiftly.',
  });
  const { subscribe } = useWebSocket();

  useEffect(() => {
    // Fetch initial metrics
    ApiClient.get<any>('/admin/metrics')
      .then((data) => {
        if (data && data.current_peak_status) {
          setPeak({
            peak_status: data.current_peak_status,
            active_orders_count: data.active_orders_count,
            recommendation: data.current_peak_status === 'CRITICAL'
              ? 'Peak Lunch Surge! Select later pickup slots to minimize waiting.'
              : data.current_peak_status === 'HIGH'
              ? 'High demand period. Real-time ETA optimization active.'
              : 'Smooth operations. Instant order processing.',
          });
        }
      })
      .catch(() => {});

    // Listen to live queue updates
    const unsubscribe = subscribe('queue:updates', (msg) => {
      if (msg && msg.data && msg.data.current_kitchen_workload) {
        setPeak((prev) => ({
          ...prev,
          peak_status: msg.data.current_kitchen_workload,
          active_orders_count: msg.data.total_active_orders || prev.active_orders_count,
        }));
      }
    });

    return () => unsubscribe();
  }, [subscribe]);

  if (peak.peak_status === 'NORMAL') {
    return null; // Don't crowd UI during calm periods
  }

  const isCritical = peak.peak_status === 'CRITICAL';
  const isHigh = peak.peak_status === 'HIGH';

  return (
    <div
      className={`px-4 py-2.5 text-xs sm:text-sm font-semibold border-b flex items-center justify-between ${
        isCritical
          ? 'bg-red-600 text-white border-red-700 animate-pulse'
          : isHigh
          ? 'bg-amber-500 text-slate-950 border-amber-600'
          : 'bg-amber-100 text-amber-900 border-amber-300'
      }`}
    >
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isCritical ? (
            <Flame className="w-5 h-5 flex-shrink-0 animate-bounce" />
          ) : (
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          )}
          <span>
            <strong>CANTEEN PEAK STATUS: [{peak.peak_status}]</strong> —{' '}
            {peak.recommendation} ({peak.active_orders_count} active orders in queue)
          </span>
        </div>
        <span className="hidden md:inline-block text-[11px] uppercase tracking-wider font-black opacity-90 px-2 py-0.5 bg-black/15 rounded">
          Dynamic Slot Optimization Active
        </span>
      </div>
    </div>
  );
}
