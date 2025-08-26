
import io
import os
import re
from collections import Counter
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from PIL import Image
import qrcode

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

# ---------- Utilities (no storage, stateless) ----------
STOPWORDS = set("""a an the and or but if in on with as is are was were be to of for from by at this that it its it's your you we they i me my our their not do does did so than then over into above below up down out off about can just only more most some any all such very have has had when where which who whom whose why how""".split())

def tokenize(text):
    # words: letters and numbers
    return re.findall(r"[A-Za-z0-9']+", text.lower())

@app.route("/")
def home():
    return render_template("index.html")

# ---------- Text Analyzer ----------
@app.route("/text", methods=["GET", "POST"])
def text_tool():
    result = None
    text = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        words = tokenize(text)
        chars = len(text)
        n_words = len(words)
        sentences = re.split(r"[.!?]+", text.strip())
        sentences = [s for s in sentences if s.strip()]
        n_sent = len(sentences)
        avg_wlen = sum(len(w) for w in words) / n_words if n_words else 0
        wpm = 200
        reading_time_min = round(n_words / wpm, 2)
        # top words excluding stopwords
        filtered = [w for w in words if w not in STOPWORDS]
        common = Counter(filtered).most_common(10)
        # letter frequency
        letters = Counter([c.lower() for c in text if c.isalpha()])
        result = {
            "chars": chars,
            "words": n_words,
            "sentences": n_sent,
            "avg_wlen": round(avg_wlen, 2),
            "reading_time_min": reading_time_min,
            "top_words": common,
            "letters": letters,
        }
    return render_template("text.html", text=text, result=result)

# ---------- Unit Converter ----------
@app.route("/convert", methods=["GET", "POST"])
def convert():
    result = None
    if request.method == "POST":
        ctype = request.form.get("ctype")
        value = request.form.get("value", "").strip()
        try:
            x = float(value)
        except:
            flash("Please enter a valid number.", "error")
            return redirect(url_for("convert"))

        if ctype == "temp":
            # Celsius to F & K
            result = {
                "C": x,
                "F": x * 9/5 + 32,
                "K": x + 273.15
            }
        elif ctype == "length":
            # meters to km, cm, mm, ft, in
            result = {
                "m": x,
                "km": x / 1000,
                "cm": x * 100,
                "mm": x * 1000,
                "ft": x * 3.28084,
                "in": x * 39.3701
            }
        elif ctype == "weight":
            # kg to g, lb, oz
            result = {
                "kg": x,
                "g": x * 1000,
                "lb": x * 2.20462,
                "oz": x * 35.274
            }
    return render_template("convert.html", result=result)

# ---------- QR Code Generator ----------
@app.route("/qr", methods=["GET", "POST"])
def qr():
    if request.method == "POST":
        data = request.form.get("data", "").strip()
        if not data:
            flash("Enter some text or a URL for the QR code.", "error")
            return render_template("qr.html")
        qr_img = qrcode.make(data)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=True, download_name="qrcode.png")
    return render_template("qr.html")

# ---------- Image Resizer (in-memory) ----------
@app.route("/image", methods=["GET", "POST"])
def image_tool():
    if request.method == "POST":
        file = request.files.get("image")
        width = request.form.get("width", "").strip()
        height = request.form.get("height", "").strip()
        if not file or file.filename == "":
            flash("Please choose an image.", "error")
            return render_template("image.html")
        try:
            width = int(width) if width else None
            height = int(height) if height else None
            img = Image.open(file.stream)
            # maintain aspect if only one dimension provided
            if width and not height:
                ratio = width / img.width
                height = int(img.height * ratio)
            elif height and not width:
                ratio = height / img.height
                width = int(img.width * ratio)
            elif not width and not height:
                width, height = img.size  # no change
            resized = img.resize((width, height))
            buf = io.BytesIO()
            # preserve format if possible else PNG
            fmt = img.format if img.format in {"JPEG","JPG","PNG","WEBP"} else "PNG"
            resized.save(buf, format=fmt)
            buf.seek(0)
            fname = f"resized.{fmt.lower()}"
            return send_file(buf, mimetype=f"image/{fmt.lower()}", as_attachment=True, download_name=fname)
        except Exception as e:
            flash(f"Error: {e}", "error")
    return render_template("image.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
