from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from app.services.processor import CropConfig, ImageProcessingSettings


@dataclass(slots=True)
class LegacyConfig:
    raw: dict[str, Any]

    @property
    def crop_settings(self) -> dict[str, Any]:
        return self.raw.get("crop_settings", {})

    @property
    def image_settings(self) -> dict[str, Any]:
        return self.raw.get("image_settings", {})

    @property
    def label_settings(self) -> dict[str, Any]:
        return self.raw.get("label_settings", {})

    @property
    def ppt_settings(self) -> dict[str, Any]:
        return self.raw.get("ppt_settings", {})

    def uniform_crop(self) -> CropConfig:
        uniform = self.crop_settings.get("uniform_crop", {})
        return CropConfig(
            left=int(uniform.get("left", 0)),
            top=int(uniform.get("top", 0)),
            width=int(uniform.get("width", 0)),
            height=int(uniform.get("height", 0)),
        )

    def ppt_layout(self) -> Dict[str, Any]:
        return {
            "columns": int(self.ppt_settings.get("columns", 4)),
            "rows": int(self.ppt_settings.get("rows", 2)),
            "column_spacing_cm": float(self.ppt_settings.get("column_spacing_cm", 0.2)),
            "row_spacing_cm": float(self.ppt_settings.get("row_spacing_cm", 0.2)),
        }


def load_legacy_config(path: Path) -> LegacyConfig:
    from app.services.processor import load_config

    data = load_config(path)
    return LegacyConfig(raw=data)


def to_processing_settings(config: LegacyConfig) -> ImageProcessingSettings:
    image_settings = config.image_settings
    label_settings = config.label_settings

    size_cm = float(image_settings.get("size_cm", 5.0))
    dpi = int(image_settings.get("dpi", 300))

    labels = label_settings.get("sample_labels", {})
    font_color = label_settings.get("font_color", "#000000")
    font_size = label_settings.get("font_size", 12)

    label_config = {
        **labels,
        "font_color": font_color,
        "font_size": font_size,
    }

    corner_radius = 0.1
    crop_settings = config.crop_settings
    uniform_crop = crop_settings.get("uniform_crop", {})

    if "corner_radius" in crop_settings:
        corner_radius = float(crop_settings["corner_radius"])

    return ImageProcessingSettings(
        dpi=dpi,
        size_cm=size_cm,
        corner_radius_ratio=corner_radius,
        label_config=label_config,
    )
