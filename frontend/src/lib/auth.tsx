"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import cookie from "cookie-cutter";
import api from "@/lib/api";

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = cookie.get("token");
      if (token) {
        try {
          const response = await api.get("/auth/me");
          setUser(response.data);
        } catch (error) {
          console.error("Failed to load user", error);
          cookie.set("token", "", { expires: new Date(0) });
        }
      }
      setLoading(false);
    }
    loadUser();
  }, []);

  const login = (token: string, userData: User) => {
    cookie.set("token", token, { path: "/" });
    setUser(userData);
  };

  const logout = () => {
    cookie.set("token", "", { expires: new Date(0), path: "/" });
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
