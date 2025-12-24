import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col items-center justify-center gap-12 px-6 py-24 text-center">
      <div className="space-y-6">
        <span className="inline-flex items-center rounded-full border border-slate-800 bg-slate-900/60 px-4 py-1 text-sm font-medium text-slate-300 backdrop-blur">
          多租户·AI标签·零成本部署
        </span>
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
          构建你的专属图片处理站点
        </h1>
        <p className="mx-auto max-w-3xl text-lg text-slate-300 md:text-xl">
          上传照片、自动生成标签与 PPT；通过一键生成子站点，为你的团队或客户提供独立的图片体验。
        </p>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-4">
        <Link
          href="/dashboard"
          className="rounded-full bg-brand-primary px-6 py-3 text-base font-medium text-white shadow-lg shadow-brand-primary/40 transition hover:-translate-y-0.5 hover:bg-brand-secondary hover:shadow-brand-secondary/40"
        >
          进入控制台
        </Link>
        <Link
          href="/docs/getting-started"
          className="rounded-full border border-slate-700 px-6 py-3 text-base font-medium text-slate-100 transition hover:-translate-y-0.5 hover:border-brand-secondary hover:text-brand-secondary"
        >
          查看使用指南
        </Link>
      </div>
      <div className="grid w-full gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <FeatureCard
          title="自动化处理"
          description="基于 Python 的图像裁剪、圆角、标签与 PPT 生成能力，全部迁移至云端。"
        />
        <FeatureCard
          title="多租户子域"
          description="每位用户拥有独立子域或自定义域，配置隔离、安全可靠。"
        />
        <FeatureCard
          title="零成本部署"
          description="充分利用 Vercel + Railway + Supabase 免费额度，极速上线你的平台。"
        />
      </div>
    </main>
  );
}

function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-left shadow-lg shadow-black/20 backdrop-blur transition hover:border-brand-secondary/60 hover:shadow-brand-secondary/20">
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm text-slate-300">{description}</p>
    </div>
  );
}
