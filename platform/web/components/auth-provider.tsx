"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { clearStoredToken, getStoredToken, setStoredToken } from "../lib/auth-storage";
import { getAuthConfig, getCurrentUser } from "../lib/platform-api";
import type { AuthConfig, UserSummary } from "../lib/sample-data";

type AuthContextValue = {
  token: string | null;
  user: UserSummary | null;
  config: AuthConfig | null;
  setSession: (token: string, user: UserSummary) => void;
  clearSession: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserSummary | null>(null);
  const [config, setConfig] = useState<AuthConfig | null>(null);

  useEffect(() => {
    void getAuthConfig().then(setConfig);
    const stored = getStoredToken();
    if (!stored) {
      return;
    }
    setToken(stored);
    void getCurrentUser(stored).then((currentUser) => {
      if (currentUser) {
        setUser(currentUser);
      }
    });
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      config,
      setSession(nextToken, nextUser) {
        setStoredToken(nextToken);
        setToken(nextToken);
        setUser(nextUser);
      },
      clearSession() {
        clearStoredToken();
        setToken(null);
        setUser(null);
      },
    }),
    [config, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return value;
}
