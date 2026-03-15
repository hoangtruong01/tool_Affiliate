"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Library,
  Upload,
  Search,
  Filter,
  Image as ImageIcon,
  Film,
  Music,
  Type,
  MoreVertical,
  Trash2,
  Download,
  Loader2,
  X,
  FileText,
} from "lucide-react";
import api from "@/lib/api";
import { cn, formatBytes, formatDate } from "@/lib/utils";

interface Asset {
  id: string;
  filename: string;
  file_path: string;
  asset_type: "image" | "video_clip" | "audio" | "font" | "template";
  mime_type: string;
  file_size: number;
  status: string;
  created_at: string;
}

const typeIcons = {
  image: ImageIcon,
  video_clip: Film,
  audio: Music,
  font: Type,
  template: FileText,
};

export default function AssetsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("all");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchAssets = async () => {
    try {
      const params: any = {};
      if (filterType !== "all") params.asset_type = filterType;
      const response = await api.get("/assets", { params });
      setAssets(response.data.items);
    } catch (error) {
      console.error("Failed to fetch assets", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, [filterType]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/assets/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchAssets();
    } catch (error) {
      console.error("Upload failed", error);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this asset?")) return;
    try {
      await api.delete(`/assets/${id}`);
      setAssets(assets.filter((a) => a.id !== id));
    } catch (error) {
      console.error("Delete failed", error);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Asset Library</h1>
          <p className="text-slate-400">
            Manage images, video clips, and audio for your renders.
          </p>
        </div>
        <div className="flex gap-3">
          <input
            type="file"
            className="hidden"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*,video/*,audio/*"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2.5 px-6 rounded-xl flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
          >
            {uploading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Upload className="w-5 h-5" />
            )}
            Upload Media
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center">
        <div className="flex gap-2 p-1 bg-slate-900/50 rounded-xl border border-slate-800 w-full md:w-auto">
          {["all", "image", "video_clip", "audio"].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={cn(
                "px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all",
                filterType === type
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                  : "text-slate-500 hover:text-slate-300",
              )}
            >
              {type}
            </button>
          ))}
        </div>
        <div className="relative flex-1 group w-full">
          <Search className="w-5 h-5 text-slate-500 absolute left-4 top-1/2 -translate-y-1/2 group-focus-within:text-blue-500 transition-colors" />
          <input
            type="text"
            placeholder="Search assets by filename..."
            className="w-full bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-2.5 pl-11 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
          />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 animate-pulse">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="aspect-square bg-slate-900 rounded-2xl border border-slate-800"
            />
          ))}
        </div>
      ) : assets.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-slate-800 rounded-3xl">
          <Library className="w-12 h-12 mb-4 opacity-20" />
          <p>Your library is empty. Upload some assets to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <AnimatePresence>
            {assets.map((asset, index) => {
              const Icon = typeIcons[asset.asset_type] || ImageIcon;
              return (
                <motion.div
                  key={asset.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ y: -4 }}
                  className="glass-card group rounded-2xl overflow-hidden relative border border-slate-800 hover:border-blue-500/30 transition-all"
                >
                  <div className="aspect-square bg-slate-900 flex items-center justify-center relative overflow-hidden bg-gradient-to-br from-slate-900 to-slate-950">
                    {asset.asset_type === "image" ? (
                      <img
                        src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/media/uploads/image/${asset.file_path.split("/").pop()}`}
                        alt={asset.filename}
                        className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity"
                      />
                    ) : (
                      <Icon className="w-12 h-12 text-slate-700 group-hover:text-blue-500/50 transition-colors" />
                    )}

                    <div className="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                      <button className="p-2 bg-blue-600 rounded-lg text-white hover:bg-blue-500 transition-colors">
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(asset.id)}
                        className="p-2 bg-red-600 rounded-lg text-white hover:bg-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="p-3">
                    <p className="text-xs font-bold text-white truncate mb-1">
                      {asset.filename}
                    </p>
                    <div className="flex items-center justify-between">
                      <p className="text-[10px] text-slate-500">
                        {formatBytes(asset.file_size)}
                      </p>
                      <p className="text-[10px] text-slate-600">
                        {formatDate(asset.created_at).split(",")[0]}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
