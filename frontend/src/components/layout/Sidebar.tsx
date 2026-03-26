"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  ShoppingBag,
  FileText,
  Library,
  PlayCircle,
  CheckCircle2,
  BarChart3,
  LineChart,
  Settings,
  LogOut,
  Video,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const menuItems = [
  { icon: LayoutDashboard, label: "Dashboard", href: "/" },
  { icon: ShoppingBag, label: "Products", href: "/products" },
  { icon: FileText, label: "Scripts", href: "/scripts" },
  { icon: Library, label: "Asset Library", href: "/assets" },
  { icon: PlayCircle, label: "Video Jobs", href: "/jobs" },
  { icon: BarChart3, label: "Product Intelligence", href: "/compare" },
  { icon: CheckCircle2, label: "Approvals", href: "/approvals" },
  { icon: LineChart, label: "Learning & Reports", href: "/reports" },
  { icon: Settings, label: "Settings", href: "/admin" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  return (
    <aside className="w-64 h-screen bg-slate-950/80 border-r border-slate-800 flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 flex items-center gap-3">
        <div className="bg-blue-600 p-2 rounded-xl">
          <Video className="w-6 h-6 text-white" />
        </div>
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
          Vidgeo AI
        </span>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group",
              pathname === item.href
                ? "bg-blue-600/10 text-blue-500 border border-blue-600/20"
                : "text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent",
            )}
          >
            <item.icon
              className={cn(
                "w-5 h-5 transition-transform duration-200",
                pathname === item.href
                  ? "text-blue-500"
                  : "group-hover:scale-110",
              )}
            />
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-900">
        <div className="px-3 py-3 mb-4 rounded-lg bg-slate-900/50">
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
            Signed in as
          </p>
          <p className="text-sm font-semibold text-white truncate">
            {user?.full_name}
          </p>
          <p className="text-xs text-slate-400 truncate uppercase">
            {user?.role}
          </p>
        </div>
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-200"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
