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
  History,
  Share2,
  BarChart3,
  PieChart,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";
import { useToast } from "@/components/ui/Toast";

interface VideoJob {
  id: string;
  script_id: string;
  script?: { 
    hook: string; 
    product: { name: string };
    angle_id?: string;
  };
  status: string;
  output_path?: string;
  duration_seconds?: number;
  error_message?: string;
  created_at: string;
  retry_count: number;
  posted_at?: string;
  platform?: string;
  post_url?: string;
  performance_notes?: string;
  is_successful?: boolean | null;
  operator_notes?: string;
  publish_outcome?: string;
  performance_metrics?: any[];
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
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchFilter, setSearchFilter] = useState<string>("");

  // Create Job State
  const [scripts, setScripts] = useState<any[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedScript, setSelectedScript] = useState("");
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);
  const [previewJob, setPreviewJob] = useState<VideoJob | null>(null);
  const { success, error } = useToast();
  const [expandedJob, setExpandedJob] = useState<string | null>(null);

  const [trackingJobId, setTrackingJobId] = useState<string | null>(null);
  const [trackingData, setTrackingData] = useState<{ 
    post_url: string; 
    performance_notes: string; 
    is_successful: boolean | null;
    platform: string;
    posted_at: string;
    operator_notes: string;
    publish_outcome: string;
  }>({
    post_url: "",
    performance_notes: "",
    is_successful: null,
    platform: "tiktok",
    posted_at: new Date().toISOString().slice(0, 16),
    operator_notes: "",
    publish_outcome: "",
  });

  const [metricsJobId, setMetricsJobId] = useState<string | null>(null);
  const [metricsData, setMetricsData] = useState({
    views: 0,
    watch_time_seconds: 0,
    ctr_estimate: 0,
    conversions: 0,
    operator_rating: 3,
    notes: "",
  });
  const [savingMetrics, setSavingMetrics] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (searchFilter) params.search = searchFilter;
      
      const response = await api.get("/jobs/", { params });
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
        api.get("/scripts/", { params: { status: "approved" } }),
        api.get("/assets/", { params: { asset_type: "image" } }),
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
  }, [statusFilter, searchFilter]);

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
      success("Video render job queued successfully");
    } catch (err: any) {
      console.error("Create failed", err);
      error(err?.response?.data?.detail || "Failed to create render job");
    } finally {
      setCreating(false);
    }
  };

  const handleUpdateTracking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackingJobId) return;
    try {
      await api.patch(`/jobs/${trackingJobId}/publish`, {
        ...trackingData,
        posted_at: trackingData.posted_at ? new Date(trackingData.posted_at).toISOString() : null
      });
      success("Publish tracking updated!");
      setTrackingJobId(null);
      fetchJobs();
    } catch (err: any) {
      console.error("Track failed", err);
      error(err?.response?.data?.detail || "Failed to update tracking info");
    }
  };

  const handleSaveMetrics = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!metricsJobId) return;
    setSavingMetrics(true);
    try {
      await api.post(`/jobs/${metricsJobId}/metrics`, metricsData);
      success("Performance metrics saved!");
      setMetricsJobId(null);
      fetchJobs();
    } catch (err: any) {
      console.error("Metrics failed", err);
      error(err?.response?.data?.detail || "Failed to save metrics");
    } finally {
      setSavingMetrics(false);
    }
  };

  const toggleAsset = (id: string) => {
    setSelectedAssets((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id],
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "needs_review":
      case "approved":
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
      case "failed":
      case "rejected":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "cancelled":
        return <X className="w-5 h-5 text-slate-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-amber-500" />;
    }
  };

  const handleRetry = async (jobId: string) => {
    try {
      await api.post(`/jobs/${jobId}/retry`);
      success("Job retry queued");
      fetchJobs();
    } catch (err: any) {
      console.error("Retry failed", err);
      error(err?.response?.data?.detail || "Failed to retry job");
    }
  };

  const handleCancel = async (jobId: string) => {
    try {
      await api.post(`/jobs/${jobId}/cancel`);
      success("Job cancelled");
      fetchJobs();
    } catch (err: any) {
      console.error("Cancel failed", err);
      error(err?.response?.data?.detail || "Failed to cancel job");
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Video Jobs</h1>
          <p className="text-slate-400">
            Track and manage your automated video rendering pipeline.
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <input
            type="text"
            placeholder="Search script hook..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-white text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-white text-sm rounded-xl focus:ring-blue-500 focus:border-blue-500 block p-2.5"
          >
            <option value="">All Statuses</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="needs_review">Needs Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button
            onClick={() => setIsModalOpen(true)}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20 whitespace-nowrap"
          >
            <Plus className="w-5 h-5" /> New Render Job
          </button>
        </div>
      </div>

      {/* Today's Activity Summary Box */}
      {!loading && jobs.length > 0 && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Needs Review", value: jobs.filter(j => j.status === "needs_review").length, color: "text-blue-400" },
            { label: "Processing / Queued", value: jobs.filter(j => j.status === "queued" || j.status === "processing").length, color: "text-amber-400" },
            { label: "Approved (All time)", value: jobs.filter(j => j.status === "approved" || j.status === "published").length, color: "text-emerald-400" },
            { label: "Needs Attention (Failed)", value: jobs.filter(j => j.status === "failed" || j.status === "rejected" || j.status === "cancelled").length, color: "text-red-400" },
          ].map((stat, i) => (
            <div key={i} className="glass-card rounded-2xl p-4 border border-slate-800 flex flex-col justify-center">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{stat.label}</span>
              <span className={cn("text-3xl font-black mt-2", stat.color)}>{stat.value}</span>
            </div>
          ))}
        </div>
      )}

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
                  <React.Fragment key={job.id}>
                  <tr
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
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <span
                            className={cn(
                              "text-xs font-bold capitalize",
                              job.status === "needs_review" || job.status === "approved" || job.status === "published"
                                ? "text-emerald-500"
                                : job.status === "failed" || job.status === "rejected"
                                  ? "text-red-500"
                                  : job.status === "processing"
                                    ? "text-blue-500"
                                    : "text-slate-500",
                            )}
                          >
                            {job.status}
                          </span>
                        </div>
                        {job.retry_count > 0 && (
                          <p className="text-[10px] text-slate-500">
                            Retries: {job.retry_count}
                          </p>
                        )}
                        {job.error_message && (
                          <p className="text-[10px] text-red-400 mt-1 max-w-[150px] truncate" title={job.error_message}>
                            {job.error_message}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs">
                      {formatDate(job.created_at)}
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-xs text-center">
                      {job.duration_seconds ? `${job.duration_seconds}s` : "-"}
                    </td>
                    <td className="px-6 py-4 text-right">
                        {job.output_path && (
                          <button 
                            onClick={() => setPreviewJob(job)}
                            className="p-2 bg-emerald-600/10 text-emerald-500 hover:bg-emerald-600 hover:text-white rounded-lg transition-all border border-emerald-600/20" title="Preview">
                            <PlayCircle className="w-4 h-4" />
                          </button>
                        )}
                        {(job.status === "needs_review" || job.status === "approved" || job.status === "published") && job.output_path && (
                          <a 
                            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/jobs/${job.id}/download`}
                            download
                            className="p-2 bg-blue-600/10 text-blue-500 hover:bg-blue-600 hover:text-white rounded-lg transition-all border border-blue-600/20" title="Download">
                            <Download className="w-4 h-4" />
                          </a>
                        )}
                        {(job.status === "failed" || job.status === "rejected" || job.status === "cancelled") && (
                          <button 
                            onClick={() => handleRetry(job.id)}
                            className="p-2 bg-amber-600/10 text-amber-500 hover:bg-amber-600 hover:text-white rounded-lg transition-all border border-amber-600/20" title="Retry">
                            <Clock className="w-4 h-4" />
                          </button>
                        )}
                        {(job.status === "queued" || job.status === "processing") && (
                          <button 
                            onClick={() => handleCancel(job.id)}
                            className="p-2 bg-red-600/10 text-red-500 hover:bg-red-600 hover:text-white rounded-lg transition-all border border-red-600/20" title="Cancel">
                            <X className="w-4 h-4" />
                          </button>
                        )}
                        <button 
                          onClick={() => setExpandedJob(expandedJob === job.id ? null : job.id)}
                          className="p-2 ml-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-all border border-slate-700" title="History">
                          <History className="w-4 h-4" />
                        </button>
                        {(job.status === "approved" || job.status === "published") && (
                          <button 
                            onClick={() => {
                              setTrackingJobId(job.id);
                              setTrackingData({
                                post_url: job.post_url || "",
                                performance_notes: job.performance_notes || "",
                                is_successful: job.is_successful ?? null,
                                platform: job.platform || "tiktok",
                                posted_at: job.posted_at ? new Date(job.posted_at).toISOString().slice(0, 16) : new Date().toISOString().slice(0, 16),
                                operator_notes: job.operator_notes || "",
                                publish_outcome: job.publish_outcome || "",
                              });
                            }}
                            className="p-2 ml-2 bg-purple-600/10 text-purple-400 hover:bg-purple-600 hover:text-white rounded-lg transition-all border border-purple-600/20" title="Track Publishing">
                            <Share2 className="w-4 h-4" />
                          </button>
                        )}
                        {job.status === "published" && (
                          <button 
                            onClick={() => {
                              setMetricsJobId(job.id);
                              const lastMetric = job.performance_metrics?.[0] || {};
                              setMetricsData({
                                views: lastMetric.views || 0,
                                watch_time_seconds: lastMetric.watch_time_seconds || 0,
                                ctr_estimate: lastMetric.ctr_estimate || 0,
                                conversions: lastMetric.conversions || 0,
                                operator_rating: lastMetric.operator_rating || 3,
                                notes: "",
                              });
                            }}
                            className="p-2 ml-2 bg-emerald-600/10 text-emerald-400 hover:bg-emerald-600 hover:text-white rounded-lg transition-all border border-emerald-600/20" title="Add Performance Snapshot">
                            <BarChart3 className="w-4 h-4" />
                          </button>
                        )}
                        <button className="p-2 ml-2 bg-slate-800 text-slate-500 hover:text-white rounded-lg transition-all border border-slate-700">
                           <Trash2 className="w-4 h-4" />
                        </button>
                    </td>
                  </tr>
                  
                  {/* Expandable History Row */}
                  <AnimatePresence>
                    {expandedJob === job.id && (
                      <motion.tr
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                      >
                        <td colSpan={5} className="px-6 py-4 bg-slate-900/80 border-b border-slate-800/50">
                          <div className="flex flex-col md:flex-row gap-6 text-sm">
                            <div className="flex-1 space-y-2">
                              <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest">Job Details</p>
                              <p className="text-slate-300"><span className="text-slate-500">Job ID:</span> {job.id}</p>
                              <p className="text-slate-300"><span className="text-slate-500">Script ID:</span> {job.script_id}</p>
                            </div>
                            {job.status === "published" && (
                              <div className="mt-2 text-xs">
                                <p className="text-slate-400 font-bold uppercase text-[10px] tracking-widest mt-4 mb-2">Publish Data</p>
                                <p className="text-slate-300"><span className="text-slate-500 pr-2">Platform:</span> <span className="capitalize">{job.platform || "Not set"}</span></p>
                                <p className="text-slate-300"><span className="text-slate-500 pr-2">Outcome:</span> <span className="capitalize">{job.publish_outcome || "Not set"}</span></p>
                                <p className="text-slate-300"><span className="text-slate-500 pr-2">Link:</span> {job.post_url ? <a href={job.post_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">Link</a> : "None"}</p>
                                <p className="text-slate-300"><span className="text-slate-500 pr-2">Operator Notes:</span> {job.operator_notes || "None"}</p>
                              </div>
                            )}
                          </div>
                        </td>
                      </motion.tr>
                    )}
                  </AnimatePresence>
                </React.Fragment>
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
                          "aspect-square rounded-xl border cursor-pointer overflow-hidden relative transition-all group",
                          selectedAssets.includes(a.id)
                            ? "ring-2 ring-blue-500 border-transparent shadow-[0_0_15px_rgba(59,130,246,0.3)]"
                            : "bg-slate-900 border-slate-800",
                        )}
                      >
                        <img 
                          src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/assets/${a.id}/preview`}
                          alt={a.filename}
                          className="w-full h-full object-cover transition-transform group-hover:scale-110"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2">
                          <span className="text-[10px] text-white truncate w-full">{a.filename}</span>
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

      {/* Video Preview Modal */}
      <AnimatePresence>
        {previewJob && (
          <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setPreviewJob(null)}
              className="absolute inset-0 bg-slate-950/90 backdrop-blur-md"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="w-full max-w-5xl aspect-video glass-card rounded-3xl overflow-hidden relative z-10 group shadow-2xl shadow-blue-500/10"
            >
              <button
                onClick={() => setPreviewJob(null)}
                className="absolute top-6 right-6 z-20 bg-slate-950/50 hover:bg-slate-900 p-2 rounded-full text-white/50 hover:text-white transition-all backdrop-blur-md border border-white/10"
              >
                <X className="w-6 h-6" />
              </button>
              
              <div className="absolute top-6 left-6 z-20 bg-slate-950/50 px-4 py-2 rounded-xl backdrop-blur-md border border-white/10">
                <p className="text-sm font-bold text-white mb-0.5">{previewJob.script?.product.name}</p>
                <p className="text-xs text-blue-400 font-medium">Status: {previewJob.status}</p>
              </div>

              {previewJob.output_path ? (
                <video 
                  src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/jobs/${previewJob.id}/preview`}
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

      {/* Tracking Modal */}
      <AnimatePresence>
        {trackingJobId && (
          <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setTrackingJobId(null)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-lg glass-card rounded-3xl p-8 relative z-10"
            >
              <h2 className="text-2xl font-bold text-white mb-6">Track Publishing</h2>
              <form onSubmit={handleUpdateTracking} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Platform</label>
                    <select
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={trackingData.platform}
                      onChange={(e) => setTrackingData({ ...trackingData, platform: e.target.value })}
                    >
                      <option value="tiktok">TikTok</option>
                      <option value="reels">Instagram Reels</option>
                      <option value="shorts">YouTube Shorts</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Publish Date</label>
                    <input
                      type="datetime-local"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={trackingData.posted_at}
                      onChange={(e) => setTrackingData({ ...trackingData, posted_at: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Live Post URL</label>
                  <input
                    type="url"
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder:text-slate-600 focus:ring-1 focus:ring-blue-500"
                    placeholder="https://tiktok.com/@..."
                    value={trackingData.post_url}
                    onChange={(e) => setTrackingData({ ...trackingData, post_url: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Publish Outcome</label>
                  <select
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                    value={trackingData.publish_outcome}
                    onChange={(e) => setTrackingData({ ...trackingData, publish_outcome: e.target.value })}
                  >
                    <option value="">Unspecified</option>
                    <option value="success_viral">Success - Viral</option>
                    <option value="success_steady">Success - Steady Views</option>
                    <option value="shadowbanned">Shadowbanned / Restricted</option>
                    <option value="copyright_strike">Copyright Strike</option>
                    <option value="low_engagement">Low Engagement</option>
                  </select>
                </div>

                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Learning Signal</label>
                    <div className="flex gap-2">
                       <button
                        type="button"
                        onClick={() => setTrackingData({ ...trackingData, is_successful: true })}
                        className={cn(
                          "flex-1 p-2 rounded-xl border transition-all text-xs font-bold",
                          trackingData.is_successful === true ? "bg-emerald-600/20 border-emerald-500 text-emerald-400" : "bg-slate-900 border-slate-800 text-slate-500"
                        )}
                      >
                        👍 Good
                      </button>
                      <button
                        type="button"
                        onClick={() => setTrackingData({ ...trackingData, is_successful: false })}
                        className={cn(
                          "flex-1 p-2 rounded-xl border transition-all text-xs font-bold",
                          trackingData.is_successful === false ? "bg-red-600/20 border-red-500 text-red-400" : "bg-slate-900 border-slate-800 text-slate-500"
                        )}
                      >
                        👎 Poor
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Operator Notes</label>
                  <textarea
                    rows={2}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder:text-slate-600 focus:ring-1 focus:ring-blue-500"
                    placeholder="Internal notes for this specific publish run..."
                    value={trackingData.operator_notes}
                    onChange={(e) => setTrackingData({ ...trackingData, operator_notes: e.target.value })}
                  />
                </div>

                <div className="pt-4 flex justify-end gap-3">
                  <button type="button" onClick={() => setTrackingJobId(null)} className="px-4 py-2 text-slate-400 hover:text-white font-bold text-sm">Cancel</button>
                  <button type="submit" className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl transition-all shadow-lg shadow-blue-600/20">
                    Update Publish Info
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Metrics Modal */}
      <AnimatePresence>
        {metricsJobId && (
          <div className="fixed inset-0 z-[110] flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMetricsJobId(null)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="w-full max-w-lg glass-card rounded-3xl p-8 relative z-10"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-emerald-600 p-2 rounded-xl">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-white">Performance Snapshot</h2>
              </div>
              <form onSubmit={handleSaveMetrics} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Views</label>
                    <input
                      type="number"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={metricsData.views}
                      onChange={(e) => setMetricsData({ ...metricsData, views: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Conversions</label>
                    <input
                      type="number"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={metricsData.conversions}
                      onChange={(e) => setMetricsData({ ...metricsData, conversions: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">CTR (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={metricsData.ctr_estimate}
                      onChange={(e) => setMetricsData({ ...metricsData, ctr_estimate: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                   <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Watch Time (s)</label>
                    <input
                      type="number"
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white focus:ring-1 focus:ring-blue-500"
                      value={metricsData.watch_time_seconds}
                      onChange={(e) => setMetricsData({ ...metricsData, watch_time_seconds: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Operator Rating (1-5)</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setMetricsData({ ...metricsData, operator_rating: star })}
                        className={cn(
                          "w-10 h-10 rounded-xl border flex items-center justify-center font-bold transition-all",
                          metricsData.operator_rating === star 
                            ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20" 
                            : "bg-slate-900 border-slate-800 text-slate-500 hover:border-slate-700"
                        )}
                      >
                        {star}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Snapshot Notes</label>
                  <textarea
                    rows={2}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-sm text-white placeholder:text-slate-600 focus:ring-1 focus:ring-blue-500"
                    placeholder="Specific observations for this metric snapshot..."
                    value={metricsData.notes}
                    onChange={(e) => setMetricsData({ ...metricsData, notes: e.target.value })}
                  />
                </div>

                <div className="pt-4 flex justify-end gap-3">
                  <button type="button" onClick={() => setMetricsJobId(null)} className="px-4 py-2 text-slate-400 hover:text-white font-bold text-sm">Cancel</button>
                  <button 
                    type="submit" 
                    disabled={savingMetrics}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 px-6 rounded-xl transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-50 flex items-center gap-2"
                  >
                    {savingMetrics && <Loader2 className="w-4 h-4 animate-spin" />}
                    Save Snapshot
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
