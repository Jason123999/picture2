import Link from "next/link";

type TaskDetailsProps = {
  params: { taskId: string };
};

const mockEvents = [
  { time: "14:32", message: "任务创建，等待处理" },
  { time: "14:33", message: "从对象存储读取原始图片" },
  { time: "14:34", message: "裁剪并生成圆角" },
  { time: "14:35", message: "写入处理后图片" },
  { time: "14:36", message: "生成 PPT 幻灯片" },
];

export default function TaskDetailsPage({ params }: TaskDetailsProps) {
  return (
    <main className="mx-auto min-h-screen max-w-5xl px-6 py-12">
      <Link
        href="/dashboard/tasks"
        className="inline-flex items-center text-sm text-slate-400 transition hover:text-brand-secondary"
      >
        ← 返回任务列表
      </Link>
      <header className="mt-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">任务 #{params.taskId}</h1>
          <p className="mt-2 text-sm text-slate-300">
            实时查看处理进度、输出结果与错误日志。
          </p>
        </div>
        <div className="rounded-full bg-slate-900/70 px-4 py-2 text-sm text-brand-secondary">
          处理中
        </div>
      </header>

      <section className="mt-10 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg shadow-black/20">
              <h2 className="text-xl font-semibold text-white">处理状态</h2>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <p>当前步骤：生成 PPT</p>
                <p>创建时间：2025-12-23 14:32</p>
                <p>耗时：4 分 28 秒</p>
                <p>由租户：demo-tenant</p>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg shadow-black/20">
              <h2 className="text-xl font-semibold text-white">事件日志</h2>
              <div className="mt-4 space-y-3">
                {mockEvents.map((event, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/40 px-4 py-3 text-sm text-slate-200"
                  >
                    <span className="text-slate-400">{event.time}</span>
                    <span>{event.message}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg shadow-black/20">
            <h2 className="text-xl font-semibold text-white">结果下载</h2>
            <p className="mt-2 text-sm text-slate-300">
              文件将在处理完成后自动生成。
            </p>
            <div className="mt-4 space-y-3">
              <button className="w-full rounded-full bg-brand-primary px-4 py-2 text-sm font-medium text-white transition hover:-translate-y-0.5 hover:bg-brand-secondary">
                下载处理后图片
              </button>
              <button className="w-full rounded-full border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 transition hover:-translate-y-0.5 hover:border-brand-secondary hover:text-brand-secondary">
                下载 PPT 报告
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg shadow-black/20">
            <h2 className="text-xl font-semibold text-white">任务信息</h2>
            <div className="mt-4 space-y-2 text-sm text-slate-300">
              <p>图片数量：32</p>
              <p>标签模板：默认四象限</p>
              <p>输出格式：PNG + PPTX</p>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
