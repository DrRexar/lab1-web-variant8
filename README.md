# ЛР1 — Разработка веб-сервисов для научных и прикладных задач

**Вариант 8.** Flask-приложение, которое меняет местами половины изображения
(левую/правую либо верхнюю/нижнюю), строит график распределения цветов и
защищено Google reCAPTCHA v2 (Checkbox). Автодеплой — через GitHub Actions
с self-hosted runner на Windows 11 (VirtualBox).

---

## Что делает приложение

Пользователь загружает изображение, выбирает режим обмена половин и проходит
капчу «Я не робот». Сервер:

1. Меняет местами половины картинки:
   - `horizontal` — левая ↔ правая,
   - `vertical` — верхняя ↔ нижняя.
2. Строит график распределения цветов R/G/B исходного изображения.
3. Возвращает страницу с исходной и обработанной картинками и обеими
   гистограммами.

Дополнительно:

- `POST /apinet` — JSON-API для программного доступа;
- `GET /health` — healthcheck, используется в CI/CD и NSSM.

---

## Порты

В проекте используются **два порта** — они относятся к разным режимам работы:

| Режим | Порт | Как запускается | Где применяется |
|---|---|---|---|
| Разработка | **5000** | `python some_app.py` (Flask dev-сервер) | локальная отладка на машине разработчика |
| Эксплуатация | **8080** | служба Windows `Lab1Service` через waitress | продакшн на целевой ВМ, куда смотрит автодеплой |

Порт **8080** выбран потому, что порт 80 в Windows 11 обычно занят системной
службой `http.sys` (IIS, WinRM). Это осознанное архитектурное решение, а не
ограничение.

---

## Стек

| Компонент | Технология |
|---|---|
| Python | 3.13 |
| Веб-фреймворк | Flask 3.1 |
| Формы | Flask-WTF, WTForms |
| Капча | Google reCAPTCHA v2 (Checkbox) |
| Обработка изображений | Pillow 11, NumPy 2.1 |
| Графики | Matplotlib (Agg backend) |
| WSGI (Windows) | waitress |
| WSGI (Linux/CI) | gunicorn |
| Служба Windows | NSSM |
| CI/CD | GitHub Actions |

---

## Структура проекта

```
lab1_web/
├── .github/workflows/ci-cd.yml     конфигурация CI/CD
├── .gitignore
├── .python-version
├── Procfile
├── README.md
├── requirements.txt
├── run_local.py                    запуск через waitress
├── run_local.bat                   ярлык запуска на Windows
└── flaskapp/
    ├── some_app.py                 основное приложение
    ├── image_utils.py              обработка изображений
    ├── wsgi.py                     точка входа WSGI
    ├── client.py                   проверка сервиса
    ├── st.sh                       скрипт для CI
    ├── static/uploads/             загруженные изображения
    └── templates/
        ├── base.html
        ├── index.html
        └── result.html
```

---

## Требования

- Windows 11 (основной сценарий — виртуальная машина в VirtualBox)
- Python 3.13
- Git
- NSSM — <https://nssm.cc/download>
- Аккаунт GitHub с репозиторием проекта

---

## Установка

### 1. Клонировать репозиторий

```powershell
cd C:\Users\Daniil\Desktop\Tusur
git clone https://github.com/DrRexar/lab1-web-variant8.git lab1_web
cd lab1_web
```

### 2. Создать venv и установить зависимости

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

`gunicorn` на Windows не установится — это нормально, он пропускается по
маркеру `sys_platform != "win32"`. На Windows вместо него используется `waitress`.

### 3. Создать файл `.env`

```powershell
notepad .env
```

Содержимое:

```env
SECRET_KEY=<случайная строка 32+ символа>
RECAPTCHA_PUBLIC_KEY=<ваш site key из Google>
RECAPTCHA_PRIVATE_KEY=<ваш secret key из Google>
```

Сгенерировать `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Запуск в режиме разработки (порт 5000)

```powershell
cd flaskapp
python some_app.py
```

Откройте в браузере: **http://127.0.0.1:5000/**

Это Flask dev-сервер, он годится только для локальной отладки. Для
эксплуатации используется waitress как служба Windows.

---

## Запуск в режиме эксплуатации (порт 8080)

Через waitress вручную:

```powershell
cd flaskapp
..\venv\Scripts\python.exe -m waitress --host=0.0.0.0 --port=8080 some_app:app
```

Откройте в браузере: **http://localhost:8080/**

Проверка healthcheck:

```powershell
(Invoke-WebRequest -UseBasicParsing http://localhost:8080/health).Content
# {"status":"ok"}
```

---

## Запуск как служба Windows (NSSM)

В **PowerShell от имени администратора**:

```powershell
C:\nssm\nssm.exe install Lab1Service "C:\Users\Daniil\Desktop\Tusur\lab1_web\venv\Scripts\python.exe" "-m waitress --host=0.0.0.0 --port=8080 some_app:app"

C:\nssm\nssm.exe set Lab1Service AppDirectory "C:\Users\Daniil\Desktop\Tusur\lab1_web\flaskapp"

New-Item -ItemType Directory -Force "C:\Users\Daniil\Desktop\Tusur\lab1_web\logs" | Out-Null
C:\nssm\nssm.exe set Lab1Service AppStdout "C:\Users\Daniil\Desktop\Tusur\lab1_web\logs\stdout.log"
C:\nssm\nssm.exe set Lab1Service AppStderr "C:\Users\Daniil\Desktop\Tusur\lab1_web\logs\stderr.log"

C:\nssm\nssm.exe set Lab1Service AppExit Default Restart
C:\nssm\nssm.exe set Lab1Service AppRestartDelay 3000
C:\nssm\nssm.exe set Lab1Service Start SERVICE_AUTO_START

C:\nssm\nssm.exe start Lab1Service
C:\nssm\nssm.exe status Lab1Service
```

Ожидаемый статус — `SERVICE_RUNNING`. Проверка:

```powershell
(Invoke-WebRequest -UseBasicParsing http://localhost:8080/health).Content
```

Управление службой:

```powershell
C:\nssm\nssm.exe restart Lab1Service
C:\nssm\nssm.exe stop Lab1Service
C:\nssm\nssm.exe status Lab1Service
```

---

## Google reCAPTCHA v2

### Как получить ключи

1. Откройте <https://www.google.com/recaptcha/admin/create>.
2. **Label**: `lab1-web-variant8`.
3. **Тип reCAPTCHA**: **reCAPTCHA v2** → галочка **«Я не робот» (Checkbox)**.
4. **Домены**: `localhost`, `127.0.0.1` (можно добавить IP вашей ВМ).
5. Примите условия → **Submit**.
6. Скопируйте **Site key** и **Secret key** в `.env`.

### Тестовые ключи Google (всегда пропускают пользователя)

- Site key: `6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI`
- Secret key: `6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe`

Используются в job `Build & Test` (CI), чтобы тесты не падали на капче.

---

## CI/CD через GitHub Actions

Файл `.github/workflows/ci-cd.yml`. Два job'а:

### `Build & Test` (ubuntu-latest)

- Устанавливает зависимости.
- Запускает приложение через gunicorn на **порту 5000**.
- Прогоняет `client.py`: проверяет `/`, `/health`, `/apinet` в обоих режимах.
- Завершается строкой `ALL TESTS PASSED`.

### `Deploy on Windows VM` (self-hosted)

- Срабатывает **только при push в `main` или `master`**.
- Переходит в `C:\Users\Daniil\Desktop\Tusur\lab1_web`.
- `git fetch --all` + `git reset --hard origin/main`.
- Обновляет зависимости в venv.
- Перезапускает `Lab1Service` через NSSM.
- Проверяет `/health` на **порту 8080** и валит job, если ответ не `ok`.

Ручной запуск (`workflow_dispatch`) **не** деплоит — защита от случайных
действий.

---

## Self-hosted runner

### Установка

1. GitHub → **Settings → Actions → Runners → New self-hosted runner → Windows x64**.
2. Скачать zip, распаковать в `C:\actions-runner`.
3. В **PowerShell от администратора**:

```powershell
cd C:\actions-runner
.\config.cmd --url https://github.com/DrRexar/lab1-web-variant8 --token <ТОКЕН>
# на вопрос "install as a service?" → N
```

### Запуск как службы через NSSM

```powershell
C:\nssm\nssm.exe install ActionRunner "C:\actions-runner\bin\Runner.Listener.exe" "run"
C:\nssm\nssm.exe set ActionRunner AppDirectory "C:\actions-runner"
C:\nssm\nssm.exe set ActionRunner AppStdout "C:\actions-runner\logs\stdout.log"
C:\nssm\nssm.exe set ActionRunner AppStderr "C:\actions-runner\logs\stderr.log"
C:\nssm\nssm.exe set ActionRunner AppExit Default Restart
C:\nssm\nssm.exe set ActionRunner AppRestartDelay 5000
C:\nssm\nssm.exe set ActionRunner Start SERVICE_AUTO_START

C:\nssm\nssm.exe start ActionRunner
```

> **Важно:** runner должен иметь доступ к папке проекта. Служба работает
> от `LocalSystem`, а папка `C:\Users\Daniil\...` ему не видна по умолчанию.
> Решение — выдать права:
>
> ```powershell
> icacls "C:\Users\Daniil\Desktop\Tusur\lab1_web" /grant "SYSTEM:(OI)(CI)F" /T
> icacls "C:\Users\Daniil\Desktop\Tusur\lab1_web\venv" /grant "SYSTEM:(OI)(CI)F" /T
> icacls "C:\Users\Daniil\Desktop\Tusur\lab1_web\logs" /grant "SYSTEM:(OI)(CI)F" /T
> ```
>
> Дополнительно нужно разрешить git работать с этим репозиторием под SYSTEM:
>
> ```powershell
> $env:HOME = "C:\Windows\System32\config\systemprofile"
> git config --global --add safe.directory "C:/Users/Daniil/Desktop/Tusur/lab1_web"
> ```

Проверка, что runner онлайн: **Settings → Actions → Runners** — статус `Idle`.

---

## Переменные окружения

| Переменная | Где задаётся | Что это |
|---|---|---|
| `SECRET_KEY` | `.env`, NSSM `AppEnvironmentExtra` | сессионный ключ Flask |
| `RECAPTCHA_PUBLIC_KEY` | `.env` | публичный ключ (в HTML) |
| `RECAPTCHA_PRIVATE_KEY` | `.env` | приватный (проверка на сервере) |

---

## JSON-API

### `POST /apinet`

**Запрос:**

```json
{
  "imagebin": "<base64 PNG/JPG>",
  "mode": "horizontal"
}
```

**Ответ:**

```json
{
  "mode": "horizontal",
  "imagebin": "<base64 PNG результата>",
  "histogram": "<base64 PNG гистограммы>"
}
```

### `GET /health`

Возвращает `{"status": "ok"}`.

---

## Проверка автодеплоя

1. Убедиться, что служба `Lab1Service` работает:
   ```powershell
   C:\nssm\nssm.exe status Lab1Service
   (Invoke-WebRequest -UseBasicParsing http://localhost:8080/health).Content
   ```

2. Убедиться, что runner **Idle**:
   <https://github.com/DrRexar/lab1-web-variant8/settings/actions/runners>

3. Сделать реальный push:
   ```powershell
   cd "C:\Users\Daniil\Desktop\Tusur\lab1_web"
   git add .
   git commit -m "test autodeploy"
   git push origin main
   ```

4. Открыть вкладку **Actions** и наблюдать, как job `Deploy on Windows VM`
   выполняется на целевой ВМ.

---

## Возможные проблемы

| Симптом | Причина | Решение |
|---|---|---|
| `pip install gunicorn` падает | Windows | нормально, gunicorn — только для Linux |
| `SERVICE_STOPPED` у `Lab1Service` | неверный путь или занятый порт | смотреть `logs\stderr.log` |
| Порт 80 занят | `http.sys` | использовать 8080 |
| Job `Deploy` в `Queued` > 2 мин | runner offline | `C:\nssm\nssm.exe status ActionRunner` |
| `Access is denied` при `Set-Location` | runner работает не под тем пользователем | `icacls ... /grant SYSTEM` |
| `detected dubious ownership in repository` | git под SYSTEM не доверяет папке | `git config --global --add safe.directory` |
| `Skipped` на `Deploy` при ручном запуске | защита от случайного деплоя | делать реальный push |
| Капча не проходит | домен не добавлен в Google Console | добавить `localhost` и IP ВМ |

---

## Список источников

1. Суханов, А. Я. Разработка веб-сервисов для научных и прикладных задач :
   учеб. пособие / А. Я. Суханов. – Томск : ФДО, ТУСУР, 2021. – 246 с.
2. Официальная документация Flask. – URL: https://flask.palletsprojects.com/
3. Flask-WTF: формы и интеграция с reCAPTCHA. – URL: https://flask-wtf.readthedocs.io/
4. Google reCAPTCHA v2 Documentation. – URL: https://developers.google.com/recaptcha/docs/display
5. GitHub Actions Documentation. – URL: https://docs.github.com/actions
6. NSSM — the Non-Sucking Service Manager. – URL: https://nssm.cc/
7. Pillow (PIL Fork) Documentation. – URL: https://pillow.readthedocs.io/

---

## Автор

**Козик Даниил Дмитриевич**

ТУСУР, факультет дистанционного обучения,
направление 09.03.01 «Информатика и вычислительная техника».