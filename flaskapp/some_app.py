"""Лабораторная работа №1, вариант 8.

Веб-приложение на Flask: меняет местами половины картинки
и строит график распределения цветов.
Проверка на робота — Google reCAPTCHA v2 (Checkbox).
"""
import os
import uuid
import base64
from io import BytesIO

from PIL import Image
from flask import (Flask, render_template, request,
                   jsonify, url_for)
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import RadioField, SubmitField, BooleanField, SelectField
from werkzeug.utils import secure_filename

from image_utils import (swap_halves, color_histogram_b64,
                         image_to_b64_png, add_timestamp)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

app.config["RECAPTCHA_USE_SSL"]    = False
app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ.get(
    "RECAPTCHA_PUBLIC_KEY",
    "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",
)
app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ.get(
    "RECAPTCHA_PRIVATE_KEY",
    "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe",
)
app.config["RECAPTCHA_OPTIONS"] = {"theme": "light"}

UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {"jpg", "jpeg", "png", "bmp", "gif"}


class UploadForm(FlaskForm):
    image = FileField(
        "Изображение",
        validators=[FileRequired(), FileAllowed(list(ALLOWED_EXT), "Только изображения!")],
    )
    mode = RadioField(
        "Что поменять местами?",
        choices=[
            ("horizontal", "Левую и правую половины"),
            ("vertical",   "Верхнюю и нижнюю половины"),
        ],
        default="horizontal",
    )
    add_stamp = BooleanField("Добавить дату и время")
    stamp_position = SelectField(
        "Расположение штампа",
        choices=[
            ("bottom-right", "Снизу справа"),
            ("bottom-left",  "Снизу слева"),
            ("top-right",    "Сверху справа"),
            ("top-left",     "Сверху слева"),
        ],
        default="bottom-right",
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Обработать")


@app.route("/", methods=["GET", "POST"])
def index():
    form = UploadForm()

    if request.method == "POST" and form.validate_on_submit():
        f = form.image.data
        safe = secure_filename(f.filename) or "image.png"
        uniq = uuid.uuid4().hex[:8]

        in_name  = f"in_{uniq}_{safe}"
        out_name = f"out_{uniq}_{safe}"
        in_path  = os.path.join(UPLOAD_DIR, in_name)
        out_path = os.path.join(UPLOAD_DIR, out_name)

        f.save(in_path)

        img = Image.open(in_path).convert("RGB")
        result = swap_halves(img, form.mode.data)

        # Наложение штампа с датой/временем, если пользователь выбрал
        if form.add_stamp.data:
            result = add_timestamp(result, position=form.stamp_position.data)

        result.save(out_path)

        return render_template(
            "result.html",
            in_image=url_for("static", filename=f"uploads/{in_name}"),
            out_image=url_for("static", filename=f"uploads/{out_name}"),
            hist_orig=color_histogram_b64(img),
            hist_new=color_histogram_b64(result),
            mode=form.mode.data,
            stamped=form.add_stamp.data,
            stamp_position=form.stamp_position.data,
        )

    return render_template("index.html", form=form)


@app.route("/apinet", methods=["POST"])
def apinet():
    if request.mimetype != "application/json":
        return jsonify({"error": "application/json required"}), 400

    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "horizontal")
    if mode not in ("horizontal", "vertical"):
        return jsonify({"error": "bad mode"}), 400
    if "imagebin" not in data:
        return jsonify({"error": "imagebin required"}), 400

    try:
        cfile = base64.b64decode(data["imagebin"].encode("utf-8"))
        img = Image.open(BytesIO(cfile)).convert("RGB")
        result = swap_halves(img, mode)
    except Exception as e:
        return jsonify({"error": f"cannot decode image: {e}"}), 400

    return jsonify({
        "mode": mode,
        "imagebin": image_to_b64_png(result),
        "histogram": color_histogram_b64(img),
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)