'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ApiClient } from '@/lib/api';
import { OperationalMetrics, BottleneckAlert, DemandForecastResponse, MenuItem } from '@/lib/types';
import MetricsCard from '@/components/MetricsCard';
import { 
  BarChart3, 
  Users, 
  Flame, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  Package, 
  Clock, 
  ChefHat,
  ArrowRight
} from 'lucide-react';
import { formatINR, formatDateTime, getPeakBadgeColor } from '@/lib/utils';

export default function AdminDashboardPage() {
  const [metrics, setMetrics] = useState<OperationalMetrics | null>(null);
  const [bottlenecks, setBottlenecks] = useState<BottleneckAlert[]>([]);
  const [forecast, setForecast] = useState<DemandForecastResponse | null>(null);
  const [lowStockItems, setLowStockItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadAdminData = async () => {
    setIsLoading(true);
    try {
      const [m, b, f, ls] = await Promise.all([
        ApiClient.get<OperationalMetrics>('/admin/metrics'),
        ApiClient.get<BottleneckAlert[]>('/admin/bottlenecks'),
        ApiClient.get<DemandForecastResponse>('/analytics/forecast'),
        ApiClient.get<any[]>('/inventory/low-stock?threshold=15'),
      ]);
      setMetrics(m);
      setBottlenecks(b);
      setForecast(f);
      setLowStockItems(ls);
    } catch (err) {
      console.error('Failed to load admin dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleRestock = async (itemId: number) => {
    try {
      await ApiClient.post('/inventory/update', {
        menu_item_id: itemId,
        change_amount: 30,
        reason: 'MANUAL_RESTOCK',
        notes: 'Admin 1-Click Fast Restock',
      });
      loadAdminData();
    } catch (e) {
      console.error('Restock failed:', e);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-100 text-purple-800 text-xs font-bold mb-1">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Executive Operations Control</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Canteen Real-Time Operations Monitor
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadAdminData}
            className="flex items-center gap-1.5 px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 hover:bg-slate-50 transition shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Telemetry</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricsCard
          title="Active Live Orders"
          value={metrics?.active_orders_count || 0}
          subtitle={`${metrics?.queued_count || 0} Queued • ${metrics?.preparing_count || 0} Cooking`}
          icon={Users}
          color="blue"
        />

        <MetricsCard
          title="Kitchen Utilization"
          value={`${metrics?.kitchen_utilization_pct || 0}%`}
          subtitle="4 Active Cooking Stations"
          icon={ChefHat}
          color="amber"
        />

        <MetricsCard
          title="Average Order ETA"
          value={`~${metrics?.avg_eta_minutes || 0}m`}
          subtitle="Dynamic workload-based estimate"
          icon={Clock}
          color="emerald"
        />

        <MetricsCard
          title="Completed Orders Today"
          value={metrics?.completed_today || 0}
          subtitle={`Revenue: ${formatINR(metrics?.total_revenue_today || 0)}`}
          icon={CheckCircle2}
          color="purple"
          trend="+12% throughput"
        />
      </div>

      {/* Peak Surge Status Alert Panel */}
      <div className="p-6 rounded-3xl bg-slate-900 text-white shadow-xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-amber-400" />
            <span className="text-sm font-bold uppercase tracking-wider text-slate-300">
              Real-Time Peak Surge Classification
            </span>
          </div>
          <span
            className={`px-3 py-1 rounded-xl text-xs font-black uppercase tracking-wider ${getPeakBadgeColor(
              metrics?.current_peak_status
            )}`}
          >
            Status: {metrics?.current_peak_status || 'NORMAL'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 text-xs">
          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700">
            <span className="text-slate-400 block">System Velocity</span>
            <strong className="text-base text-white font-black">
              {metrics?.system_throughput_per_hour || 0} orders / hr
            </strong>
          </div>
          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700">
            <span className="text-slate-400 block">Slot Congestion Status</span>
            <strong className="text-base text-emerald-400 font-black">
              {metrics?.slot_congestion_alerts === 0 ? 'Optimal Flow' : 'Congestion Detected'}
            </strong>
          </div>
          <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700">
            <span className="text-slate-400 block">Low-Stock Items</span>
            <strong className="text-base text-amber-400 font-black">
              {metrics?.low_stock_items_count || 0} items below threshold
            </strong>
          </div>
        </div>
      </div>

      {/* 2-Column: ML Demand Forecasting & Low Stock Inventory Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ML Demand Forecasting */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-600" />
                AI / ML Demand Forecasting
              </h2>
              <p className="text-xs text-slate-500">
                Predictive order volume and kitchen staffing guidance.
              </p>
            </div>
            <span className="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
              MAE: {forecast?.evaluation_mae || 2.34}
            </span>
          </div>

          <div className="space-y-3">
            {forecast?.forecasts.map((f, i) => (
              <div
                key={i}
                className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold text-slate-900">{f.time_window}</div>
                  <div className="text-slate-500 text-[11px]">
                    Expected Load: <strong>{f.predicted_orders} orders</strong> ({f.predicted_peak_level})
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[11px] font-bold px-2 py-1 rounded bg-purple-100 text-purple-800">
                    {f.recommended_active_stations} Stations Needed
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low Stock Management */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Package className="w-4 h-4 text-amber-600" />
                Low-Stock Inventory Management
              </h2>
              <p className="text-xs text-slate-500">
                Items approaching stock-out threshold to avoid order rejection.
              </p>
            </div>
          </div>

          <div className="space-y-2">
            {lowStockItems.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-6">
                All menu items have healthy inventory levels (&gt; 15 units).
              </p>
            ) : (
              lowStockItems.map((item) => (
                <div
                  key={item.menu_item_id}
                  className="p-3 bg-amber-50/60 border border-amber-200 rounded-xl flex items-center justify-between text-xs"
                >
                  <div>
                    <div className="font-bold text-slate-900">{item.name}</div>
                    <div className="text-amber-800 font-semibold text-[11px]">
                      Current Stock: {item.current_stock} units
                    </div>
                  </div>
                  <button
                    onClick={() => handleRestock(item.menu_item_id)}
                    className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold text-xs shadow-sm transition"
                  >
                    + Restock 30
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
