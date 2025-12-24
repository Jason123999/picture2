"use client";

import Link from "next/link";
import { useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";

import { TenantSwitcher } from "@/src/components/TenantSwitcher";
import { useAssets } from "@/src/hooks/useAssets";
import { useTasks } from "@/src/hooks/useTasks";
import { useTenants } from "@/src/hooks/useTenants";
import type { Tenant } from "@/src/types";
import { useAuth } from "@/src/context/AuthContext";

const quickLinks = [
  {
    title: "上传新图片",
    description: "通过 Web 端或 API 上传图片并自动触发处理流程。",
    href: "/dashboard/upload",
  },
  {
    title: "管理标签模板",
    description: "为 PPT 与展示页配置自定义标签模板。",
    href: "/dashboard/templates",
  },
  {
    title: "设置子域名",
    description: "绑定你的专属子域或自定义域名。",
    href: "/dashboard/domain",
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const { accessToken, tenantId, selectTenant } = useAuth();
  const { tenants, isLoading: tenantsLoading } = useTenants();

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

  const selectedTenant = useMemo(() => {
    if (!tenants || tenantId === null) return null;
    return tenants.find((tenant) => tenant.id === tenantId) ?? null;
  }, [tenantId, tenants]);

  const { tasks, isLoading: tasksLoading } = useTasks(tenantId);
  const { assets, isLoading: assetsLoading } = useAssets(tenantId);

  const stats = useMemo(() => {
    const totalUploads = assets?.length ?? 0;
    const processingCount = tasks?.filter((task) => task.status === "processing").length ?? 0;
    const successCount = tasks?.filter((task) => task.status === "completed").length ?? 0;

    return [
      {
        label: "资源数量",
        value: tenants?.length ? String(tenants.length) : "-",
        caption: "平台内租户总数",
      },
      {
        label: "图片资产",
        value: totalUploads ? String(totalUploads) : "-",
        caption: "当前租户的图片总数",
      },
      {
        label: "进行中任务",
        value: processingCount ? String(processingCount) : "0",
        caption: "当前仍在排队或执行的任务",
      },
      {
        label: "成功任务",
        value: successCount ? String(successCount) : "0",
        caption: "已完成处理的任务总计",
      },
    ];
  }, [assets, tasks, tenants]);

  const latestTasks = useMemo(() => {
    if (!tasks) return [];
    return [...tasks]
      .sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
      .slice(0, 5);
  }, [tasks]);

  const latestAssets = useMemo(() => {
    if (!assets) return [];
    return [...assets]
      .sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
      .slice(0, 5);
  }, [assets]);

  const handleTenantSelect = (tenant: Tenant) => {
    selectTenant(tenant.id);
  };

  return (
    <main className="mx-auto min-h-screen max-w-7xl px-6 py-12">
      <header className="mb-12 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">控制台总览</h1>
          <p className="mt-2 text-sm text-slate-300">
            选择租户后，查看图片资产、任务状态以及关键指标。
          </p>
        </div>
        <div className="flex flex-col items-start gap-3 md:flex-row md:items-center">
          {!tenantsLoading && tenants ? (
            <TenantSwitcher
              tenants={tenants}
              selectedTenant={selectedTenant}
              onSelect={handleTenantSelect}
            />
          ) : (
            <div className="rounded-full border border-slate-800 px-6 py-3 text-sm text-slate-400">
              正在加载租户...
            </div>
          )}
          <div className="flex gap-3">
            <Link
              href="/dashboard/upload"
              className="rounded-full bg-brand-primary px-5 py-2 text-sm font-medium text-white transition hover:-translate-y-0.5 hover:bg-brand-secondary"
            >
              新建上传任务
            </Link>
            <Link
              href="/dashboard/settings"
              className="rounded-full border border-slate-700 px-5 py-2 text-sm font-medium text-slate-200 transition hover:-translate-y-0.5 hover:border-brand-secondary hover:text-brand-secondary"
            >
              租户设置
            </Link>
          </div>
        </div>
      </header>

      <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((item) => (
          <div
            key={item.label}
            className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg shadow-black/20"
          >
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className="mt-4 text-3xl font-semibold text-white">{item.value}</p>
            <p className="mt-1 text-xs text-slate-500">{item.caption}</p>
          </div>
        ))}
      </section>

      <section className="mt-12 grid gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">最新任务</h2>
              <Link
                href="/dashboard/tasks"
                className="text-sm text-brand-secondary transition hover:opacity-80"
              >
                查看全部
              </Link>
            </div>
            <div className="mt-6 space-y-4 text-sm">
              {tasksLoading && <div className="text-slate-400">加载任务中...</div>}
              {!tasksLoading && latestTasks.length === 0 && (
                <div className="rounded-2xl border border-dashed border-slate-800 px-4 py-6 text-center text-slate-400">
                  暂无任务，尝试上传图片以开启处理流程。
                </div>
              )}
              {!tasksLoading &&
                latestTasks.map((task) => (
                  <div
                    key={task.id}
                    className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-white">任务 #{task.id}</p>
                      <p className="text-xs text-slate-400">
                        {new Date(task.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-wide text-brand-secondary">
                      {task.status}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
            <h2 className="text-xl font-semibold text-white">最新图片资产</h2>
            <div className="mt-6 space-y-4 text-sm">
              {assetsLoading && <div className="text-slate-400">加载图片中...</div>}
              {!assetsLoading && latestAssets.length === 0 && (
                <div className="rounded-2xl border border-dashed border-slate-800 px-4 py-6 text-center text-slate-400">
                  暂无图片，请先上传资源。
                </div>
              )}
              {!assetsLoading &&
                latestAssets.map((asset) => (
                  <div
                    key={asset.id}
                    className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 px-4 py-3"
                  >
                    <div>
                      <p className="font-medium text-white">{asset.original_path}</p>
                      <p className="text-xs text-slate-400">
                        {new Date(asset.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
                      {asset.status}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
            <h2 className="text-xl font-semibold text-white">快速入口</h2>
            <div className="mt-4 space-y-4">
              {quickLinks.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block rounded-2xl border border-slate-800 bg-slate-900/40 px-4 py-4 transition hover:border-brand-secondary hover:text-brand-secondary"
                >
                  <p className="text-base font-medium text-white">{item.title}</p>
                  <p className="mt-1 text-xs text-slate-400">{item.description}</p>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
