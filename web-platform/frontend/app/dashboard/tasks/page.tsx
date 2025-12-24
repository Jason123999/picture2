"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/src/context/AuthContext";
import { useTasks } from "@/src/hooks/useTasks";
import { useTenants } from "@/src/hooks/useTenants";
import { API_BASE_URL } from "@/src/lib/api";
import type { Task } from "@/src/types";

function getBackendOrigin(): string {
  // API_BASE_URL is like http://127.0.0.1:8001/api
  return API_BASE_URL.replace(/\/api\/?$/, "");
}

function normalizeResultHref(resultPath: string | null | undefined): string | null {
  if (!resultPath) return null;

  if (resultPath.startsWith("http://") || resultPath.startsWith("https://")) {
    return resultPath;
  }

  // New local storage returns relative url like /storage/<key>
  if (resultPath.startsWith("/storage/")) {
    return `${getBackendOrigin()}${resultPath}`;
  }

  // Old records may store Windows absolute path like D:\\...\\storage\\tenants\\...
  const lowered = resultPath.toLowerCase();

  // Handle paths that contain /storage/ already.
  const markerSlash = "/storage/";
  const idxSlash = lowered.indexOf(markerSlash);
  if (idxSlash >= 0) {
    const rel = resultPath.slice(idxSlash + markerSlash.length).replace(/\\/g, "/");
    return `${getBackendOrigin()}/storage/${rel.replace(/^\/+/, "")}`;
  }

  // Handle Windows-style backslashes.
  const markerBackslash = "\\storage\\";
  const idxBackslash = lowered.indexOf(markerBackslash);
  if (idxBackslash >= 0) {
    const rel = resultPath.slice(idxBackslash + markerBackslash.length).replace(/\\/g, "/");
    return `${getBackendOrigin()}/storage/${rel.replace(/^\/+/, "")}`;
  }

  return null;
}

function formatTime(value: string) {
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function StatusPill({ status }: { status: Task["status"] }) {
  const color =
    status === "completed"
      ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/20"
      : status === "failed"
        ? "bg-rose-500/10 text-rose-300 border-rose-500/20"
        : status === "processing"
          ? "bg-amber-500/10 text-amber-300 border-amber-500/20"
          : "bg-slate-800 text-slate-200 border-slate-700";

  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs uppercase tracking-wide ${color}`}> 
      {status}
    </span>
  );
}

export default function TasksPage() {
  const router = useRouter();
  const { accessToken, tenantId, selectTenant } = useAuth();
  const { tenants, isLoading: tenantsLoading } = useTenants();
  const { tasks, isLoading, error } = useTasks(tenantId);

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, router]);

  useEffect(() => {
    if (!tenantsLoading && tenants && tenants.length > 0) {
      if (tenantId === null) {
        selectTenant(tenants[0].id);
      } else if (!tenants.some((tenant) => tenant.id === tenantId)) {
        selectTenant(tenants[0].id);
      }
    }
  }, [tenantId, tenants, tenantsLoading, selectTenant]);

  const sorted = useMemo(() => {
    if (!tasks) return [];
    return [...tasks].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }, [tasks]);

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-12">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">任务列表</h1>
          <p className="mt-2 text-sm text-slate-300">查看任务状态、错误信息与生成的 PPT 下载链接。</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/dashboard"
            className="rounded-full border border-slate-700 px-5 py-2 text-sm font-medium text-slate-200 transition hover:-translate-y-0.5 hover:border-brand-secondary hover:text-brand-secondary"
          >
            返回控制台
          </Link>
          <Link
            href="/dashboard/upload"
            className="rounded-full bg-brand-primary px-5 py-2 text-sm font-medium text-white transition hover:-translate-y-0.5 hover:bg-brand-secondary"
          >
            新建上传任务
          </Link>
        </div>
      </header>

      <section className="mt-10 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
        {isLoading && <div className="text-slate-300">加载任务中...</div>}
        {!isLoading && error && <div className="text-rose-300">{String(error)}</div>}
        {!isLoading && !error && tenantId == null && (
          <div className="rounded-2xl border border-dashed border-slate-800 px-4 py-10 text-center text-slate-400">
            未选择租户，请返回控制台选择租户或等待系统自动选择。
          </div>
        )}
        {!isLoading && !error && tenantId != null && sorted.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-800 px-4 py-10 text-center text-slate-400">
            暂无任务。请先上传图片创建任务。
          </div>
        )}

        {!isLoading && !error && tenantId != null && sorted.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-slate-400">
                <tr className="border-b border-slate-800">
                  <th className="py-3 pr-4">任务</th>
                  <th className="py-3 pr-4">状态</th>
                  <th className="py-3 pr-4">创建时间</th>
                  <th className="py-3 pr-4">结果</th>
                  <th className="py-3">操作</th>
                </tr>
              </thead>
              <tbody className="text-slate-200">
                {sorted.map((task) => {
                  const href = normalizeResultHref(task.result_path);
                  return (
                    <tr key={task.id} className="border-b border-slate-800/60">
                      <td className="py-4 pr-4 font-medium text-white">#{task.id}</td>
                      <td className="py-4 pr-4">
                        <StatusPill status={task.status} />
                      </td>
                      <td className="py-4 pr-4 text-slate-300">{formatTime(task.created_at)}</td>
                      <td className="py-4 pr-4">
                        {task.status === "completed" && href ? (
                          <a
                            href={href}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex rounded-full bg-brand-primary px-4 py-2 text-xs font-medium text-white transition hover:bg-brand-secondary"
                          >
                            下载 PPT
                          </a>
                        ) : task.status === "failed" ? (
                          <span className="text-rose-300" title={task.error_message ?? undefined}>
                            {task.error_message ? "失败（查看原因）" : "失败"}
                          </span>
                        ) : (
                          <span className="text-slate-400">-</span>
                        )}
                      </td>
                      <td className="py-4">
                        <Link
                          href={`/tasks/${task.id}`}
                          className="text-sm text-brand-secondary transition hover:opacity-80"
                        >
                          详情
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {tenantId == null && (
              <p className="mt-4 text-xs text-amber-300">未选择租户：请选择租户后再查看任务列表。</p>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
