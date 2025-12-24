from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

import httpx
from PIL import Image

DEFAULT_BASE = "http://127.0.0.1:8001/api"
DEFAULT_TENANT_SLUG = "demo-tenant"


def create_test_image(path: Path) -> None:
    img = Image.new("RGB", (256, 256), (80, 120, 200))
    img.save(path)


async def _login(
    *,
    client: httpx.AsyncClient,
    base: str,
    email: str,
    password: str,
    tenant_slug: str,
) -> str:
    token_resp = await client.post(
        f"{base}/auth/token",
        data={
            "username": email,
            "password": password,
            "tenant_slug": tenant_slug,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token_resp.raise_for_status()
    return token_resp.json()["access_token"]


async def _resolve_tenant_id(
    *,
    client: httpx.AsyncClient,
    base: str,
    headers: dict[str, str],
    tenant_slug: str,
) -> int:
    resp = await client.get(f"{base}/tenants", headers=headers)
    resp.raise_for_status()
    tenants = resp.json() or []
    for t in tenants:
        if t.get("slug") == tenant_slug:
            return int(t["id"])
    raise RuntimeError(f"Tenant not found in /tenants response: {tenant_slug}")


async def _maybe_provision(
    *,
    client: httpx.AsyncClient,
    base: str,
    headers: dict[str, str],
    tenant_slug: str,
    tenant_name: str,
    admin_email: str,
    admin_password: str,
) -> None:
    resp = await client.post(
        f"{base}/admin/provision",
        json={
            "tenant_name": tenant_name,
            "tenant_slug": tenant_slug,
            "admin_email": admin_email,
            "admin_password": admin_password,
        },
        headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()
    print("provision_ok", json.dumps(data, ensure_ascii=False))


async def main(
    *,
    base: str,
    tenant_slug: str,
    email: str,
    password: str,
    provision: bool,
    provision_tenant_name: str,
    provision_admin_email: str,
    provision_admin_password: str,
) -> None:
    test_img = Path(__file__).resolve().parent.parent.parent / "_smoke_test.png"
    create_test_image(test_img)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # 0) health
        health = await client.get(f"{base}/health")
        health.raise_for_status()
        print("health_ok", health.json())

        # 1) login (bootstrap)
        token = await _login(
            client=client,
            base=base,
            email=email,
            password=password,
            tenant_slug=tenant_slug,
        )
        headers = {"Authorization": f"Bearer {token}", "x-tenant-slug": tenant_slug}
        print("login_ok", email, tenant_slug)

        # 1.5) provision (optional)
        if provision:
            await _maybe_provision(
                client=client,
                base=base,
                headers=headers,
                tenant_slug=tenant_slug,
                tenant_name=provision_tenant_name,
                admin_email=provision_admin_email,
                admin_password=provision_admin_password,
            )
            # login as provisioned tenant admin
            token = await _login(
                client=client,
                base=base,
                email=provision_admin_email,
                password=provision_admin_password,
                tenant_slug=tenant_slug,
            )
            headers = {"Authorization": f"Bearer {token}", "x-tenant-slug": tenant_slug}
            print("login_ok", provision_admin_email, tenant_slug)

        tenant_id = await _resolve_tenant_id(
            client=client,
            base=base,
            headers=headers,
            tenant_slug=tenant_slug,
        )
        print("tenant_ok", tenant_id, tenant_slug)

        # 2) upload
        with test_img.open("rb") as f:
            files = {"file": (test_img.name, f, "image/png")}
            upload_resp = await client.post(
                f"{base}/uploads/",
                files=files,
                headers=headers,
            )
        upload_resp.raise_for_status()
        upload = upload_resp.json()
        storage_key = upload["storage_key"]
        print("upload_ok", storage_key)

        # 3) create asset
        asset_payload = {
            "tenant_id": tenant_id,
            "original_path": storage_key,
            "processed_path": None,
            "thumbnail_path": None,
            "status": "uploaded",
            "meta_json": json.dumps({"filename": test_img.name, "storage_key": storage_key}, ensure_ascii=False),
        }
        asset_resp = await client.post(f"{base}/assets", json=asset_payload, headers=headers)
        asset_resp.raise_for_status()
        asset = asset_resp.json()
        asset_id = asset["id"]
        print("asset_ok", asset_id)

        # 4) create task
        task_payload = {
            "tenant_id": tenant_id,
            "image_asset_id": asset_id,
            "config_path": "config.json",
            "output_dir": "processed",
        }
        task_resp = await client.post(f"{base}/tasks", json=task_payload, headers=headers)
        task_resp.raise_for_status()
        task = task_resp.json()
        task_id = task["id"]
        print("task_created", task_id, task["status"])

        # 5) poll task
        for i in range(30):
            await asyncio.sleep(0.5)
            t = await client.get(f"{base}/tasks/{task_id}", headers=headers)
            t.raise_for_status()
            status = t.json()["status"]
            print("poll", i, status)
            if status in ("completed", "failed"):
                print("final", t.json())
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--tenant-slug", default=DEFAULT_TENANT_SLUG)
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--password", default="admin123456")

    parser.add_argument("--provision", action="store_true")
    parser.add_argument("--provision-tenant-name", default="Demo Tenant")
    parser.add_argument("--provision-admin-email", default="tenant-admin@example.com")
    parser.add_argument("--provision-admin-password", default="admin123456")
    args = parser.parse_args()
    asyncio.run(
        main(
            base=args.base,
            tenant_slug=args.tenant_slug,
            email=args.email,
            password=args.password,
            provision=args.provision,
            provision_tenant_name=args.provision_tenant_name,
            provision_admin_email=args.provision_admin_email,
            provision_admin_password=args.provision_admin_password,
        )
    )
