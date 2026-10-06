'use client';

import React from 'react';
import { Check, Clock, ChefHat, Bell, CheckCircle2 } from 'lucide-react';
import { OrderStatus } from '@/lib/types';

interface StatusStepperProps {
  status: OrderStatus;
}

const steps = [
  { key: 'CONFIRMED', label: 'Confirmed', icon: Check },
  { key: 'QUEUED', label: 'In Queue', icon: Clock },
  { key: 'PREPARING', label: 'Preparing', icon: ChefHat },
  { key: 'READY', label: 'Ready', icon: Bell },
  { key: 'PICKED_UP', label: 'Picked Up', icon: CheckCircle2 },
];

export default function StatusStepper({ status }: StatusStepperProps) {
  const getStepIndex = (st: OrderStatus): number => {
    switch (st) {
      case 'CREATED':
      case 'PAYMENT_PENDING':
      case 'CONFIRMED':
        return 0;
      case 'QUEUED':
      case 'ACCEPTED':
        return 1;
      case 'PREPARING':
        return 2;
      case 'READY':
        return 3;
      case 'PICKED_UP':
        return 4;
      default:
        return 0;
    }
  };

  const currentIndex = getStepIndex(status);
  const isCancelled = status === 'CANCELLED' || status === 'REFUNDED';

  if (isCancelled) {
    return (
      <div className="p-3 bg-red-50 text-red-800 text-sm font-bold rounded-xl border border-red-200 text-center">
        Order {status} (Inventory and Slot Released)
      </div>
    );
  }

  return (
    <div className="w-full py-4">
      <div className="flex items-center justify-between relative">
        {/* Progress Line */}
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-slate-200 -z-0" />
        <div
          className="absolute left-0 top-1/2 -translate-y-1/2 h-1 bg-emerald-500 transition-all duration-500 -z-0"
          style={{ width: `${(currentIndex / (steps.length - 1)) * 100}%` }}
        />

        {steps.map((step, idx) => {
          const isCompleted = idx <= currentIndex;
          const isCurrent = idx === currentIndex;
          const Icon = step.icon;

          return (
            <div key={step.key} className="flex flex-col items-center relative z-10">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300 font-bold ${
                  isCompleted
                    ? isCurrent
                      ? 'bg-emerald-600 text-white ring-4 ring-emerald-100 shadow-md scale-110'
                      : 'bg-emerald-500 text-white shadow-sm'
                    : 'bg-white border-2 border-slate-300 text-slate-400'
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
              <span
                className={`text-[11px] mt-1.5 font-bold tracking-tight text-center ${
                  isCurrent
                    ? 'text-emerald-700 font-black'
                    : isCompleted
                    ? 'text-slate-800'
                    : 'text-slate-400'
                }`}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
