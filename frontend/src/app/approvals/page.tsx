"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  XCircle,
  Clock,
  MessageSquare,
  ChevronRight,
  FileText,
  PlayCircle,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  ExternalLink,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";

interface ApprovalItem {
  id: string;
  type: "script" | "video_job";
  title: string;
  details: string;
  creator: string;
  status: string;
  created_at: string;
  original_id: string;
  output_path?: string;
}

export default function ApprovalsPage() {
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"pending" | "history">("pending");
  const [actioning, setActioning] = useState<string | null>(null);
  const [comments, setComments] = useState<Record<string, string>>({});
  const [previewItem, setPreviewItem] = useState<ApprovalItem | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      // In a real app, we'd have a specific /approvals endpoint
      // Here we'll fetch scripts and jobs based on activeTab
      const statuses = activeTab === "pending" 
        ? { script: "pending_approval", job: "needs_review" }
        : { script: "approved,rejected", job: "approved,rejected" };

      const [scriptsRes, jobsRes] = await Promise.all([
        api.get("/scripts/", { params: { status: statuses.script } }),
        api.get("/jobs/", { params: { status: statuses.job } }),
      ]);

      const scriptItems = scriptsRes.data.items.map((s: any) => ({
        id: `script-${s.id}`,
        original_id: s.id,
        type: "script",
        title: `Script: ${s.product.name}`,
        details: s.hook,
        creator: s.user?.full_name || "AI System",
        status: s.status,
        created_at: s.created_at,
      }));

      const jobItems = jobsRes.data.items.map((j: any) => ({
        id: `job-${j.id}`,
        original_id: j.id,
        type: "video_job",
        title: `Video: ${j.script?.product.name || "Unknown"}`,
        details: "Rendered video ready for final review.",
        creator: "Render Engine",
        status: j.status,
        created_at: j.created_at,
        output_path: j.output_path,
      }));

      const allItems = [...scriptItems, ...jobItems].sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      
      setItems(allItems as ApprovalItem[]);
    } catch (error) {
      console.error("Failed to fetch approvals", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [activeTab]);

  const handleAction = async (
    item: ApprovalItem,
    action: "approve" | "reject",
  ) => {
    setActioning(item.id);
    try {
      if (item.type === "script") {
        // Scripts use a direct PATCH for status in this MVP version
        // but we'll normalize the value
        const status = action === "approve" ? "approved" : "rejected";
        await api.patch(`/scripts/${item.original_id}`, { status });
      } else {
        // Video jobs use the dedicated approval endpoint
        await api.post(`/jobs/${item.original_id}/approve`, {
          decision: action === "approve" ? "approved" : "rejected",
          comment: comments[item.id] || "Reviewed via dashboard",
        });
      }
      // Clear comment for this item
      const newComments = { ...comments };
      delete newComments[item.id];
      setComments(newComments);
      
      await fetchApprovals();
    } catch (error) {
      console.error("Action failed", error);
    } finally {
      setActioning(null);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Content Approval</h1>
        <p className="text-slate-400">
          Review and approve AI-generated content before publishing.
        </p>
      </div>

      <div className="flex gap-4 border-b border-slate-900">
        <button
          onClick={() => setActiveTab("pending")}
          className={cn(
            "pb-4 px-2 text-sm font-bold transition-all relative",
            activeTab === "pending"
              ? "text-blue-500"
              : "text-slate-500 hover:text-slate-300",
          )}
        >
          Pending Review
          {activeTab === "pending" && (
            <motion.div
              layoutId="tab"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={cn(
            "pb-4 px-2 text-sm font-bold transition-all relative",
            activeTab === "history"
              ? "text-blue-500"
              : "text-slate-500 hover:text-slate-300",
          )}
        >
          Approval History
          {activeTab === "history" && (
            <motion.div
              layoutId="tab"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500 rounded-full"
            />
          )}
        </button>
      </div>

      {loading ? (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-40 bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-3xl">
          <CheckCircle2 className="w-12 h-12 mb-4 opacity-10" />
          <p>Inbox is clear. No items pending review.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          <AnimatePresence>
            {items.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass-card group rounded-2xl overflow-hidden flex flex-col md:flex-row border border-slate-800 hover:border-blue-500/20 transition-all"
              >
                <div className="p-6 flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div
                      className={cn(
                        "p-2 rounded-xl",
                        item.type === "script"
                          ? "bg-amber-500/10"
                          : "bg-blue-500/10",
                      )}
                    >
                      {item.type === "script" ? (
                        <FileText className="w-5 h-5 text-amber-500" />
                      ) : (
                        <PlayCircle className="w-5 h-5 text-blue-500" />
                      )}
                    </div>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                      {item.type}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-800" />
                    <span className="text-xs text-slate-600">
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2">
                    {item.title}
                  </h3>
                  <p className="text-slate-400 text-sm line-clamp-2 italic mb-4">
                    "{item.details}"
                  </p>

                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                      {item.creator.charAt(0)}
                    </div>
                    <span className="text-xs text-slate-500 font-medium">
                      Created by {item.creator}
                    </span>
                  </div>

                  {item.output_path && (
                    <button 
                      onClick={() => setPreviewItem(item)}
                      className="mt-4 mb-2 flex items-center gap-2 text-blue-500 hover:text-blue-400 text-sm font-bold transition-all"
                    >
                      <PlayCircle className="w-4 h-4" /> Preview Video
                    </button>
                  )}

                  <div className="mt-4">
                    <textarea
                      placeholder="Add a review note (optional)..."
                      className="w-full bg-slate-900/50 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all resize-none"
                      rows={2}
                      value={comments[item.id] || ""}
                      onChange={(e) => setComments({ ...comments, [item.id]: e.target.value })}
                    />
                  </div>
                </div>

                {activeTab === "pending" && (
                  <div className="p-6 bg-slate-900/30 border-t md:border-t-0 md:border-l border-slate-800 flex flex-row md:flex-col justify-center gap-3 min-w-[200px]">
                    <button
                      disabled={actioning === item.id}
                      onClick={() => handleAction(item, "approve")}
                      className="flex-1 flex items-center justify-center gap-2 bg-emerald-600/10 hover:bg-emerald-600 text-emerald-500 hover:text-white dark-transition border border-emerald-500/20 font-bold py-2.5 rounded-xl text-sm"
                    >
                      {actioning === item.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <ThumbsUp className="w-4 h-4" />
                      )}
                      Approve
                    </button>
                    <button
                      disabled={actioning === item.id}
                      onClick={() => handleAction(item, "reject")}
                      className="flex-1 flex items-center justify-center gap-2 bg-red-600/10 hover:bg-red-600 text-red-500 hover:text-white dark-transition border border-red-500/20 font-bold py-2.5 rounded-xl text-sm"
                    >
                      {actioning === item.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <ThumbsDown className="w-4 h-4" />
                      )}
                      Reject
                    </button>
                  </div>
                )}
                {activeTab === "history" && (
                  <div className="p-6 bg-slate-900/30 border-t md:border-t-0 md:border-l border-slate-800 flex flex-col justify-center items-center min-w-[200px]">
                    <div className={cn(
                      "px-4 py-2 rounded-full text-xs font-bold uppercase tracking-widest border",
                      item.status === "approved" 
                        ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                        : "bg-red-500/10 text-red-500 border-red-500/20"
                    )}>
                      {item.status}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Video Preview Modal */}
      <AnimatePresence>
        {previewItem && (
          <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setPreviewItem(null)}
              className="absolute inset-0 bg-slate-950/90 backdrop-blur-md"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="w-full max-w-5xl aspect-video glass-card rounded-3xl overflow-hidden relative z-10 group shadow-2xl shadow-blue-500/10"
            >
              <button
                onClick={() => setPreviewItem(null)}
                className="absolute top-6 right-6 z-20 bg-slate-950/50 hover:bg-slate-900 p-2 rounded-full text-white/50 hover:text-white transition-all backdrop-blur-md border border-white/10"
              >
                <XCircle className="w-6 h-6" />
              </button>
              
              <div className="absolute top-6 left-6 z-20 bg-slate-950/50 px-4 py-2 rounded-xl backdrop-blur-md border border-white/10">
                <p className="text-sm font-bold text-white mb-0.5">{previewItem.title}</p>
                <p className="text-xs text-blue-400 font-medium">Status: {previewItem.status}</p>
              </div>

              {previewItem.output_path ? (
                <video 
                  src={previewItem.output_path}
                  controls
                  autoPlay
                  className="w-full h-full object-contain bg-black"
                />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500">
                  <PlayCircle className="w-16 h-16 mb-4 opacity-10" />
                  <p>Video output not available</p>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
