"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShoppingBag,
  Plus,
  Search,
  Filter,
  MoreVertical,
  ExternalLink,
  Zap,
  Trash2,
  Edit2,
  Loader2,
  X,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";

interface Product {
  id: string;
  name: string;
  source_url?: string;
  category?: string;
  status: string;
  created_at: string;
  selling_angles: any[];
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Create Form State
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchProducts = async () => {
    try {
      const response = await api.get("/products", { params: { search } });
      setProducts(response.data.items);
    } catch (error) {
      console.error("Failed to fetch products", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchProducts();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post("/products", { name: newName, source_url: newUrl });
      await fetchProducts();
      setIsModalOpen(false);
      setNewName("");
      setNewUrl("");
    } catch (error) {
      console.error("Create failed", error);
    } finally {
      setCreating(false);
    }
  };

  const handleAnalyze = async (id: string) => {
    try {
      await api.post(`/products/${id}/analyze`);
      alert("Analysis queued! Check back in a few moments.");
      await fetchProducts();
    } catch (error) {
      console.error("Analysis failed", error);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Products</h1>
          <p className="text-slate-400">
            Manage affiliate products and analyze selling angles.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
        >
          <Plus className="w-5 h-5" /> Add Product
        </button>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center">
        <div className="relative flex-1 group w-full">
          <Search className="w-5 h-5 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2 group-focus-within:text-blue-500 transition-colors" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search products by name..."
            className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 pl-11 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto">
          <button className="bg-slate-900 border border-slate-800 p-3 rounded-xl hover:bg-slate-800 transition-colors text-slate-400">
            <Filter className="w-5 h-5" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-48 bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-2xl">
          <ShoppingBag className="w-12 h-12 mb-4 opacity-20" />
          <p>No products found. Start by adding your first product.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {products.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.05 }}
                className="glass-card group rounded-2xl overflow-hidden flex flex-col"
              >
                <div className="p-6 flex-1">
                  <div className="flex justify-between items-start mb-4">
                    <span
                      className={cn(
                        "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border",
                        product.status === "analyzed"
                          ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                          : "bg-blue-500/10 text-blue-500 border-blue-500/20",
                      )}
                    >
                      {product.status}
                    </span>
                    <button className="text-slate-600 hover:text-white transition-colors">
                      <MoreVertical className="w-5 h-5" />
                    </button>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-2 line-clamp-1 group-hover:text-blue-400 transition-colors">
                    {product.name}
                  </h3>

                  <div className="flex items-center gap-2 text-slate-500 text-xs mb-4">
                    <ShoppingBag className="w-3.5 h-3.5" />
                    <span>{product.category || "Uncategorized"}</span>
                    <span className="w-1 h-1 rounded-full bg-slate-800" />
                    <span>{formatDate(product.created_at)}</span>
                  </div>

                  {product.source_url && (
                    <a
                      href={product.source_url}
                      target="_blank"
                      className="text-xs text-blue-500 hover:underline flex items-center gap-1 mb-6"
                    >
                      View Source <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>

                <div className="p-4 bg-slate-900/50 border-t border-slate-800 flex items-center gap-2">
                  {product.status !== "analyzed" ? (
                    <button
                      onClick={() => handleAnalyze(product.id)}
                      className="flex-1 bg-emerald-600/10 hover:bg-emerald-600 text-emerald-500 hover:text-white dark-transition border border-emerald-500/20 font-bold py-2 rounded-lg flex items-center justify-center gap-2 text-sm"
                    >
                      <Zap className="w-4 h-4" /> AI Analyze
                    </button>
                  ) : (
                    <button className="flex-1 bg-blue-600/10 hover:bg-blue-600 text-blue-500 hover:text-white dark-transition border border-blue-600/20 font-bold py-2 rounded-lg flex items-center justify-center gap-2 text-sm">
                      <Edit2 className="w-4 h-4" /> View Angles
                    </button>
                  )}
                  <button className="p-2 aspect-square rounded-lg bg-red-500/5 hover:bg-red-500 text-slate-600 hover:text-white border border-transparent hover:border-red-500/20 transition-all">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Create Product Modal */}
      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsModalOpen(false)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-lg glass-card rounded-3xl p-8 relative z-10"
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-white">
                  Add New Product
                </h2>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-slate-500 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleCreateProduct} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Product Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g. Premium Wireless Headphones"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Affiliate / Store URL (optional)
                  </label>
                  <input
                    type="url"
                    value={newUrl}
                    onChange={(e) => setNewUrl(e.target.value)}
                    placeholder="https://shopee.vn/product-name"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  />
                </div>

                <button
                  disabled={creating}
                  className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-98 shadow-lg shadow-blue-600/20"
                >
                  {creating ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    "Create Product"
                  )}
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
