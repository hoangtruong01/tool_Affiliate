"use client";

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ShoppingBag,
  PlayCircle,
  CheckCircle2,
  Zap,
  ArrowUpRight,
  Clock,
  AlertCircle,
} from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

interface Stats {
  products_total: number;
  scripts_total: number;
  jobs_total: number;
  assets_total: number;
  job_status_breakdown: Record<string, number>;
  pending_approvals: {
    scripts: number;
    video_jobs: number;
  };
  success_rate: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await api.get("/analytics/dashboard");
        setStats(response.data);
      } catch (error: any) {
        console.error("Failed to fetch stats", error);
        if (error.response?.status === 401) {
          window.location.href = "/login";
        }
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  const statCards = [
    {
      label: "Products",
      value: stats?.products_total || 0,
      icon: ShoppingBag,
      color: "text-blue-500",
      bg: "bg-blue-500/10",
    },
    {
      label: "Total Jobs",
      value: stats?.jobs_total || 0,
      icon: PlayCircle,
      color: "text-purple-500",
      bg: "bg-purple-500/10",
    },
    {
      label: "Approved",
      value: stats?.job_status_breakdown?.approved || 0,
      icon: CheckCircle2,
      color: "text-emerald-500",
      bg: "bg-emerald-500/10",
    },
    {
      label: "Success Rate",
      value: `${stats?.success_rate || 0}%`,
      icon: Zap,
      color: "text-amber-500",
      bg: "bg-amber-500/10",
    },
  ];

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-10 w-64 bg-slate-900 rounded-lg" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-32 bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
        <p className="text-slate-400">
          Here's what's happening with your video automation pipeline.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 rounded-2xl group hover:border-blue-500/50 transition-colors"
          >
            <div className="flex justify-between items-start mb-4">
              <div className={cn("p-2 rounded-xl", stat.bg)}>
                <stat.icon className={cn("w-6 h-6", stat.color)} />
              </div>
              <ArrowUpRight className="w-4 h-4 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div>
              <p className="text-slate-400 text-sm font-medium mb-1">
                {stat.label}
              </p>
              <h3 className="text-2xl font-bold text-white">{stat.value}</h3>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 rounded-2xl"
        >
          <div className="flex items-center gap-2 mb-6">
            <Clock className="w-5 h-5 text-blue-500" />
            <h2 className="text-xl font-bold text-white">Pending Approvals</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 hover:bg-slate-900 transition-colors cursor-pointer group">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                <span className="text-slate-200 font-medium">
                  Video Scripts
                </span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-500 text-xs font-bold border border-blue-500/20 group-hover:bg-blue-500 group-hover:text-white transition-colors">
                {stats?.pending_approvals.scripts}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 hover:bg-slate-900 transition-colors cursor-pointer group">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]" />
                <span className="text-slate-200 font-medium">
                  Rendered Videos
                </span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-500 text-xs font-bold border border-purple-500/20 group-hover:bg-purple-500 group-hover:text-white transition-colors">
                {stats?.pending_approvals.video_jobs}
              </span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6 rounded-2xl"
        >
          <div className="flex items-center gap-2 mb-6">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <h2 className="text-xl font-bold text-white">Recent Failures</h2>
          </div>

          {stats?.job_status_breakdown.failed ? (
            <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/10">
              <p className="text-red-400 text-sm font-medium">
                {stats.job_status_breakdown.failed} jobs encountered errors.
                Check the Video Jobs tab to investigate.
              </p>
            </div>
          ) : (
            <div className="h-28 flex flex-col items-center justify-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
              <CheckCircle2 className="w-8 h-8 mb-2 opacity-20" />
              <p className="text-sm">No recent errors detected.</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
