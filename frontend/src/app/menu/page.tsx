'use client';

import React, { useState, useEffect } from 'react';
import { MenuItem, Category } from '@/lib/types';
import { ApiClient } from '@/lib/api';
import { useCart } from '@/context/CartContext';
import { 
  Search, 
  Plus, 
  Minus, 
  Clock, 
  Flame, 
  Leaf, 
  AlertCircle, 
  ShoppingCart, 
  Check,
  Filter
} from 'lucide-react';
import { formatINR } from '@/lib/utils';
import Link from 'next/link';

export default function MenuPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<MenuItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [vegOnly, setVegOnly] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const { items: cartItems, addItem, updateQuantity, totalItemsCount, subtotal } = useCart();

  useEffect(() => {
    async function loadMenuData() {
      setIsLoading(true);
      try {
        const [catData, itemData] = await Promise.all([
          ApiClient.get<Category[]>('/menu/categories'),
          ApiClient.get<MenuItem[]>('/menu/items?available_only=false'),
        ]);
        setCategories(catData);
        setItems(itemData);
      } catch (err) {
        console.error('Failed to load menu from backend:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadMenuData();
  }, []);

  const filteredItems = items.filter((item) => {
    if (selectedCategory && item.category_id !== selectedCategory) return false;
    if (vegOnly && !item.is_veg) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        item.name.toLowerCase().includes(q) ||
        (item.description && item.description.toLowerCase().includes(q))
      );
    }
    return true;
  });

  const getItemCartQuantity = (itemId: number) => {
    const found = cartItems.find((ci) => ci.menuItem.id === itemId);
    return found ? found.quantity : 0;
  };

  return (
    <div className="space-y-6 pb-24">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Campus Canteen Menu
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Fresh meals prepared on-demand with live kitchen queue estimation.
          </p>
        </div>

        {/* Search & Veg Filter */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search dosa, thali, chai..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
            />
          </div>

          <button
            onClick={() => setVegOnly(!vegOnly)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border text-xs font-bold transition shadow-sm ${
              vegOnly
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-emerald-200'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
            }`}
          >
            <Leaf className="w-3.5 h-3.5" />
            <span>Veg Only</span>
          </button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition ${
            selectedCategory === null
              ? 'bg-slate-900 text-white shadow-md'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
          }`}
        >
          All Items ({items.length})
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition ${
              selectedCategory === cat.id
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-200'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Menu Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
            <div
              key={n}
              className="p-5 rounded-2xl bg-white border border-slate-200 animate-pulse space-y-3"
            >
              <div className="h-5 bg-slate-200 rounded w-3/4" />
              <div className="h-10 bg-slate-100 rounded" />
              <div className="h-6 bg-slate-200 rounded w-1/3" />
            </div>
          ))}
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800">No menu items found</h3>
          <p className="text-xs text-slate-500">Try adjusting your filters or search query.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map((item) => {
            const inCartQty = getItemCartQuantity(item.id);
            const isOutOfStock = !item.is_available || item.stock_quantity <= 0;
            const isLowStock = item.stock_quantity > 0 && item.stock_quantity <= 10;

            return (
              <div
                key={item.id}
                className={`p-5 rounded-2xl bg-white border transition flex flex-col justify-between ${
                  isOutOfStock
                    ? 'border-slate-200 opacity-60'
                    : 'border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-300'
                }`}
              >
                {/* Item Details */}
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-base font-bold text-slate-900 leading-snug">
                      {item.name}
                    </h3>
                    <span
                      className={`w-4 h-4 rounded flex items-center justify-center border text-[9px] font-black flex-shrink-0 mt-0.5 ${
                        item.is_veg
                          ? 'border-emerald-600 text-emerald-600'
                          : 'border-red-600 text-red-600'
                      }`}
                      title={item.is_veg ? 'Vegetarian' : 'Non-Vegetarian'}
                    >
                      ●
                    </span>
                  </div>

                  <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                    {item.description || 'Prepared fresh with campus hygiene standards.'}
                  </p>

                  {/* Metadata: Prep Time & Stock Badges */}
                  <div className="flex items-center gap-2 pt-1 flex-wrap">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                      <Clock className="w-3 h-3 text-slate-400" />
                      ~{item.prep_time_minutes} min prep
                    </span>

                    {isOutOfStock ? (
                      <span className="text-[10px] font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded-md">
                        Sold Out
                      </span>
                    ) : isLowStock ? (
                      <span className="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded-md flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        Only {item.stock_quantity} left
                      </span>
                    ) : (
                      <span className="text-[10px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                        {item.stock_quantity} available
                      </span>
                    )}
                  </div>
                </div>

                {/* Price & Action */}
                <div className="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-lg font-black text-slate-900">
                      {formatINR(item.price)}
                    </span>
                  </div>

                  {/* Add / Modify Quantity Button */}
                  <div>
                    {isOutOfStock ? (
                      <button
                        disabled
                        className="px-3 py-1.5 rounded-xl bg-slate-100 text-slate-400 text-xs font-bold cursor-not-allowed"
                      >
                        Unavailable
                      </button>
                    ) : inCartQty > 0 ? (
                      <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-xl p-1">
                        <button
                          onClick={() => updateQuantity(item.id, inCartQty - 1)}
                          className="w-7 h-7 rounded-lg bg-white text-emerald-700 hover:bg-emerald-100 font-bold text-xs flex items-center justify-center shadow-sm"
                          aria-label="Decrease quantity"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="text-xs font-black text-emerald-800 px-1">
                          {inCartQty}
                        </span>
                        <button
                          onClick={() => addItem(item, 1)}
                          disabled={inCartQty >= item.stock_quantity}
                          className="w-7 h-7 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 font-bold text-xs flex items-center justify-center shadow-sm disabled:opacity-50"
                          aria-label="Increase quantity"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => addItem(item, 1)}
                        className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm shadow-emerald-200 transition active:scale-95"
                      >
                        <Plus className="w-3.5 h-3.5" />
                        Add
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Floating Sticky Cart Bar */}
      {totalItemsCount > 0 && (
        <div className="fixed bottom-4 left-0 right-0 max-w-lg mx-auto px-4 z-40">
          <Link
            href="/cart"
            className="flex items-center justify-between p-4 bg-slate-900 text-white rounded-2xl shadow-2xl border border-slate-700 hover:bg-slate-800 transition transform hover:-translate-y-0.5"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500 text-slate-950 flex items-center justify-center font-black">
                <ShoppingCart className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-slate-300">
                  {totalItemsCount} {totalItemsCount === 1 ? 'item' : 'items'} in cart
                </div>
                <div className="text-base font-black text-emerald-400">
                  {formatINR(subtotal)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-xs font-black px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 shadow-md">
              <span>View Cart & Select Slot</span>
            </div>
          </Link>
        </div>
      )}
    </div>
  );
}
