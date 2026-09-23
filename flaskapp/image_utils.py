"""Утилиты обработки изображений для варианта 8."""
import io
import base64
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFont

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


def add_timestamp(img: Image.Image,
                  text: str = None,
                  position: str = "bottom-right",
                  font_size: int = 24,
                  opacity: int = 180) -> Image.Image:
    """
    Накладывает на изображение плашку с датой и временем.

    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
    opacity:  прозрачность плашки 0..255
    """
    img = img.convert("RGB").copy()
    W, H = img.size

    if text is None:
        text = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    # Шрифт — сначала TrueType, иначе дефолтный
    font = None
    for fname in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            font = ImageFont.truetype(fname, font_size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Размер текста
    try:
        bbox = font.getbbox(text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        tw, th = font.getsize(text)

    pad = 10
    box_w = tw + 2 * pad
    box_h = th + 2 * pad

    if position == "top-left":
        x, y = 10, 10
    elif position == "top-right":
        x, y = W - box_w - 10, 10
    elif position == "bottom-left":
        x, y = 10, H - box_h - 10
    else:  # bottom-right
        x, y = W - box_w - 10, H - box_h - 10

    # Полупрозрачная подложка
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    draw_ov.rectangle([x, y, x + box_w, y + box_h], fill=(0, 0, 0, opacity))

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Сам текст
    draw = ImageDraw.Draw(img)
    draw.text((x + pad, y + pad), text, fill=(255, 255, 255), font=font)

    return img