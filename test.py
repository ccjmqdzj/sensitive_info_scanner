import pytesseract
from PIL import Image
import os
import sys

# 指定 Tesseract 路径（如果需要）
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 使用命令行参数，或者默认使用当前目录下的test.png
if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    image_path = 'test.png'

if not os.path.exists(image_path):
    print(f"错误：文件不存在: {image_path}")
    sys.exit(1)

# 打开图片
try:
    image = Image.open(image_path)
except Exception as e:
    print(f"错误：无法打开图片: {str(e)}")
    sys.exit(1)

# 提取文本
text = pytesseract.image_to_string(image, lang='chi_sim+eng')

# 打印提取的文本
print("提取的文本:")
print(text)
