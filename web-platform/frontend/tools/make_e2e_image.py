from pathlib import Path

from PIL import Image


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "public" / "e2e_test.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (320, 240), (200, 120, 80))
    img.save(out_path)
    print(str(out_path))


if __name__ == "__main__":
    main()
