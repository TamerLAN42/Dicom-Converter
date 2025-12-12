# utils.py
import os
import numpy as np
import pydicom
from PIL import Image


def convert_dicom_metadata_to_txt(dcm_filename, output_directory):
    """
    Извлекает метаданные из DICOM-отчёта и сохраняет в TXT.
    """
    try:
        dcm_data = pydicom.dcmread(dcm_filename, force=True)
    except:
        return None

    os.makedirs(output_directory, exist_ok=True)
    # Создаём текстовый файл
    base_name = os.path.basename(dcm_filename)
    if '.' in base_name:
        base_name = base_name.rsplit('.', 1)[0]

    txt_filename = os.path.join(output_directory, f"{base_name}_meta.txt")

    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(f"=== DICOM Metadata: {os.path.basename(dcm_filename)} ===\n\n")

        # Основные поля
        fields_to_extract = [
            'PatientName', 'PatientID', 'StudyDate', 'Modality',
            'StudyDescription', 'SeriesDescription', 'SOPClassUID'
        ]

        for field in fields_to_extract:
            if hasattr(dcm_data, field):
                f.write(f"{field}: {getattr(dcm_data, field)}\n")

        f.write("\n--- Все доступные поля ---\n")

        # Все остальные поля (кроме пиксельных данных)
        for elem in dcm_data:
            if hasattr(elem, 'name') and hasattr(elem, 'value'):
                # Пропускаем большие бинарные поля
                if elem.name not in ['Pixel Data', 'Float Pixel Data',
                                     'Double Float Pixel Data']:
                    try:
                        f.write(f"{elem.name}: {elem.value}\n")
                    except:
                        f.write(f"{elem.name}: [binary data]\n")

    return txt_filename

def convert_dcm_to_gif(dcm_data, dcm_filename, output_directory,
                       contrast_factor=1.0, brightness_factor=1.0,
                       duration=200, loop=0):
    """
    Создаёт анимированный GIF из всех слоёв 3D DICOM.

    Args:
        dcm_filename: путь к DICOM файлу
        output_directory: папка для сохранения
        contrast_factor: контрастность
        brightness_factor: яркость
        duration: длительность кадра в мс
        loop: количество повторов (0 = бесконечно)

    Returns:
        str: путь к созданному GIF файлу
    """
    pixel_array = dcm_data.pixel_array.astype(float)
    layers = pixel_array.shape[0]

    frames = []
    for layer_idx in range(layers):
        # Обрабатываем каждый слой
        layer = pixel_array[layer_idx]
        layer = layer * contrast_factor + brightness_factor
        layer = np.clip(layer, 0, 255)
        layer = (layer / np.max(layer)) * 255

        img = Image.fromarray(np.uint8(layer))
        frames.append(img)

    # Сохраняем GIF
    os.makedirs(output_directory, exist_ok=True)
    base_name = os.path.basename(dcm_filename)
    if '.' in base_name:
        base_name = base_name.rsplit('.', 1)[0]

    gif_path = os.path.join(output_directory, f"{base_name}.gif")

    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=True
    )

    return gif_path


def convert_dcm_to_jpg(dcm_filename, output_directory, contrast_factor=1.0, brightness_factor=1.0):
    """
    Convert a DICOM file to a JPEG image.

    Args:
        dcm_filename (str): Filename of the input DICOM file.
        output_directory (str): Directory to save the output JPEG file.
        contrast_factor (float): Factor to adjust contrast.
        brightness_factor (float): Factor to adjust brightness.

    Returns:
        str: Filename of the converted JPEG image.
    """
    try:
        dcm_data = pydicom.dcmread(dcm_filename)
    finally:
        if hasattr(dcm_data, 'fileobj') and dcm_data.fileobj:
            dcm_data.fileobj.close()
    # Если не изображение - извлекаем метаданные
    if not hasattr(dcm_data, 'pixel_array'):
        return convert_dicom_metadata_to_txt(dcm_filename, output_directory)

    pixel_array = dcm_data.pixel_array.astype(float)
    # Если 3d - все слои объединяем в .gif
    if len(pixel_array.shape) == 3:
        return convert_dcm_to_gif(
            dcm_data, dcm_filename,
            output_directory,
            contrast_factor, brightness_factor
        )


    # Adjust contrast and brightness
    pixel_array = pixel_array * contrast_factor + brightness_factor

    # Normalize pixel values
    pixel_array = np.clip(pixel_array, 0, 255)
    pixel_array = (pixel_array / np.max(pixel_array)) * 255

    # Convert to uint8 and create PIL Image
    image = Image.fromarray(np.uint8(pixel_array))

    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Save JPEG file
    base_name = os.path.basename(dcm_filename) + '.jpg'
    jpg_filename = os.path.join(output_directory, base_name)
    image.save(jpg_filename)
    return jpg_filename
