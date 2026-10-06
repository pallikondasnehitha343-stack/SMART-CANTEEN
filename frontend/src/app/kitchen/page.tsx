'use client';

import React, { useState, useEffect } from 'react';
import { ApiClient } from '@/lib/api';
import { Order, QueueSummary } from '@/lib/types';
import { useWebSocket } from '@/context/WebSocketContext';
import KitchenOrderCard from '@/components/KitchenOrderCard';
import { 
  ChefHat, 
  Clock, 
  Flame, 
  RefreshCw, 
  Layers, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';

export default function KitchenKDSPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [queueSummary, setQueueSummary] = useState<QueueSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const { subscribe } = useWebSocket();

  const loadKdsData = async () => {
    try {
      const [orderList, summary] = await Promise.all([
        ApiClient.get<Order[]>('/kitchen/orders'),
        ApiClient.get<QueueSummary>('/queue/summary'),
      ]);
      setOrders(orderList);
      setQueueSummary(summary);
    } catch (err) {
      console.error('Failed to load KDS data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadKdsData();

    // Subscribe to KDS real-time events
    const unsubscribe = subscribe('kitchen:kds', () => {
      loadKdsData();
    });

    return () => unsubscribe();
  }, [subscribe]);

  const handleStartPrep = async (orderId: number) => {
    try {
      await ApiClient.post<Order>(`/kitchen/orders/${orderId}/start-prep`);
      loadKdsData();
    } catch (err) {
      console.error('Failed to start prep:', err);
    }
  };

  const handleMarkReady = async (orderId: number) => {
    try {
      await ApiClient.post<Order>(`/kitchen/orders/${orderId}/mark-ready`);
      loadKdsData();
    } catch (err) {
      console.error('Failed to mark ready:', err);
    }
  };

  const queuedOrders = orders.filter((o) =>
    ['CREATED', 'CONFIRMED', 'QUEUED', 'ACCEPTED'].includes(o.status)
  );
  const preparingOrders = orders.filter((o) => o.status === 'PREPARING');
  const readyOrders = orders.filter((o) => o.status === 'READY');

  return (
    <div className="space-y-6 pb-16">
      {/* KDS Header & Telemetry */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900 text-white p-6 rounded-3xl shadow-xl border border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider">
            <ChefHat className="w-4 h-4" />
            <span>Kitchen Display System (KDS)</span>
          </div>
          <h1 className="text-2xl font-black tracking-tight">
            Live Cooking & Preparation Kanban
          </h1>
        </div>

        {/* Live Workload & Active Stations */}
        <div className="flex items-center gap-3">
          <div className="bg-slate-800 px-4 py-2 rounded-2xl border border-slate-700 text-xs">
            <div className="text-slate-400">Workload</div>
            <div className="font-extrabold text-amber-400 text-sm">
              {queueSummary?.current_kitchen_workload || 'NORMAL'}
            </div>
          </div>

          <div className="bg-slate-800 px-4 py-2 rounded-2xl border border-slate-700 text-xs">
            <div className="text-slate-400">Avg Wait Time</div>
            <div className="font-extrabold text-white text-sm">
              ~{queueSummary?.avg_waiting_time_minutes || 6.5}m
            </div>
          </div>

          <button
            onClick={loadKdsData}
            className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 text-white transition"
            title="Refresh KDS"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* 3-Column Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Column 1: Queued (Incoming) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-2xl text-blue-900">
            <div className="flex items-center gap-2 font-black text-sm">
              <Clock className="w-4 h-4 text-blue-600" />
              <span>Queued (Fair Aging Priority)</span>
            </div>
            <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-black flex items-center justify-center">
              {queuedOrders.length}
            </span>
          </div>

          <div className="space-y-3">
            {queuedOrders.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400 text-xs font-semibold">
                No orders waiting in queue
              </div>
            ) : (
              queuedOrders.map((order) => (
                <KitchenOrderCard
                  key={order.id}
                  order={order}
                  onStartPrep={handleStartPrep}
                  onMarkReady={handleMarkReady}
                />
              ))
            )}
          </div>
        </div>

        {/* Column 2: Preparing (Active Cooking) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-2xl text-amber-900">
            <div className="flex items-center gap-2 font-black text-sm">
              <ChefHat className="w-4 h-4 text-amber-600" />
              <span>Preparing (Cooking Stations)</span>
            </div>
            <span className="w-6 h-6 rounded-full bg-amber-500 text-slate-950 text-xs font-black flex items-center justify-center">
              {preparingOrders.length}
            </span>
          </div>

          <div className="space-y-3">
            {preparingOrders.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400 text-xs font-semibold">
                No orders currently in prep
              </div>
            ) : (
              preparingOrders.map((order) => (
                <KitchenOrderCard
                  key={order.id}
                  order={order}
                  onStartPrep={handleStartPrep}
                  onMarkReady={handleMarkReady}
                />
              ))
            )}
          </div>
        </div>

        {/* Column 3: Ready for Pickup */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-emerald-50 border border-emerald-200 rounded-2xl text-emerald-900">
            <div className="flex items-center gap-2 font-black text-sm">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Ready for Counter Pickup</span>
            </div>
            <span className="w-6 h-6 rounded-full bg-emerald-600 text-white text-xs font-black flex items-center justify-center">
              {readyOrders.length}
            </span>
          </div>

          <div className="space-y-3">
            {readyOrders.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400 text-xs font-semibold">
                No ready orders waiting
              </div>
            ) : (
              readyOrders.map((order) => (
                <KitchenOrderCard
                  key={order.id}
                  order={order}
                  onStartPrep={handleStartPrep}
                  onMarkReady={handleMarkReady}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
