# create-icon.py
from PIL import Image, ImageDraw, ImageFont

def create_programmatic_icon():
    # Увеличиваем до 256x256 для прорисовки, потом уменьшим
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Фон - голубой круг
    draw.ellipse([0, 0, size, size], fill=(70, 130, 180, 255))

    # Белый документ (крупнее)
    doc_width, doc_height = 180, 220
    doc_x = (size - doc_width) // 2
    doc_y = (size - doc_height) // 2

    draw.rounded_rectangle(
        [doc_x, doc_y, doc_x + doc_width, doc_y + doc_height],
        radius=20,
        fill='white',
        outline='white'
    )

    # Буквы DCM крупным планом
    try:
        # Пробуем загрузить жирный шрифт
        font = ImageFont.truetype("arialbd.ttf", 72)  # Bold
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 72)
        except:
            # Fallback - bitmap шрифт
            font = ImageFont.load_default()
            # Масштабируем для bitmap
            font = ImageFont.truetype("arial.ttf", 36)

    # Текст "DCM"
    text = "DCM"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Центрируем текст
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    draw.text((x, y), text, fill=(70, 130, 180), font=font)

    # Уменьшаем до стандартного размера для трея (64x64)
    img = img.resize((64, 64), Image.LANCZOS)
    return img

if __name__ == "__main__":
    img = create_programmatic_icon()
    img.save('app_icon.ico', format='ICO',
         sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])