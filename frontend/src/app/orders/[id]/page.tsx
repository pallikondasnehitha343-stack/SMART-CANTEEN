'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ApiClient } from '@/lib/api';
import { Order } from '@/lib/types';
import { useWebSocket } from '@/context/WebSocketContext';
import StatusStepper from '@/components/StatusStepper';
import ETACountdown from '@/components/ETACountdown';
import LiveQueueBadge from '@/components/LiveQueueBadge';
import QRCodeDisplay from '@/components/QRCodeDisplay';
import { 
  ArrowLeft, 
  Clock, 
  MapPin, 
  Receipt, 
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { formatINR, formatDateTime, getStatusBadgeColor } from '@/lib/utils';

export default function OrderTrackingPage() {
  const params = useParams();
  const router = useRouter();
  const orderId = Number(params.id);

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { subscribe } = useWebSocket();

  const fetchOrderDetails = async () => {
    try {
      const data = await ApiClient.get<Order>(`/orders/${orderId}`);
      setOrder(data);
    } catch (err: any) {
      console.error('Failed to load order tracking details:', err);
      setErrorMessage(err.message || 'Order not found');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderDetails();

    // Subscribe to real-time order specific updates
    const unsubscribe = subscribe(`order:${orderId}`, (updatedData) => {
      if (updatedData) {
        setOrder((prev) => (prev ? { ...prev, ...updatedData } : updatedData));
      }
    });

    return () => unsubscribe();
  }, [orderId, subscribe]);

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center space-y-4 animate-pulse">
        <div className="w-16 h-16 bg-slate-200 rounded-3xl mx-auto" />
        <div className="h-6 bg-slate-200 rounded w-1/2 mx-auto" />
        <div className="h-32 bg-white rounded-3xl border border-slate-200" />
      </div>
    );
  }

  if (!order || errorMessage) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-800">Unable to load order</h2>
        <p className="text-xs text-slate-500">{errorMessage || 'Order ID invalid'}</p>
        <Link
          href="/orders"
          className="inline-block px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold"
        >
          Return to Orders
        </Link>
      </div>
    );
  }

  const isReady = order.status === 'READY';
  const isUsed = order.is_qr_used === 1 || order.status === 'PICKED_UP';

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-20">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <Link
          href="/orders"
          className="flex items-center gap-1 text-xs font-bold text-slate-600 hover:text-slate-900 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Orders</span>
        </Link>
        <button
          onClick={fetchOrderDetails}
          className="flex items-center gap-1 text-xs font-bold text-emerald-600 hover:text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Order Status Stepper Card */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Order Reference
            </div>
            <div className="text-lg font-black text-slate-900">
              {order.order_number}
            </div>
          </div>
          <span
            className={`text-xs font-bold px-3 py-1 rounded-full border ${getStatusBadgeColor(
              order.status
            )}`}
          >
            {order.status}
          </span>
        </div>

        {/* Visual Stepper */}
        <StatusStepper status={order.status} />

        {/* Live Queue Telemetry Badge */}
        {order.status !== 'PICKED_UP' && order.status !== 'CANCELLED' && (
          <LiveQueueBadge
            queuePosition={order.queue_position}
            ordersAhead={order.orders_ahead}
            workloadLevel={order.kitchen_workload_level}
          />
        )}
      </div>

      {/* Dynamic Live Countdown ETA */}
      <ETACountdown
        status={order.status}
        estimatedReadyTime={order.estimated_ready_time}
        initialEtaMinutes={order.estimated_prep_time_minutes}
      />

      {/* Cryptographic QR Pickup Token */}
      <QRCodeDisplay
        qrToken={order.pickup_qr_token}
        orderNumber={order.order_number}
        tokenNumber={order.token_number}
        isReady={isReady}
        isUsed={isUsed}
      />

      {/* Order Item Details & Receipt */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 border-b border-slate-100 pb-3">
          <Receipt className="w-4 h-4 text-slate-400" />
          Order Items Breakdown
        </h3>

        <div className="divide-y divide-slate-100 text-xs">
          {order.items.map((item) => (
            <div key={item.id} className="py-2.5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-800">
                  {item.quantity}x
                </span>
                <span className="text-slate-700">{item.menu_item_name}</span>
              </div>
              <span className="font-bold text-slate-900">
                {formatINR(item.total_price)}
              </span>
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-slate-200 flex items-baseline justify-between">
          <span className="text-xs font-bold text-slate-600">Total Paid</span>
          <span className="text-lg font-black text-slate-900">
            {formatINR(order.total_amount)}
          </span>
        </div>

        {order.special_instructions && (
          <div className="p-3 bg-slate-50 text-slate-600 rounded-xl text-xs">
            <strong>Notes:</strong> {order.special_instructions}
          </div>
        )}
      </div>
    </div>
  );
}
