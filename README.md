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

## Стек

| Компонент | Технология |
|---|---|
| Python | 3.13 |
| Веб-фреймворк | Flask 3.1 |
| Формы | Flask-WTF, WTForms |
| Капча | **Google reCAPTCHA v2 (Checkbox)** |
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
├── .github/workflows/ci-cd.yml
├── .gitignore
├── .python-version
├── Procfile
├── README.md
├── requirements.txt
├── run_local.py
├── run_local.bat
└── flaskapp/
    ├── some_app.py
    ├── image_utils.py
    ├── wsgi.py
    ├── client.py
    ├── st.sh
    ├── static/uploads/
    └── templates/
        ├── base.html
        ├── index.html
        └── result.html
```

---

## Требования

- Windows 11 (в VirtualBox)
- Python 3.13
- Git
- NSSM — <https://nssm.cc/download>
- Аккаунт GitHub с репозиторием проекта

---

## Установка и запуск (Windows 11)

### 1. Клонировать репозиторий

```powershell
cd C:\Users\Daniil\Desktop\Tusur
git clone git@github-drrexar:DrRexar/lab1-web-variant8.git lab1_web
cd lab1_web
```

### 2. Создать venv и установить зависимости

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

`gunicorn` на Windows не установится — это нормально, он пропускается
по маркеру `sys_platform != "win32"`. На Windows используется `waitress`.

### 3. Создать `.env`

```powershell
notepad .env
```

Содержимое:

```env
SECRET_KEY=<случайная строка 32+ символа>
RECAPTCHA_PUBLIC_KEY=<ваш site key>
RECAPTCHA_PRIVATE_KEY=<ваш secret key>
```

Сгенерировать `SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Запуск в режиме разработки

```powershell
cd flaskapp
python some_app.py
```

Откройте <http://127.0.0.1:5000/>.

### 5. Полная проверка через waitress

Из корня проекта:

```powershell
python run_local.py
```

Ожидаемое завершение — `ALL TESTS PASSED`.

---

## Google reCAPTCHA v2 (Checkbox)

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

Эти ключи используются в job `Build & Test` (CI), чтобы тесты не падали
на капче.

### Как это работает в коде

В `some_app.py` объявлен класс формы:

```python
from flask_wtf import FlaskForm, RecaptchaField

class UploadForm(FlaskForm):
    # ...
    recaptcha = RecaptchaField()
    submit = SubmitField("Обработать")
```

Flask-WTF сам вставляет виджет Google и подключает скрипт
`https://www.google.com/recaptcha/api.js`. При `validate_on_submit()`
он проверяет ответ через `https://www.google.com/recaptcha/api/siteverify`
с вашим `RECAPTCHA_PRIVATE_KEY`.

В `templates/index.html` виджет выводится так:

```html
{{ form.recaptcha }}
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
# {"status":"ok"}
```

Управление службой:

```powershell
C:\nssm\nssm.exe restart Lab1Service
C:\nssm\nssm.exe stop Lab1Service
C:\nssm\nssm.exe status Lab1Service
```

**Порт.** Используется **8080**, потому что порт 80 в Windows 11 обычно
занят `http.sys`. Если 80 свободен — можно использовать его, но не забудьте
поменять порт во всех командах и в workflow.

---

## CI/CD через GitHub Actions

Файл `.github/workflows/ci-cd.yml`. Два job'а:

### `Build & Test` (ubuntu-latest)

- Устанавливает зависимости.
- Запускает gunicorn, прогоняет `client.py`.
- Проверяет `/`, `/health` и `/apinet` (оба режима).
- Завершается строкой `ALL TESTS PASSED`.

### `Deploy on Windows VM` (self-hosted)

- Срабатывает **только при push в `main` или `master`**.
- Переходит в `C:\Users\Daniil\Desktop\Tusur\lab1_web`.
- `git fetch --all` + `git reset --hard origin/main`.
- Обновляет зависимости в venv.
- Перезапускает `Lab1Service` через NSSM.
- Проверяет `/health`, при неудаче валит job.

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
.\config.cmd --url https://github.com/DrRexar/lab1-web-variant8 --token <ТОКЕН> --runasservice
```

Токен живёт 1 час. Проверка:

```powershell
Get-Service "actions.runner.*"
```

На странице **Settings → Actions → Runners** раннер должен быть **Idle**
(зелёная точка).

### Если служба не ставится

Запуск вручную:

```powershell
cd C:\actions-runner
.\run.cmd
```

Окно держать открытым. При перезагрузке — запускать заново.

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

1. Служба:
   ```powershell
   C:\nssm\nssm.exe status Lab1Service
   (Invoke-WebRequest -UseBasicParsing http://localhost:8080/health).Content
   ```
2. Раннер **Idle**: <https://github.com/DrRexar/lab1-web-variant8/settings/actions/runners>
3. Реальный push:
   ```powershell
   cd "C:\Users\Daniil\Desktop\Tusur\lab1_web"
   git add .
   git commit -m "test autodeploy"
   git push origin main
   ```
4. Вкладка **Actions** — оба job'а должны стать зелёными.

---

## Возможные проблемы

| Симптом | Причина | Решение |
|---|---|---|
| `pip install gunicorn` падает | Windows | это норма, gunicorn — только Linux |
| `Could not connect to github.com:22` | порт 22 закрыт | SSH через 443 (`~/.ssh/config`) |
| `Permission to ... denied to ...` | два GitHub-аккаунта | `git@github-drrexar:DrRexar/...` |
| `SERVICE_STOPPED` у NSSM | неверный путь / порт занят | смотреть `logs\stderr.log` |
| `Port 80 permission denied` | занят `http.sys` | использовать 8080 |
| Job `Deploy` в `Queued` > 2 мин | runner offline | `Get-Service "actions.runner.*"`, `Start-Service` |
| `Skipped` на `Deploy` при ручном запуске | защита от случайного деплоя | сделать настоящий push |
| Капча не проходит | домен не добавлен в Google Console | добавить `localhost` и IP ВМ |

---

## Материалы

- Суханов А. Я. «Разработка веб-сервисов для научных и прикладных задач», ТУСУР, 2021.
- Flask — <https://flask.palletsprojects.com/>
- Flask-WTF — <https://flask-wtf.readthedocs.io/>
- Google reCAPTCHA v2 — <https://developers.google.com/recaptcha/docs/display>
- GitHub Actions — <https://docs.github.com/actions>
- NSSM — <https://nssm.cc/>
- waitress — <https://docs.pylonsproject.org/projects/waitress/>

---

## Автор

Даниил, ТУСУР, ФДО, направление 09.03.01
«Информатика и вычислительная техника».