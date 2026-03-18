"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  BarChart3, 
  Check, 
  ChevronDown, 
  Info, 
  MoreHorizontal, 
  Plus, 
  ShoppingBag, 
  Star, 
  Target, 
  TrendingUp, 
  X,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";

// Dummy data for initial UI (will be replaced by real data in production)
const DUMMY_PRODUCTS = [
  {
    id: "1",
    name: "Aura Smart Ring",
    category: "Wearables",
    rating: 4.8,
    price: "$299",
    conversion: "5.2%",
    profit: "$45/sale",
    angles: ["Sleep Optimization", "Minimalist Tech", "Health Tracking"],
    score: 92
  },
  {
    id: "2",
    name: "Nova AI Headset",
    category: "Audio",
    rating: 4.6,
    price: "$199",
    conversion: "4.8%",
    profit: "$30/sale",
    angles: ["Focus Enhancement", "AI Noise Cancellation", "Ergonomic Design"],
    score: 88
  },
  {
    id: "3",
    name: "ZenFlow Desk",
    category: "Home Office",
    rating: 4.9,
    price: "$450",
    conversion: "3.5%",
    profit: "$80/sale",
    angles: ["Productivity Hack", "Aesthetic Workspace", "Wellness at Work"],
    score: 95
  }
];

export default function ComparisonPage() {
  const [selectedIds, setSelectedIds] = useState<string[]>(["1", "3"]);
  const selectedProducts = DUMMY_PRODUCTS.filter(p => selectedIds.includes(p.id));

  const toggleProduct = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(p => p !== id) 
        : (prev.length < 3 ? [...prev, id] : prev)
    );
  };

  return (
    <div className="space-y-10 pb-20">
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-white to-slate-500 bg-clip-text text-transparent mb-2">
            Product Intelligence
          </h1>
          <p className="text-slate-400">
            Compare performance metrics and AI-sculpted angles across your portfolio.
          </p>
        </div>
        <div className="flex gap-3">
          <div className="px-4 py-2 bg-slate-900/50 border border-slate-800 rounded-xl flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-sm font-medium text-slate-300">Live Analysis Tracking</span>
          </div>
        </div>
      </header>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 items-start">
        {selectedProducts.map((product, idx) => (
          <motion.div
            key={product.id}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.15 }}
            className="group relative"
          >
            {/* Spotlight effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-b from-blue-500/20 to-purple-500/0 rounded-[2rem] blur opacity-0 group-hover:opacity-100 transition duration-1000 group-hover:duration-200" />
            
            <div className="glass-card relative rounded-[2rem] p-8 space-y-8 flex flex-col border border-slate-800 transition-colors group-hover:border-slate-700/50">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <div className="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-widest rounded-full border border-blue-500/20 w-fit">
                    {product.category}
                  </div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-blue-400 transition-colors">
                    {product.name}
                  </h3>
                </div>
                <button 
                  onClick={() => toggleProduct(product.id)}
                  className="p-2 bg-slate-900 rounded-xl text-slate-500 hover:text-white transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Score Indicator */}
              <div className="relative h-2 bg-slate-900/50 rounded-full overflow-hidden border border-slate-800">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${product.score}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                  className="absolute h-full bg-gradient-to-r from-blue-600 via-blue-400 to-purple-500"
                />
                <div className="absolute -top-6 right-0 text-xs font-bold text-slate-500">
                  MVP Score: {product.score}
                </div>
              </div>

              {/* Stats Block */}
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Price", value: product.price, icon: ShoppingBag, color: "text-blue-500" },
                  { label: "Profit", value: product.profit, icon: TrendingUp, color: "text-emerald-500" },
                  { label: "Conv. Rate", value: product.conversion, icon: BarChart3, color: "text-purple-500" },
                  { label: "Rating", value: product.rating, icon: Star, color: "text-amber-500" }
                ].map((stat) => (
                  <div key={stat.label} className="p-4 bg-slate-900/30 rounded-2xl border border-slate-800/50">
                    <p className="text-[10px] font-bold text-slate-500 uppercase mb-2 flex items-center gap-1">
                      <stat.icon className={cn("w-3 h-3", stat.color)} /> {stat.label}
                    </p>
                    <p className="text-lg font-bold text-white tracking-tight">{stat.value}</p>
                  </div>
                ))}
              </div>

              {/* AI Angles */}
              <div className="space-y-4 pt-4 border-t border-slate-800/50">
                <h4 className="text-xs font-bold text-blue-500 uppercase tracking-widest flex items-center gap-2">
                  <Target className="w-3 h-3" /> Winning Angles
                </h4>
                <div className="space-y-2">
                  {product.angles.map((angle) => (
                    <div key={angle} className="flex items-center gap-3 group/item">
                      <div className="w-5 h-5 rounded-lg bg-blue-500/10 flex items-center justify-center border border-blue-500/20 group-hover/item:bg-blue-500 transition-colors">
                        <Check className="w-3 h-3 text-blue-500 group-hover/item:text-white" />
                      </div>
                      <span className="text-sm text-slate-300">{angle}</span>
                    </div>
                  ))}
                </div>
              </div>

              <button className="w-full bg-white text-slate-950 font-bold py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-blue-500 hover:text-white transition-all shadow-xl shadow-white/5 active:scale-95 group">
                <Zap className="w-4 h-4 fill-current group-hover:scale-125 transition-transform" /> 
                Scale Production
              </button>
            </div>
          </motion.div>
        ))}

        {selectedIds.length < 3 && (
          <button 
            onClick={() => {/* Open selector logic */}}
            className="h-full min-h-[500px] border-2 border-dashed border-slate-800 rounded-[2rem] flex flex-col items-center justify-center gap-6 group hover:border-blue-500/30 hover:bg-blue-500/5 transition-all"
          >
            <div className="w-16 h-16 rounded-3xl bg-slate-900 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Plus className="w-8 h-8 text-slate-500 group-hover:text-blue-500" />
            </div>
            <div className="text-center">
              <p className="text-white font-bold text-lg mb-1">Compare Another</p>
              <p className="text-slate-500 text-sm">Select up to 3 products</p>
            </div>
          </button>
        )}
      </div>

      {/* Selector Area */}
      <section className="pt-12">
        <div className="flex items-center gap-4 mb-8">
          <div className="h-[1px] flex-1 bg-slate-900" />
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">Inventory Repository</h3>
          <div className="h-[1px] flex-1 bg-slate-900" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {DUMMY_PRODUCTS.map(p => (
            <div 
              key={p.id}
              onClick={() => toggleProduct(p.id)}
              className={cn(
                "p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between",
                selectedIds.includes(p.id)
                  ? "bg-blue-600/10 border-blue-500/50"
                  : "bg-slate-900/50 border-slate-800 hover:border-slate-700"
              )}
            >
              <div className="flex items-center gap-4">
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center",
                  selectedIds.includes(p.id) ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-500"
                )}>
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-bold text-white">{p.name}</p>
                  <p className="text-[10px] text-slate-500">{p.category}</p>
                </div>
              </div>
              {selectedIds.includes(p.id) && (
                <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <Check className="w-3 h-3 text-white" />
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
