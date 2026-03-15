"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Plus,
  Search,
  Zap,
  MessageSquare,
  Copy,
  Trash2,
  CheckCircle2,
  Clock,
  X,
  Loader2,
  ChevronRight,
  Monitor,
  Layout,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";

interface Product {
  id: string;
  name: string;
  selling_angles: any[];
}

interface Script {
  id: string;
  product_id: string;
  hook: string;
  body: string;
  cta: string;
  status: string;
  platform: string;
  tone: string;
  created_at: string;
}

export default function ScriptsPage() {
  const [scripts, setScripts] = useState<Script[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Generation State
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [selectedAngle, setSelectedAngle] = useState<string>("");
  const [tone, setTone] = useState("casual");
  const [platform, setPlatform] = useState("tiktok");
  const [generating, setGenerating] = useState(false);

  const fetchScripts = async () => {
    try {
      const response = await api.get("/scripts");
      setScripts(response.data.items);
    } catch (error) {
      console.error("Failed to fetch scripts", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get("/products", {
        params: { status: "analyzed" },
      });
      setProducts(response.data.items);
    } catch (error) {
      console.error("Failed to fetch products", error);
    }
  };

  useEffect(() => {
    fetchScripts();
    fetchProducts();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await api.post("/scripts/generate", {
        product_id: selectedProduct,
        angle_id: selectedAngle || undefined,
        tone: tone,
        platform: platform,
      });
      alert("Generation queued! It will appear in the list shortly.");
      setIsModalOpen(false);
      // We don't fetch immediately because it's async in backend
    } catch (error) {
      console.error("Generation failed", error);
    } finally {
      setGenerating(false);
    }
  };

  const getProductAngles = () => {
    const p = products.find((p) => p.id === selectedProduct);
    return p?.selling_angles || [];
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Video Scripts</h1>
          <p className="text-slate-400">
            AI-generated scripts for TikTok, Shopee, and more.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
        >
          <Zap className="w-5 h-5" /> Generate Script
        </button>
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-32 bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      ) : scripts.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-3xl">
          <FileText className="w-12 h-12 mb-4 opacity-20" />
          <p>No scripts generated yet. Try creating one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          <AnimatePresence>
            {scripts.map((script, index) => (
              <motion.div
                key={script.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass-card group rounded-2xl p-6 border border-slate-800 hover:border-blue-500/30 transition-all"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span
                        className={cn(
                          "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border",
                          script.status === "approved"
                            ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                            : "bg-amber-500/10 text-amber-500 border-amber-500/20",
                        )}
                      >
                        {script.status}
                      </span>
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                        {script.platform}
                      </span>
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                        {script.tone}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">
                          Hook
                        </p>
                        <p className="text-sm text-white line-clamp-2">
                          {script.hook}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">
                          Body
                        </p>
                        <p className="text-sm text-slate-300 line-clamp-2">
                          {script.body}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">
                          CTA
                        </p>
                        <p className="text-sm text-slate-400 line-clamp-2">
                          {script.cta}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 ml-4">
                    <button className="p-2 bg-slate-900 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all border border-slate-800">
                      <Copy className="w-4 h-4" />
                    </button>
                    <button className="p-2 bg-slate-900 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all border border-slate-800">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Generation Modal */}
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
              className="w-full max-w-2xl glass-card rounded-3xl p-8 relative z-10"
            >
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-600 p-2 rounded-xl">
                    <Zap className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">
                    Generate Script
                  </h2>
                </div>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="text-slate-500 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form
                onSubmit={handleGenerate}
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">
                      Select Product
                    </label>
                    <select
                      required
                      value={selectedProduct}
                      onChange={(e) => {
                        setSelectedProduct(e.target.value);
                        setSelectedAngle("");
                      }}
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                    >
                      <option value="">Choose a product...</option>
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">
                      Selling Angle (optional)
                    </label>
                    <select
                      value={selectedAngle}
                      onChange={(e) => setSelectedAngle(e.target.value)}
                      disabled={!selectedProduct}
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all disabled:opacity-50"
                    >
                      <option value="">AI picks best angle</option>
                      {getProductAngles().map((a: any) => (
                        <option key={a.id} value={a.id}>
                          {a.title}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">
                      Target Platform
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {["tiktok", "shopee"].map((p) => (
                        <button
                          key={p}
                          type="button"
                          onClick={() => setPlatform(p)}
                          className={cn(
                            "py-3 rounded-xl border font-bold capitalize transition-all",
                            platform === p
                              ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20"
                              : "bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300",
                          )}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">
                      Script Tone
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      {["casual", "professional", "funny", "urgent"].map(
                        (t) => (
                          <button
                            key={t}
                            type="button"
                            onClick={() => setTone(t)}
                            className={cn(
                              "py-2 rounded-xl border text-xs font-bold capitalize transition-all",
                              tone === t
                                ? "bg-white border-white text-slate-950 shadow-lg"
                                : "bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300",
                            )}
                          >
                            {t}
                          </button>
                        ),
                      )}
                    </div>
                  </div>
                </div>

                <button
                  disabled={generating || !selectedProduct}
                  className="md:col-span-2 w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-98 shadow-lg shadow-blue-600/20 disabled:opacity-50"
                >
                  {generating ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" /> Generating
                      Script...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 fill-white" /> Start Magic
                      Generation
                    </>
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
