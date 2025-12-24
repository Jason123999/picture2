from __future__ import annotations

from pathlib import Path

from app.services.processor import (
    CropConfig,
    ImageProcessingSettings,
    create_ppt,
    crop_image_to_rounded_rectangle,
)


def test_crop_image_to_rounded_rectangle(tmp_path: Path, sample_image: Path) -> None:
    settings = ImageProcessingSettings(
        dpi=300,
        size_cm=5.0,
        corner_radius_ratio=0.1,
        label_config={"top_left": "A"},
    )
    cropped = crop_image_to_rounded_rectangle(
        sample_image,
        CropConfig(left=0, top=0, width=400, height=400),
        400,
        settings.corner_radius_ratio,
    )
    assert cropped.mode == "RGBA"


def test_create_ppt(tmp_path: Path, sample_image: Path) -> None:
    settings = ImageProcessingSettings(
        dpi=300,
        size_cm=5.0,
        corner_radius_ratio=0.1,
        label_config={"top_left": "A"},
    )
    image = crop_image_to_rounded_rectangle(
        sample_image,
        CropConfig(left=0, top=0, width=400, height=400),
        400,
        settings.corner_radius_ratio,
    )
    prs = create_ppt(
        [image],
        [sample_image.name],
        settings,
        columns=1,
        rows=1,
        column_spacing_cm=0.2,
        row_spacing_cm=0.2,
    )
    output_path = tmp_path / "output.pptx"
    prs.save(output_path)
    assert output_path.exists()
