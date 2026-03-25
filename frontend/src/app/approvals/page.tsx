"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  XCircle,
  FileText,
  PlayCircle,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  Download,
  Copy,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";
import { useToast } from "@/components/ui/Toast";

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
  bundle?: {
    hook: string;
    caption: string;
    hashtags: string;
    link: string;
  };
}

export default function ApprovalsPage() {
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"pending" | "history">("pending");
  const [actioning, setActioning] = useState<string | null>(null);
  const [comments, setComments] = useState<Record<string, string>>({});
  const [previewItem, setPreviewItem] = useState<ApprovalItem | null>(null);
  const { success, error } = useToast();

  const fetchApprovals = async () => {
    try {
      setLoading(true);
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
        details: j.status === "approved" ? "Final asset bundle ready for publishing." : "Rendered video ready for final review.",
        creator: "Render Engine",
        status: j.status,
        created_at: j.created_at,
        output_path: j.output_path,
        bundle: j.status === "approved" ? {
          hook: j.script?.hook || "Must-have find!",
          caption: j.script?.body || "Check out this amazing product!",
          hashtags: j.script?.product?.category ? `#${j.script.product.category.replace(/\s+/g, '')} #musthave #finds` : "#musthave #finds",
          link: j.script?.product?.affiliate_link || "https://example.com/mock-link"
        } : undefined
      }));

      const allItems = [...scriptItems, ...jobItems].sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      
      setItems(allItems as ApprovalItem[]);
    } catch (err: any) {
      console.error("Failed to fetch approvals", err);
      // Don't show toast for fetch errors directly on load to avoid spam
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [activeTab]);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      success(`${label} copied to clipboard`);
    } catch (err) {
      error("Failed to copy text");
    }
  };

  const handleAction = async (
    item: ApprovalItem,
    action: "approve" | "reject",
  ) => {
    setActioning(item.id);
    try {
      if (item.type === "script") {
        const status = action === "approve" ? "approved" : "rejected";
        await api.patch(`/scripts/${item.original_id}`, { status });
      } else {
        await api.post(`/jobs/${item.original_id}/approve`, {
          decision: action === "approve" ? "approved" : "rejected",
          comment: comments[item.id] || "Reviewed via dashboard",
        });
      }
      
      const newComments = { ...comments };
      delete newComments[item.id];
      setComments(newComments);
      
      success(action === "approve" ? "Successfully approved item" : "Rejected item");
      await fetchApprovals();
    } catch (err: any) {
      console.error("Action failed", err);
      error(err?.response?.data?.detail || `Failed to ${action} item`);
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

                  {item.output_path && item.type === "video_job" && (
                    <div className="flex gap-4 mt-4 mb-2">
                        <button 
                        onClick={() => setPreviewItem(item)}
                        className="flex items-center gap-2 text-blue-500 hover:text-blue-400 text-sm font-bold transition-all"
                        >
                        <PlayCircle className="w-4 h-4" /> Preview
                        </button>
                        <a 
                            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/jobs/${item.original_id}/download`}
                            download
                            className="flex items-center gap-2 text-emerald-500 hover:text-emerald-400 text-sm font-bold transition-all"
                        >
                            <Download className="w-4 h-4" /> Download Video
                        </a>
                    </div>
                  )}

                  {activeTab === "history" && item.type === "video_job" && item.status === "approved" && item.bundle && (
                    <div className="mt-4 p-4 bg-slate-900/50 rounded-xl border border-slate-800 space-y-3">
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Publishing Asset Bundle</h4>
                      
                      <div className="flex bg-slate-950 rounded-lg border border-slate-800 p-3 items-center justify-between group">
                        <div className="truncate mr-4 flex-1">
                          <span className="text-[10px] text-slate-500 block">Hook</span>
                          <span className="text-sm text-slate-300 truncate">{item.bundle.hook}</span>
                        </div>
                        <button onClick={() => item.bundle && copyToClipboard(item.bundle.hook, "Hook")} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="flex bg-slate-950 rounded-lg border border-slate-800 p-3 items-start justify-between group">
                        <div className="mr-4 flex-1">
                          <span className="text-[10px] text-slate-500 block">Caption Body</span>
                          <span className="text-sm text-slate-300 line-clamp-2">{item.bundle.caption}</span>
                        </div>
                        <button onClick={() => item.bundle && copyToClipboard(item.bundle.caption, "Caption")} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="flex bg-slate-950 rounded-lg border border-slate-800 p-3 items-center justify-between group">
                        <div className="truncate mr-4 flex-1">
                          <span className="text-[10px] text-slate-500 block">Hashtags</span>
                          <span className="text-sm text-blue-400 font-mono truncate">{item.bundle.hashtags}</span>
                        </div>
                        <button onClick={() => item.bundle && copyToClipboard(item.bundle.hashtags, "Hashtags")} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="flex bg-slate-950 rounded-lg border border-slate-800 p-3 items-center justify-between group">
                        <div className="truncate mr-4 flex-1">
                          <span className="text-[10px] text-slate-500 block">Affiliate Link</span>
                          <span className="text-sm text-emerald-400 truncate font-mono">{item.bundle.link}</span>
                        </div>
                        <button onClick={() => item.bundle && copyToClipboard(item.bundle.link, "Link")} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-400 hover:text-white transition-colors">
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>

                      <button 
                        onClick={() => item.bundle && copyToClipboard(`${item.bundle.hook}\n\n${item.bundle.caption}\n\nGet it here: ${item.bundle.link}\n\n${item.bundle.hashtags}`, "Full Post")} 
                        className="w-full mt-2 bg-blue-600/10 hover:bg-blue-600 text-blue-500 hover:text-white border border-blue-500/20 py-2 rounded-lg text-sm font-bold transition-all flex justify-center items-center gap-2"
                      >
                        <Copy className="w-4 h-4" /> Copy Entire Post
                      </button>
                    </div>
                  )}

                  {activeTab === "pending" && (
                    <div className="mt-4">
                      <textarea
                        placeholder="Add a review note (optional)..."
                        className="w-full bg-slate-900/50 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all resize-none"
                        rows={2}
                        value={comments[item.id] || ""}
                        onChange={(e) => setComments({ ...comments, [item.id]: e.target.value })}
                      />
                    </div>
                  )}
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
                  src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/jobs/${previewItem.original_id}/preview`}
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
