from werkzeug.middleware.dispatcher import DispatcherMiddleware

from some_app import app

# WSGI-приложение для продакшн-сервера:
# корень (/) и префикс /lab1web отдают одно и то же приложение.
# При запросе через /lab1web werkzeug выставляет SCRIPT_NAME,
# поэтому url_for корректно генерирует ссылки с префиксом.
application = DispatcherMiddleware(app, {"/lab1web": app})

if __name__ == "__main__":
    app.run()
