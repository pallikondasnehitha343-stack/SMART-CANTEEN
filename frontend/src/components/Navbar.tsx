'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { useCart } from '@/context/CartContext';
import { 
  UtensilsCrossed, 
  ShoppingCart, 
  ClipboardList, 
  ChefHat, 
  ScanLine, 
  BarChart3, 
  UserCircle, 
  LogOut,
  Layers
} from 'lucide-react';

export default function Navbar() {
  const { user, quickSwitchDemoUser, logout } = useAuth();
  const { totalItemsCount } = useCart();

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2.5 text-emerald-700 hover:text-emerald-800 transition">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-200">
              <UtensilsCrossed className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-slate-900 block leading-tight">
                Smart<span className="text-emerald-600">Canteen</span>
              </span>
              <span className="text-[10px] font-semibold tracking-wider uppercase text-slate-500 block">
                Campus Queue & Pickup
              </span>
            </div>
          </Link>

          {/* Nav Links based on Role */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              href="/menu"
              className="px-3.5 py-2 text-sm font-semibold text-slate-700 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition"
            >
              Campus Menu
            </Link>
            <Link
              href="/orders"
              className="px-3.5 py-2 text-sm font-semibold text-slate-700 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition"
            >
              My Orders
            </Link>

            {(user?.role === 'STAFF' || user?.role === 'ADMIN') && (
              <>
                <Link
                  href="/kitchen"
                  className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition border border-amber-200 ml-2"
                >
                  <ChefHat className="w-4 h-4" />
                  Kitchen KDS
                </Link>
                <Link
                  href="/staff/scanner"
                  className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition border border-blue-200"
                >
                  <ScanLine className="w-4 h-4" />
                  QR Scanner
                </Link>
              </>
            )}

            {user?.role === 'ADMIN' && (
              <Link
                href="/admin"
                className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-semibold text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition border border-purple-200 ml-1"
              >
                <BarChart3 className="w-4 h-4" />
                Admin Console
              </Link>
            )}
          </nav>

          {/* Right Actions: Cart & Role Switcher */}
          <div className="flex items-center gap-3">
            {/* Quick Role Switcher for Campus Demonstration */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
              <button
                onClick={() => quickSwitchDemoUser('STUDENT')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  user?.role === 'STUDENT'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="Switch to Student Persona"
              >
                Student
              </button>
              <button
                onClick={() => quickSwitchDemoUser('STAFF')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  user?.role === 'STAFF'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="Switch to Kitchen Staff Persona"
              >
                Staff (KDS)
              </button>
              <button
                onClick={() => quickSwitchDemoUser('ADMIN')}
                className={`px-2.5 py-1 rounded-lg transition ${
                  user?.role === 'ADMIN'
                    ? 'bg-purple-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="Switch to Administrator Persona"
              >
                Admin
              </button>
            </div>

            {/* Cart Button */}
            <Link
              href="/cart"
              className="relative p-2.5 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition"
              aria-label="View Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {totalItemsCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-emerald-600 text-white text-[11px] font-black flex items-center justify-center shadow-sm animate-scale">
                  {totalItemsCount}
                </span>
              )}
            </Link>

            {/* User Profile / Status */}
            {user && (
              <div className="hidden lg:flex items-center gap-2 pl-2 border-l border-slate-200">
                <div className="text-right">
                  <div className="text-xs font-bold text-slate-800 leading-tight">
                    {user.full_name}
                  </div>
                  <div className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider">
                    {user.campus_id}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
