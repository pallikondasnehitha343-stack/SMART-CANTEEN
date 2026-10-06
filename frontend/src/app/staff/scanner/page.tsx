'use client';

import React, { useState, useEffect } from 'react';
import { ApiClient } from '@/lib/api';
import { Order } from '@/lib/types';
import { 
  ScanLine, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  User, 
  QrCode,
  Sparkles
} from 'lucide-react';
import { formatDateTime } from '@/lib/utils';

export default function StaffScannerPage() {
  const [qrInput, setQrInput] = useState<string>('');
  const [isVerifying, setIsVerifying] = useState<boolean>(false);
  const [scanResult, setScanResult] = useState<any | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [readyOrders, setReadyOrders] = useState<Order[]>([]);

  const loadReadyOrders = async () => {
    try {
      const allOrders = await ApiClient.get<Order[]>('/kitchen/orders');
      setReadyOrders(allOrders.filter((o) => o.status === 'READY'));
    } catch (e) {}
  };

  useEffect(() => {
    loadReadyOrders();
  }, []);

  const handleVerifyQR = async (tokenToVerify?: string) => {
    const token = tokenToVerify || qrInput;
    if (!token.trim()) return;

    setIsVerifying(true);
    setErrorMessage(null);
    setScanResult(null);

    try {
      const res = await ApiClient.post<any>('/orders/verify-qr', { qr_token: token.trim() });
      setScanResult(res);
      setQrInput('');
      loadReadyOrders();
    } catch (err: any) {
      console.error('QR verification failed:', err);
      setErrorMessage(err.message || 'Verification rejected');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-16">
      <div className="text-center space-y-1">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold mb-1">
          <ScanLine className="w-3.5 h-3.5" />
          <span>Pickup Counter Terminal</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          QR Token Verification Terminal
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          Validates cryptographic HMAC signature and prevents token reuse upon delivery.
        </p>
      </div>

      {/* Manual Token Input / Camera Simulator */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <label className="text-xs font-bold text-slate-700 block">
          Scan or Enter Cryptographic QR Token
        </label>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Paste raw QR token string here..."
            value={qrInput}
            onChange={(e) => setQrInput(e.target.value)}
            className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => handleVerifyQR()}
            disabled={isVerifying || !qrInput.trim()}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            {isVerifying ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ShieldCheck className="w-4 h-4" />
            )}
            <span>Verify & Claim</span>
          </button>
        </div>
      </div>

      {/* Success Result Modal/Card */}
      {scanResult && (
        <div className="p-6 rounded-3xl bg-emerald-50 border-2 border-emerald-400 text-emerald-950 space-y-3 shadow-md animate-scale">
          <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
            <CheckCircle2 className="w-5 h-5" />
            <span>PICKUP VERIFIED & DELIVERED</span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs pt-2 border-t border-emerald-200">
            <div>
              <span className="text-emerald-700 block">Order Token</span>
              <strong className="text-base text-emerald-950">{scanResult.token_number}</strong>
            </div>
            <div>
              <span className="text-emerald-700 block">Order Reference</span>
              <strong className="text-base text-emerald-950">{scanResult.order_number}</strong>
            </div>
            <div>
              <span className="text-emerald-700 block">Student Name</span>
              <strong className="text-emerald-950">{scanResult.user_name}</strong>
            </div>
            <div>
              <span className="text-emerald-700 block">Verified Timestamp</span>
              <strong className="text-emerald-950">{formatDateTime(scanResult.verified_at)}</strong>
            </div>
          </div>
        </div>
      )}

      {/* Failure / Security Alert Message */}
      {errorMessage && (
        <div className="p-5 rounded-3xl bg-red-50 border-2 border-red-300 text-red-900 space-y-1 shadow-sm">
          <div className="flex items-center gap-2 font-black text-sm text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>Verification Error / Replay Rejection</span>
          </div>
          <p className="text-xs text-red-800 font-medium">{errorMessage}</p>
        </div>
      )}

      {/* Live Ready Orders with 1-Click Verification for Fast Testing */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500" />
            Currently Ready Orders Awaiting Pickup ({readyOrders.length})
          </h2>
          <button
            onClick={loadReadyOrders}
            className="text-xs text-slate-500 hover:text-slate-800"
          >
            Refresh List
          </button>
        </div>

        {readyOrders.length === 0 ? (
          <p className="text-xs text-slate-400 text-center py-4">
            No orders currently marked as READY in kitchen.
          </p>
        ) : (
          <div className="space-y-2">
            {readyOrders.map((ro) => (
              <div
                key={ro.id}
                className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between text-xs"
              >
                <div className="space-y-0.5">
                  <div className="font-black text-slate-900 text-sm">
                    {ro.token_number} • {ro.order_number}
                  </div>
                  <div className="text-slate-500">
                    {ro.user_name || 'Student'} • {ro.items.length} items
                  </div>
                </div>

                <button
                  onClick={() => handleVerifyQR(ro.pickup_qr_token)}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold text-xs shadow-sm transition"
                >
                  Simulate QR Scan
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
