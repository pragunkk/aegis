import React, { useEffect, useState } from 'react';
import { Package, ShieldCheck, X, Search } from 'lucide-react';
import { fetchProducts } from '../lib/api';
import type { Product } from '../types';

interface CatalogDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const MERCHANT_FLOOR_DATA: Record<string, number> = {
  'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d': 3800.0,
  'b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e': 9500.0,
  'c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f': 6200.0,
  'd4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a': 2200.0,
};

export const CatalogDrawer: React.FC<CatalogDrawerProps> = ({ isOpen, onClose }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchProducts()
        .then((data) => setProducts(data))
        .catch((err) => console.error(err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const filteredProducts = products.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl rounded-2xl bg-[#121216] border border-zinc-800/90 p-6 shadow-2xl space-y-5">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Package className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base font-heading font-bold text-zinc-100">
                Merchant Product Margins
              </h3>
              <p className="text-xs text-zinc-400 mt-0.5">
                Confidential price floors enforced by AegisPay during AI agent negotiations.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-zinc-800 transition cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search catalog products by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-zinc-900 border border-zinc-800 focus:border-indigo-500 rounded-lg text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition shadow-xs"
          />
        </div>

        {/* Product Items List */}
        <div className="max-h-80 overflow-y-auto space-y-2.5 pr-1">
          {filteredProducts.length === 0 ? (
            <div className="text-center py-8 text-xs text-zinc-500">
              No products found matching "{searchQuery}"
            </div>
          ) : (
            filteredProducts.map((p) => {
              // Directly use the confidential floor coming securely from the database/API model
              const floor = p.price_floor || p.mrp * 0.85;
              const maxDiscount = p.mrp - floor;
              const discountPct = Math.round((maxDiscount / p.mrp) * 100);

              return (
                <div
                  key={p.id}
                  className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
                >
                  <div className="space-y-0.5 max-w-sm">
                    <h4 className="font-semibold text-xs text-zinc-100">{p.name}</h4>
                    <p className="text-[11px] text-zinc-400 line-clamp-1">{p.description}</p>
                    <div className="text-[10px] text-zinc-500 font-mono pt-0.5">Stock: {p.stock} units</div>
                  </div>

                  <div className="flex items-center gap-5 shrink-0 text-xs bg-black/20 p-2 rounded-lg border border-white/5">
                    <div>
                      <div className="text-[10px] text-zinc-500 uppercase tracking-wider">MRP</div>
                      <div className="font-semibold text-zinc-200">₹{p.mrp.toLocaleString('en-IN')}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-emerald-400 font-medium uppercase tracking-wider">Floor Price</div>
                      <div className="font-semibold text-emerald-400">₹{floor.toLocaleString('en-IN')}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-zinc-500 uppercase tracking-wider">Max Discount</div>
                      <div className="font-medium text-indigo-300">
                        ₹{maxDiscount.toLocaleString('en-IN')} ({discountPct}%)
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info note */}
        <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80 text-xs">
          <div className="flex items-center gap-1.5 text-zinc-400 text-[11px]">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
            <span>Floor prices are never exposed to buyer agents during discovery.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold transition cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
