# app.py
from flask import Flask, render_template, request, send_file, send_from_directory
from utils import convert_dcm_to_jpg
import webbrowser
import threading
import pystray
from create_icon import create_programmatic_icon
import io, zipfile
import shutil
import os, sys
import tempfile

app = Flask(__name__)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')


@app.route('/convert', methods=['POST'])
def convert():
    # Получаем файлы и настройки из формы
    files = request.files.getlist('dicom_files')
    contrast = float(request.form.get('contrast', 1.5))
    brightness = float(request.form.get('brightness', 50))

    dcm_files = []
    for file in files:
        filename = file.filename.lower()

        if filename.endswith('.dcm') or '.' not in filename:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dcm', prefix=file.filename + '_') as tmp:
                file.save(tmp.name)
                dcm_files.append(tmp.name)
        else:
            continue

    jpg_files = []

    for dcm in dcm_files:
        try:
            jpg = convert_dcm_to_jpg(
                dcm,
                output_directory=OUTPUTS_DIR,
                contrast_factor=contrast,
                brightness_factor=brightness
            )
            if jpg:
                jpg_files.append(jpg)
        finally:
            if os.path.exists(dcm):
                os.remove(dcm)

    # Возвращаем результат
    return {'success': True, 'redirect': '/results'}

@app.route('/results')
def results():
    """Показывает все конвертированные файлы"""
    files = []
    output_dir = OUTPUTS_DIR

    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(('.jpg', '.gif', '.txt')):
                files.append(f)

    return render_template('results.html', files=files)


@app.route('/download-all')
def download_all():
    """Скачивает все файлы как ZIP"""
    output_dir = OUTPUTS_DIR

    if not os.path.exists(output_dir):
        return "No files", 404

    # Создаём ZIP в памяти
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in os.listdir(output_dir):
            if file.endswith(('.jpg', '.gif', '.txt')):
                zf.write(os.path.join(output_dir, file), file)

    memory_file.seek(0)

    try:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"Ошибка очистки outputs: {e}")

    # Отправляем ZIP
    return send_file(
        memory_file,
        download_name='converted_files.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

@app.route('/outputs/<filename>')
def serve_output(filename):
    """Раздаёт файлы из папки outputs"""
    return send_from_directory(OUTPUTS_DIR, filename)

@app.route('/')
def index():
    return render_template('index.html')


def on_exit(icon, item):
    """Выход из приложения"""
    icon.stop()
    os._exit(0)


def open_browser():
    """Открыть браузер"""
    webbrowser.open('http://localhost:5000')


def setup_tray():
    """Настройка иконки в трее"""
    image = create_programmatic_icon()

    icon = pystray.Icon(
        "DCM Viewer",
        image,
        "DCM → JPG Converter\nhttp://localhost:5000",
        menu=pystray.Menu(
            pystray.MenuItem("Открыть в браузере", open_browser),
            pystray.MenuItem("Выход", on_exit)
        )
    )
    return icon


if __name__ == '__main__':
    # Запускаем Flask в фоне
    threading.Thread(
        target=lambda: app.run(
            port=5000,
            debug=False,
            use_reloader=False,
            host='127.0.0.1'  # локально, не для сети
        ),
        daemon=True
    ).start()

    open_browser()

    # Запускаем иконку в трее (блокирующий вызов)
    icon = setup_tray()
    icon.run()