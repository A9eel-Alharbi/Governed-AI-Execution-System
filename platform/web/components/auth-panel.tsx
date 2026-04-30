"use client";

import { useState, useTransition } from "react";

import { demoLogin } from "../lib/platform-api";
import { useAuth } from "./auth-provider";
import { StatusPill } from "./status-pill";

export function AuthPanel() {
  const [email, setEmail] = useState("demo@aos-cdd.local");
  const [isPending, startTransition] = useTransition();
  const { user, config, setSession, clearSession } = useAuth();

  function login() {
    startTransition(async () => {
      const session = await demoLogin(email);
      setSession(session.token, session.user);
    });
  }

  function logout() {
    clearSession();
  }

  return (
    <div className="rounded-[1.3rem] border border-white/10 bg-white/5 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-sage/70">Auth</p>
        {user ? <StatusPill label={user.role} tone="success" /> : <StatusPill label="guest" tone="neutral" />}
      </div>
      <p className="mb-3 text-xs uppercase tracking-[0.16em] text-cloud/52">{config ? `${config.provider_name} · ${config.mode}` : "Loading auth mode"}</p>
      {user ? (
        <div className="space-y-2 text-sm text-cloud/82">
          <p className="font-semibold text-cloud">{user.name}</p>
          <p>{user.email}</p>
          <button onClick={logout} className="mt-2 rounded-full border border-white/12 px-3 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-cloud">
            Sign out
          </button>
        </div>
      ) : config?.mode === "external" ? (
        <div className="space-y-3 text-sm text-cloud/82">
          <p>External authentication is enabled for this platform deployment.</p>
          {config.login_path ? (
            <a
              href={config.login_path}
              className="inline-flex rounded-full bg-moss px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-cloud"
            >
              Continue to sign in
            </a>
          ) : (
            <p className="text-cloud/64">Configure an external login path to complete provider sign-in.</p>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-2xl border border-white/12 bg-white/8 px-4 py-3 text-sm text-cloud outline-none placeholder:text-cloud/45"
            placeholder="demo@aos-cdd.local"
          />
          <button
            onClick={login}
            disabled={isPending}
            className="rounded-full bg-moss px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-cloud disabled:opacity-60"
          >
            {isPending ? "Signing in..." : "Demo sign in"}
          </button>
        </div>
      )}
    </div>
  );
}
