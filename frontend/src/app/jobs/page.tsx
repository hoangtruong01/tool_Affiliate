"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PlayCircle,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Download,
  Trash2,
  Loader2,
  X,
  FileText,
  Image as ImageIcon,
  ChevronRight,
  Settings2,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";

interface VideoJob {
  id: string;
  script_id: string;
  script?: { hook: string; product: { name: string } };
  status: string;
  output_path?: string;
  duration_seconds?: number;
  error_message?: string;
  created_at: string;
}

interface Asset {
  id: string;
  filename: string;
  asset_type: string;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Create Job State
  const [scripts, setScripts] = useState<any[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedScript, setSelectedScript] = useState("");
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);

  const fetchJobs = async () => {
    try {
      const response = await api.get("/jobs");
      setJobs(response.data.items);
    } catch (error) {
      console.error("Failed to fetch jobs", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      const [scriptsRes, assetsRes] = await Promise.all([
        api.get("/scripts", { params: { status: "approved" } }),
        api.get("/assets", { params: { asset_type: "image" } }),
      ]);
      setScripts(scriptsRes.data.items);
      setAssets(assetsRes.data.items);
    } catch (error) {
      console.error("Failed to fetch data", error);
    }
  };

  useEffect(() => {
    fetchJobs();
    fetchData();
  }, []);

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post("/jobs", {
        script_id: selectedScript,
        asset_ids: selectedAssets,
      });
      await fetchJobs();
      setIsModalOpen(false);
      setSelectedScript("");
      setSelectedAssets([]);
    } catch (error) {
      console.error("Create failed", error);
    } finally {
      setCreating(false);
    }
  };

  const toggleAsset = (id: string) => {
    setSelectedAssets((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id],
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "rendered":
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case "failed":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-amber-500" />;
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Video Jobs</h1>
          <p className="text-slate-400">
            Track and manage your automated video rendering pipeline.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
        >
          <Plus className="w-5 h-5" /> New Render Job
        </button>
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-24 bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-3xl">
          <PlayCircle className="w-12 h-12 mb-4 opacity-20" />
          <p>No render jobs found. Create your first video now.</p>
        </div>
      ) : (
        <div className="glass-card rounded-2xl overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-900/50 border-b border-slate-800">
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Product / Script
                  </th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {jobs.map((job) => (
                  <tr
                    key={job.id}
                    className="hover:bg-slate-900/40 transition-colors group"
                  >
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-sm font-bold text-white truncate max-w-[200px] group-hover:text-blue-400 transition-colors">
                          {job.script?.product.name || "Unknown Product"}
                        </span>
                        <span className="text-xs text-slate-500 truncate max-w-[200px]">
                          {job.script?.hook || "No script attached"}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(job.status)}
                        <span
                          className={cn(
                            "text-xs font-bold capitalize",
                            job.status === "rendered"
                              ? "text-emerald-500"
                              : job.status === "failed"
                                ? "text-red-500"
                                : job.status === "processing"
                                  ? "text-blue-500"
                                  : "text-amber-500",
                          )}
                        >
                          {job.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {formatDate(job.created_at)}
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs text-center">
                      {job.duration_seconds ? `${job.duration_seconds}s` : "-"}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {job.status === "rendered" && (
                          <button className="p-2 bg-blue-600/10 text-blue-500 hover:bg-blue-600 hover:text-white rounded-lg transition-all border border-blue-600/20">
                            <Download className="w-4 h-4" />
                          </button>
                        )}
                        <button className="p-2 bg-slate-800 text-slate-500 hover:text-white rounded-lg transition-all border border-slate-700">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Create Job Modal */}
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
              className="w-full max-w-4xl glass-card rounded-3xl p-8 relative z-10 flex flex-col max-h-[90vh]"
            >
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-600 p-2 rounded-xl">
                    <Settings2 className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold text-white">
                    Configure Render Job
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
                onSubmit={handleCreateJob}
                className="flex-1 overflow-y-auto space-y-8 pr-2 custom-scrollbar"
              >
                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                    <FileText className="w-4 h-4" /> 1. Select Approved Script
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {scripts.length > 0 ? (
                      scripts.map((s) => (
                        <div
                          key={s.id}
                          onClick={() => setSelectedScript(s.id)}
                          className={cn(
                            "p-4 rounded-xl border cursor-pointer transition-all",
                            selectedScript === s.id
                              ? "bg-blue-600/10 border-blue-500/50"
                              : "bg-slate-900 border-slate-800 hover:border-slate-700",
                          )}
                        >
                          <p className="text-sm font-bold text-white mb-1">
                            {s.product.name}
                          </p>
                          <p className="text-xs text-slate-400 line-clamp-1">
                            {s.hook}
                          </p>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-amber-500 italic md:col-span-2">
                        No approved scripts available. Please approve a script
                        first.
                      </p>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                    <ImageIcon className="w-4 h-4" /> 2. Select Visual Assets
                    (Images)
                  </h3>
                  <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                    {assets.map((a) => (
                      <div
                        key={a.id}
                        onClick={() => toggleAsset(a.id)}
                        className={cn(
                          "aspect-square rounded-xl border cursor-pointer overflow-hidden relative transition-all",
                          selectedAssets.includes(a.id)
                            ? "ring-2 ring-blue-500 border-transparent shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                            : "bg-slate-900 border-slate-800",
                        )}
                      >
                        <div className="w-full h-full flex items-center justify-center bg-slate-800 text-slate-600">
                          <ImageIcon className="w-8 h-8" />
                        </div>
                        {selectedAssets.includes(a.id) && (
                          <div className="absolute top-1 right-1 bg-blue-600 rounded-full p-0.5">
                            <CheckCircle2 className="w-3 h-3 text-white" />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 sticky bottom-0 bg-slate-950/50 backdrop-blur-md pb-2">
                  <button
                    disabled={
                      creating || !selectedScript || selectedAssets.length === 0
                    }
                    className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-2 transition-all active:scale-98 shadow-lg shadow-blue-600/20 disabled:opacity-50"
                  >
                    {creating ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                      "Start Rendering Pipeline"
                    )}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
