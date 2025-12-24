# Photo Platform (Web)

一个基于 **FastAPI + Next.js** 的多租户图片处理平台：上传图片 → 自动裁剪/圆角 → 自动生成标签与 PPT → 仪表盘展示任务与结果。

## 目录

- **backend/**：FastAPI 后端（多租户、认证、上传、任务处理、对象存储）
- **frontend/**：Next.js 前端（登录、控制台、上传、任务查看）

---

## 后端（backend）本地启动

### 1) 配置环境变量

复制示例：

- `backend/.env.example` → `backend/.env`

关键项：

- `DATABASE_URL`：默认 SQLite（async）
- `JWT_SECRET_KEY`：务必改成随机字符串
- `STORAGE_BACKEND`：`local` 或 `supabase`
- `STORAGE_LOCAL_ROOT`：本地存储目录（local 模式）

### 2) 安装依赖

使用你已有的虚拟环境（`web-platform/.venv`）：

```powershell
# 在 d:\图片处理程序3.8 目录
.\web-platform\.venv\Scripts\pip install -r web-platform\backend\requirements.txt
```

### 3) 启动后端

```powershell
# 在 d:\图片处理程序3.8\web-platform\backend
..\..\web-platform\.venv\Scripts\uvicorn app.main:app --reload
```

访问：

- `http://127.0.0.1:8000/api/docs`
- `http://127.0.0.1:8000/api/health`

---

## 前端（frontend）本地启动

> 前端需要 Node.js LTS。若当前机器未安装，请手动安装。

### 1) 环境变量

- `frontend/.env.local.example` → `frontend/.env.local`

设置：

- `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api`

### 2) 安装依赖 & 启动

```powershell
# 在 d:\图片处理程序3.8\web-platform\frontend
pnpm install
pnpm dev
```

访问：

- `http://localhost:3000`
- 登录页：`/login`
- 控制台：`/dashboard`
- 上传页：`/dashboard/upload`

---

## 体验流程（本地）

1. `POST /api/tenants/` 创建租户
2. `POST /api/auth/register` 创建用户（指定 `tenant_id`）
3. `POST /api/auth/token` 获取 JWT
4. 前端登录后，在 `/dashboard/upload` 上传图片并创建任务
5. 在 `/dashboard` 查看任务与资产

---

## local 存储模式

当 `STORAGE_BACKEND=local`：

- 后端会挂载静态目录：`/storage`
- 上传/处理结果会保存在 `STORAGE_LOCAL_ROOT` 下

---

## 部署（下一步）

- 前端：Vercel
- 后端：Railway / Render
- 数据库：Supabase Postgres / Neon
- 存储：Supabase Storage / Cloudflare R2

详细部署与自动建站脚本将在后续补齐。
