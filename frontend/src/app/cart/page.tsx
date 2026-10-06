'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCart } from '@/context/CartContext';
import { PickupSlot } from '@/lib/types';
import { ApiClient } from '@/lib/api';
import { 
  Trash2, 
  Plus, 
  Minus, 
  Clock, 
  Sparkles, 
  ArrowRight, 
  ShoppingCart, 
  AlertCircle,
  FileText,
  ChevronRight
} from 'lucide-react';
import { formatINR } from '@/lib/utils';

export default function CartPage() {
  const router = useRouter();
  const {
    items,
    updateQuantity,
    removeItem,
    clearCart,
    subtotal,
    totalItemsCount,
    selectedSlot,
    setSelectedSlot,
    specialInstructions,
    setSpecialInstructions,
  } = useCart();

  const [slots, setSlots] = useState<PickupSlot[]>([]);
  const [isLoadingSlots, setIsLoadingSlots] = useState<boolean>(true);

  useEffect(() => {
    async function fetchSlots() {
      setIsLoadingSlots(true);
      try {
        const data = await ApiClient.get<PickupSlot[]>('/pickup/slots');
        setSlots(data);
        // Auto-select recommended slot if not chosen
        if (!selectedSlot && data.length > 0) {
          const rec = data.find((s) => s.is_recommended) || data.find((s) => s.status === 'AVAILABLE') || data[0];
          setSelectedSlot(rec);
        }
      } catch (err) {
        console.error('Failed to load slots:', err);
      } finally {
        setIsLoadingSlots(false);
      }
    }
    fetchSlots();
  }, [selectedSlot, setSelectedSlot]);

  if (items.length === 0) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4">
        <div className="w-16 h-16 rounded-3xl bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
          <ShoppingCart className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-black text-slate-900">Your Cart is Empty</h2>
        <p className="text-sm text-slate-500">
          Looks like you haven't added any campus meals to your cart yet.
        </p>
        <div className="pt-2">
          <Link
            href="/menu"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-200 transition"
          >
            Explore Menu
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Review Order & Pickup Slot
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Select a dynamic pickup window to avoid peak-hour counter waiting.
          </p>
        </div>
        <button
          onClick={clearCart}
          className="text-xs font-semibold text-red-600 hover:text-red-700 hover:bg-red-50 px-3 py-1.5 rounded-lg border border-red-200 transition"
        >
          Clear Cart
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Cart Items & Special Instructions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Item List */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3">
              Selected Items ({totalItemsCount})
            </h2>

            <div className="divide-y divide-slate-100">
              {items.map(({ menuItem, quantity }) => (
                <div key={menuItem.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-slate-900">
                        {menuItem.name}
                      </span>
                      <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        ~{menuItem.prep_time_minutes}m
                      </span>
                    </div>
                    <div className="text-xs font-black text-emerald-600">
                      {formatINR(menuItem.price * quantity)}
                      <span className="text-[10px] text-slate-400 font-normal ml-1">
                        ({formatINR(menuItem.price)} each)
                      </span>
                    </div>
                  </div>

                  {/* Quantity Stepper */}
                  <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl p-1">
                    <button
                      onClick={() => updateQuantity(menuItem.id, quantity - 1)}
                      className="w-7 h-7 rounded-lg bg-white text-slate-700 hover:bg-slate-100 font-bold text-xs flex items-center justify-center shadow-sm"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="text-xs font-black text-slate-900 px-1.5">
                      {quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(menuItem.id, quantity + 1)}
                      disabled={quantity >= menuItem.stock_quantity}
                      className="w-7 h-7 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 font-bold text-xs flex items-center justify-center shadow-sm disabled:opacity-50"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => removeItem(menuItem.id)}
                      className="w-7 h-7 rounded-lg text-red-500 hover:bg-red-50 font-bold text-xs flex items-center justify-center ml-1"
                      title="Remove item"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dynamic Capacity Pickup Slot Selector */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-emerald-600" />
                  Dynamic Pickup Window
                </h2>
                <p className="text-xs text-slate-500">
                  Select when you plan to collect your meal from the counter.
                </p>
              </div>
            </div>

            {isLoadingSlots ? (
              <div className="grid grid-cols-2 gap-3 animate-pulse">
                {[1, 2, 3, 4].map((n) => (
                  <div key={n} className="h-16 bg-slate-100 rounded-2xl" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {slots.map((slot) => {
                  const isSelected = selectedSlot?.id === slot.id;
                  const isFull = slot.status === 'FULL';
                  const isBusy = slot.status === 'BUSY';

                  return (
                    <button
                      key={slot.id}
                      type="button"
                      disabled={isFull}
                      onClick={() => setSelectedSlot(slot)}
                      className={`p-3.5 rounded-2xl border-2 text-left transition relative flex flex-col justify-between ${
                        isSelected
                          ? 'border-emerald-600 bg-emerald-50/50 ring-2 ring-emerald-100 shadow-sm'
                          : isFull
                          ? 'border-slate-200 bg-slate-100 opacity-50 cursor-not-allowed'
                          : 'border-slate-200 hover:border-slate-300 bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-slate-900">
                          {slot.slot_label}
                        </span>
                        {slot.is_recommended && (
                          <span className="text-[10px] font-black uppercase text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            Recommended
                          </span>
                        )}
                      </div>

                      <div className="mt-2 flex items-center justify-between text-[11px]">
                        <span className="text-slate-500 font-medium">
                          Capacity: {slot.capacity - slot.booked_count} left
                        </span>

                        <span
                          className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                            isFull
                              ? 'bg-red-100 text-red-700'
                              : isBusy
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-emerald-100 text-emerald-700'
                          }`}
                        >
                          {slot.status}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Special Instructions */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-2">
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-slate-400" />
              Special Preparation Notes (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Less spicy, extra sambar, crispier dosa..."
              value={specialInstructions}
              onChange={(e) => setSpecialInstructions(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 font-medium"
            />
          </div>
        </div>

        {/* Right 1 Col: Summary & Checkout Action */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4 sticky top-24">
            <h2 className="text-base font-bold text-slate-900 border-b border-slate-100 pb-3">
              Bill Summary
            </h2>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Items Total ({totalItemsCount})</span>
                <span className="font-bold text-slate-800">{formatINR(subtotal)}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Dynamic Queue Token Fee</span>
                <span className="font-bold text-emerald-600">FREE (Campus subsidized)</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Assigned Slot</span>
                <span className="font-bold text-slate-900">{selectedSlot?.slot_label || 'Standard'}</span>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-3 flex items-baseline justify-between">
              <span className="text-sm font-black text-slate-900">Total Payable</span>
              <span className="text-2xl font-black text-emerald-600">
                {formatINR(subtotal)}
              </span>
            </div>

            <button
              onClick={() => router.push('/checkout')}
              className="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-black text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-200 transition transform active:scale-95"
            >
              <span>Proceed to Digital Payment</span>
              <ChevronRight className="w-4 h-4" />
            </button>

            <div className="text-[11px] text-slate-400 text-center flex items-center justify-center gap-1">
              <span>●</span>
              <span>Idempotent payment transaction protected</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
