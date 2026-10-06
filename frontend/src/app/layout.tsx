import './globals.css';
import type { Metadata } from 'next';
import { AuthProvider } from '@/context/AuthContext';
import { CartProvider } from '@/context/CartContext';
import { WebSocketProvider } from '@/context/WebSocketContext';
import Navbar from '@/components/Navbar';
import PeakAlertBanner from '@/components/PeakAlertBanner';

export const metadata: Metadata = {
  title: 'Smart Canteen — Real-Time Queue & Pickup Orchestration',
  description: 'Intelligent Campus Canteen Management with Real-Time Queue Optimization, Dynamic ETA, and Digital QR Pickup.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased text-slate-900 bg-slate-50 min-h-screen flex flex-col">
        <AuthProvider>
          <CartProvider>
            <WebSocketProvider>
              <PeakAlertBanner />
              <Navbar />
              <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {children}
              </main>
              <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
                <div className="max-w-7xl mx-auto px-4">
                  Smart Canteen Real-Time Queue & Order Orchestration System • Real-Time Capacity-Aware Campus Operations
                </div>
              </footer>
            </WebSocketProvider>
          </CartProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
