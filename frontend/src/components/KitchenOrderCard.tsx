'use client';

import React from 'react';
import { Order, OrderStatus } from '@/lib/types';
import { Clock, Play, CheckCircle, AlertCircle, ChefHat, User } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';

interface KitchenOrderCardProps {
  order: Order;
  onStartPrep: (orderId: number) => Promise<void>;
  onMarkReady: (orderId: number) => Promise<void>;
}

export default function KitchenOrderCard({
  order,
  onStartPrep,
  onMarkReady,
}: KitchenOrderCardProps) {
  const isQueued = order.status === 'QUEUED' || order.status === 'CONFIRMED' || order.status === 'ACCEPTED';
  const isPreparing = order.status === 'PREPARING';
  const isReady = order.status === 'READY';

  return (
    <div
      className={`p-4 rounded-2xl border-2 transition shadow-sm ${
        isPreparing
          ? 'bg-amber-50/60 border-amber-400 ring-2 ring-amber-100 shadow-md'
          : isReady
          ? 'bg-emerald-50/60 border-emerald-400'
          : 'bg-white border-slate-200 hover:border-slate-300'
      }`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200/80">
        <div className="flex items-center gap-2">
          <span className="text-xl font-black text-slate-900 tracking-tight">
            {order.token_number}
          </span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
            {order.order_number}
          </span>
        </div>
        <div className="text-right">
          <div className="text-[11px] font-bold text-slate-500 flex items-center gap-1 justify-end">
            <Clock className="w-3.5 h-3.5" />
            <span>{formatDateTime(order.created_at)}</span>
          </div>
          {order.pickup_slot && (
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded mt-0.5 block">
              Slot: {order.pickup_slot.slot_label}
            </span>
          )}
        </div>
      </div>

      {/* Student & Special Notes */}
      <div className="py-2 text-xs text-slate-600 flex items-center justify-between">
        <span className="flex items-center gap-1 font-medium">
          <User className="w-3.5 h-3.5 text-slate-400" />
          {order.user_name || 'Student'} ({order.campus_id || 'ID'})
        </span>
        <span className="font-semibold text-slate-700">
          ETA: ~{order.estimated_prep_time_minutes} min
        </span>
      </div>

      {order.special_instructions && (
        <div className="p-2 mb-2 bg-amber-100/70 text-amber-900 rounded-lg text-xs font-medium border border-amber-200">
          <strong>Note:</strong> {order.special_instructions}
        </div>
      )}

      {/* Items Breakdown */}
      <div className="space-y-1.5 my-3">
        {order.items.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between text-sm py-1 px-2 rounded-lg bg-slate-50 border border-slate-100"
          >
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-md bg-slate-800 text-white font-black text-xs flex items-center justify-center">
                {item.quantity}x
              </span>
              <span className="font-bold text-slate-900">
                {item.menu_item_name}
              </span>
            </div>
            <span className="text-xs text-slate-500 font-medium">
              ~{item.prep_time_snapshot}m
            </span>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="pt-2">
        {isQueued && (
          <button
            onClick={() => onStartPrep(order.id)}
            className="w-full py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-sm transition active:scale-95"
          >
            <ChefHat className="w-4 h-4" />
            Start Preparing (Station-1)
          </button>
        )}

        {isPreparing && (
          <button
            onClick={() => onMarkReady(order.id)}
            className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-md shadow-emerald-100 transition active:scale-95 animate-pulse"
          >
            <CheckCircle className="w-4 h-4" />
            Mark READY for Pickup
          </button>
        )}

        {isReady && (
          <div className="py-2 text-center text-xs font-bold text-emerald-800 bg-emerald-100 rounded-xl border border-emerald-300">
            Awaiting Student QR Scan at Counter
          </div>
        )}
      </div>
    </div>
  );
}
