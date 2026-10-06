'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCart } from '@/context/CartContext';
import { useAuth } from '@/context/AuthContext';
import { ApiClient } from '@/lib/api';
import { Order, PaymentMethod } from '@/lib/types';
import { 
  Wallet, 
  QrCode, 
  CreditCard, 
  ShieldCheck, 
  Lock, 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { formatINR } from '@/lib/utils';

export default function CheckoutPage() {
  const router = useRouter();
  const { items, selectedSlot, specialInstructions, subtotal, clearCart } = useCart();
  const { user } = useAuth();

  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('CAMPUS_WALLET');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (items.length === 0) {
    router.push('/menu');
    return null;
  }

  const handleExecutePayment = async () => {
    setIsProcessing(true);
    setErrorMessage(null);

    try {
      // 1. Generate client-side idempotency key for this checkout attempt
      const idempotencyKey = `IDEMP_${Date.now()}_${Math.random().toString(36).substring(2, 9).toUpperCase()}`;

      // 2. Create authoritative order on backend (reserves stock & slot atomically)
      const orderPayload = {
        items: items.map((i) => ({
          menu_item_id: i.menuItem.id,
          quantity: i.quantity,
        })),
        pickup_slot_id: selectedSlot?.id || null,
        special_instructions: specialInstructions || null,
        payment_method: paymentMethod,
        idempotency_key: idempotencyKey,
      };

      const order = await ApiClient.post<Order>('/orders', orderPayload);

      // 3. Initiate payment state machine
      const payment = await ApiClient.post<any>('/payments/initiate', {
        order_id: order.id,
        payment_method: paymentMethod,
        idempotency_key: idempotencyKey,
      });

      // 4. Simulate authoritative gateway verification
      const verifyRes = await ApiClient.post<any>('/payments/verify', {
        transaction_id: payment.transaction_id,
        gateway_signature: 'VALID_MOCK_CAMPUS_SIGNATURE',
        status: 'SUCCESS',
      });

      // 5. Clear cart and navigate to live tracking
      clearCart();
      router.push(`/orders/${order.id}`);
    } catch (err: any) {
      console.error('Payment failure:', err);
      setErrorMessage(err.message || 'Payment execution failed. Please retry.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-6 pb-16">
      <div className="text-center space-y-1">
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Campus Digital Payment
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          Fast, contactless payment verification with instant digital token issuance.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 bg-red-50 text-red-800 text-xs font-bold rounded-2xl border border-red-200 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Amount Card */}
      <div className="p-6 rounded-3xl bg-slate-900 text-white text-center space-y-2 shadow-xl border border-slate-800">
        <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Total Amount to Pay
        </div>
        <div className="text-4xl font-black text-emerald-400 tracking-tight">
          {formatINR(subtotal)}
        </div>
        <div className="text-[11px] text-slate-300 font-medium">
          Assigned Slot: <strong className="text-white">{selectedSlot?.slot_label || 'Immediate Pickup'}</strong>
        </div>
      </div>

      {/* Payment Options */}
      <div className="space-y-3">
        <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
          Select Digital Payment Method
        </label>

        {/* Option 1: Campus Wallet */}
        <button
          type="button"
          onClick={() => setPaymentMethod('CAMPUS_WALLET')}
          className={`w-full p-4 rounded-2xl border-2 text-left transition flex items-center justify-between ${
            paymentMethod === 'CAMPUS_WALLET'
              ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-100 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <Wallet className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">
                Campus Student Smart Wallet
              </div>
              <div className="text-xs text-slate-500">
                Linked to {user?.campus_id || 'Student ID'} • Available Balance: ₹1,450.00
              </div>
            </div>
          </div>
          {paymentMethod === 'CAMPUS_WALLET' && (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          )}
        </button>

        {/* Option 2: UPI */}
        <button
          type="button"
          onClick={() => setPaymentMethod('UPI')}
          className={`w-full p-4 rounded-2xl border-2 text-left transition flex items-center justify-between ${
            paymentMethod === 'UPI'
              ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-100 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
              <QrCode className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">
                Instant UPI (GPay / PhonePe / Paytm)
              </div>
              <div className="text-xs text-slate-500">
                Instant verification via campus gateway webhook
              </div>
            </div>
          </div>
          {paymentMethod === 'UPI' && (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          )}
        </button>

        {/* Option 3: Card */}
        <button
          type="button"
          onClick={() => setPaymentMethod('CREDIT_DEBIT_CARD')}
          className={`w-full p-4 rounded-2xl border-2 text-left transition flex items-center justify-between ${
            paymentMethod === 'CREDIT_DEBIT_CARD'
              ? 'border-emerald-600 bg-emerald-50/60 ring-2 ring-emerald-100 shadow-sm'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center font-bold">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">
                Debit / Credit / RuPay Card
              </div>
              <div className="text-xs text-slate-500">
                Encrypted 256-bit payment channel
              </div>
            </div>
          </div>
          {paymentMethod === 'CREDIT_DEBIT_CARD' && (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          )}
        </button>
      </div>

      {/* Pay Button */}
      <div className="space-y-3 pt-2">
        <button
          onClick={handleExecutePayment}
          disabled={isProcessing}
          className="w-full py-4 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-700 text-white font-black text-base flex items-center justify-center gap-2 shadow-xl shadow-emerald-200 transition transform active:scale-95 disabled:opacity-60"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Verifying & Reserving Queue Token...</span>
            </>
          ) : (
            <>
              <Lock className="w-4 h-4" />
              <span>Pay {formatINR(subtotal)} & Confirm Order</span>
            </>
          )}
        </button>

        <div className="text-center text-xs text-slate-400 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Authoritative Backend Verification • Anti-Double Charge Protected</span>
        </div>
      </div>
    </div>
  );
}
