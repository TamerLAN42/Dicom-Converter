# build.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'app.py',
    '--name=DICOM Converter',
    '--onefile',
    '--icon=app_icon.ico',
    '--windowed',
    '--add-data=templates;templates',
    '--add-data=static;static',
    '--add-data=app_icon.ico:.',
    '--clean'
])