"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Cpu,
  Key,
  ShieldCheck,
  Users,
  History,
  Save,
  RefreshCcw,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Plus,
} from "lucide-react";
import api from "@/lib/api";
import { cn } from "@/lib/utils";

interface AIProvider {
  id: string;
  provider_name: string;
  api_key_masked: string;
  is_active: boolean;
  priority: number;
}

export default function AdminSettingsPage() {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState<"ai" | "users" | "logs">(
    "ai",
  );
  const [saving, setSaving] = useState(false);

  const fetchProviders = async () => {
    try {
      const response = await api.get("/admin/ai-providers");
      setProviders(response.data);
    } catch (error) {
      console.error("Failed to fetch providers", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">System Settings</h1>
        <p className="text-slate-400">
          Configure AI models, user permissions, and system preferences.
        </p>
      </div>

      <div className="flex gap-4 p-1 bg-slate-900 border border-slate-800 rounded-2xl w-fit">
        {[
          { id: "ai", label: "AI Providers", icon: Cpu },
          { id: "users", label: "Team Members", icon: Users },
          { id: "logs", label: "Audit Logs", icon: History },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id as any)}
            className={cn(
              "flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition-all",
              activeSubTab === tab.id
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "text-slate-500 hover:text-slate-300",
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-8">
        <AnimatePresence mode="wait">
          {activeSubTab === "ai" && (
            <motion.div
              key="ai-settings"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-white">
                  Configured Providers
                </h2>
                <button className="bg-slate-900 border border-slate-800 text-slate-300 hover:text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition-all">
                  <Plus className="w-4 h-4" /> Add Provider
                </button>
              </div>

              {loading ? (
                <div className="h-40 bg-slate-900 animate-pulse rounded-2xl" />
              ) : providers.length === 0 ? (
                <div className="p-8 rounded-2xl border-2 border-dashed border-slate-800 text-center text-slate-500">
                  <p>No AI providers configured. Using system defaults.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {providers.map((p) => (
                    <div
                      key={p.id}
                      className="glass-card p-6 rounded-2xl border border-slate-800 flex flex-col justify-between"
                    >
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center">
                            <Key className="w-5 h-5 text-blue-500" />
                          </div>
                          <div>
                            <h3 className="font-bold text-white capitalize">
                              {p.provider_name}
                            </h3>
                            <p className="text-xs text-slate-500">
                              Priority {p.priority}
                            </p>
                          </div>
                        </div>
                        <div
                          className={cn(
                            "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border",
                            p.is_active
                              ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                              : "bg-slate-800 text-slate-500 border-slate-700",
                          )}
                        >
                          {p.is_active ? "Active" : "Inactive"}
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between items-center">
                          <code className="text-xs text-slate-400">
                            {p.api_key_masked}
                          </code>
                          <RefreshCcw className="w-3.5 h-3.5 text-slate-600 hover:text-blue-500 cursor-pointer transition-colors" />
                        </div>
                        <div className="flex gap-2">
                          <button className="flex-1 bg-slate-900 hover:bg-slate-800 text-white font-bold py-2 rounded-lg text-xs transition-colors border border-slate-800">
                            Edit Config
                          </button>
                          <button
                            className={cn(
                              "px-4 py-2 rounded-lg text-xs font-bold transition-all",
                              p.is_active
                                ? "bg-white text-slate-950"
                                : "bg-blue-600 text-white",
                            )}
                          >
                            {p.is_active ? "Deactivate" : "Activate"}
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="glass-card p-8 rounded-3xl border border-blue-500/20 bg-blue-500/5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-blue-600/20 rounded-lg">
                    <ShieldCheck className="w-5 h-5 text-blue-500" />
                  </div>
                  <h3 className="text-lg font-bold text-white">
                    Automated Provisioning
                  </h3>
                </div>
                <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                  System automatically rotates API keys and monitors usage
                  limits. If a provider fails more than 3 times in a row, the
                  system will fallback to the next available provider in
                  priority.
                </p>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-xs text-slate-500 font-medium">
                      Auto-Healing Enabled
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <span className="text-xs text-slate-500 font-medium">
                      Smart Fallback On
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeSubTab === "users" && (
            <motion.div
              key="user-settings"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="glass-card p-20 rounded-3xl flex flex-col items-center justify-center text-slate-500 text-center"
            >
              <Users className="w-12 h-12 mb-4 opacity-20" />
              <p className="font-bold text-white mb-2">Multi-user Management</p>
              <p className="text-sm max-w-sm">
                This module allows you to invite team members and assign roles
                (Reviewer, Editor, Admin).
              </p>
              <button className="mt-6 bg-blue-600 text-white px-6 py-2 rounded-xl text-sm font-bold">
                Invite User
              </button>
            </motion.div>
          )}

          {activeSubTab === "logs" && (
            <motion.div
              key="log-settings"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="glass-card rounded-2xl overflow-hidden border border-slate-800"
            >
              <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                <h3 className="font-bold text-white">System Audit Logs</h3>
                <button className="text-xs text-blue-500 hover:underline">
                  Export CSV
                </button>
              </div>
              <div className="h-64 flex items-center justify-center text-slate-600 italic text-sm">
                Loading recent activity logs...
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="flex justify-end pt-4">
        <button
          disabled={saving}
          className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-8 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
        >
          {saving ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Save className="w-5 h-5" />
          )}
          Save All Changes
        </button>
      </div>
    </div>
  );
}
