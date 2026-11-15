# Лабораторная работа № 1 — Веб-приложение на Flask (вариант 8)

Веб-приложение на **Python + Flask** для обработки изображений: обмен половинами изображения (по горизонтали/вертикали), построение гистограммы распределения цветов, наложение штампа даты/времени, защита формы через **Google reCAPTCHA v2 (Checkbox)**. Реализован эндпоинт верификации `/verify` с персональным токеном и заголовком `X-Verify-Hash`.

- **Демо (актуальное развёртывание):** https://lab1.veheys.online/
- **Проверка работоспособности:** https://lab1.veheys.online/health
- **Верификация:** https://lab1.veheys.online/verify

## Возможности

- Загрузка изображения (PNG/JPG/BMP/GIF) и выбор режима обмена половин: `horizontal` / `vertical`
- Визуализация распределения цветов (R/G/B) исходного и обработанного изображений
- Наложение штампа с датой и временем (по желанию пользователя)
- Защита формы: Google reCAPTCHA v2
- API: `POST /apinet` (JSON, base64) — обработка изображения
- Служебные эндпоинты: `GET /health`, `GET /verify`

## Стек

- Python 3.11+, Flask 3, Flask-WTF/WTForms
- Pillow, NumPy, Matplotlib (backend Agg)
- WSGI: waitress (Windows/контейнер), gunicorn (Linux/CI)

## Структура проекта

```text
lab1_web/
├─ .github/workflows/ci-cd.yml   # CI/CD (тесты + деплой по SSH)
├─ flaskapp/
│  ├─ some_app.py                # маршруты, формы, /health, /verify
│  ├─ image_utils.py             # обработка изображений, гистограмма, штамп
│  ├─ wsgi.py                    # WSGI-точка входа (/, /lab1web)
│  ├─ client.py                  # тестовый клиент для CI
│  ├─ st.sh                      # сценарий теста в CI
│  ├─ static/                    # статика и загрузки
│  └─ templates/                 # HTML-шаблоны
├─ requirements.txt
└─ README.md
```

## Локальный запуск

Требования: Python 3.11+.

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows (PowerShell)
# .\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Создайте файл `.env` в корне проекта (опционально, есть тестовые ключи reCAPTCHA по умолчанию):

```env
SECRET_KEY=your-secret-key
RECAPTCHA_PUBLIC_KEY=your-site-key
RECAPTCHA_PRIVATE_KEY=your-secret-key
```

Запуск (режим разработки):

```bash
cd flaskapp
python some_app.py
# http://127.0.0.1:5000/
```

Запуск через waitress (рекомендуется для проверки):

```bash
cd flaskapp
waitress-serve --listen=0.0.0.0:8080 wsgi:application
# http://localhost:8080/
```

## Развёртывание (актуальное)

Приложение развёрнуто на сервере **Proxmox VE** в LXC-контейнере (Debian 12):

- приложение: `/opt/lab1/flaskapp`, venv: `/opt/lab1/venv`
- WSGI-сервер: **waitress** на `0.0.0.0:8080` (служба `systemd` `lab1.service`)
- публикация: **nginx** (reverse proxy) + **Cloudflare Tunnel** → https://lab1.veheys.online/ (также доступен префикс `/lab1web`)

## CI/CD

Workflow: `.github/workflows/ci-cd.yml`

- **Build & Test** (ubuntu-latest): установка зависимостей и запуск теста приложения (`flaskapp/st.sh`, gunicorn + `client.py`).
- **Deploy to server** (ubuntu-latest, только push в `main/master`): деплой по SSH на сервер. Для работы требуются секреты репозитория GitHub:
  - `DEPLOY_HOST` — адрес хоста Proxmox
  - `DEPLOY_USER` — пользователь SSH
  - `DEPLOY_SSH_KEY` — приватный ключ SSH
  - `DEPLOY_PORT` — порт SSH (опционально, по умолчанию 22)

> Примечание: job деплоя обновляет код и перезапускает службу в контейнере на сервере. Если секреты не настроены или хост недоступен из GitHub Actions, шаг деплоя завершится ошибкой — тесты при этом выполняются независимо.

## API

### `POST /apinet`

Запрос:

```json
{
  "imagebin": "<base64 PNG/JPG>",
  "mode": "horizontal",
  "add_stamp": false
}
```

Ответ: JSON с обработанным изображением (`imagebin`, base64 PNG) и гистограммой (`histogram`, base64 PNG).

### `GET /health`

```json
{"status": "ok"}
```

### `GET /verify`

HTML-страница с персональным токеном и датой, заголовок `X-Verify-Hash` (SHA-256 нормализованного HTML).

## Автор

Козик Д. Д., гр. з-436П8-5 — ТУСУР, «Разработка веб-сервисов для обработки и применения данных», лаб. № 1 (вариант 8).
