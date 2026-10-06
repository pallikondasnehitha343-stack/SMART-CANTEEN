'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ApiClient } from '@/lib/api';
import { Order } from '@/lib/types';
import { useAuth } from '@/context/AuthContext';
import { 
  ClipboardList, 
  Clock, 
  ChevronRight, 
  Utensils, 
  CheckCircle, 
  AlertCircle,
  QrCode
} from 'lucide-react';
import { formatINR, formatDateTime, getStatusBadgeColor } from '@/lib/utils';

export default function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadOrders() {
      setIsLoading(true);
      try {
        const data = await ApiClient.get<Order[]>('/orders/my');
        setOrders(data);
      } catch (err) {
        console.error('Failed to load user orders:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadOrders();
  }, [user]);

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            My Campus Orders
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Track real-time queue position and access your digital QR pickup tokens.
          </p>
        </div>
        <Link
          href="/menu"
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition shadow-sm"
        >
          + New Order
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-28 bg-white rounded-3xl border border-slate-200" />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
            <ClipboardList className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800">No Orders Found</h3>
          <p className="text-xs text-slate-500">
            You haven't placed any canteen orders today.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const isActive = ['CONFIRMED', 'QUEUED', 'ACCEPTED', 'PREPARING', 'READY'].includes(
              order.status
            );

            return (
              <Link
                key={order.id}
                href={`/orders/${order.id}`}
                className={`block p-5 sm:p-6 rounded-3xl bg-white border transition hover:shadow-md ${
                  order.status === 'READY'
                    ? 'border-emerald-500 ring-2 ring-emerald-100'
                    : isActive
                    ? 'border-blue-300'
                    : 'border-slate-200'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  {/* Left Info */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-xl font-black text-slate-900 tracking-tight">
                        {order.token_number}
                      </span>
                      <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                        {order.order_number}
                      </span>
                      <span
                        className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${getStatusBadgeColor(
                          order.status
                        )}`}
                      >
                        {order.status}
                      </span>
                    </div>

                    <div className="text-xs text-slate-600 font-medium">
                      {order.items.map((i) => `${i.quantity}x ${i.menu_item_name}`).join(', ')}
                    </div>

                    <div className="flex items-center gap-4 text-xs text-slate-400">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        Placed: {formatDateTime(order.created_at)}
                      </span>
                      {order.pickup_slot && (
                        <span>Slot: {order.pickup_slot.slot_label}</span>
                      )}
                    </div>
                  </div>

                  {/* Right Actions & Amount */}
                  <div className="flex items-center justify-between sm:justify-end gap-4 border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-100">
                    <div className="text-right">
                      <div className="text-lg font-black text-slate-900">
                        {formatINR(order.total_amount)}
                      </div>
                      {isActive && (
                        <div className="text-xs font-bold text-emerald-600 flex items-center gap-1 justify-end">
                          <QrCode className="w-3.5 h-3.5" />
                          <span>View Live Token</span>
                        </div>
                      )}
                    </div>
                    <ChevronRight className="w-5 h-5 text-slate-400" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
