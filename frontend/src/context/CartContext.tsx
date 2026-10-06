'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { MenuItem, PickupSlot } from '@/lib/types';

export interface CartItem {
  menuItem: MenuItem;
  quantity: number;
}

interface CartContextType {
  items: CartItem[];
  addItem: (item: MenuItem, quantity?: number) => void;
  removeItem: (itemId: number) => void;
  updateQuantity: (itemId: number, quantity: number) => void;
  clearCart: () => void;
  selectedSlot: PickupSlot | null;
  setSelectedSlot: (slot: PickupSlot | null) => void;
  specialInstructions: string;
  setSpecialInstructions: (instructions: string) => void;
  subtotal: number;
  totalItemsCount: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<PickupSlot | null>(null);
  const [specialInstructions, setSpecialInstructions] = useState<string>('');

  // Load from local storage
  useEffect(() => {
    const saved = localStorage.getItem('smart_canteen_cart');
    if (saved) {
      try {
        setItems(JSON.parse(saved));
      } catch (e) {
        localStorage.removeItem('smart_canteen_cart');
      }
    }
  }, []);

  // Save to local storage
  useEffect(() => {
    localStorage.setItem('smart_canteen_cart', JSON.stringify(items));
  }, [items]);

  const addItem = (item: MenuItem, quantity = 1) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.menuItem.id === item.id);
      if (existing) {
        const newQty = Math.min(existing.quantity + quantity, item.stock_quantity);
        return prev.map((i) =>
          i.menuItem.id === item.id ? { ...i, quantity: newQty } : i
        );
      }
      return [...prev, { menuItem: item, quantity: Math.min(quantity, item.stock_quantity) }];
    });
  };

  const removeItem = (itemId: number) => {
    setItems((prev) => prev.filter((i) => i.menuItem.id !== itemId));
  };

  const updateQuantity = (itemId: number, quantity: number) => {
    if (quantity <= 0) {
      removeItem(itemId);
      return;
    }
    setItems((prev) =>
      prev.map((i) => (i.menuItem.id === itemId ? { ...i, quantity } : i))
    );
  };

  const clearCart = () => {
    setItems([]);
    setSelectedSlot(null);
    setSpecialInstructions('');
    localStorage.removeItem('smart_canteen_cart');
  };

  const subtotal = items.reduce(
    (sum, item) => sum + item.menuItem.price * item.quantity,
    0
  );

  const totalItemsCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <CartContext.Provider
      value={{
        items,
        addItem,
        removeItem,
        updateQuantity,
        clearCart,
        selectedSlot,
        setSelectedSlot,
        specialInstructions,
        setSpecialInstructions,
        subtotal,
        totalItemsCount,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
