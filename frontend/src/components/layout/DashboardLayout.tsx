"use client";

import React from "react";
import { useAuth } from "@/lib/auth";
import Sidebar from "./Sidebar";
import { Loader2 } from "lucide-react";
import { usePathname } from "next/navigation";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const pathname = usePathname();

  // Pages that don't need the dashboard layout (like login/register)
  const isAuthPage =
    pathname.startsWith("/login") || pathname.startsWith("/register");

  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-slate-950">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
      </div>
    );
  }

  if (isAuthPage) {
    return <div className="min-h-screen bg-slate-950">{children}</div>;
  }

  // If not logged in and not on auth page, Next.js middleware or api interceptor handles it,
  // but we should still handle the UI state here.
  if (!user && !isAuthPage) {
    return null; // or a redirect component
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex">
      <Sidebar />
      <main className="flex-1 ml-64 p-8 relative min-h-screen overflow-x-hidden">
        {/* Abstract Background Elements */}
        <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-blue-600/5 blur-[120px] rounded-full -mr-64 -mt-64 pointer-events-none" />
        <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-purple-600/5 blur-[100px] rounded-full -ml-32 -mb-32 pointer-events-none" />

        <div className="relative z-10 w-full max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
}
