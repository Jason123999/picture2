from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import httpx


class VercelError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


@dataclass(frozen=True)
class VercelProjectRef:
    id: str
    name: str


@dataclass(frozen=True)
class VercelDeploymentRef:
    id: str
    url: str


class VercelClient:
    def __init__(
        self,
        *,
        token: str,
        team_id: Optional[str] = None,
        team_slug: Optional[str] = None,
        api_base: str = "https://api.vercel.com",
        timeout_seconds: float = 30.0,
    ) -> None:
        self._token = token
        self._team_id = team_id
        self._team_slug = team_slug
        self._api_base = api_base.rstrip("/")
        self._timeout = timeout_seconds

    def _common_params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        if self._team_id:
            params["teamId"] = self._team_id
        if self._team_slug:
            params["slug"] = self._team_slug
        return params

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    async def get_project(self, *, id_or_name: str) -> VercelProjectRef:
        url = f"{self._api_base}/v9/projects/{id_or_name}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                url,
                params=self._common_params(),
                headers=self._headers(),
            )

        if resp.status_code >= 400:
            raise VercelError(
                f"get_project failed: {resp.status_code} {resp.text}",
                status_code=resp.status_code,
                response_text=resp.text,
            )

        data = resp.json()
        project_id = str(data.get("id") or "")
        project_name = str(data.get("name") or id_or_name)
        if not project_id:
            raise VercelError(f"get_project returned no id: {data}")
        return VercelProjectRef(id=project_id, name=project_name)

    async def create_project(
        self,
        *,
        name: str,
        framework: str = "nextjs",
        git_repo: Optional[str] = None,
        git_provider: str = "github",
        root_directory: Optional[str] = None,
        build_command: Optional[str] = None,
        install_command: Optional[str] = None,
        output_directory: Optional[str] = None,
    ) -> VercelProjectRef:
        url = f"{self._api_base}/v9/projects"

        body: dict[str, Any] = {
            "name": name,
            "framework": framework,
        }

        if root_directory:
            body["rootDirectory"] = root_directory
        if build_command:
            body["buildCommand"] = build_command
        if install_command:
            body["installCommand"] = install_command
        if output_directory:
            body["outputDirectory"] = output_directory

        if git_repo:
            body["gitRepository"] = {
                "type": git_provider,
                "repo": git_repo,
            }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                url,
                params=self._common_params(),
                headers=self._headers(),
                json=body,
            )

        if resp.status_code >= 400:
            raise VercelError(
                f"create_project failed: {resp.status_code} {resp.text}",
                status_code=resp.status_code,
                response_text=resp.text,
            )

        data = resp.json()
        project_id = str(data.get("id") or "")
        project_name = str(data.get("name") or name)
        if not project_id:
            raise VercelError(f"create_project returned no id: {data}")
        return VercelProjectRef(id=project_id, name=project_name)

    async def upsert_env_vars(
        self,
        *,
        project_id_or_name: str,
        variables: dict[str, str],
        target: list[str] | None = None,
        var_type: str = "plain",
    ) -> None:
        if not variables:
            return

        url = f"{self._api_base}/v10/projects/{project_id_or_name}/env"

        request_body: list[dict[str, Any]] = []
        for key, value in variables.items():
            request_body.append(
                {
                    "key": key,
                    "value": value,
                    "type": var_type,
                    "target": target or ["production", "preview"],
                }
            )

        payload: Any
        if len(request_body) == 1:
            payload = request_body[0]
        else:
            payload = request_body

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                url,
                params={**self._common_params(), "upsert": "true"},
                headers=self._headers(),
                json=payload,
            )

        if resp.status_code >= 400:
            raise VercelError(
                f"upsert_env_vars failed: {resp.status_code} {resp.text}",
                status_code=resp.status_code,
                response_text=resp.text,
            )

    async def create_deployment_from_git(
        self,
        *,
        project_name: str,
        project_id: str | None = None,
        git_org: str,
        git_repo: str,
        git_ref: str = "main",
        git_provider: str = "github",
        target: str = "production",
    ) -> VercelDeploymentRef:
        url = f"{self._api_base}/v13/deployments"

        body: dict[str, Any] = {
            "name": project_name,
            "target": target,
            "gitSource": {
                "type": git_provider,
                "org": git_org,
                "repo": git_repo,
                "ref": git_ref,
            },
        }
        if project_id:
            body["project"] = project_id

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                url,
                params=self._common_params(),
                headers=self._headers(),
                json=body,
            )

        if resp.status_code >= 400:
            raise VercelError(
                f"create_deployment failed: {resp.status_code} {resp.text}",
                status_code=resp.status_code,
                response_text=resp.text,
            )

        data = resp.json()
        deployment_id = str(data.get("id") or "")
        deployment_url = str(data.get("url") or "")
        if not deployment_id or not deployment_url:
            raise VercelError(f"create_deployment returned no id/url: {data}")
        return VercelDeploymentRef(id=deployment_id, url=deployment_url)
