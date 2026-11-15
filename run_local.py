"""Локальная проверка проекта.

Запускает waitress, ждёт 5 секунд, дергает client.py, гасит сервер.
Работает на Windows, Linux и macOS.
"""
import os
import sys
import time
import subprocess

HOST = "127.0.0.1"
PORT = "5000"


def main() -> int:
    # UTF-8 для консоли Windows
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    cmd = [
        sys.executable, "-m", "waitress",
        f"--host={HOST}", f"--port={PORT}",
        "--call", "some_app:app",
    ]
    print("Starting:", " ".join(cmd))
    proc = subprocess.Popen(cmd)

    rc = 1
    try:
        time.sleep(5)
        print("=== start client ===")
        rc = subprocess.call([sys.executable, "client.py"])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    print(f"=== app code: {rc} ===")
    return rc


if __name__ == "__main__":
    sys.exit(main())