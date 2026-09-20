# ЛР1. Разработка веб-сервисов — Вариант 8

Flask-приложение: меняет местами половины изображения (левую/правую либо
верхнюю/нижнюю), строит график распределения цветов, реализует Google
reCAPTCHA v2 и JSON-API `/apinet`. Есть CI (GitHub Actions) и деплой на Heroku.

## Требования

- Python 3.13
- Windows 11 / Linux / macOS

## Установка (Windows 11)

    py -3.13 -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

> Если `py` не находит 3.13 — проверьте `py -0p` и установите нужную версию
> с https://www.python.org/downloads/windows/

## Установка (Linux/macOS)

    python3.13 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Запуск локально (режим отладки)

Windows:

    cd flaskapp
    python some_app.py

Linux/macOS:

    cd flaskapp
    python some_app.py

Открыть в браузере: http://127.0.0.1:5000/

## Полная проверка (как в CI)

Windows:

    python run_local.py

или двойной клик по `run_local.bat`.

Linux/macOS:

    python run_local.py

Ожидаемый вывод в конце: `ALL TESTS PASSED`.

## Переменные окружения (опционально)

Скопируйте `.env.example` в `.env` и заполните своими ключами.
Без этого используются официальные тестовые ключи Google — они всегда
пропускают пользователя и удобны для разработки.

## Деплой

- CI/CD настроены в `.github/workflows/ci-cd.yml`.
- Секреты репозитория: `HEROKU_API_KEY`, `HEROKU_APP_NAME`, `HEROKU_EMAIL`.
- Ключи reCAPTCHA для продакшена задаются в Heroku Config Vars.

## Частые вопросы

- **`pip install gunicorn` падает на Windows** — это нормально, gunicorn
  устанавливается только на Linux (см. маркеры в `requirements.txt`).
  На Windows используется `waitress`.
- **Кириллица в консоли превращается в кракозябры** — запустите
  `chcp 65001` или используйте `run_local.bat`.
- **`ModuleNotFoundError: No module named 'matplotlib'`** — активируйте
  venv и переустановите: `pip install -r requirements.txt`.