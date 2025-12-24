"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { api } from "@/src/lib/api";
import { useAuth } from "@/src/context/AuthContext";
import { useAssets } from "@/src/hooks/useAssets";
import { useTasks } from "@/src/hooks/useTasks";
import type { ImageAsset, Task, UploadResponse } from "@/src/types";

export default function UploadPage() {
  const router = useRouter();
  const { tenantId } = useAuth();
  const { mutate: mutateAssets } = useAssets(tenantId);
  const { mutate: mutateTasks } = useTasks(tenantId);

  const [file, setFile] = useState<File | null>(null);
  const [configPath, setConfigPath] = useState<string>("config.json");
  const [outputDir, setOutputDir] = useState<string>("processed");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus(null);
    setError(null);

    if (!tenantId) {
      setError("未检测到租户，请先登录并选择租户。");
      return;
    }

    if (!file) {
      setError("请先选择要上传的文件。");
      return;
    }

    try {
      setLoading(true);

      const uploadResult = await api.upload<UploadResponse>("/uploads/", file);

      const assetPayload = {
        tenant_id: tenantId,
        original_path: uploadResult.storage_key,
        processed_path: null,
        thumbnail_path: null,
        status: "uploaded",
        meta_json: JSON.stringify({ url: uploadResult.url, filename: uploadResult.filename }),
      } satisfies Parameters<typeof api.post<ImageAsset>>[1];

      const asset = await api.post<ImageAsset>("/assets", assetPayload);

      const taskPayload = {
        tenant_id: tenantId,
        image_asset_id: asset.id,
        config_path: configPath,
        output_dir: outputDir,
      } satisfies Parameters<typeof api.post<Task>>[1];

      await api.post<Task>("/tasks", taskPayload);

      await Promise.all([mutateAssets(), mutateTasks()]);

      setStatus("上传并创建任务成功！即将跳转到控制台……");
      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "上传失败，请重试。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-8 px-6 py-12">
      <div>
        <h1 className="text-3xl font-bold text-white">上传图片并创建任务</h1>
        <p className="mt-2 text-sm text-slate-300">
          上传文件将自动保存到租户存储中，并创建后台任务执行裁剪、圆角与 PPT 生成。
        </p>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm text-slate-300" htmlFor="file">
            选择图片文件
          </label>
          <input
            id="file"
            type="file"
            accept="image/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm text-slate-300" htmlFor="config">
              配置文件路径
            </label>
            <input
              id="config"
              type="text"
              value={configPath}
              onChange={(event) => setConfigPath(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300" htmlFor="output">
              输出目录
            </label>
            <input
              id="output"
              type="text"
              value={outputDir}
              onChange={(event) => setOutputDir(event.target.value)}
              className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white focus:border-brand-secondary focus:outline-none"
            />
          </div>
        </div>

        {error && <p className="text-sm text-rose-400">{error}</p>}
        {status && <p className="text-sm text-emerald-400">{status}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-2xl bg-brand-primary px-6 py-3 text-sm font-medium text-white shadow-lg shadow-brand-primary/40 transition hover:-translate-y-0.5 hover:bg-brand-secondary disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "处理中..." : "上传并创建任务"}
        </button>
      </form>

      <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        <h2 className="text-lg font-semibold text-white">操作说明</h2>
        <ul className="mt-4 space-y-2">
          <li>选择图片后系统会自动上传到对象存储。</li>
          <li>上传完成后会创建图片资产记录并触发处理任务。</li>
          <li>任务状态可在控制台仪表盘中实时查看。</li>
        </ul>
        <div className="mt-4 text-xs text-slate-500">
          <Link href="/dashboard" className="text-brand-secondary hover:underline">
            返回控制台
          </Link>
        </div>
      </div>
    </main>
  );
}
