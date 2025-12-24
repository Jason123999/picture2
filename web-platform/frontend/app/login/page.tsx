"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { API_BASE_URL } from "@/src/lib/api";
import { useAuth } from "@/src/context/AuthContext";
import { getTenantSlugFromLocation } from "@/src/lib/tenant";

export default function LoginPage() {
  const router = useRouter();
  const { accessToken, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantSlug, setTenantSlug] = useState<string | null>(() => getTenantSlugFromLocation());
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (accessToken) {
      router.replace("/dashboard");
    }
  }, [accessToken, router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: email,
          password,
          ...(tenantSlug ? { tenant_slug: tenantSlug } : {}),
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "登录失败");
      }

      const data = await response.json();
      login(data.access_token);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 px-4 py-12">
      <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/70 p-8 shadow-xl shadow-black/30">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-semibold text-white">登录你的图片处理站点</h1>
          <p className="mt-2 text-sm text-slate-400">
            输入账号密码以访问多租户控制台与自动化处理功能。
          </p>
        </div>
        <form className="space-y-6" onSubmit={handleSubmit}>
          {tenantSlug === null && (
            <div>
              <label className="block text-sm text-slate-300" htmlFor="tenant">
                租户子域（tenant）
              </label>
              <input
                id="tenant"
                type="text"
                required
                value={tenantSlug ?? ""}
                onChange={(event) => setTenantSlug(event.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
                placeholder="例如：demo-tenant"
                autoComplete="off"
              />
            </div>
          )}
          <div>
            <label className="block text-sm text-slate-300" htmlFor="email">
              邮箱
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300" htmlFor="password">
              密码
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
              placeholder="输入密码"
              autoComplete="current-password"
            />
          </div>
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center rounded-2xl bg-brand-primary px-4 py-3 text-sm font-medium text-white shadow-lg shadow-brand-primary/40 transition hover:-translate-y-0.5 hover:bg-brand-secondary disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "登录中..." : "登录"}
          </button>
        </form>
        <div className="mt-6 text-center text-xs text-slate-500">
          <p>还没有账号？请联系管理员为你的租户创建用户。</p>
          <p className="mt-1">
            <Link href="/" className="text-brand-secondary hover:underline">
              返回首页
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
