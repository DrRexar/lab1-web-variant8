"""Утилиты обработки изображений для варианта 8."""
import io
import base64
import numpy as np
from PIL import Image

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def swap_halves(img: Image.Image, mode: str = "horizontal") -> Image.Image:
    """
    Переставляет половины изображения местами.

    mode = 'horizontal' — меняет местами ЛЕВУЮ и ПРАВУЮ половины;
    mode = 'vertical'   — меняет местами ВЕРХНЮЮ и НИЖНЮЮ половины.
    """
    if mode not in ("horizontal", "vertical"):
        raise ValueError("mode must be 'horizontal' or 'vertical'")

    arr = np.asarray(img.convert("RGB"))

    if mode == "horizontal":
        mid = arr.shape[1] // 2
        new_arr = np.concatenate([arr[:, mid:, :], arr[:, :mid, :]], axis=1)
    else:
        mid = arr.shape[0] // 2
        new_arr = np.concatenate([arr[mid:, :, :], arr[:mid, :, :]], axis=0)

    return Image.fromarray(new_arr)


def color_histogram_b64(img: Image.Image) -> str:
    """Строит график распределения цветов R/G/B и возвращает PNG в base64."""
    arr = np.asarray(img.convert("RGB"))

    fig, ax = plt.subplots(figsize=(6, 4))
    for i, c in enumerate(("r", "g", "b")):
        hist, bins = np.histogram(arr[:, :, i].ravel(), bins=256, range=(0, 256))
        ax.plot(bins[:-1], hist, color=c, alpha=0.8, linewidth=1.2)

    ax.set_xlabel("Интенсивность (0–255)")
    ax.set_ylabel("Кол-во пикселей")
    ax.set_title("Распределение цветов")
    ax.legend(["R", "G", "B"])
    ax.grid(alpha=0.3)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def image_to_b64_png(img: Image.Image) -> str:
    """Сохраняет PIL-изображение в base64 PNG (для JSON-API)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")