import Link from "next/link";

export default function GettingStartedPage() {
  return (
    <main className="mx-auto min-h-screen max-w-3xl px-6 py-12 text-slate-100">
      <header className="space-y-3">
        <h1 className="text-3xl font-bold">快速开始</h1>
        <p className="text-sm text-slate-300">
          本页用于快速验证本地联调链路：登录 → 上传 → 任务完成 → 下载 PPT。
        </p>
      </header>

      <section className="mt-10 space-y-6 rounded-3xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl shadow-black/20">
        <div>
          <h2 className="text-xl font-semibold">后端（FastAPI）</h2>
          <p className="mt-2 text-sm text-slate-300">PowerShell：</p>
          <pre className="mt-3 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{`# 初始化管理员（只需一次）
.\\web-platform\\scripts\\init_admin.ps1

# 启动后端（默认 8001）
$env:BACKEND_PORT=8001
.\\web-platform\\scripts\\run_backend.ps1

# 健康检查
$env:BACKEND_PORT=8001
.\\web-platform\\scripts\\health_check.ps1`}</pre>
        </div>

        <div>
          <h2 className="text-xl font-semibold">前端（Next.js）</h2>
          <p className="mt-2 text-sm text-slate-300">在 frontend 目录执行：</p>
          <pre className="mt-3 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{`npm install
npm run dev`}</pre>
          <p className="mt-2 text-sm text-slate-300">默认地址： http://localhost:3000</p>
        </div>

        <div>
          <h2 className="text-xl font-semibold">Web 验证路径</h2>
          <div className="mt-3 space-y-2 text-sm text-slate-300">
            <p>1) /login 登录（admin@example.com / admin123456）</p>
            <p>2) /dashboard/upload 上传图片并创建任务</p>
            <p>3) /dashboard/tasks 查看任务状态与下载 PPT</p>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/login"
              className="rounded-full bg-brand-primary px-5 py-2 text-sm font-medium text-white transition hover:-translate-y-0.5 hover:bg-brand-secondary"
            >
              去登录
            </Link>
            <Link
              href="/dashboard"
              className="rounded-full border border-slate-700 px-5 py-2 text-sm font-medium text-slate-200 transition hover:-translate-y-0.5 hover:border-brand-secondary hover:text-brand-secondary"
            >
              去控制台
            </Link>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold">说明</h2>
          <div className="mt-3 space-y-2 text-sm text-slate-300">
            <p>如果你之前访问 /docs/getting-started 看到 404，这是因为之前未实现 docs 路由；现在已补齐。</p>
            <p>如果遇到 No module named 'app'：请使用 scripts 目录下的 ps1 脚本启动后端，它会自动设置 PYTHONPATH。</p>
            <p className="pt-2 text-slate-200">方案1（每租户一个 tenant.vercel.app，零域名成本）：</p>
            <p>1) 后端（Render）：部署 FastAPI，配置 CORS 允许 https://*.vercel.app（推荐使用 CORS_ALLOW_ORIGIN_REGEX）。</p>
            <p>2) 后端（Render）：配置 Vercel 自动建站变量（VERCEL_TOKEN、VERCEL_GIT_REPO、VERCEL_FRONTEND_API_BASE_URL 等）。</p>
            <p>3) 使用超级管理员调用 POST /api/admin/provision 创建租户与管理员，响应会返回 site_url_stable（稳定别名，例如 https://&lt;tenant&gt;.vercel.app）以及 site_url_immediate / deployment_url（即时访问/排障）。</p>
            <p>4) 打开 site_url → /login，用新创建的管理员邮箱与密码登录并验证上传/任务/下载。</p>
            <p className="pt-2 text-slate-200">公网 A 模式（泛子域）部署结构建议：</p>
            <p>1) 前端（Vercel）：绑定域名 app.&lt;root&gt; 和通配符 *.&lt;root&gt;</p>
            <p>2) 后端（Render）：绑定域名 api.&lt;root&gt;</p>
            <p>3) DNS（Cloudflare）：</p>
            <p className="ml-4">- CNAME: app → Vercel</p>
            <p className="ml-4">- CNAME: * → Vercel（泛子域）</p>
            <p className="ml-4">- CNAME: api → Render</p>
            <p>4) Supabase：启用 Postgres + Storage（bucket 例如 photo-platform）</p>
            <p className="pt-2 text-slate-200">一键烟测（推荐，用于本地或 Render 线上快速验收）：</p>
            <pre className="mt-2 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{`# 本地（默认 demo-tenant）
python -m app.scripts.smoke_test --base http://127.0.0.1:8001/api --tenant-slug demo-tenant

# 线上（Render）
python -m app.scripts.smoke_test --base https://<your-render-service>.onrender.com/api --tenant-slug <tenant>

# 可选：先调用 /api/admin/provision 创建租户/管理员，再用新管理员跑完整链路
python -m app.scripts.smoke_test --base https://<your-render-service>.onrender.com/api --tenant-slug <tenant> --provision \
  --provision-tenant-name <Tenant Name> --provision-admin-email <email> --provision-admin-password <pwd>`}</pre>
            <p className="pt-2 text-slate-200">部署就绪检查（快速确认缺哪些变量）：</p>
            <pre className="mt-2 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{`# 1) 先登录拿 token（示例）
curl -X POST https://<your-render-service>.onrender.com/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=admin@example.com" \
  --data-urlencode "password=admin123456" \
  --data-urlencode "tenant_slug=demo-tenant"

# 2) 用 token 调 deploy-check
curl https://<your-render-service>.onrender.com/api/admin/deploy-check \
  -H "Authorization: Bearer <token>"`}</pre>
            <p className="pt-2 text-slate-200">方案1 后端变量清单（示例）：</p>
            <pre className="mt-2 overflow-x-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-200">{`# 必填
VERCEL_TOKEN=***
VERCEL_GIT_REPO=your-org/your-repo
VERCEL_FRONTEND_API_BASE_URL=https://your-render-service.onrender.com/api

# 可选
VERCEL_TEAM_ID=
VERCEL_TEAM_SLUG=
VERCEL_GIT_REF=main
VERCEL_FRONTEND_ROOT_DIR=web-platform/frontend

# 推荐（方案1）
CORS_ALLOW_ORIGIN_REGEX=^https://([a-z0-9-]+\\.)*vercel\\.app$`}</pre>
          </div>
        </div>
      </section>
    </main>
  );
}
