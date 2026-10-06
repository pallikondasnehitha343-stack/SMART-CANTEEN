'use client';

import React from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { ShieldCheck, QrCode, Lock } from 'lucide-react';

interface QRCodeDisplayProps {
  qrToken?: string;
  orderNumber: string;
  tokenNumber: string;
  isReady: boolean;
  isUsed: boolean;
}

export default function QRCodeDisplay({
  qrToken,
  orderNumber,
  tokenNumber,
  isReady,
  isUsed,
}: QRCodeDisplayProps) {
  if (isUsed) {
    return (
      <div className="p-6 bg-slate-100 rounded-2xl border-2 border-dashed border-slate-300 text-center">
        <div className="w-12 h-12 rounded-full bg-slate-200 text-slate-500 mx-auto flex items-center justify-center mb-2">
          <Lock className="w-6 h-6" />
        </div>
        <div className="text-sm font-bold text-slate-700">QR Token Consumed</div>
        <div className="text-xs text-slate-500 mt-1">
          This digital token has already been validated and food picked up.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 shadow-md text-center relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-100">
        <div className="text-left">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Digital Pickup Token
          </div>
          <div className="text-xl font-black text-slate-900">
            {tokenNumber}
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>HMAC Verified</span>
        </div>
      </div>

      {/* QR Code Canvas */}
      <div className="p-4 bg-slate-50 rounded-xl inline-block border border-slate-200 shadow-inner">
        {qrToken ? (
          <QRCodeSVG
            value={qrToken}
            size={180}
            level="H"
            includeMargin={true}
            className="mx-auto"
          />
        ) : (
          <div className="w-[180px] h-[180px] flex items-center justify-center bg-slate-200 text-slate-400 text-xs font-medium">
            Generating Secure Token...
          </div>
        )}
      </div>

      {/* Verification instructions */}
      <div className="mt-4">
        <div className="text-xs font-bold text-slate-800">
          {orderNumber}
        </div>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Present this QR screen at the kitchen pickup counter scanner.
        </p>
      </div>

      {!isReady && (
        <div className="mt-3 p-2 bg-amber-50 rounded-lg text-amber-800 text-xs font-medium border border-amber-200">
          QR token active upon kitchen READY signal.
        </div>
      )}
    </div>
  );
}
