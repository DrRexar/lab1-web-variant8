"""Проверка веб-сервиса после запуска gunicorn (используется в CI)."""
import os
import base64
import sys
import requests
from PIL import Image
import numpy as np

BASE = "http://localhost:5000"


def ensure_test_image(path: str) -> None:
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    arr = (np.random.rand(224, 224, 3) * 255).astype("uint8")
    arr[:112, :, :] = [220, 40, 40]
    arr[112:, :, :] = [40, 40, 220]
    Image.fromarray(arr).save(path)


def main() -> int:
    r = requests.get(BASE + "/", timeout=10)
    print("GET / ->", r.status_code)
    if r.status_code != 200:
        return 1
    assert "recaptcha" in r.text.lower() or "g-recaptcha" in r.text.lower()
    print("captcha present: OK")

    r = requests.get(BASE + "/health", timeout=10)
    print("GET /health ->", r.status_code, r.json())
    if not r.ok:
        return 1

    path = os.path.join("static", "image0008.png")
    ensure_test_image(path)
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("utf-8")

    for mode in ("horizontal", "vertical"):
        res = requests.post(
            BASE + "/apinet",
            json={"imagebin": b64, "mode": mode},
            timeout=30,
        )
        print(f"POST /apinet mode={mode} -> {res.status_code}")
        if not res.ok:
            print(res.text)
            return 1
        data = res.json()
        assert data["mode"] == mode
        assert len(data["imagebin"]) > 0
        assert len(data["histogram"]) > 0
        print(f"  image bytes(b64): {len(data['imagebin'])}, "
              f"hist bytes(b64): {len(data['histogram'])}")

    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())