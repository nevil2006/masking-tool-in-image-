

import os
import re
import cv2
import numpy as np
import pytesseract
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(APP_ROOT, "static", "uploads")
RESULT_DIR = os.path.join(APP_ROOT, "static", "results")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

if os.name == "nt":
    tess_path = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path

SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
DATE_REGEX = re.compile(r"\b(?:\d{1,2}[\-/]){2}\d{2,4}\b")

def detect_and_mask(img, hide_types):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n = len(data["text"])
    out = img.copy()

    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]

        label = None
        if "SSN" in hide_types and SSN_REGEX.search(text):
            label = "SSN"
        elif "DOB" in hide_types and DATE_REGEX.search(text):
            label = "DOB"
        elif "NAME" in hide_types and text.istitle():
            label = "NAME"

        if label:
            cv2.rectangle(out, (x, y), (x+w, y+h), (255, 255, 255), thickness=-1)

            mask_text = "XXXXX"
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = max(0.6, h / 25)  
            thickness = 2
            (tw, th), _ = cv2.getTextSize(mask_text, font, scale, thickness)

            tx = x + (w - tw) // 2
            ty = y + (h + th) // 2

            cv2.putText(out, mask_text, (tx, ty), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

    return out

app = Flask(__name__, template_folder="templates", static_folder=os.path.join(APP_ROOT, "static"))
app.secret_key = "dev-secret"

ALLOWED_IMG = {"png", "jpg", "jpeg"}
ALLOWED_TXT = {"txt"}

def allowed_file(filename, allowed_set):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    file_img = request.files.get("image")
    file_txt = request.files.get("rules")

    if not file_img or not allowed_file(file_img.filename, ALLOWED_IMG):
        flash("Invalid or missing image file")
        return redirect(url_for("index"))

    if not file_txt or not allowed_file(file_txt.filename, ALLOWED_TXT):
        flash("Invalid or missing text file")
        return redirect(url_for("index"))

    img_name = secure_filename(file_img.filename)
    txt_name = secure_filename(file_txt.filename)

    img_path = os.path.join(UPLOAD_DIR, img_name)
    txt_path = os.path.join(UPLOAD_DIR, txt_name)

    file_img.save(img_path)
    file_txt.save(txt_path)

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read().upper()
    hide_types = set()
    if "SSN" in content: hide_types.add("SSN")
    if "DOB" in content: hide_types.add("DOB")
    if "NAME" in content: hide_types.add("NAME")

    img = cv2.imdecode(np.frombuffer(open(img_path, 'rb').read(), np.uint8), cv2.IMREAD_COLOR)
    masked = detect_and_mask(img, hide_types)

    out_name = f"masked_{img_name}.png"
    out_path = os.path.join(RESULT_DIR, out_name)
    cv2.imwrite(out_path, masked)

    result_url = url_for('static', filename=f"results/{out_name}")
    return render_template("index.html", result_url=result_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
