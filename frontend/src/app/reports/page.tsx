"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  MousePointer2, 
  Eye,
  ArrowRight,
  RefreshCcw,
  AlertTriangle,
  Clock
} from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

interface LearningReport {
  top_products: any[];
  top_hooks: any[];
  top_angles: any[];
  candidates_to_retry: any[];
  candidates_to_drop: any[];
  stuck_jobs?: any[];
}

export default function ReportsPage() {
  const [report, setReport] = useState<LearningReport | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const response = await api.get("/analytics/learning");
      setReport(response.data);
    } catch (error) {
      console.error("Failed to fetch report", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <RefreshCcw className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Learning & Reports</h1>
          <p className="text-slate-400">Rule-based insights from your live publishing data.</p>
        </div>
        <button 
          onClick={fetchReport}
          className="p-2 hover:bg-slate-800 rounded-xl transition-colors text-slate-400 hover:text-white"
        >
          <RefreshCcw className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Products */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-blue-600/20 p-2 rounded-lg text-blue-500">
              <Target className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white">Top Products</h3>
          </div>
          <div className="space-y-4">
            {report?.top_products.map((p, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-slate-800">
                <span className="text-sm font-medium text-slate-300 truncate max-w-[150px]">{p.product_name}</span>
                <span className="text-xs font-black text-blue-400 bg-blue-400/10 px-2 py-1 rounded-md">{p.avg_rating.toFixed(1)} / 5</span>
              </div>
            ))}
            {report?.top_products.length === 0 && <p className="text-sm text-slate-500 italic">No data yet</p>}
          </div>
        </div>

        {/* Top Hooks */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-purple-600/20 p-2 rounded-lg text-purple-500">
              <Eye className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white">Top Performance Hooks</h3>
          </div>
          <div className="space-y-4">
            {report?.top_hooks.map((h, i) => (
              <div key={i} className="flex flex-col p-3 rounded-xl bg-slate-900/50 border border-slate-800">
                <span className="text-xs text-slate-300 line-clamp-1 mb-2">"{h.hook}"</span>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] text-slate-500 uppercase font-bold">{h.product_name}</span>
                  <span className="text-xs font-black text-purple-400">{h.avg_views.toLocaleString()} views</span>
                </div>
              </div>
            ))}
             {report?.top_hooks.length === 0 && <p className="text-sm text-slate-500 italic">No data yet</p>}
          </div>
        </div>

        {/* Top Angles */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-emerald-600/20 p-2 rounded-lg text-emerald-500">
              <MousePointer2 className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white">Winning Angles</h3>
          </div>
          <div className="space-y-4">
            {report?.top_angles.map((a, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/50 border border-slate-800">
                <span className="text-sm font-medium text-slate-300 truncate max-w-[150px]">{a.angle_name}</span>
                <span className="text-xs font-black text-emerald-400">{a.avg_ctr.toFixed(1)}% CTR</span>
              </div>
            ))}
             {report?.top_angles.length === 0 && <p className="text-sm text-slate-500 italic">No data yet</p>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Candidates to Retry */}
        <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-amber-600/20 p-2 rounded-lg text-amber-500">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white">Candidates to Optimize/Retry</h3>
          </div>
          <div className="space-y-4">
            {report?.candidates_to_retry.map((c, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex justify-between items-center group cursor-default">
                <div>
                  <p className="text-sm font-bold text-white mb-1">{c.product_name}</p>
                  <p className="text-xs text-slate-500">Rating: {c.avg_rating.toFixed(1)} | {c.avg_views.toLocaleString()} views</p>
                </div>
                <div className="flex items-center gap-2 text-amber-500 opacity-60 group-hover:opacity-100 transition-opacity">
                  <span className="text-xs font-bold">Good Rating, Mid Views</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            ))}
             {report?.candidates_to_retry.length === 0 && <p className="text-sm text-slate-500 italic">No candidates found yet.</p>}
          </div>
        </div>

         {/* Candidates to Drop */}
         <div className="glass-card rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-red-600/20 p-2 rounded-lg text-red-500">
              <TrendingDown className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white">Candidates to Drop</h3>
          </div>
          <div className="space-y-4">
            {report?.candidates_to_drop.map((c, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex justify-between items-center group cursor-default">
                 <div>
                  <p className="text-sm font-bold text-white mb-1">{c.product_name}</p>
                  <p className="text-xs text-slate-500">Rating: {c.avg_rating.toFixed(1)} | {c.avg_views.toLocaleString()} views</p>
                </div>
                <div className="flex items-center gap-2 text-red-500 opacity-60 group-hover:opacity-100 transition-opacity">
                  <span className="text-xs font-bold">Low Rating & Views</span>
                  <AlertTriangle className="w-4 h-4" />
                </div>
              </div>
            ))}
            {report?.candidates_to_drop.length === 0 && <p className="text-sm text-slate-500 italic">No candidates found yet.</p>}
          </div>
        </div>
      </div>

      {/* Stuck Jobs Monitoring */}
      {report?.stuck_jobs && report.stuck_jobs.length > 0 && (
        <div className="glass-card rounded-2xl p-6 border border-amber-600/30 bg-amber-600/5">
          <div className="flex items-center gap-3 mb-6 font-bold text-amber-500 uppercase tracking-widest text-xs">
            <Clock className="w-5 h-5" />
            Active Bottlenecks (Stuck {">"}30m)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {report.stuck_jobs.map((s: any, i: number) => (
              <div key={i} className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
                <div>
                    <p className="text-xs font-bold text-white mb-1">Job {s.job_id.slice(0,8)}</p>
                    <p className="text-[10px] text-slate-500">Started: {new Date(s.started_at).toLocaleString()}</p>
                </div>
                <div className="bg-amber-600/20 text-amber-500 px-2 py-1 rounded text-[10px] font-black">STUCK</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
