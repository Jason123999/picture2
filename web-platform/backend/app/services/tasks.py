from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Iterable, Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings
from app.models import ImageAsset, ProcessingTask, TaskStatus
from app.services.config_loader import LegacyConfig, load_legacy_config, to_processing_settings
from app.services.processor import CropConfig, ImageProcessingSettings, create_ppt, process_images
from app.services.storage import get_storage_backend

_LOGGER = logging.getLogger(__name__)


async def execute_processing_task(session: AsyncSession, task: ProcessingTask) -> None:
    storage = get_storage_backend()
    app_settings = get_settings()

    asset = await session.get(ImageAsset, task.image_asset_id)
    if asset is None:
        task.status = TaskStatus.FAILED
        task.error_message = "Image asset not found"
        await session.commit()
        return

    task.status = TaskStatus.PROCESSING
    await session.commit()

    try:
        config = _load_config(task)
        processing_settings = to_processing_settings(config)
        crop_config = config.uniform_crop()
        layout = config.ppt_layout()

        local_root = Path(app_settings.storage_local_root)
        if not local_root.is_absolute():
            backend_app_root = Path(__file__).resolve().parents[2]
            local_root = (backend_app_root / local_root).resolve()

        original_files = _resolve_original_files(asset.original_path, str(local_root))
        processed_images = await asyncio.to_thread(
            process_images,
            original_files,
            lambda path: crop_config,
            processing_settings,
        )

        ppt = await asyncio.to_thread(
            create_ppt,
            processed_images,
            [Path(f).name for f in original_files],
            processing_settings,
            layout["columns"],
            layout["rows"],
            layout["column_spacing_cm"],
            layout["row_spacing_cm"],
        )

        output_dir = Path(task.output_dir or "processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        result_files = await _save_processed_images(processed_images, output_dir)
        ppt_path = output_dir / "output.pptx"
        await asyncio.to_thread(ppt.save, ppt_path)

        uploaded_paths = await _upload_results(storage, asset, result_files, ppt_path)

        asset.processed_path = uploaded_paths["images"].get("primary")
        task.result_path = uploaded_paths["ppt"]
        task.status = TaskStatus.COMPLETED
        await session.commit()
    except Exception as exc:  # pragma: no cover
        _LOGGER.exception("Task %s failed", task.id)
        task.status = TaskStatus.FAILED
        task.error_message = str(exc)
        await session.commit()


def _load_config(task: ProcessingTask) -> LegacyConfig:
    raw = task.config_path or "config.json"
    config_path = Path(raw)

    if config_path.exists():
        return load_legacy_config(config_path)

    # If relative and missing, try common roots.
    if not config_path.is_absolute():
        services_file = Path(__file__).resolve()
        candidates = [
            Path.cwd() / config_path,
            services_file.parents[2] / config_path,  # backend/app/
            services_file.parents[3] / config_path,  # backend/
            services_file.parents[4] / config_path,  # web-platform/
            services_file.parents[5] / config_path,  # d:/图片处理程序3.8/
        ]
        for cand in candidates:
            if cand.exists():
                return load_legacy_config(cand)

    # Fall back to original path to keep error message meaningful.
    return load_legacy_config(config_path)


def _resolve_original_files(original_path: str, storage_root: str) -> Sequence[str]:
    """Resolve original files.

    In local storage mode, `original_path` is usually a storage key like
    `tenants/<id>/uploads/.../file.ext`. We map it to an actual file path under
    `storage_root`.
    """

    candidate = Path(original_path)

    # If it's already a real path, use it.
    if candidate.exists():
        path = candidate
    else:
        # Treat as storage key under local storage root.
        path = (Path(storage_root) / original_path).resolve()

    if path.is_dir():
        files: list[str] = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff"):
            files.extend(str(file) for file in path.glob(ext))
        return sorted(files)

    if path.is_file():
        return [str(path)]

    raise FileNotFoundError(str(path))


async def _save_processed_images(images, output_dir: Path) -> Sequence[Path]:
    result_paths = []
    for idx, image in enumerate(images, start=1):
        filename = output_dir / f"processed_{idx:03}.png"
        await asyncio.to_thread(image.save, filename, format="PNG", optimize=True)
        result_paths.append(filename)
    return result_paths


async def _upload_results(storage, asset: ImageAsset, images: Iterable[Path], ppt_path: Path):
    image_urls = {}
    for idx, image_path in enumerate(images, start=1):
        with open(image_path, "rb") as f:
            stored = await storage.upload_file(
                key=f"tenants/{asset.tenant_id}/images/{image_path.name}",
                data=f.read(),
                content_type="image/png",
            )
            image_urls[f"image_{idx}"] = stored.url
            if idx == 1:
                image_urls["primary"] = stored.url

    with open(ppt_path, "rb") as f:
        ppt_stored = await storage.upload_file(
            key=f"tenants/{asset.tenant_id}/ppt/{ppt_path.name}",
            data=f.read(),
            content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    return {"images": image_urls, "ppt": ppt_stored.url}
